import logging
from pathlib import Path

import pytest
from netCDF4 import Dataset

from cc_plugin_sgrid import logger
from cc_plugin_sgrid.checker_100 import SgridChecker100

logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


romsnc = (
    Path(__file__).absolute().parent.parent.joinpath("resources", "roms.nc")
)


@pytest.fixture
def check():
    """Load checker."""
    return SgridChecker100()


@pytest.fixture
def nc():
    """Load test data in memory."""
    dset = Dataset(
        romsnc,
        "r+",
        diskless=True,
        persist=False,
    )
    yield dset
    dset.close()


def test_check_grid_variable(check, nc):
    """Test check_grid_variable."""
    r = check.check_grid_variable(nc)
    assert r.value == (1, 1)


def test_check_invalid_grid_variable(check, nc):
    """Test check_invalid_grid_variable."""
    nc.variables["grid"].cf_role = "blah"
    r = check.check_grid_variable(nc)
    assert r.value == (0, 1)


def test_check_mesh_toplogy_grid_variable(check, nc):
    """Test check_mesh_toplogy_grid_variable."""
    nc.variables["grid"].cf_role = "mesh_toplogy"
    r = check.check_grid_variable(nc)
    assert r.value == (0, 1)


def test_check_no_cf_role_variable(check, nc):
    """Test check_no_cf_role_variable."""
    del nc.variables["grid"].cf_role
    r = check.check_grid_variable(nc)
    assert r.value == (0, 1)


def test_check_topology_dimension(check, nc):
    """Test check_topology_dimension."""
    r = check.check_topology_dimension(nc)
    assert r.value == (1, 1)

    nc.variables["grid"].topology_dimension = 0
    r = check.check_topology_dimension(nc)
    assert r.value == (0, 1)

    nc.variables["grid"].topology_dimension = 9
    r = check.check_topology_dimension(nc)
    assert r.value == (0, 1)


def test_check_node_dimension_size(check, nc):
    """Test check_node_dimension_size."""
    r = check.check_node_dimensions_size(nc)
    assert r.value == (1, 1)

    nc.variables["grid"].topology_dimension = 3
    r = check.check_node_dimensions_size(nc)
    assert r.value == (0, 1)

    nc.variables["grid"].topology_dimension = 2
    nc.variables["grid"].node_dimensions = "first second third"
    r = check.check_node_dimensions_size(nc)
    assert r.value == (0, 1)


def test_check_node_dimension_dimensions(check, nc):
    """Test check_node_dimension_dimensions."""
    r = check.check_node_dimensions_dimensions(nc)
    assert r.value == (1, 1)

    nc.variables["grid"].node_dimensions = "hi bye"
    r = check.check_node_dimensions_dimensions(nc)
    assert r.value == (0, 1)


def test_check_face_dimension_size(check, nc):
    """Test check_face_dimension_size."""
    r = check.check_face_dimensions_size(nc)
    assert r.value == (1, 1)

    nc.variables["grid"].topology_dimension = 3
    r = check.check_face_dimensions_size(nc)
    assert r.value == (0, 1)

    nc.variables["grid"].topology_dimension = 2
    nc.variables["grid"].face_dimensions = "first second third"
    r = check.check_face_dimensions_size(nc)
    assert r.value == (0, 1)

    nc.variables["grid"].face_dimensions = "hi: bye (padding: foo)"
    r = check.check_face_dimensions_size(nc)
    assert r.value == (0, 1)


def test_check_face_dimension_dimensions(check, nc):
    """Test check_face_dimension_dimensions."""
    r = check.check_face_dimensions_dimensions(nc)
    assert r.value == (1, 1)

    nc.variables["grid"].face_dimensions = "hi: bye (padding: foo)"
    r = check.check_face_dimensions_dimensions(nc)
    assert r is None  # Size doesn't match, which is a dependency

    nc.variables[
        "grid"
    ].face_dimensions = (
        "xi_rho: xi_psi (padding: NOTCORRECT) eta_rho: eta_psi (padding: both)"
    )
    r = check.check_face_dimensions_dimensions(nc)
    assert r.value == (0, 1)

    nc.variables[
        "grid"
    ].face_dimensions = (
        "xi_rho: xi_psi (NOTPADDING: both) eta_rho: eta_psi (padding: both)"
    )
    r = check.check_face_dimensions_dimensions(nc)
    assert r.value == (0, 1)

    nc.variables[
        "grid"
    ].face_dimensions = (
        "xi_rho: xi_psi (padding: low) eta_rho: eta_psi (padding: high)"
    )
    r = check.check_face_dimensions_dimensions(nc)
    assert r.value == (1, 1)

    # nc.variables['grid'].face_dimensions = 'hi: bye (padding: foo)'
    # r = check.check_face_dimensions_dimensions(nc)
    # assert r is None  # Size doesn't match, which is a dependency
