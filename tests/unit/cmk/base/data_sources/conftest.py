#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from contextlib import suppress

import pytest  # type: ignore[import]

from cmk.base.data_sources import ABCChecker, FileCacheConfigurator
from cmk.base.data_sources.agent import AgentChecker
from cmk.base.data_sources.snmp import SNMPChecker


@pytest.fixture(autouse=True)
def reset_mutable_global_state():
    def reset(cls, attr, value):
        # Make sure we are not *adding* any field.
        assert hasattr(cls, attr)
        setattr(cls, attr, value)

    def delete(cls, attr):
        with suppress(AttributeError):
            delattr(cls, attr)

    yield
    delete(AgentChecker, "_use_outdated_persisted_sections")
    delete(SNMPChecker, "_use_outdated_persisted_sections")

    reset(FileCacheConfigurator, "disabled", False)
    reset(FileCacheConfigurator, "maybe", False)
    reset(FileCacheConfigurator, "use_outdated", False)
    reset(ABCChecker, "_use_outdated_persisted_sections", False)
