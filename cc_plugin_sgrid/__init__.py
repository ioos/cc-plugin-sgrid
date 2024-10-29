"""SGRID Compliance-Checker Plugin."""

import logging

from compliance_checker.base import BaseNCCheck, Result

try:
    from ._version import __version__
except ImportError:
    __version__ = "unknown"


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class SgridChecker(BaseNCCheck):
    """SgridChecker."""

    _cc_spec = "SGRID"
    _cc_url = "https://github.com/ioos/cc-plugin-sgrid"
    _cc_author = "Kyle Wilcox <kyle@axiomdatascience.com>"
    _cc_checker_version = __version__

    @classmethod
    def beliefs(cls):
        """Beliefs."""
        return {}

    @classmethod
    def make_result(cls, level, score, out_of, name, messages):
        """Make results."""
        return Result(level, (score, out_of), name, messages)

    def setup(self, ds):  # noqa: D102
        pass
