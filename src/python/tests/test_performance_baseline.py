"""
Test to establish baseline performance metrics before optimization.
This will measure the current implementation and compare each optimization step.
"""

import time
import random
import gc
from typing import Dict, List, Tuple
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bplus_tree import BPlusTreeMap


class PerformanceBaseline:
    """Measure baseline performance metrics for B+ tree operations."""
    
    def __init__(self, tree_size: int = 10000, order: int = 128):
        self.tree_size = tree_size
        self.order = order
        self.keys = list(range(tree_size))
        random.shuffle(self.keys)
        self.tree = None
        
    def measure_operation(self, operation, iterations: int = 1) -> Tuple[float, float]:
        """Measure operation time and return (total_time, per_operation_time)."""
        gc.collect()
        gc.disable()
        
        start = time.perf_counter()
        for _ in range(iterations):
            operation()
        end = time.perf_counter()
        
        gc.enable()
        total_time = end - start
        per_op_time = total_time / iterations
        return total_time, per_op_time
    
    def test_sequential_insert(self) -> Dict[str, float]:
        """Test sequential insertion performance."""
        self.tree = BPlusTreeMap(capacity=self.order)
        
        def insert_all():
            for i in range(self.tree_size):
                self.tree[i] = i * 2
        
        total_time, per_op_time = self.measure_operation(insert_all)
        
        return {
            'total_time': total_time,
            'per_operation_ns': per_op_time * 1e9 / self.tree_size,
            'operations_per_second': self.tree_size / total_time
        }
    
    def test_random_insert(self) -> Dict[str, float]:
        """Test random insertion performance."""
        self.tree = BPlusTreeMap(capacity=self.order)
        
        def insert_all():
            for key in self.keys:
                self.tree[key] = key * 2
        
        total_time, per_op_time = self.measure_operation(insert_all)
        
        return {
            'total_time': total_time,
            'per_operation_ns': per_op_time * 1e9 / self.tree_size,
            'operations_per_second': self.tree_size / total_time
        }
    
    def test_lookup_performance(self) -> Dict[str, float]:
        """Test lookup performance on full tree."""
        # Build tree first
        self.tree = BPlusTreeMap(capacity=self.order)
        for key in self.keys:
            self.tree[key] = key * 2
        
        lookup_iterations = 10
        
        def lookup_all():
            for key in self.keys:
                _ = self.tree[key]
        
        total_time, per_op_time = self.measure_operation(lookup_all, lookup_iterations)
        
        return {
            'total_time': total_time,
            'per_operation_ns': per_op_time * 1e9 / self.tree_size,
            'operations_per_second': (self.tree_size * lookup_iterations) / total_time
        }
    
    def test_range_query(self) -> Dict[str, float]:
        """Test range query performance."""
        # Build tree first
        self.tree = BPlusTreeMap(capacity=self.order)
        for i in range(self.tree_size):
            self.tree[i] = i * 2
        
        range_size = self.tree_size // 10  # 10% of data
        
        def range_queries():
            # Test 10 different ranges
            for start in range(0, self.tree_size - range_size, self.tree_size // 10):
                count = 0
                for k, v in self.tree.items(start, start + range_size):
                    count += 1
        
        total_time, per_op_time = self.measure_operation(range_queries)
        
        return {
            'total_time': total_time,
            'ranges_per_second': 10 / total_time,
            'items_per_second': (range_size * 10) / total_time
        }
    
    def run_all_tests(self) -> Dict[str, Dict[str, float]]:
        """Run all performance tests and return results."""
        results = {
            'sequential_insert': self.test_sequential_insert(),
            'random_insert': self.test_random_insert(),
            'lookup': self.test_lookup_performance(),
            'range_query': self.test_range_query()
        }
        return results


def test_baseline_performance():
    """Test to establish baseline performance metrics."""
    print("Establishing B+ Tree Performance Baseline")
    print("=" * 50)
    
    # Test with different tree sizes
    sizes = [1000, 10000, 100000]
    
    for size in sizes:
        print(f"\nTree Size: {size:,} items")
        print("-" * 30)
        
        baseline = PerformanceBaseline(tree_size=size)
        results = baseline.run_all_tests()
        
        for test_name, metrics in results.items():
            print(f"\n{test_name.replace('_', ' ').title()}:")
            for metric, value in metrics.items():
                if 'per_second' in metric:
                    print(f"  {metric}: {value:,.0f}")
                elif 'ns' in metric:
                    print(f"  {metric}: {value:.1f}")
                else:
                    print(f"  {metric}: {value:.4f}s")
    
    # Save baseline for comparison
    print("\n" + "=" * 50)
    print("Baseline established. Use these metrics to measure optimization impact.")


if __name__ == "__main__":
    test_baseline_performance()