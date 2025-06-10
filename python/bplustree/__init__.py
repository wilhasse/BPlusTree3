"""
B+ Tree mapping implementation with optional C extension.

This package provides an ordered key-value mapping based on a B+ tree.
It supports efficient insertion, deletion, lookup, and range queries. If the
optional C extension is available, it is used automatically for improved
performance; otherwise, the pure Python implementation is used.
"""

# Prefer C extension for performance, fallback to Python implementation
_using_c_extension = False

try:
    from . import bplustree_c as _c_ext
except ImportError:
    from .bplus_tree import BPlusTreeMap
else:

    class BPlusTreeMap(_c_ext.BPlusTree):
        """Wrapper around the C extension to provide a consistent API."""

        def __init__(self, capacity=None):
            if capacity is None:
                super().__init__()
            else:
                super().__init__(capacity=capacity)

        def get(self, key, default=None):
            """Get value with default."""
            try:
                return self[key]
            except KeyError:
                return default

        def values(self):
            """Return iterator over values."""
            for key, value in self.items():
                yield value

        @property
        def capacity(self):
            """Return node capacity (from C default)."""
            return 8

        @property
        def root(self):
            """Not exposed by the C extension."""
            raise AttributeError("C extension does not expose internal tree structure")

        @property
        def leaves(self):
            """Not exposed by the C extension."""
            raise AttributeError("C extension does not expose internal tree structure")

    _using_c_extension = True

# Always import Python node classes for compatibility
from .bplus_tree import Node, LeafNode, BranchNode

__version__ = "0.1.0"
__all__ = ["BPlusTreeMap", "Node", "LeafNode", "BranchNode"]


def get_implementation():
    """Return which implementation is being used."""
    return "C extension" if _using_c_extension else "Pure Python"
