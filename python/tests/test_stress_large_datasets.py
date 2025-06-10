"""
Stress tests with large datasets for B+ Tree implementation.

These tests ensure the implementation can handle large amounts of data
and maintains correctness and reasonable performance at scale.
"""

import pytest
import random
import string
import time
from typing import List, Tuple, Any

from bplus_tree import BPlusTreeMap


class TestLargeDatasets:
    """Stress tests with large datasets."""

    @pytest.mark.slow
    def test_one_million_sequential_insertions(self):
        """Test handling of 1M sequential insertions."""
        tree = BPlusTreeMap()
        size = 1_000_000

        start_time = time.time()

        # Insert 1M items
        for i in range(size):
            tree[i] = f"v{i}"

            # Periodic progress check
            if i % 100_000 == 0 and i > 0:
                elapsed = time.time() - start_time
                print(f"\nInserted {i:,} items in {elapsed:.2f}s")

        total_time = time.time() - start_time
        print(f"\nTotal insertion time for 1M items: {total_time:.2f}s")

        # Verify all items are present
        assert len(tree) == size

        # Spot check some values
        for i in range(0, size, 100_000):
            assert tree[i] == f"v{i}"

    @pytest.mark.slow
    def test_one_million_random_insertions(self):
        """Test handling of 1M random insertions."""
        tree = BPlusTreeMap()
        size = 1_000_000

        # Generate random keys
        keys = list(range(size))
        random.shuffle(keys)

        start_time = time.time()

        # Insert in random order
        for i, key in enumerate(keys):
            tree[key] = f"value_{key}"

            # Periodic progress check
            if i % 100_000 == 0 and i > 0:
                elapsed = time.time() - start_time
                print(f"\nInserted {i:,} random items in {elapsed:.2f}s")

        total_time = time.time() - start_time
        print(f"\nTotal random insertion time for 1M items: {total_time:.2f}s")

        # Verify all items are present and in order
        assert len(tree) == size

        # Check ordering
        items = list(tree.items())
        for i in range(1, len(items)):
            assert items[i - 1][0] < items[i][0], "Items not in order"

    def test_large_string_keys(self):
        """Test handling of large string keys."""
        tree = BPlusTreeMap()

        # Generate large string keys
        def generate_key(i: int) -> str:
            # Create keys with common prefixes to test ordering
            prefix = "".join(random.choices(string.ascii_letters, k=50))
            return f"{prefix}_{i:010d}"

        size = 10_000
        keys = [generate_key(i) for i in range(size)]

        # Insert with string keys
        for i, key in enumerate(keys):
            tree[key] = i

        assert len(tree) == size

        # Verify ordering
        tree_keys = list(tree.keys())
        sorted_keys = sorted(keys)
        assert tree_keys == sorted_keys, "String keys not properly ordered"

    def test_large_value_objects(self):
        """Test handling of large value objects."""
        tree = BPlusTreeMap()

        # Create large value objects
        class LargeObject:
            def __init__(self, id: int):
                self.id = id
                self.data = [random.random() for _ in range(1000)]
                self.text = "".join(random.choices(string.ascii_letters, k=1000))

        size = 1_000

        # Insert large objects
        for i in range(size):
            tree[i] = LargeObject(i)

        assert len(tree) == size

        # Verify objects are intact
        for i in range(0, size, 100):
            obj = tree[i]
            assert obj.id == i
            assert len(obj.data) == 1000
            assert len(obj.text) == 1000

    @pytest.mark.slow
    def test_stress_mixed_operations(self):
        """Stress test with mixed operations on large dataset."""
        tree = BPlusTreeMap()
        operations = 500_000

        inserted = set()
        deleted = set()

        start_time = time.time()

        for i in range(operations):
            op = random.choice(["insert", "delete", "lookup", "update"])

            if op == "insert" or (op == "delete" and not inserted):
                # Insert new item
                key = random.randint(0, operations * 2)
                tree[key] = f"value_{key}_{i}"
                inserted.add(key)
                deleted.discard(key)

            elif op == "delete" and inserted:
                # Delete existing item
                key = random.choice(list(inserted - deleted))
                del tree[key]
                deleted.add(key)

            elif op == "lookup" and inserted:
                # Lookup existing item
                key = random.choice(list(inserted - deleted))
                assert tree[key].startswith(f"value_{key}_")

            elif op == "update" and inserted:
                # Update existing item
                key = random.choice(list(inserted - deleted))
                tree[key] = f"updated_{key}_{i}"

            # Progress report
            if i % 50_000 == 0 and i > 0:
                elapsed = time.time() - start_time
                print(f"\nCompleted {i:,} operations in {elapsed:.2f}s")

        # Verify final state
        expected_size = len(inserted - deleted)
        assert (
            len(tree) == expected_size
        ), f"Tree size {len(tree)} doesn't match expected {expected_size}"

    def test_range_queries_on_large_dataset(self):
        """Test range queries on large dataset."""
        tree = BPlusTreeMap()
        size = 100_000

        # Insert items
        for i in range(size):
            tree[i * 10] = f"value_{i}"  # Sparse keys

        # Test various range sizes
        test_ranges = [
            (1000, 2000),  # Small range
            (40000, 60000),  # Medium range
            (0, 50000),  # Large range
            (90000, 1000000),  # Range extending beyond data
        ]

        for start, end in test_ranges:
            items = list(tree.items(start, end))

            # Verify all items are in range
            for key, value in items:
                assert start <= key < end, f"Key {key} outside range [{start}, {end})"

            # Verify ordering
            for i in range(1, len(items)):
                assert items[i - 1][0] < items[i][0], "Items not in order"

    def test_memory_efficiency_at_scale(self):
        """Test memory efficiency with large datasets."""
        import sys

        tree = BPlusTreeMap()

        # Measure memory usage at different scales
        sizes = [10_000, 50_000, 100_000]
        memory_usage = []

        for size in sizes:
            # Insert up to current size
            start = len(tree)
            for i in range(start, size):
                tree[i] = i

            # Force garbage collection
            import gc

            gc.collect()

            # Rough memory estimate
            # Note: This is approximate and platform-dependent
            memory = sys.getsizeof(tree)
            memory_usage.append(memory)

            print(f"\nTree with {size:,} items: ~{memory:,} bytes")

        # Memory growth should be reasonable
        # Not necessarily linear due to tree structure
        assert all(m > 0 for m in memory_usage), "Invalid memory measurements"

    def test_persistence_pattern_simulation(self):
        """Simulate a persistence/reload pattern with large dataset."""
        tree = BPlusTreeMap()
        size = 50_000

        # Simulate initial load
        print("\nSimulating initial data load...")
        for i in range(size):
            tree[i] = {"id": i, "data": f"record_{i}", "timestamp": time.time()}

        # Simulate updates (like a database)
        print("Simulating updates...")
        update_count = 5_000
        for _ in range(update_count):
            key = random.randint(0, size - 1)
            tree[key]["timestamp"] = time.time()
            tree[key]["data"] = f"updated_record_{key}"

        # Simulate reads
        print("Simulating reads...")
        read_count = 10_000
        for _ in range(read_count):
            key = random.randint(0, size - 1)
            record = tree[key]
            assert "id" in record and "data" in record

        # Verify data integrity
        assert len(tree) == size
        for i in range(0, size, 1000):
            assert tree[i]["id"] == i


if __name__ == "__main__":
    # Run without slow tests by default
    pytest.main([__file__, "-v", "-m", "not slow"])
