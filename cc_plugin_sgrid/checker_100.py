#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from cc_plugin_sgrid import SgridChecker, logger
from compliance_checker.base import BaseCheck


class Sge(Exception):
    pass


class SgridChecker100(SgridChecker):

    _cc_spec_version = '1.0.0'
    _cc_description = 'SGRID {} compliance-checker'.format(_cc_spec_version)

    METHODS_REGEX = re.compile('(\w+: *\w+) \((\w+: *\w+)\) *')
    PADDING_TYPES = [ "none", "low", "high", "both" ]

    def check_something1(self, ds):
        level = BaseCheck.HIGH
        score = 1
        out_of = 1
        messages = ['passed']
        desc = 'Does something'

        return self.make_result(level, score, out_of, desc, messages)

    def check_grid_variable(self, ds):
        level = BaseCheck.HIGH
        score = 0
        out_of = 1
        messages = []
        desc = 'grid variable exists'

        grids = ds.get_variables_by_attributes(cf_role='grid_topology')
        if len(grids) == 1:
            score += 1
        elif len(grids) > 1:
            m = ('Only one variable with the attribute name "cf_role" '
                 'and value of "grid_toplogy" is allowed')
            messages.append(m)
        elif len(grids) < 1:
            m = ('A variable with the attribute name "cf_role" '
                 'and value of "grid_toplogy" must be present')
            messages.append(m)

        return self.make_result(level, score, out_of, desc, messages)

    def check_topology_dimension(self, ds):
        level = BaseCheck.HIGH
        score = 0
        out_of = 1
        messages = []
        desc = 'grid\'s topology_dimension attribute is 2 or 3'

        try:
            grid = ds.get_variables_by_attributes(cf_role='grid_topology')[0]
            assert grid.topology_dimension in [2, 3]
        except IndexError:
            # No grid variable, just skip the test... there are larger issues
            return None
        except AttributeError:
            m = ('"topology_dimension" attribute does not exists on grid')
            messages.append(m)
        except AssertionError:
            m = ('"topology_dimension" attribute must be equal to 2 or 3')
            messages.append(m)
        else:
            score += 1

        return self.make_result(level, score, out_of, desc, messages)

    def check_node_dimensions_size(self, ds):
        level = BaseCheck.HIGH
        score = 0
        out_of = 1
        messages = []
        desc = 'grid\'s node_dimensions attribute must be of valid length'

        # DEPENDENCIES
        # Skip if no topology_dimension
        dep = self.check_topology_dimension(ds)
        if not dep or dep.value[0] != dep.value[1]:
            return None

        try:
            grid = ds.get_variables_by_attributes(cf_role='grid_topology')[0]
            nds = grid.node_dimensions.split(' ')
            assert len(nds) == grid.topology_dimension
        except IndexError:
            # No grid variable, just skip the test... there are larger issues
            return None
        except AttributeError:
            m = ('"node_dimensions" attribute does not exists on grid')
            messages.append(m)
        except AssertionError:
            m = ('length of "node_dimensions" attribute must be equal to '
                 '"topology_dimension" attribute')
            messages.append(m)
        else:
            score += 1

        return self.make_result(level, score, out_of, desc, messages)

    def check_node_dimensions_dimensions(self, ds):
        level = BaseCheck.HIGH
        score = 0
        out_of = 1
        messages = []
        desc = 'grid\'s node_dimensions members must match actual dimensions'

        try:
            grid = ds.get_variables_by_attributes(cf_role='grid_topology')[0]
            nds = grid.node_dimensions.split(' ')
            for n in nds:
                assert n in ds.dimensions.keys()
        except IndexError:
            # No grid variable, just skip the test... there are larger issues
            return None
        except AttributeError:
            # No node_dimensions attribute... there are larger issues
            return None
        except AssertionError:
            m = '"node_dimensions" member "{}" is not a dimension'.format(n)
            messages.append(m)
        else:
            score += 1

        return self.make_result(level, score, out_of, desc, messages)

    def check_face_dimensions_size(self, ds):
        level = BaseCheck.HIGH
        score = 0
        out_of = 1
        messages = []
        desc = 'grid\'s face_dimensions attribute must be of valid length'

        # DEPENDENCIES
        # Skip if no topology_dimension
        dep = self.check_topology_dimension(ds)
        if not dep or dep.value[0] != dep.value[1]:
            return None

        try:
            grid = ds.get_variables_by_attributes(cf_role='grid_topology')[0]
            if not hasattr(grid, 'face_dimensions'):
                raise Sge('"face_dimensions" attribute does not exists on grid')

            face_dims = self.METHODS_REGEX.findall(grid.face_dimensions)
            if len(face_dims) != grid.topology_dimension:
                m = ('length of "face_dimensions" attribute must be equal to '
                     '"topology_dimension" attribute')
                raise Sge(m)
        except Sge as sge:
            logger.debug(sge)
            messages.append(str(sge))
        else:
            score += 1

        return self.make_result(level, score, out_of, desc, messages)

    def check_face_dimensions_dimensions(self, ds):
        level = BaseCheck.HIGH
        score = 0
        out_of = 1
        messages = []
        desc = 'grid\'s face_dimensions members must match actual dimensions'

        # DEPENDENCIES
        # Skip if no topology_dimension
        dep = self.check_topology_dimension(ds)
        if not dep or dep.value[0] != dep.value[1]:
            return None
        # Skip if size doesn't match topology_dimension
        dep = self.check_face_dimensions_size(ds)
        if not dep or dep.value[0] != dep.value[1]:
            return None

        try:
            grid = ds.get_variables_by_attributes(cf_role='grid_topology')[0]
            if not hasattr(grid, 'face_dimensions'):
                raise Sge('Could not parse the "face_dimensions" attribute')

            face_dims = self.METHODS_REGEX.findall(grid.face_dimensions)
            if len(face_dims) != grid.topology_dimension:
                raise Sge('Could not parse the "face_dimensions" attribute')

            # face_dimension1: node_dimension1 (padding: type1)
            for member in face_dims:
                fn, pad = member
                # face_dimension1: node_dimension1
                fd, nd = fn.split(':')
                if fd.strip() not in ds.dimensions:
                    raise Sge('"face" dimension "{}" not found'.format(fd))
                if fd.strip() not in ds.dimensions:
                    raise Sge('"node" dimension "{}" not found'.format(nd))

                # padding: type1
                pad_str, pad_type = pad.split(':')
                if pad_str.strip().lower() != 'padding':
                    raise Sge('key must be equal to "padding", got "{}"'.format(pad_str.strip()))
                if pad_type.strip().lower() not in self.PADDING_TYPES:
                    raise Sge('padding type "{}"" not allowed. Must be in {}'.format(pad_type.strip(), self.PADDING_TYPES))
        except Sge as sge:
            logger.debug(sge)
            messages.append(str(sge))
        else:
            score += 1

        return self.make_result(level, score, out_of, desc, messages)
