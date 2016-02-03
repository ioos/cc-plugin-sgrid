#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest
from pkg_resources import resource_filename as rs

import netCDF4 as nc4
from compliance_checker.base import DSPair
from wicken.netcdf_dogma import NetCDFDogma

from cc_plugin_sgrid.checker_100 import SgridChecker100


class TestSgridChecker100(unittest.TestCase):

    def setUp(self):
        self.check = SgridChecker100()

    def pair(self, path):
        nc = nc4.Dataset(path)
        self.addCleanup(nc.close)
        dg = NetCDFDogma('nc', self.check.beliefs(), nc)
        return DSPair(nc, dg)

    def test_someting(self):
        fp = rs('cc_plugin_sgrid', os.path.join('resources', 'roms.nc'))
        ds = self.pair(fp)
        r = self.check.check_something1(ds)
        self.assertEquals(r.value, (1, 1))
