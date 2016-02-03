#!/usr/bin/env python
# -*- coding: utf-8 -*-
from cc_plugin_sgrid import SgridChecker
from compliance_checker.base import BaseCheck


class SgridChecker100(SgridChecker):
    _cc_spec_version = '1.0.0'
    _cc_description = 'SGRID {} Compliance Checker Plugin'.format(_cc_spec_version)

    def check_something1(self, ds):
        level = BaseCheck.HIGH
        out_of = 1
        score = 1
        messages = ['passed']
        desc = 'Does something'

        return self.make_result(level, score, out_of, desc, messages)
