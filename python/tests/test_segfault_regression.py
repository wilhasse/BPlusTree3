"""
Regression test for segfault bug.
Following TDD: write a failing test that replicates the problem, then fix it.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import bplustree_c

    HAS_C_EXTENSION = True
except ImportError:
    HAS_C_EXTENSION = False


def test_no_segfault_on_large_operations():
    """
    Test that must NOT segfault under any circumstances.
    This test replicates the conditions that cause segfaults.
    """
    if not HAS_C_EXTENSION:
        pytest.skip("C extension not available")

    # This specific test was segfaulting - it must pass
    tree = bplustree_c.BPlusTree(capacity=128)

    # Insert many items (this was causing segfaults)
    for i in range(2000):
        tree[i] = i * 2

    # Verify tree is functional
    assert len(tree) == 2000
    assert tree[0] == 0
    assert tree[1999] == 3998

    # Test iteration (potential source of segfaults)
    keys = list(tree.keys())
    assert len(keys) == 2000
    assert keys[0] == 0
    assert keys[-1] == 1999

    # Test items iteration
    items = list(tree.items())
    assert len(items) == 2000
    assert items[0] == (0, 0)
    assert items[-1] == (1999, 3998)


def test_no_segfault_multiple_trees():
    """Test creating multiple trees doesn't cause segfaults."""
    if not HAS_C_EXTENSION:
        pytest.skip("C extension not available")

    trees = []
    for i in range(10):
        tree = bplustree_c.BPlusTree(capacity=64)
        for j in range(100):
            tree[j] = j * i
        trees.append(tree)

    # Verify all trees work
    for i, tree in enumerate(trees):
        assert len(tree) == 100
        assert tree[0] == 0
        assert tree[99] == 99 * i


def test_no_segfault_stress_iterations():
    """Test that stress iterations don't segfault."""
    if not HAS_C_EXTENSION:
        pytest.skip("C extension not available")

    for iteration in range(5):
        tree = bplustree_c.BPlusTree(capacity=32)

        # Insert items
        for i in range(200):
            tree[i] = i

        # Force iteration
        keys = list(tree.keys())
        items = list(tree.items())

        # Verify
        assert len(keys) == 200
        assert len(items) == 200

        # Clean up
        del tree


if __name__ == "__main__":
    # Run the specific failing tests
    test_no_segfault_on_large_operations()
    test_no_segfault_multiple_trees()
    test_no_segfault_stress_iterations()
    print("✅ All segfault regression tests passed")
