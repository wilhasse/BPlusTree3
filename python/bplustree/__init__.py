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

        def clear(self):
            """Remove all items from the tree."""
            # C extension doesn't have clear method, so remove keys one by one
            # Use while loop to avoid issues with iterator invalidation
            while len(self) > 0:
                # Get first key and delete it
                for key in self.keys():
                    del self[key]
                    break

        def pop(self, key, *args):
            """Remove and return value for key with optional default."""
            if len(args) > 1:
                raise TypeError(
                    f"pop expected at most 2 arguments, got {len(args) + 1}"
                )
            try:
                value = self[key]
                del self[key]
                return value
            except KeyError:
                if args:
                    return args[0]
                raise

        def popitem(self):
            """Remove and return an arbitrary (key, value) pair."""
            try:
                # Get the first key-value pair
                for key, value in self.items():
                    del self[key]
                    return (key, value)
            except:
                pass
            raise KeyError("popitem(): tree is empty")

        def setdefault(self, key, default=None):
            """Get value for key, setting and returning default if not present."""
            try:
                return self[key]
            except KeyError:
                self[key] = default
                return default

        def update(self, other):
            """Update tree with key-value pairs from other mapping or iterable."""
            if hasattr(other, "items"):
                # other is a mapping (dict-like)
                for key, value in other.items():
                    self[key] = value
            elif hasattr(other, "keys"):
                # other has keys method but no items (like dict.keys())
                for key in other.keys():
                    self[key] = other[key]
            else:
                # other is an iterable of (key, value) pairs
                for key, value in other:
                    self[key] = value

        def copy(self):
            """Create a shallow copy of the tree."""
            new_tree = BPlusTreeMap(capacity=self.capacity)
            for key, value in self.items():
                new_tree[key] = value
            return new_tree

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

# Node classes are internal implementation details, not exported
from .bplus_tree import Node as _Node, LeafNode as _LeafNode, BranchNode as _BranchNode

__version__ = "0.1.0"
__all__ = ["BPlusTreeMap", "get_implementation"]


def get_implementation():
    """Return which implementation is being used."""
    return "C extension" if _using_c_extension else "Pure Python"
