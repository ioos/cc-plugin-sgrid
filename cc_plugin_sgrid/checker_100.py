"""SGRID Checker."""

import re

from compliance_checker.base import BaseCheck

from cc_plugin_sgrid import SgridChecker, logger


class SgridError(Exception):
    """SGRID Error."""


class SgridChecker100(SgridChecker):
    """SgridChecker 1.0.0."""

    _cc_spec_version = "1.0.0"
    _cc_description = f"SGRID {_cc_spec_version} compliance-checker"

    METHODS_REGEX = re.compile(r"(\w+: *\w+) \((\w+: *\w+)\) *")
    PADDING_TYPES = ("none", "low", "high", "both")

    def check_something1(self):
        """Check something1."""
        level = BaseCheck.HIGH
        score = 1
        out_of = 1
        messages = ["passed"]
        desc = "Does something"

        return self.make_result(level, score, out_of, desc, messages)

    def check_grid_variable(self, ds):
        """Check grid variable."""
        level = BaseCheck.HIGH
        score = 0
        out_of = 1
        messages = []
        desc = "grid variable exists"

        grids = ds.get_variables_by_attributes(cf_role="grid_topology")
        if len(grids) == 1:
            score += 1
        elif len(grids) > 1:
            m = 'Only one variable with the attribute name "cf_role" and value of "grid_toplogy" is allowed'
            messages.append(m)
        elif len(grids) < 1:
            m = 'A variable with the attribute name "cf_role" and value of "grid_toplogy" must be present'
            messages.append(m)

        return self.make_result(level, score, out_of, desc, messages)

    def check_topology_dimension(self, ds):
        """Check topology dimension."""
        level = BaseCheck.HIGH
        score = 0
        out_of = 1
        messages = []
        desc = "grid's topology_dimension attribute is 2 or 3"

        try:
            grid = ds.get_variables_by_attributes(cf_role="grid_topology")[0]
            if grid.topology_dimension not in [2, 3]:
                raise SgridError
        except IndexError:
            # No grid variable, just skip the test... there are larger issues
            return None
        except AttributeError:
            m = '"topology_dimension" attribute does not exists on grid'
            messages.append(m)
        except SgridError:
            m = '"topology_dimension" attribute must be equal to 2 or 3'
            messages.append(m)
        else:
            score += 1

        return self.make_result(level, score, out_of, desc, messages)

    def check_node_dimensions_size(self, ds):
        """Check node dimensions size."""
        level = BaseCheck.HIGH
        score = 0
        out_of = 1
        messages = []
        desc = "grid's node_dimensions attribute must be of valid length"

        # DEPENDENCIES
        # Skip if no topology_dimension
        dep = self.check_topology_dimension(ds)
        if not dep or dep.value[0] != dep.value[1]:
            return None

        try:
            grid = ds.get_variables_by_attributes(cf_role="grid_topology")[0]
            nds = grid.node_dimensions.split(" ")
            if len(nds) != grid.topology_dimension:
                raise SgridError
        except SgridError:
            m = 'length of "node_dimensions" attribute must be equal to "topology_dimension" attribute'
            messages.append(m)
        except IndexError:
            # No grid variable, just skip the test... there are larger issues
            return None
        except AttributeError:
            m = '"node_dimensions" attribute does not exists on grid'
            messages.append(m)
        else:
            score += 1

        return self.make_result(level, score, out_of, desc, messages)

    def check_node_dimensions_dimensions(self, ds):
        """Check node dimensions dimensions."""
        level = BaseCheck.HIGH
        score = 0
        out_of = 1
        messages = []
        desc = "grid's node_dimensions members must match actual dimensions"

        try:
            grid = ds.get_variables_by_attributes(cf_role="grid_topology")[0]
            nds = grid.node_dimensions.split(" ")
            for n in nds:
                if n not in ds.dimensions:
                    raise SgridError
        except SgridError:
            m = f'"node_dimensions" member "{n}" is not a dimension'
            messages.append(m)
        except IndexError:
            # No grid variable, just skip the test... there are larger issues
            return None
        except AttributeError:
            # No node_dimensions attribute... there are larger issues
            return None
        else:
            score += 1

        return self.make_result(level, score, out_of, desc, messages)

    def check_face_dimensions_size(self, ds):
        """Check face dimensions size."""
        level = BaseCheck.HIGH
        score = 0
        out_of = 1
        messages = []
        desc = "grid's face_dimensions attribute must be of valid length"

        # DEPENDENCIES
        # Skip if no topology_dimension
        dep = self.check_topology_dimension(ds)
        if not dep or dep.value[0] != dep.value[1]:
            return None

        try:
            grid = ds.get_variables_by_attributes(cf_role="grid_topology")[0]
            if not hasattr(grid, "face_dimensions"):
                msg = '"face_dimensions" attribute does not exists on grid'
                raise SgridError(msg)

            face_dims = self.METHODS_REGEX.findall(grid.face_dimensions)
            if len(face_dims) != grid.topology_dimension:
                m = 'length of "face_dimensions" attribute must be equal to "topology_dimension" attribute'
                raise SgridError(m)
        except SgridError as sge:
            logger.debug(sge)
            messages.append(str(sge))
        else:
            score += 1

        return self.make_result(level, score, out_of, desc, messages)

    def check_face_dimensions_dimensions(self, ds):  # noqa: C901
        """Check face dimensions dimensions."""
        level = BaseCheck.HIGH
        score = 0
        out_of = 1
        messages = []
        desc = "grid's face_dimensions members must match actual dimensions"

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
            grid = ds.get_variables_by_attributes(cf_role="grid_topology")[0]
            if not hasattr(grid, "face_dimensions"):
                msg = 'Could not parse the "face_dimensions" attribute'
                raise SgridError(msg)

            face_dims = self.METHODS_REGEX.findall(grid.face_dimensions)
            if len(face_dims) != grid.topology_dimension:
                msg = 'Could not parse the "face_dimensions" attribute'
                raise SgridError(msg)

            # face_dimension1: node_dimension1 (padding: type1)
            for member in face_dims:
                fn, pad = member
                # face_dimension1: node_dimension1
                fd, nd = fn.split(":")
                if fd.strip() not in ds.dimensions:
                    msg = f'"face" dimension "{fd}" not found'
                    raise SgridError(msg)
                if fd.strip() not in ds.dimensions:
                    msg = f'"node" dimension "{nd}" not found'
                    raise SgridError(msg)

                # padding: type1
                pad_str, pad_type = pad.split(":")
                if pad_str.strip().lower() != "padding":
                    msg = f'key must be equal to "padding", got "{pad_str.strip()}"'
                    raise SgridError(msg)
                if pad_type.strip().lower() not in self.PADDING_TYPES:
                    msg = f'padding type "{pad_type.strip()}"" not allowed. Must be in {self.PADDING_TYPES}'
                    raise SgridError(msg)
        except SgridError as sge:
            logger.debug(sge)
            messages.append(str(sge))
        else:
            score += 1

        return self.make_result(level, score, out_of, desc, messages)
