#!/usr/bin/env python3
"""
Performance benchmark for B+ Tree implementation.

This script runs standardized benchmarks and outputs results in a format
suitable for CI/CD performance tracking.
"""

import time
import random
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bplus_tree import BPlusTreeMap


class BenchmarkSuite:
    """Suite of performance benchmarks."""

    def __init__(self, size: int = 10000):
        self.size = size
        self.results = {}

    def time_operation(self, name: str, operation):
        """Time an operation and store the result."""
        start = time.perf_counter()
        result = operation()
        end = time.perf_counter()
        duration = end - start

        self.results[name] = {
            "duration": duration,
            "operations": self.size,
            "ops_per_second": self.size / duration if duration > 0 else 0,
        }

        return result

    def benchmark_sequential_insertion(self):
        """Benchmark sequential insertions."""
        tree = BPlusTreeMap()

        def insert_sequential():
            for i in range(self.size):
                tree[i] = f"value_{i}"
            return tree

        return self.time_operation("sequential_insertion", insert_sequential)

    def benchmark_random_insertion(self):
        """Benchmark random insertions."""
        tree = BPlusTreeMap()
        keys = list(range(self.size))
        random.shuffle(keys)

        def insert_random():
            for key in keys:
                tree[key] = f"value_{key}"
            return tree

        return self.time_operation("random_insertion", insert_random)

    def benchmark_lookups(self, tree: BPlusTreeMap):
        """Benchmark lookups on existing tree."""
        keys = list(range(self.size))
        random.shuffle(keys)

        def perform_lookups():
            for key in keys:
                _ = tree[key]

        self.time_operation("random_lookups", perform_lookups)

    def benchmark_range_queries(self, tree: BPlusTreeMap):
        """Benchmark range queries."""
        # Test 10% range queries
        range_size = self.size // 10

        def perform_range_queries():
            results = []
            for i in range(10):
                start = i * range_size
                end = (i + 1) * range_size
                results.append(list(tree.items(start, end)))
            return results

        return self.time_operation("range_queries_10_percent", perform_range_queries)

    def benchmark_iteration(self, tree: BPlusTreeMap):
        """Benchmark full iteration."""

        def iterate_tree():
            return list(tree.items())

        return self.time_operation("full_iteration", iterate_tree)

    def benchmark_deletions(self, tree: BPlusTreeMap):
        """Benchmark deletions."""
        keys = list(range(self.size))
        random.shuffle(keys)

        def perform_deletions():
            for key in keys:
                del tree[key]

        self.time_operation("random_deletions", perform_deletions)

    def benchmark_dict_comparison(self):
        """Compare with standard dict performance."""
        # B+ Tree sequential
        tree = BPlusTreeMap()
        tree_start = time.perf_counter()
        for i in range(self.size):
            tree[i] = f"value_{i}"
        tree_time = time.perf_counter() - tree_start

        # Dict sequential
        d = {}
        dict_start = time.perf_counter()
        for i in range(self.size):
            d[i] = f"value_{i}"
        dict_time = time.perf_counter() - dict_start

        self.results["comparison_vs_dict"] = {
            "bplustree_time": tree_time,
            "dict_time": dict_time,
            "ratio": tree_time / dict_time if dict_time > 0 else 0,
        }

        # Sorted iteration comparison
        tree_iter_start = time.perf_counter()
        tree_items = list(tree.items())
        tree_iter_time = time.perf_counter() - tree_iter_start

        dict_sort_start = time.perf_counter()
        dict_items = sorted(d.items())
        dict_sort_time = time.perf_counter() - dict_sort_start

        self.results["sorted_iteration_comparison"] = {
            "bplustree_time": tree_iter_time,
            "dict_sort_time": dict_sort_time,
            "ratio": tree_iter_time / dict_sort_time if dict_sort_time > 0 else 0,
        }

    def run_all_benchmarks(self):
        """Run all benchmarks and return results."""
        print(f"Running benchmarks with {self.size:,} items...")

        # Sequential insertion
        print("- Sequential insertion...")
        tree_seq = self.benchmark_sequential_insertion()

        # Random insertion
        print("- Random insertion...")
        tree_rand = self.benchmark_random_insertion()

        # Lookups
        print("- Random lookups...")
        self.benchmark_lookups(tree_seq)

        # Range queries
        print("- Range queries...")
        self.benchmark_range_queries(tree_seq)

        # Iteration
        print("- Full iteration...")
        self.benchmark_iteration(tree_seq)

        # Deletions
        print("- Random deletions...")
        self.benchmark_deletions(tree_seq)

        # Dict comparison
        print("- Dictionary comparison...")
        self.benchmark_dict_comparison()

        return self.results


def format_results(results: Dict[str, Any]) -> str:
    """Format results for display."""
    output = []
    output.append("\n" + "=" * 60)
    output.append("B+ Tree Performance Benchmark Results")
    output.append("=" * 60)

    for test_name, data in results.items():
        output.append(f"\n{test_name}:")
        if "duration" in data:
            output.append(f"  Duration: {data['duration']:.4f} seconds")
            if "ops_per_second" in data:
                output.append(f"  Operations/second: {data['ops_per_second']:,.0f}")
        else:
            for key, value in data.items():
                if isinstance(value, float):
                    output.append(f"  {key}: {value:.4f}")
                else:
                    output.append(f"  {key}: {value}")

    output.append("\n" + "=" * 60)
    return "\n".join(output)


def save_results(results: Dict[str, Any], filename: str = None):
    """Save results to JSON file."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"benchmark_results_{timestamp}.json"

    # Add metadata
    full_results = {
        "timestamp": datetime.now().isoformat(),
        "size": results.get("size", 10000),
        "results": results,
    }

    with open(filename, "w") as f:
        json.dump(full_results, f, indent=2)

    return filename


def main():
    """Run benchmarks with different sizes."""
    sizes = [1000, 10000, 50000] if "--full" in sys.argv else [10000]

    all_results = {}

    for size in sizes:
        print(f"\n{'='*60}")
        print(f"Running benchmarks for size: {size:,}")
        print("=" * 60)

        suite = BenchmarkSuite(size)
        results = suite.run_all_benchmarks()
        all_results[size] = results

        print(format_results(results))

    # Save results if requested
    if "--save" in sys.argv:
        filename = save_results(all_results)
        print(f"\nResults saved to: {filename}")

    # Check for performance regressions
    if "--check-regression" in sys.argv:
        # Simple regression check - you can make this more sophisticated
        baseline_size = 10000
        if baseline_size in all_results:
            sequential_time = all_results[baseline_size]["sequential_insertion"][
                "duration"
            ]
            if sequential_time > 0.5:  # 0.5 seconds threshold
                print(
                    f"\n⚠️  WARNING: Sequential insertion took {sequential_time:.4f}s, "
                    f"exceeding threshold of 0.5s"
                )
                sys.exit(1)

    print("\n✅ All benchmarks completed successfully!")


if __name__ == "__main__":
    main()
