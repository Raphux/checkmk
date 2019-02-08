#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# +------------------------------------------------------------------+
# |             ____ _               _        __  __ _  __           |
# |            / ___| |__   ___  ___| | __   |  \/  | |/ /           |
# |           | |   | '_ \ / _ \/ __| |/ /   | |\/| | ' /            |
# |           | |___| | | |  __/ (__|   <    | |  | | . \            |
# |            \____|_| |_|\___|\___|_|\_\___|_|  |_|_|\_\           |
# |                                                                  |
# | Copyright Mathias Kettner 2014             mk@mathias-kettner.de |
# +------------------------------------------------------------------+
#
# This file is part of Check_MK.
# The official homepage is at http://mathias-kettner.de/check_mk.
#
# check_mk is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# tails. You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    Float,
    TextAscii,
    Tuple,
)

from cmk.gui.plugins.wato import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersApplications,
)


@rulespec_registry.register
class RulespecCheckgroupParametersMssqlPageActivity(CheckParameterRulespecWithItem):
    @property
    def group(self):
        return RulespecGroupCheckParametersApplications

    @property
    def check_group_name(self):
        return "mssql_page_activity"

    @property
    def title(self):
        return _("MSSQL Page Activity")

    @property
    def match_type(self):
        return "dict"

    @property
    def parameter_valuespec(self):
        return Dictionary(
            title=_("Page Activity Levels"),
            elements=[
                ("page_reads/sec",
                 Tuple(
                     title=_("Reads/sec"),
                     elements=[
                         Float(title=_("warning at"), unit=_("/sec")),
                         Float(title=_("critical at"), unit=_("/sec")),
                     ],
                 )),
                ("page_writes/sec",
                 Tuple(
                     title=_("Writes/sec"),
                     elements=[
                         Float(title=_("warning at"), unit=_("/sec")),
                         Float(title=_("critical at"), unit=_("/sec")),
                     ],
                 )),
                ("page_lookups/sec",
                 Tuple(
                     title=_("Lookups/sec"),
                     elements=[
                         Float(title=_("warning at"), unit=_("/sec")),
                         Float(title=_("critical at"), unit=_("/sec")),
                     ],
                 )),
            ],
        )

    @property
    def item_spec(self):
        return TextAscii(title=_("Service descriptions"), allow_empty=False)
