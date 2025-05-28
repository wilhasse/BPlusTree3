#!/usr/bin/env python3
"""
Test to expose the missing invariant check for minimum children
"""

from bplus_tree import BPlusTreeMap
from _invariant_checker import BPlusTreeInvariantChecker


def check_invariants(tree: BPlusTreeMap) -> bool:
    """Helper function to check tree invariants"""
    checker = BPlusTreeInvariantChecker(tree.capacity)
    return checker.check_invariants(tree.root, tree.leaves)


def test_invariant_checker_catches_single_child():
    """Test that invariant checker should catch single-child branch nodes"""
    tree = BPlusTreeMap(capacity=4)

    # Build tree that leads to problematic structure
    for i in range(8):
        tree[i] = f"value_{i}"

    print("After insertions:")
    print(f"Invariants: {check_invariants(tree)}")

    # Force the tree into a state with detailed inspection
    print("\nDeleting items to create problematic structure...")

    for i in [1, 3, 5, 7]:
        del tree[i]
        print(f"After deleting {i}: invariants={check_invariants(tree)}")
        _print_tree_structure(tree.root, 0)

    # This should potentially reveal single-child parents
    for i in [0, 2, 4]:
        del tree[i]
        print(f"After deleting {i}: invariants={check_invariants(tree)}")
        _print_tree_structure(tree.root, 0)


def _print_tree_structure(node, level):
    """Print tree structure to see actual layout"""
    indent = "  " * level
    if node.is_leaf():
        print(f"{indent}Leaf: {len(node.keys)} keys = {node.keys}")
    else:
        print(f"{indent}Branch: {len(node.keys)} keys, {len(node.children)} children")
        if len(node.children) == 1:
            print(f"{indent}*** SINGLE CHILD DETECTED ***")
        for i, child in enumerate(node.children):
            print(f"{indent}Child {i}:")
            _print_tree_structure(child, level + 1)


if __name__ == "__main__":
    test_invariant_checker_catches_single_child()
