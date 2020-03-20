#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
"""Background tools required to register a section plugin
"""
from typing import (  # pylint: disable=unused-import
    Any, Generator, List, Optional, Union)
import inspect
import itertools

from cmk.utils.exceptions import MKGeneralException
from cmk.utils.regex import regex
import cmk.base.snmp_utils as snmp_utils
from cmk.base.discovered_labels import HostLabel
from cmk.base.api import PluginName
from cmk.base.api.agent_based.section_types import (
    AgentParseFunction,
    AgentSectionPlugin,
    HostLabelFunction,
    SNMPDetectSpec,
    SNMPParseFunction,
    SNMPSectionPlugin,
)
from cmk.base.api.agent_based.section_types import SNMPTree  # pylint: disable=unused-import


def _validate_parse_function(parse_function):
    # type: (Union[AgentParseFunction, SNMPParseFunction]) -> None
    """Validate the parse functions signature and type"""

    if not inspect.isfunction(parse_function):
        raise TypeError("parse function must be a function: %r" % (parse_function,))

    if inspect.isgeneratorfunction(parse_function):
        raise TypeError("parse function must not be a generator function: %r" % (parse_function,))

    parameters = inspect.signature(parse_function).parameters
    if list(parameters) != ['string_table']:
        raise ValueError("parse function must accept exactly one argument 'string_table'")


def _validate_host_label_function(host_label_function):
    # type: (HostLabelFunction) -> None
    """Validate the host label functions signature and type"""

    if not inspect.isgeneratorfunction(host_label_function):
        raise TypeError("host label function must be a generator function: %r" %
                        (host_label_function,))

    parameters = inspect.signature(host_label_function).parameters
    if list(parameters) not in (['section'], ['_section']):
        raise ValueError("host label function must accept exactly one argument 'section'")


def _validate_supercedings(supercedes):
    # type: (List[PluginName]) -> None
    if not len(supercedes) == len(set(supercedes)):
        raise ValueError("duplicate supercedes entry")


def _validate_detect_spec(detect_spec):
    # type: (SNMPDetectSpec) -> None
    if not (isinstance(detect_spec, list) and
            all(isinstance(element, list) for element in detect_spec)):
        raise TypeError("value of 'detect' keyword must be a list of lists of 3-tuples")

    for atom in itertools.chain(*detect_spec):
        if not isinstance(atom, tuple) or not len(atom) == 3:
            raise TypeError("value of 'detect' keyword must be a list of lists of 3-tuples")
        oid_string, expression, expected_match = atom

        if not isinstance(oid_string, str):
            raise TypeError("value of 'detect' keywords first element must be a string: %r" %
                            (oid_string,))
        if not str(oid_string).startswith('.'):
            raise ValueError("OID in value of 'detect' keyword must start with '.': %r" %
                             (oid_string,))
        snmp_utils.OIDSpec.validate(oid_string.rstrip('.*'))

        if expression is not None:
            try:
                _ = regex(expression)
            except MKGeneralException as exc:
                raise ValueError("invalid regex in value of 'detect' keyword: %s" % exc)

        if not isinstance(expected_match, bool):
            TypeError("value of 'detect' keywords third element must be a boolean: %r" %
                      (expected_match,))


def _noop_host_label_function(section):  # pylint: disable=unused-argument
    # type: (Any) -> Generator[HostLabel, None, None]
    return
    yield  # pylint: disable=unreachable


def _create_host_label_function(host_label_function):
    # type: (Optional[HostLabelFunction]) -> HostLabelFunction
    if host_label_function is None:
        return _noop_host_label_function

    _validate_host_label_function(host_label_function)
    return host_label_function


def _create_supercedes(supercedes):
    # type: (Optional[List[str]]) -> List[PluginName]
    if supercedes is None:
        return []

    supercedes_plugins = [PluginName(n) for n in supercedes]
    _validate_supercedings(supercedes_plugins)

    return sorted(supercedes_plugins)


def create_agent_section_plugin(
    *,
    name,  # type: str
    parsed_section_name=None,  # type: Optional[str]
    parse_function,  # type: AgentParseFunction
    host_label_function=None,  # type: Optional[HostLabelFunction]
    supercedes=None,  # type:  Optional[List[str]]
    forbidden_names,  # type: List[PluginName]
):
    # type: (...) -> AgentSectionPlugin
    """Return an AgentSectionPlugin object after validating and converting the arguments one by one

    For a detailed description of the parameters please refer to the exposed function in the
    'register' namespace of the API.
    """
    # TODO (mo): Well, implement it, and remove pragma below!
    if supercedes is not None:
        raise NotImplementedError("supercedes is not yet available")
    if parsed_section_name is not None:
        raise NotImplementedError("parsed_section_name is not yet available")

    plugin_name = PluginName(name, forbidden_names=forbidden_names)

    _validate_parse_function(parse_function)

    return AgentSectionPlugin(
        plugin_name,
        PluginName(parsed_section_name) if parsed_section_name else plugin_name,  # type: ignore
        parse_function,
        _create_host_label_function(host_label_function),
        _create_supercedes(supercedes),
    )


def create_snmp_section_plugin(
    *,
    name,  # type: str
    parsed_section_name=None,  # type: Optional[str]
    parse_function,  # type: SNMPParseFunction
    host_label_function=None,  # type: Optional[HostLabelFunction]
    supercedes=None,  # type:  Optional[List[str]]
    detect_spec,  # type: SNMPDetectSpec
    trees,  # type: List[SNMPTree]
    forbidden_names,  # type: List[PluginName]
):
    # type: (...) -> SNMPSectionPlugin
    """Return an SNMPSectionPlugin object after validating and converting the arguments one by one

    For a detailed description of the parameters please refer to the exposed function in the
    'register' namespace of the API.
    """
    # TODO (mo): Well, implement it, and remove pragma below!
    if supercedes is not None:
        raise NotImplementedError("supercedes is not yet available")
    if parsed_section_name is not None:
        raise NotImplementedError("parsed_section_name is not yet available")

    plugin_name = PluginName(name, forbidden_names)

    _validate_parse_function(parse_function)
    _validate_detect_spec(detect_spec)

    return SNMPSectionPlugin(
        plugin_name,
        PluginName(parsed_section_name) if parsed_section_name else plugin_name,  # type: ignore
        parse_function,
        _create_host_label_function(host_label_function),
        _create_supercedes(supercedes),
        detect_spec,
        trees,
    )