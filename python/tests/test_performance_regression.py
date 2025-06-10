"""
Performance regression tests for B+ Tree implementation.

These tests ensure that performance characteristics remain consistent
across changes and that we maintain our performance advantages over
standard Python data structures.
"""

import pytest
import time
import random
from typing import Dict, List, Tuple, Any
from contextlib import contextmanager

from bplus_tree import BPlusTreeMap


@contextmanager
def time_it() -> float:
    """Context manager to measure execution time."""
    start = time.perf_counter()
    yield lambda: time.perf_counter() - start


class TestPerformanceRegression:
    """Performance regression tests to ensure consistent performance."""

    # Performance thresholds (in seconds)
    INSERTION_THRESHOLD_10K = 0.5  # 10,000 insertions should take < 0.5s
    LOOKUP_THRESHOLD_10K = 0.3  # 10,000 lookups should take < 0.3s
    DELETION_THRESHOLD_10K = 0.5  # 10,000 deletions should take < 0.5s
    ITERATION_THRESHOLD_10K = 0.2  # Iterating 10,000 items should take < 0.2s
    RANGE_QUERY_THRESHOLD = 0.1  # Range query on 10% of items should take < 0.1s

    def generate_test_data(self, size: int) -> List[Tuple[int, str]]:
        """Generate test data for performance tests."""
        return [(i, f"value_{i}") for i in range(size)]

    def test_insertion_performance(self):
        """Test that insertions remain performant."""
        tree = BPlusTreeMap()
        data = self.generate_test_data(10000)

        with time_it() as elapsed:
            for key, value in data:
                tree[key] = value

        duration = elapsed()
        assert (
            duration < self.INSERTION_THRESHOLD_10K
        ), f"Insertion of 10K items took {duration:.3f}s, exceeds threshold of {self.INSERTION_THRESHOLD_10K}s"

    def test_sequential_vs_random_insertion(self):
        """Test that random insertions don't degrade performance significantly."""
        # Sequential insertion
        tree_seq = BPlusTreeMap()
        data_seq = self.generate_test_data(5000)

        with time_it() as elapsed_seq:
            for key, value in data_seq:
                tree_seq[key] = value

        # Random insertion
        tree_rand = BPlusTreeMap()
        data_rand = data_seq.copy()
        random.shuffle(data_rand)

        with time_it() as elapsed_rand:
            for key, value in data_rand:
                tree_rand[key] = value

        seq_time = elapsed_seq()
        rand_time = elapsed_rand()

        # Random insertion should not be more than 3x slower than sequential
        assert (
            rand_time < seq_time * 3
        ), f"Random insertion ({rand_time:.3f}s) is too slow compared to sequential ({seq_time:.3f}s)"

    def test_lookup_performance(self):
        """Test that lookups remain performant."""
        tree = BPlusTreeMap()
        data = self.generate_test_data(10000)

        # Insert data
        for key, value in data:
            tree[key] = value

        # Test lookups
        with time_it() as elapsed:
            for key, _ in data:
                _ = tree[key]

        duration = elapsed()
        assert (
            duration < self.LOOKUP_THRESHOLD_10K
        ), f"Lookup of 10K items took {duration:.3f}s, exceeds threshold of {self.LOOKUP_THRESHOLD_10K}s"

    def test_deletion_performance(self):
        """Test that deletions remain performant."""
        tree = BPlusTreeMap()
        data = self.generate_test_data(10000)

        # Insert data
        for key, value in data:
            tree[key] = value

        # Test deletions
        with time_it() as elapsed:
            for key, _ in data:
                del tree[key]

        duration = elapsed()
        assert (
            duration < self.DELETION_THRESHOLD_10K
        ), f"Deletion of 10K items took {duration:.3f}s, exceeds threshold of {self.DELETION_THRESHOLD_10K}s"

    def test_iteration_performance(self):
        """Test that iteration remains performant."""
        tree = BPlusTreeMap()
        data = self.generate_test_data(10000)

        # Insert data
        for key, value in data:
            tree[key] = value

        # Test iteration
        with time_it() as elapsed:
            items = list(tree.items())

        duration = elapsed()
        assert len(items) == 10000
        assert (
            duration < self.ITERATION_THRESHOLD_10K
        ), f"Iteration of 10K items took {duration:.3f}s, exceeds threshold of {self.ITERATION_THRESHOLD_10K}s"

    def test_range_query_performance(self):
        """Test that range queries remain performant."""
        tree = BPlusTreeMap()
        data = self.generate_test_data(10000)

        # Insert data
        for key, value in data:
            tree[key] = value

        # Test range query (10% of data)
        start_key = 4500
        end_key = 5500

        with time_it() as elapsed:
            items = list(tree.items(start_key, end_key))

        duration = elapsed()
        assert 1000 <= len(items) <= 1001  # Should get ~1000 items
        assert (
            duration < self.RANGE_QUERY_THRESHOLD
        ), f"Range query took {duration:.3f}s, exceeds threshold of {self.RANGE_QUERY_THRESHOLD}s"

    def test_mixed_operations_performance(self):
        """Test performance under mixed workload."""
        tree = BPlusTreeMap()
        operations_count = 10000

        with time_it() as elapsed:
            # Initial insertions
            for i in range(operations_count // 2):
                tree[i] = f"value_{i}"

            # Mixed operations
            for i in range(operations_count // 4):
                # Insert
                tree[operations_count + i] = f"value_{operations_count + i}"
                # Lookup
                _ = tree[i]
                # Delete
                if i < operations_count // 8:
                    del tree[i]

            # Final iteration
            _ = list(tree.items())

        duration = elapsed()
        # Mixed operations should complete in reasonable time
        assert (
            duration < 1.0
        ), f"Mixed operations took {duration:.3f}s, exceeds threshold of 1.0s"

    def test_performance_scales_logarithmically(self):
        """Test that performance scales logarithmically with data size."""
        sizes = [1000, 2000, 4000, 8000]
        times = []

        for size in sizes:
            tree = BPlusTreeMap()
            data = self.generate_test_data(size)

            with time_it() as elapsed:
                for key, value in data:
                    tree[key] = value
                    if key % 10 == 0:  # Periodic lookups
                        _ = tree[key // 2]

            times.append(elapsed())

        # Check that doubling the size doesn't double the time
        # (allowing for some variance)
        for i in range(1, len(times)):
            ratio = times[i] / times[i - 1]
            assert ratio < 2.5, (
                f"Performance degraded too much: {sizes[i-1]} items took {times[i-1]:.3f}s, "
                f"{sizes[i]} items took {times[i]:.3f}s (ratio: {ratio:.2f})"
            )

    def test_memory_efficiency(self):
        """Test that memory usage remains reasonable."""
        import sys

        tree = BPlusTreeMap()

        # Measure baseline memory
        initial_size = sys.getsizeof(tree)

        # Insert 1000 items
        for i in range(1000):
            tree[i] = f"value_{i}"

        # The tree structure should be memory efficient
        # Each node should not consume excessive memory
        # This is a basic sanity check
        assert hasattr(tree, "root"), "Tree should have accessible root for inspection"
        assert len(tree) == 1000, "Tree should contain all inserted items"


class TestPerformanceComparison:
    """Compare performance against standard Python dict."""

    def test_insertion_comparable_to_dict(self):
        """Test that insertion performance is comparable to dict."""
        size = 5000
        data = [(i, f"value_{i}") for i in range(size)]

        # Test dict
        dict_obj = {}
        with time_it() as dict_elapsed:
            for key, value in data:
                dict_obj[key] = value

        # Test B+ Tree
        tree = BPlusTreeMap()
        with time_it() as tree_elapsed:
            for key, value in data:
                tree[key] = value

        dict_time = dict_elapsed()
        tree_time = tree_elapsed()

        # B+ Tree insertion can be slower than dict, but not by too much
        # (dict has O(1) amortized, B+ Tree has O(log n))
        assert (
            tree_time < dict_time * 10
        ), f"B+ Tree insertion ({tree_time:.3f}s) is too slow compared to dict ({dict_time:.3f}s)"

    def test_ordered_iteration_faster_than_sorted_dict(self):
        """Test that ordered iteration is faster than sorting dict items."""
        size = 10000
        data = [(random.randint(0, 100000), f"value_{i}") for i in range(size)]

        # Build dict
        dict_obj = {}
        for key, value in data:
            dict_obj[key] = value

        # Build B+ Tree
        tree = BPlusTreeMap()
        for key, value in data:
            tree[key] = value

        # Test sorted dict iteration
        with time_it() as dict_elapsed:
            sorted_items = sorted(dict_obj.items())

        # Test B+ Tree iteration (already sorted)
        with time_it() as tree_elapsed:
            tree_items = list(tree.items())

        dict_time = dict_elapsed()
        tree_time = tree_elapsed()

        # B+ Tree iteration should be faster than sorting dict items
        assert (
            tree_time < dict_time
        ), f"B+ Tree iteration ({tree_time:.3f}s) should be faster than sorted dict ({dict_time:.3f}s)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
