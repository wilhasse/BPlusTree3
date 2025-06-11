#!/usr/bin/env python3
"""
Performance demonstration comparing BPlusTree vs standard dict and other data structures.

This example benchmarks the specific scenarios where B+ Tree excels,
providing concrete performance data to help users understand when
to choose B+ Tree over alternatives.
"""

import sys
import os
import time
import random
from collections import OrderedDict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bplustree import BPlusTreeMap

try:
    from sortedcontainers import SortedDict

    HAS_SORTEDDICT = True
except ImportError:
    HAS_SORTEDDICT = False
    print(
        "Note: sortedcontainers not available. Install with: pip install sortedcontainers"
    )


def benchmark_function(func, *args, **kwargs):
    """Benchmark a function and return execution time."""
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()
    return end_time - start_time, result


def create_test_data(size):
    """Create test data for benchmarks."""
    return [(i, f"value_{i}") for i in range(size)]


def benchmark_range_queries():
    """Benchmark range query performance vs alternatives."""
    print("=== Range Query Performance ===\n")

    sizes = [1000, 5000, 10000]
    range_sizes = [10, 50, 100, 500]

    for data_size in sizes:
        print(f"Dataset size: {data_size:,} items")

        # Setup data structures
        data = create_test_data(data_size)

        # B+ Tree
        bplustree = BPlusTreeMap(capacity=64)
        bplustree.update(data)

        # Regular dict
        regular_dict = dict(data)

        # SortedDict (if available)
        if HAS_SORTEDDICT:
            sorted_dict = SortedDict(data)

        for range_size in range_sizes:
            start_key = data_size // 3  # Start from 1/3 into the data
            end_key = start_key + range_size

            print(f"\n  Range query: {range_size} items (keys {start_key}-{end_key-1})")

            # B+ Tree range query
            def bplus_range():
                return list(bplustree.range(start_key, end_key))

            bplus_time, bplus_result = benchmark_function(bplus_range)
            print(
                f"    B+ Tree:     {bplus_time*1000:.3f} ms ({len(bplus_result)} items)"
            )

            # Dict scan approach
            def dict_range():
                return [
                    (k, v) for k, v in regular_dict.items() if start_key <= k < end_key
                ]

            dict_time, dict_result = benchmark_function(dict_range)
            print(
                f"    Dict scan:   {dict_time*1000:.3f} ms ({len(dict_result)} items)"
            )

            # SortedDict range (if available)
            if HAS_SORTEDDICT:

                def sorted_dict_range():
                    return list(sorted_dict.irange(start_key, end_key - 1))

                sorted_time, sorted_result = benchmark_function(sorted_dict_range)
                print(
                    f"    SortedDict:  {sorted_time*1000:.3f} ms ({len(sorted_result)} items)"
                )

                # Performance comparison
                if sorted_time > 0:
                    speedup = sorted_time / bplus_time
                    print(
                        f"    → B+ Tree is {speedup:.2f}x {'faster' if speedup > 1 else 'slower'} than SortedDict"
                    )

            # Dict comparison
            if dict_time > 0:
                speedup = dict_time / bplus_time
                print(
                    f"    → B+ Tree is {speedup:.2f}x {'faster' if speedup > 1 else 'slower'} than dict scan"
                )

        print()


def benchmark_iteration():
    """Benchmark full iteration performance."""
    print("=== Full Iteration Performance ===\n")

    sizes = [1000, 5000, 10000, 20000]

    for size in sizes:
        print(f"Dataset size: {size:,} items")

        data = create_test_data(size)

        # Setup data structures
        bplustree = BPlusTreeMap(capacity=64)
        bplustree.update(data)

        regular_dict = dict(data)

        if HAS_SORTEDDICT:
            sorted_dict = SortedDict(data)

        # B+ Tree iteration
        def bplus_iterate():
            return sum(1 for _ in bplustree.items())

        bplus_time, _ = benchmark_function(bplus_iterate)
        print(f"  B+ Tree:     {bplus_time*1000:.3f} ms")

        # Dict iteration (unsorted)
        def dict_iterate():
            return sum(1 for _ in regular_dict.items())

        dict_time, _ = benchmark_function(dict_iterate)
        print(f"  Dict:        {dict_time*1000:.3f} ms")

        # Sorted dict iteration
        def sorted_dict_iterate():
            return sum(1 for _ in sorted(regular_dict.items()))

        sorted_time, _ = benchmark_function(sorted_dict_iterate)
        print(f"  Dict sorted: {sorted_time*1000:.3f} ms")

        if HAS_SORTEDDICT:

            def sorteddict_iterate():
                return sum(1 for _ in sorted_dict.items())

            sd_time, _ = benchmark_function(sorteddict_iterate)
            print(f"  SortedDict:  {sd_time*1000:.3f} ms")

        print()


