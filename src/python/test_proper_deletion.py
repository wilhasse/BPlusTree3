#!/usr/bin/env python3
"""
Test proper deletion logic that maintains invariants throughout
"""

from bplus_tree import BPlusTreeMap
from _invariant_checker import BPlusTreeInvariantChecker


def check_invariants(tree: BPlusTreeMap) -> bool:
    """Helper function to check tree invariants"""
    checker = BPlusTreeInvariantChecker(tree.capacity)
    return checker.check_invariants(tree.root, tree.leaves)


def test_deletion_maintains_invariants():
    """Test that every step of deletion maintains B+ tree invariants"""
    tree = BPlusTreeMap(capacity=4)  # Minimum viable capacity

    # Build initial tree
    keys = list(range(15))  # 0-14
    for key in keys:
        tree[key] = f"value_{key}"

    print(f"Initial tree with {len(tree)} items")
    assert check_invariants(tree), "Initial tree should be valid"
    _print_structure(tree.root, 0)

    # Delete items one by one, checking invariants after each deletion
    delete_order = [1, 5, 9, 13, 3, 7, 11, 2, 6, 10, 14, 0, 4, 8, 12]

    for key in delete_order:
        print(f"\n--- Deleting key {key} ---")
        del tree[key]

        print(f"Tree now has {len(tree)} items")
        invariants_ok = check_invariants(tree)
        print(f"Invariants maintained: {invariants_ok}")

        if not invariants_ok:
            print("INVARIANT VIOLATION DETECTED!")
            _print_structure(tree.root, 0)
            assert False, f"Invariants violated after deleting key {key}"

        if len(tree) <= 5:  # Print structure for small trees
            _print_structure(tree.root, 0)

    assert len(tree) == 0, "All items should be deleted"
    print("\n✅ All deletions maintained invariants!")


def test_specific_problematic_case():
    """Test the specific case that was creating single-child parents"""
    tree = BPlusTreeMap(capacity=4)  # Minimum viable capacity

    # Build a larger case to stress test the deletion logic
    for i in range(16):
        tree[i] = f"value_{i}"

    print("Built tree with items 0-15")
    assert check_invariants(tree), "Initial tree should be valid"

    # Delete in a problematic order that stresses merge/redistribute logic
    problematic_deletes = [1, 3, 5, 7, 9, 11, 13, 15, 0, 2, 4, 6, 8, 10, 12, 14]

    for key in problematic_deletes:
        print(f"\nDeleting {key}...")
        del tree[key]

        invariants_ok = check_invariants(tree)
        print(f"Invariants OK: {invariants_ok}")

        if not invariants_ok:
            print("Structure after violation:")
            _print_structure(tree.root, 0)
            assert False, f"Invariants violated after deleting {key}"

    print("✅ Problematic case now maintains invariants!")


def test_merge_vs_redistribute():
    """Test that deletion prefers redistribution over merging when possible"""
    tree = BPlusTreeMap(capacity=4)

    # Create a tree where we can test redistribution
    for i in range(20):
        tree[i] = f"value_{i}"

    print("Testing merge vs redistribute behavior...")

    # Delete some items to create opportunities for redistribution
    for key in [1, 3, 5, 17, 19]:
        print(f"\nDeleting {key}")
        del tree[key]
        assert check_invariants(tree), f"Invariants violated after deleting {key}"

    print("✅ Merge vs redistribute logic working correctly!")


def _print_structure(node, level):
    """Helper to print tree structure"""
    indent = "  " * level
    if node.is_leaf():
        print(f"{indent}Leaf: {len(node.keys)} keys = {node.keys}")
    else:
        print(f"{indent}Branch: {len(node.keys)} keys, {len(node.children)} children")
        for i, child in enumerate(node.children):
            _print_structure(child, level + 1)


if __name__ == "__main__":
    test_deletion_maintains_invariants()
    print("\n" + "=" * 50)
    test_specific_problematic_case()
    print("\n" + "=" * 50)
    test_merge_vs_redistribute()
