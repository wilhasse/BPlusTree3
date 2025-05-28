#!/usr/bin/env python3
"""
Simple test for the single-child parent edge case
"""

import pytest
from bplus_tree import BPlusTreeMap


def test_single_child_parent_handled():
    """Test that single-child parent case doesn't crash"""
    tree = BPlusTreeMap(capacity=4)  # Small capacity to force structure

    # Build tree and delete to trigger the edge case
    for i in range(8):
        tree[i] = f"value_{i}"

    # Delete in pattern that creates single-child parents
    for i in [1, 3, 5, 7, 0, 2, 4]:
        del tree[i]

    # This should not crash - just handle it gracefully
    assert len(tree) == 1
    assert tree[6] == "value_6"


if __name__ == "__main__":
    test_single_child_parent_handled()
    print("✅ Test passed - single child parent handled gracefully")
