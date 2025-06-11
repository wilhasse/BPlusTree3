"""
B+ Tree package.

This package provides a high-performance B+ tree implementation with
optional C extension for improved performance.
"""

# Re-export from the subpackage
from bplustree import BPlusTreeMap, Node, LeafNode, BranchNode, get_implementation

__version__ = "0.1.0"
__all__ = ["BPlusTreeMap", "Node", "LeafNode", "BranchNode", "get_implementation"]