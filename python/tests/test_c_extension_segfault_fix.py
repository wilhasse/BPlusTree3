"""
Test that the C extension segfault issue has been fixed.

This test specifically targets the reference counting bug in node splitting
that was causing segfaults during large sequential insertions.
"""

import pytest
import gc
import sys
import os

# Add parent directory to path to import the C extension
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCExtensionSegfaultFix:
    """Test that C extension no longer segfaults on large insertions."""

    def test_sequential_insertion_no_segfault(self):
        """Test that sequential insertion of 5000 items doesn't segfault."""
        try:
            from bplustree_c import BPlusTree
        except ImportError:
            pytest.skip("C extension not available")

        # Create tree with small capacity to force many splits
        tree = BPlusTree(capacity=4)

        # Insert 5000 items sequentially - this used to segfault
        for i in range(5000):
            tree[i] = f"value_{i}"

            # Force garbage collection periodically to stress test memory management
            if i % 100 == 0:
                gc.collect()

        # Verify all items are accessible
        assert len(tree) == 5000

        # Spot check some values
        assert tree[0] == "value_0"
        assert tree[2500] == "value_2500"
        assert tree[4999] == "value_4999"

    def test_random_insertion_no_segfault(self):
        """Test that random insertion doesn't cause segfaults."""
        try:
            from bplustree_c import BPlusTree
        except ImportError:
            pytest.skip("C extension not available")

        import random

        tree = BPlusTree(capacity=8)

        # Insert in random order
        keys = list(range(2000))
        random.shuffle(keys)

        for key in keys:
            tree[key] = f"value_{key}"

        assert len(tree) == 2000

    def test_deletion_after_splits_no_segfault(self):
        """Test that deletion after many splits doesn't segfault."""
        try:
            from bplustree_c import BPlusTree
        except ImportError:
            pytest.skip("C extension not available")

        tree = BPlusTree(capacity=4)

        # Insert many items to cause splits
        for i in range(1000):
            tree[i] = f"value_{i}"

        # Delete half the items
        for i in range(0, 1000, 2):
            del tree[i]

        assert len(tree) == 500

        # Verify remaining items
        for i in range(1, 1000, 2):
            assert tree[i] == f"value_{i}"

    def test_iteration_after_splits_no_segfault(self):
        """Test that iteration after splits doesn't segfault."""
        try:
            from bplustree_c import BPlusTree
        except ImportError:
            pytest.skip("C extension not available")

        tree = BPlusTree(capacity=16)

        # Insert items
        for i in range(3000):
            tree[i] = i * 2

        # Iterate and verify
        count = 0
        for key, value in tree.items():
            assert value == key * 2
            count += 1

        assert count == 3000

    def test_concurrent_modification_safety(self):
        """Test that we handle concurrent modification errors gracefully."""
        try:
            from bplustree_c import BPlusTree
        except ImportError:
            pytest.skip("C extension not available")

        tree = BPlusTree(capacity=8)

        # Insert initial items
        for i in range(100):
            tree[i] = f"value_{i}"

        # Get an iterator
        iterator = iter(tree.items())

        # Consume a few items
        for _ in range(10):
            next(iterator)

        # Modify the tree
        tree[1000] = "new_value"

        # Continue iteration - should either complete or raise RuntimeError
        # but should NOT segfault
        try:
            remaining = list(iterator)
            # If it completes, it's acceptable - C extension doesn't detect modification
            # What's important is that it doesn't segfault
            pass
        except RuntimeError as e:
            # This is also acceptable - iterator detected modification
            assert "changed size during iteration" in str(e)

    def test_memory_stress_test(self):
        """Stress test memory management with many insertions and deletions."""
        try:
            from bplustree_c import BPlusTree
        except ImportError:
            pytest.skip("C extension not available")

        tree = BPlusTree(capacity=32)

        # Multiple rounds of insert/delete
        for round in range(5):
            # Insert batch
            for i in range(round * 1000, (round + 1) * 1000):
                tree[i] = f"round_{round}_value_{i}"

            # Delete some from previous rounds
            if round > 0:
                for i in range((round - 1) * 1000, (round - 1) * 1000 + 500):
                    if i in tree:
                        del tree[i]

            # Force garbage collection
            gc.collect()

        # Verify tree is still functional
        assert len(tree) > 0

        # Check some remaining values
        for key in list(tree.keys())[:10]:
            value = tree[key]
            assert value.startswith("round_")


if __name__ == "__main__":
    # Run the tests
    test = TestCExtensionSegfaultFix()

    print("Running sequential insertion test...")
    test.test_sequential_insertion_no_segfault()
    print("✓ Passed")

    print("Running random insertion test...")
    test.test_random_insertion_no_segfault()
    print("✓ Passed")

    print("Running deletion test...")
    test.test_deletion_after_splits_no_segfault()
    print("✓ Passed")

    print("Running iteration test...")
    test.test_iteration_after_splits_no_segfault()
    print("✓ Passed")

    print("Running concurrent modification test...")
    test.test_concurrent_modification_safety()
    print("✓ Passed")

    print("Running memory stress test...")
    test.test_memory_stress_test()
    print("✓ Passed")

    print("\nAll tests passed! The segfault issue appears to be fixed.")
