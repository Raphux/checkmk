#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import ast
from multiprocessing.pool import ThreadPool
import sys

from pathlib2 import Path
import requests
import urllib3  # type: ignore[import]

import cmk.utils.version as cmk_version
import cmk.utils.site
from cmk.utils.regex import regex
from cmk.utils.exceptions import MKException

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AggregationData(object):
    def __init__(self, bi_rawdata, config, error):
        super(AggregationData, self).__init__()
        self._bi_rawdata = bi_rawdata
        self._error = error

        self._output = []
        self._options = config.get("options", {})
        self._assignments = config.get("assignments", {})
        self._missing_sites = []
        self._missing_aggr = []
        self._aggregation_targets = {}

    @property
    def bi_rawdata(self):
        return self._bi_rawdata

    @property
    def missing_aggr(self):
        return self._missing_aggr

    @property
    def missing_sites(self):
        return self._missing_sites

    @property
    def error(self):
        return self._error

    @property
    def output(self):
        return self._output

    def evaluate(self):
        if not self._bi_rawdata:
            return

        self._missing_sites = self._bi_rawdata["missing_sites"]
        self._missing_aggr = self._bi_rawdata["missing_aggr"]

        for aggr_row in self._bi_rawdata["rows"]:
            aggr_tree = aggr_row["tree"]
            self._rewrite_aggregation(aggr_tree)
            self._process_assignments(aggr_tree)

        # Output result
        for target_host, aggregations in self._aggregation_targets.iteritems():
            if target_host is None:
                self._output.append("<<<<>>>>")
            else:
                self._output.append("<<<<%s>>>>" % target_host)

            self._output.append("<<<bi_aggregation:sep(0)>>>")
            self._output.append(repr(aggregations))

    def _rewrite_aggregation(self, aggr_tree):
        aggr_state = aggr_tree["aggr_state"]
        aggr_state["state_computed_by_agent"] = aggr_state["state"]
        if aggr_state["in_downtime"] and "state_scheduled_downtime" in self._options:
            aggr_state["state_computed_by_agent"] = self._options["state_scheduled_downtime"]

        if aggr_state["acknowledged"] and "state_acknowledged" in self._options:
            aggr_state["state_computed_by_agent"] = self._options["state_acknowledged"]

    def _process_assignments(self, aggr):
        aggr_name = aggr["aggr_name"]
        if not self._assignments:
            self._aggregation_targets.setdefault(None, {})[aggr_name] = aggr
            return

        if "querying_host" in self._assignments:
            self._aggregation_targets.setdefault(None, {})[aggr_name] = aggr

        if "affected_hosts" in self._assignments:
            for _site, hostname in aggr["aggr_hosts"]:
                self._aggregation_targets.setdefault(hostname, {})[aggr_name] = aggr

        for pattern, target_host in self._assignments.get("regex", []):
            if regex(pattern).match(aggr_name):
                self._aggregation_targets.setdefault(target_host, {})[aggr_name] = aggr


class RawdataException(MKException):
    pass


class AggregationRawdataGenerator(object):
    def __init__(self, config):
        super(AggregationRawdataGenerator, self).__init__()
        self._config = config

        self._credentials = config["credentials"]
        if self._credentials == "automation":
            self._username = self._credentials

            secret_file_path = Path(
                cmk.utils.paths.var_dir) / "web" / self._username / "automation.secret"

            with secret_file_path.open(encoding="utf-8") as f:
                self._secret = f.read()
        else:
            self._username, self._secret = self._credentials[1]

        site_config = config["site"]

        if site_config == "local":
            self._site_url = "http://localhost:%d/%s" % (cmk.utils.site.get_apache_port(),
                                                         cmk_version.omd_site())
        else:
            self._site_url = site_config[1]

        self._errors = []

    def generate_data(self):
        try:
            response_text = self._fetch_aggregation_data()
            rawdata = self._parse_response_text(response_text)
            return AggregationData(rawdata, self._config, None)
        except RawdataException as e:
            return AggregationData(None, self._config, str(e))
        except requests.exceptions.RequestException as e:
            return AggregationData(None, self._config, "Request Error %s" % e)

    def _fetch_aggregation_data(self):
        response = requests.post("%s/check_mk/webapi.py?action=get_bi_aggregations" %
                                 self._site_url,
                                 data={
                                     "_username": self._username,
                                     "_secret": self._secret,
                                     "request": repr({"filter": self._config.get("filter", {})}),
                                     "request_format": "python",
                                     "output_format": "python"
                                 })
        response.raise_for_status()
        return response.text

    def _parse_response_text(self, response_text):
        try:
            rawdata = ast.literal_eval(response_text)
        except (ValueError, SyntaxError):  # ast.literal_eval
            if "automation secret" in response_text:
                raise RawdataException(
                    "Error: Unable to parse data from monitoring instance. Please check the login credentials"
                )
            else:
                raise RawdataException("Error: Unable to parse data from monitoring instance")

        if not isinstance(rawdata, dict):
            raise RawdataException("Error: Unable to process parsed data from monitoring instance")

        result_code = rawdata.get("result_code")
        if result_code is None:
            raise RawdataException("API Error: No error description available")

        if result_code != 0:
            raise RawdataException("API Error: %r" % (rawdata,))

        return rawdata["result"]


class AggregationOutputRenderer(object):
    def render(self, aggregation_data_results):
        connection_info_fields = ["missing_sites", "missing_aggr", "generic_errors"]
        connection_info = {}
        for field in connection_info_fields:
            connection_info[field] = set()

        output = []
        for aggregation_result in aggregation_data_results:
            aggregation_result.evaluate()
            connection_info["missing_aggr"].update(set(aggregation_result.missing_aggr))
            connection_info["missing_sites"].update(set(aggregation_result.missing_sites))
            if aggregation_result.error:
                connection_info["generic_errors"].add(aggregation_result.error)
            output.extend(aggregation_result.output)

        if not output:
            sys.stderr.write("Agent error(s): %s" % "\n".join(connection_info["generic_errors"]))
            sys.exit(1)

        sys.stdout.write("<<<bi_aggregation_connection:sep(0)>>>\n")
        for field in connection_info_fields:
            connection_info[field] = list(connection_info[field])
        sys.stdout.write(repr(connection_info) + "\n")

        output.append("<<<<>>>>\n")
        sys.stdout.write("\n".join(output))


def query_data(config):
    output_generator = AggregationRawdataGenerator(config)
    return output_generator.generate_data()


def main():
    try:
        # Config is a list of site connections
        config = ast.literal_eval(sys.stdin.read())
        p = ThreadPool()
        results = p.map(query_data, config)
        AggregationOutputRenderer().render(results)
    except Exception as e:
        sys.stderr.write("%s" % e)
        return 1
    return 0