"""
Test cases based on patterns discovered by fuzz testing.

These tests exercise specific operation sequences that were identified
during fuzz testing as potentially stressful to the B+ tree implementation.
"""

import pytest
import sys
import os

# Fix import path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bplus_tree import BPlusTreeMap
from tests._invariant_checker import BPlusTreeInvariantChecker


def check_invariants(tree: BPlusTreeMap) -> bool:
    """Helper function to check tree invariants"""
    checker = BPlusTreeInvariantChecker(tree.capacity)
    return checker.check_invariants(tree.root, tree.leaves)


class TestFuzzDiscoveredPatterns:
    """Test cases based on patterns discovered during fuzz testing"""

    def test_rapid_deletion_followed_by_insertion(self):
        """
        Test rapid deletion pattern followed by insertion.

        This pattern was discovered during fuzz testing and exercises
        the tree's ability to handle multiple deletions followed by
        new insertions, which can stress rebalancing logic.
        """
        tree = BPlusTreeMap(capacity=4)

        # Pre-populate with some keys to create a multi-level tree
        initial_keys = [
            10,
            14,
            17,
            20,
            23,
            25,
            30,
            35,
            40,
            45,
            50,
            55,
            60,
            65,
            70,
            75,
            80,
            85,
            90,
            95,
            100,
            141,
            150,
            160,
            170,
            180,
            190,
            200,
            210,
            218,
        ]
        for key in initial_keys:
            tree[key] = f"value_{key}"

        # Verify initial state
        assert check_invariants(tree), "Initial tree should satisfy invariants"
        initial_size = len(tree)

        # Pattern discovered: rapid deletions
        deletions = [14, 20, 25, 141, 17, 23]
        for key in deletions:
            if key in tree:
                del tree[key]
                assert check_invariants(
                    tree
                ), f"Invariants should hold after deleting {key}"

        # Verify deletions worked
        for key in deletions:
            assert key not in tree, f"Key {key} should be deleted"

        # Pattern discovered: insertion after deletions
        new_key = 6787
        new_value = "value_223943"
        tree[new_key] = new_value
        assert check_invariants(tree), "Invariants should hold after insertion"

        # Verify insertion worked
        assert tree[new_key] == new_value, "New key should be retrievable"

        # Verify tree is still functional
        expected_remaining = (
            initial_size - len([k for k in deletions if k in initial_keys]) + 1
        )
        assert (
            len(tree) == expected_remaining
        ), f"Tree size should be {expected_remaining}"

    def test_mixed_operations_stress_pattern(self):
        """
        Test mixed operations pattern that stresses tree structure.

        This pattern exercises a mix of deletions, gets, and insertions
        in a sequence that was observed during fuzz testing.
        """
        tree = BPlusTreeMap(capacity=8)

        # Pre-populate with keys that will be used in the pattern
        initial_keys = [14, 17, 20, 23, 25, 141, 210, 218]
        for key in initial_keys:
            tree[key] = f"initial_value_{key}"

        assert check_invariants(tree), "Initial tree should satisfy invariants"

        # Execute the discovered pattern
        operations = [
            ("delete", 14),
            ("get", 210),
            ("delete", 20),
            ("delete", 25),
            ("delete", 141),
            ("delete", 17),
            ("delete_nonexistent", 4799),  # This should not crash
            ("insert", 6787, "value_223943"),
            ("get", 218),
            ("delete", 23),
        ]

        for op in operations:
            if op[0] == "delete":
                key = op[1]
                if key in tree:
                    del tree[key]
                    assert check_invariants(
                        tree
                    ), f"Invariants should hold after deleting {key}"

            elif op[0] == "delete_nonexistent":
                key = op[1]
                # Should raise KeyError for non-existent key
                with pytest.raises(KeyError):
                    del tree[key]
                assert check_invariants(
                    tree
                ), "Invariants should hold after failed deletion"

            elif op[0] == "get":
                key = op[1]
                if key in tree:
                    value = tree[key]
                    assert (
                        value == f"initial_value_{key}"
                    ), f"Retrieved value should match for key {key}"
                else:
                    with pytest.raises(KeyError):
                        _ = tree[key]

            elif op[0] == "insert":
                key, value = op[1], op[2]
                tree[key] = value
                assert check_invariants(
                    tree
                ), f"Invariants should hold after inserting {key}"
                assert (
                    tree[key] == value
                ), f"Inserted value should be retrievable for key {key}"

        # Final verification
        assert check_invariants(tree), "Final tree should satisfy invariants"

    def test_high_capacity_rapid_operations(self):
        """
        Test rapid operations on higher capacity tree.

        Based on fuzz testing with capacity=16, this tests rapid
        operations on a tree with larger node capacity.
        """
        tree = BPlusTreeMap(capacity=16)

        # Pre-populate to create a reasonable tree structure
        for i in range(1, 201):
            tree[i] = f"prepop_value_{i}"

        assert check_invariants(tree), "Initial tree should satisfy invariants"
        initial_size = len(tree)

        # Rapid insertions with large keys (pattern from fuzz test)
        large_keys = [5038, 4765, 2459, 2247, 8154, 5123, 7444, 4952]
        for key in large_keys:
            tree[key] = f"large_value_{key}"
            assert check_invariants(
                tree
            ), f"Invariants should hold after inserting large key {key}"

        # Mixed operations with existing and new keys
        mixed_ops = [
            (89, "updated_value_89"),  # Update existing
            (35, None),  # Get existing
            (8974, "new_value_8974"),  # Insert new
            (6, "updated_value_6"),  # Update existing
            (125, None),  # Delete existing
        ]

        for key, value in mixed_ops:
            if value is None and key <= 200:  # Get or delete existing
                if key == 125:  # Delete
                    del tree[key]
                    assert key not in tree, f"Key {key} should be deleted"
                else:  # Get
                    retrieved = tree[key]
                    assert retrieved is not None, f"Should be able to get key {key}"
            else:  # Insert or update
                tree[key] = value
                assert tree[key] == value, f"Value should be set for key {key}"

            assert check_invariants(
                tree
            ), f"Invariants should hold after operation on key {key}"

        # Verify final state
        # initial_size=200, +8 large_keys, +1 new insert (8974), -1 deletion (125)
        expected_size = (
            initial_size + len(large_keys) + 1 - 1
        )  # +large_keys +1_new_insert -1_deletion
        assert (
            len(tree) == expected_size
        ), f"Final tree size should be {expected_size}, actual: {len(tree)}"

    def test_small_capacity_stress_pattern(self):
        """
        Test stress pattern on small capacity tree.

        Based on fuzz testing with capacity=4, this tests operations
        that force frequent node splits and merges.
        """
        tree = BPlusTreeMap(capacity=4)

        # Build up a tree with many small nodes
        for i in range(1, 51):
            tree[i] = f"small_value_{i}"

        assert check_invariants(tree), "Initial tree should satisfy invariants"

        # Pattern: alternating deletions and insertions that stress rebalancing
        operations = [
            ("delete", 14),
            ("delete", 20),
            ("delete", 25),
            ("insert", 1000, "new_1000"),
            ("delete", 17),
            ("delete", 23),
            ("delete", 30),
            ("insert", 2000, "new_2000"),
            ("delete", 35),
            ("delete", 40),
            ("insert", 3000, "new_3000"),
            ("get", 1000),
            ("get", 2000),
            ("get", 3000),
        ]

        for op_type, key, *args in operations:
            if op_type == "delete":
                if key in tree:
                    del tree[key]
                    assert key not in tree, f"Key {key} should be deleted"
            elif op_type == "insert":
                value = args[0]
                tree[key] = value
                assert tree[key] == value, f"Key {key} should have value {value}"
            elif op_type == "get":
                value = tree[key]
                assert value is not None, f"Should be able to retrieve key {key}"

            assert check_invariants(
                tree
            ), f"Invariants should hold after {op_type} on key {key}"

        # Final verification
        assert check_invariants(tree), "Final tree should satisfy invariants"

        # Verify specific keys exist
        assert tree[1000] == "new_1000"
        assert tree[2000] == "new_2000"
        assert tree[3000] == "new_3000"

        # Verify specific keys were deleted
        deleted_keys = [14, 20, 25, 17, 23, 30, 35, 40]
        for key in deleted_keys:
            assert key not in tree, f"Key {key} should remain deleted"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