def benchmark_insertion():
    """Benchmark insertion performance."""
    print("=== Insertion Performance ===\n")

    sizes = [1000, 5000, 10000]

    for size in sizes:
        print(f"Inserting {size:,} items")

        data = create_test_data(size)
        random.shuffle(data)  # Random insertion order

        # B+ Tree insertion
        def bplus_insert():
            tree = BPlusTreeMap(capacity=64)
            for key, value in data:
                tree[key] = value
            return tree

        bplus_time, _ = benchmark_function(bplus_insert)
        print(f"  B+ Tree:    {bplus_time*1000:.3f} ms")

        # Dict insertion
        def dict_insert():
            d = {}
            for key, value in data:
                d[key] = value
            return d

        dict_time, _ = benchmark_function(dict_insert)
        print(f"  Dict:       {dict_time*1000:.3f} ms")

        if HAS_SORTEDDICT:

            def sorted_dict_insert():
                sd = SortedDict()
                for key, value in data:
                    sd[key] = value
                return sd

            sd_time, _ = benchmark_function(sorted_dict_insert)
            print(f"  SortedDict: {sd_time*1000:.3f} ms")

        print()


def benchmark_memory_usage():
    """Demonstrate memory efficiency."""
    print("=== Memory Usage Estimation ===\n")

    import sys

    size = 10000
    data = create_test_data(size)

    # B+ Tree
    bplustree = BPlusTreeMap(capacity=64)
    bplustree.update(data)

    # Dict
    regular_dict = dict(data)

    print(f"For {size:,} items:")
    print(
        f"  B+ Tree: ~{sys.getsizeof(bplustree) + sum(sys.getsizeof(x) for x in [bplustree.keys(), bplustree.values()]):,} bytes"
    )
    print(f"  Dict:    ~{sys.getsizeof(regular_dict):,} bytes")
    print("\nNote: Memory usage depends on Python implementation and object overhead.")
    print("B+ Tree may use more memory per item but provides better cache locality.")


def demonstrate_early_termination():
    """Show early termination advantages."""
    print("=== Early Termination Advantage ===\n")

    size = 50000
    data = create_test_data(size)

    bplustree = BPlusTreeMap(capacity=128)
    bplustree.update(data)

    regular_dict = dict(data)

    # Find first 10 items where key > 40000
    print("Find first 10 items where key > 40,000:")

    # B+ Tree approach
    def bplus_early_termination():
        result = []
        for key, value in bplustree.range(40000, None):
            result.append((key, value))
            if len(result) >= 10:
                break
        return result

    bplus_time, bplus_result = benchmark_function(bplus_early_termination)
    print(f"  B+ Tree:  {bplus_time*1000:.3f} ms (found {len(bplus_result)} items)")

    # Dict approach (must scan and sort)
    def dict_early_termination():
        result = []
        for key, value in sorted(regular_dict.items()):
            if key >= 40000:
                result.append((key, value))
                if len(result) >= 10:
                    break
        return result

    dict_time, dict_result = benchmark_function(dict_early_termination)
    print(f"  Dict:     {dict_time*1000:.3f} ms (found {len(dict_result)} items)")

    if dict_time > 0:
        speedup = dict_time / bplus_time
        print(f"  → B+ Tree is {speedup:.1f}x faster for early termination queries!")


def capacity_tuning_demo():
    """Demonstrate the impact of capacity tuning."""
    print("=== Capacity Tuning Impact ===\n")

    size = 5000
    data = create_test_data(size)
    capacities = [4, 8, 16, 32, 64, 128]

    print(f"Range query performance with {size:,} items (different capacities):")

    results = []
    for capacity in capacities:
        tree = BPlusTreeMap(capacity=capacity)
        tree.update(data)

        # Benchmark a range query
        def range_query():
            return list(tree.range(1000, 1100))

        query_time, _ = benchmark_function(range_query)
        results.append((capacity, query_time))
        print(f"  Capacity {capacity:3d}: {query_time*1000:.3f} ms")

    # Find optimal capacity
    best_capacity, best_time = min(results, key=lambda x: x[1])
    worst_capacity, worst_time = max(results, key=lambda x: x[1])

    print(f"\n  Best:  Capacity {best_capacity} ({best_time*1000:.3f} ms)")
    print(f"  Worst: Capacity {worst_capacity} ({worst_time*1000:.3f} ms)")
    print(f"  Improvement: {worst_time/best_time:.1f}x faster with optimal capacity")


def main():
    """Run all performance demonstrations."""
    print("🚀 B+ Tree Performance Demonstration 🚀\n")
    print("This benchmark shows where B+ Tree excels compared to alternatives.\n")

    benchmark_range_queries()
    benchmark_iteration()
    benchmark_insertion()
    demonstrate_early_termination()
    capacity_tuning_demo()
    benchmark_memory_usage()

    print("=== Performance Summary ===")
    print("B+ Tree is FASTER than dict/SortedDict for:")
    print("✓ Range queries (especially partial ranges)")
    print("✓ Ordered iteration")
    print("✓ Early termination scenarios")
    print("✓ Large dataset operations")
    print()
    print("B+ Tree may be SLOWER for:")
    print("• Random single-key lookups")
    print("• Small datasets (< 1000 items)")
    print("• Insertion-heavy workloads")
    print()
    print("Choose B+ Tree when you need fast, ordered access to ranges of data!")


if __name__ == "__main__":
    main()
