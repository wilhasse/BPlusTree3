#!/usr/bin/env python3
"""
Stress tests for B+ tree edge cases based on fuzz testing patterns.
These tests target specific scenarios that could expose bugs.
"""

import pytest
import random
from bplus_tree import BPlusTreeMap
from _invariant_checker import BPlusTreeInvariantChecker


def check_invariants(tree: BPlusTreeMap) -> bool:
    """Helper function to check tree invariants"""
    checker = BPlusTreeInvariantChecker(tree.capacity)
    return checker.check_invariants(tree.root, tree.leaves)


class TestStressEdgeCases:
    """Stress tests for edge cases that could break B+ tree invariants"""

    def test_minimum_capacity_heavy_deletion(self):
        """Test minimum capacity (4) with heavy deletion patterns"""
        tree = BPlusTreeMap(capacity=4)

        # Build a substantial tree
        keys = list(range(100))
        for key in keys:
            tree[key] = f"value_{key}"

        assert check_invariants(tree), "Tree should be valid after insertions"

        # Delete in patterns that stress rebalancing
        # Pattern 1: Delete every 3rd key
        for i in range(0, 100, 3):
            if i in tree:
                del tree[i]
                assert check_invariants(tree), f"Invariants broken after deleting {i}"

        # Pattern 2: Delete consecutive ranges
        for start in range(10, 90, 20):
            for i in range(start, min(start + 5, 100)):
                if i in tree:
                    del tree[i]
                    assert check_invariants(
                        tree
                    ), f"Invariants broken after deleting {i}"

    def test_alternating_insert_delete_stress(self):
        """Test alternating insert/delete operations that could cause instability"""
        tree = BPlusTreeMap(capacity=8)

        # Start with some data
        for i in range(50):
            tree[i] = f"initial_{i}"

        assert check_invariants(tree), "Initial tree should be valid"

        # Alternating pattern that stresses the tree
        for round_num in range(10):
            # Insert a batch
            for i in range(100 + round_num * 20, 120 + round_num * 20):
                tree[i] = f"round_{round_num}_{i}"
                assert check_invariants(tree), f"Insert {i} broke invariants"

            # Delete a batch from different area
            for i in range(round_num * 5, round_num * 5 + 10):
                if i in tree:
                    del tree[i]
                    assert check_invariants(tree), f"Delete {i} broke invariants"

    def test_large_capacity_edge_cases(self):
        """Test very large capacity to stress single-level tree edge cases"""
        tree = BPlusTreeMap(capacity=1024)

        # Fill up close to capacity
        for i in range(1000):
            tree[i] = f"value_{i}"

        assert tree.root.is_leaf(), "Should still be single-level tree"
        assert check_invariants(tree), "Large single-level tree should be valid"

        # Delete most items to test underflow handling
        for i in range(0, 1000, 2):  # Delete every other item
            del tree[i]
            assert check_invariants(tree), f"Delete {i} broke invariants"

        # Add items back to test growth
        for i in range(1000, 1100):
            tree[i] = f"new_value_{i}"
            assert check_invariants(tree), f"Insert {i} broke invariants"

    def test_sequential_vs_random_patterns(self):
        """Test different insertion/deletion patterns"""
        for pattern_name, key_generator in [
            ("sequential", lambda: list(range(200))),
            ("reverse", lambda: list(range(199, -1, -1))),
            ("random", lambda: random.sample(range(1000), 200)),
        ]:
            tree = BPlusTreeMap(capacity=16)

            # Insert with pattern
            keys = key_generator()
            for key in keys:
                tree[key] = f"value_{key}_{pattern_name}"
                assert check_invariants(
                    tree
                ), f"Insert {key} broke invariants in {pattern_name}"

            # Delete with different pattern
            random.shuffle(keys)  # Always delete in random order
            for key in keys[:100]:  # Delete half
                del tree[key]
                assert check_invariants(
                    tree
                ), f"Delete {key} broke invariants in {pattern_name}"

    def test_duplicate_key_operations(self):
        """Test operations on duplicate keys and edge cases"""
        tree = BPlusTreeMap(capacity=8)

        # Insert initial data
        for i in range(50):
            tree[i] = f"initial_{i}"

        # Test updating existing keys
        for i in range(25):
            tree[i] = f"updated_{i}"
            assert check_invariants(tree), f"Update {i} broke invariants"

        # Test deleting non-existent keys (should not crash)
        for i in range(100, 150):
            try:
                del tree[i]
                assert False, f"Should have raised KeyError for non-existent key {i}"
            except KeyError:
                pass  # Expected
            assert check_invariants(tree), f"Non-existent delete {i} broke invariants"

    def test_empty_tree_operations(self):
        """Test operations on empty tree"""
        tree = BPlusTreeMap(capacity=16)

        # Empty tree should be valid
        assert check_invariants(tree), "Empty tree should be valid"
        assert len(tree) == 0

        # Test operations on empty tree
        with pytest.raises(KeyError):
            _ = tree[42]

        with pytest.raises(KeyError):
            del tree[42]

        # Add one item
        tree[42] = "answer"
        assert check_invariants(tree), "Single-item tree should be valid"
        assert len(tree) == 1

        # Remove the only item
        del tree[42]
        assert check_invariants(tree), "Empty tree after deletion should be valid"
        assert len(tree) == 0

    def test_capacity_boundary_conditions(self):
        """Test operations right at capacity boundaries"""
        for capacity in [4, 8, 16, 32]:
            # Test each capacity separately
            tree = BPlusTreeMap(capacity=capacity)

            # Fill exactly to capacity
            for i in range(capacity):
                tree[i] = f"value_{i}"

            assert check_invariants(
                tree
            ), f"Tree at capacity {capacity} should be valid"

            # Add one more to trigger split
            tree[capacity] = f"value_{capacity}"
            assert check_invariants(
                tree
            ), f"Tree after split at capacity {capacity} should be valid"

            # Delete back to capacity
            del tree[capacity]
            assert check_invariants(
                tree
            ), f"Tree after delete at capacity {capacity} should be valid"

    def test_deep_tree_stress(self):
        """Create a deep tree and stress test it"""
        tree = BPlusTreeMap(capacity=4)  # Small capacity forces depth

        # Create a deep tree
        for i in range(500):
            tree[i] = f"value_{i}"

        # Verify it's actually deep
        depth = 0
        node = tree.root
        while not node.is_leaf():
            depth += 1
            node = node.children[0]

        assert depth >= 3, f"Tree should be deep (depth={depth})"
        assert check_invariants(tree), "Deep tree should be valid"

        # Stress test with random operations
        random.seed(42)  # Reproducible
        for _ in range(200):
            operation = random.choice(["insert", "delete", "update"])
            key = random.randint(0, 600)

            if operation == "insert" or operation == "update":
                tree[key] = f"stress_{key}"
            elif operation == "delete" and key in tree:
                del tree[key]

            assert check_invariants(
                tree
            ), f"Stress operation {operation} on key {key} broke invariants"


if __name__ == "__main__":
    # Run tests manually for debugging
    test = TestStressEdgeCases()

    tests = [
        ("minimum_capacity_heavy_deletion", test.test_minimum_capacity_heavy_deletion),
        (
            "alternating_insert_delete_stress",
            test.test_alternating_insert_delete_stress,
        ),
        ("large_capacity_edge_cases", test.test_large_capacity_edge_cases),
        ("sequential_vs_random_patterns", test.test_sequential_vs_random_patterns),
        ("duplicate_key_operations", test.test_duplicate_key_operations),
        ("empty_tree_operations", test.test_empty_tree_operations),
        ("capacity_boundary_conditions", test.test_capacity_boundary_conditions),
        ("deep_tree_stress", test.test_deep_tree_stress),
    ]

    for test_name, test_func in tests:
        print(f"=== {test_name} ===")
        try:
            test_func()
            print("✅ PASSED")
        except Exception as e:
            print(f"❌ FAILED: {e}")
            import traceback

            traceback.print_exc()
        print()
