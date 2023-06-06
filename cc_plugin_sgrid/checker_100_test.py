#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
import logging
import unittest
import tempfile
from pkg_resources import resource_filename as rs

import netCDF4 as nc4

from cc_plugin_sgrid.checker_100 import SgridChecker100
from cc_plugin_sgrid import logger
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class TestSgridChecker100(unittest.TestCase):

    def setUp(self):
        self.check = SgridChecker100()

    def nc(self, ncpath):
        _, tf = tempfile.mkstemp(suffix='.nc')
        shutil.copy(ncpath, tf)
        ncd = nc4.Dataset(tf, 'r+')
        self.addCleanup(ncd.close)
        self.addCleanup(lambda: os.remove(tf))
        return ncd

    def test_check_grid_variable(self):
        ncd = self.nc(rs('cc_plugin_sgrid', os.path.join('resources', 'roms.nc')))

        r = self.check.check_grid_variable(ncd)
        assert r.value == (1, 1)

    def test_check_invalid_grid_variable(self):
        ncd = self.nc(rs('cc_plugin_sgrid', os.path.join('resources', 'roms.nc')))
        ncd.variables['grid'].cf_role = 'blah'
        r = self.check.check_grid_variable(ncd)
        assert r.value == (0, 1)

    def test_check_mesh_toplogy_grid_variable(self):
        ncd = self.nc(rs('cc_plugin_sgrid', os.path.join('resources', 'roms.nc')))
        ncd.variables['grid'].cf_role = 'mesh_toplogy'
        r = self.check.check_grid_variable(ncd)
        assert r.value == (0, 1)


    def test_check_no_cf_role_variable(self):
        ncd = self.nc(rs('cc_plugin_sgrid', os.path.join('resources', 'roms.nc')))
        del ncd.variables['grid'].cf_role
        r = self.check.check_grid_variable(ncd)
        assert r.value == (0, 1)        

    def test_check_topology_dimension(self):
        ncd = self.nc(rs('cc_plugin_sgrid', os.path.join('resources', 'roms.nc')))

        r = self.check.check_topology_dimension(ncd)
        assert r.value == (1, 1)

        ncd.variables['grid'].topology_dimension = 0
        r = self.check.check_topology_dimension(ncd)
        assert r.value == (0, 1)

        ncd.variables['grid'].topology_dimension = 9
        r = self.check.check_topology_dimension(ncd)
        assert r.value == (0, 1)

    def test_check_node_dimension_size(self):
        ncd = self.nc(rs('cc_plugin_sgrid', os.path.join('resources', 'roms.nc')))

        r = self.check.check_node_dimensions_size(ncd)
        assert r.value == (1, 1)

        ncd.variables['grid'].topology_dimension = 3
        r = self.check.check_node_dimensions_size(ncd)
        assert r.value == (0, 1)

        ncd.variables['grid'].topology_dimension = 2
        ncd.variables['grid'].node_dimensions = 'first second third'
        r = self.check.check_node_dimensions_size(ncd)
        assert r.value == (0, 1)

    def test_check_node_dimension_dimensions(self):
        ncd = self.nc(rs('cc_plugin_sgrid', os.path.join('resources', 'roms.nc')))

        r = self.check.check_node_dimensions_dimensions(ncd)
        assert r.value == (1, 1)

        ncd.variables['grid'].node_dimensions = 'hi bye'
        r = self.check.check_node_dimensions_dimensions(ncd)
        assert r.value == (0, 1)

    def test_check_face_dimension_size(self):
        ncd = self.nc(rs('cc_plugin_sgrid', os.path.join('resources', 'roms.nc')))

        r = self.check.check_face_dimensions_size(ncd)
        assert r.value == (1, 1)

        ncd.variables['grid'].topology_dimension = 3
        r = self.check.check_face_dimensions_size(ncd)
        assert r.value == (0, 1)

        ncd.variables['grid'].topology_dimension = 2
        ncd.variables['grid'].face_dimensions = 'first second third'
        r = self.check.check_face_dimensions_size(ncd)
        assert r.value == (0, 1)

        ncd.variables['grid'].face_dimensions = 'hi: bye (padding: foo)'
        r = self.check.check_face_dimensions_size(ncd)
        assert r.value == (0, 1)

    def test_check_face_dimension_dimensions(self):
        ncd = self.nc(rs('cc_plugin_sgrid', os.path.join('resources', 'roms.nc')))

        r = self.check.check_face_dimensions_dimensions(ncd)
        assert r.value == (1, 1)

        ncd.variables['grid'].face_dimensions = 'hi: bye (padding: foo)'
        r = self.check.check_face_dimensions_dimensions(ncd)
        assert r is None  # Size doesn't match, which is a dependency

        ncd.variables['grid'].face_dimensions = 'xi_rho: xi_psi (padding: NOTCORRECT) eta_rho: eta_psi (padding: both)'
        r = self.check.check_face_dimensions_dimensions(ncd)
        assert r.value == (0, 1)

        ncd.variables['grid'].face_dimensions = 'xi_rho: xi_psi (NOTPADDING: both) eta_rho: eta_psi (padding: both)'
        r = self.check.check_face_dimensions_dimensions(ncd)
        assert r.value == (0, 1)

        ncd.variables['grid'].face_dimensions = 'xi_rho: xi_psi (padding: low) eta_rho: eta_psi (padding: high)'
        r = self.check.check_face_dimensions_dimensions(ncd)
        assert r.value == (1, 1)

        #ncd.variables['grid'].face_dimensions = 'hi: bye (padding: foo)'
        #r = self.check.check_face_dimensions_dimensions(ncd)
        #assert r is None  # Size doesn't match, which is a dependency
