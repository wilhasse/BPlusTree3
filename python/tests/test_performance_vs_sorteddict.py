"""
Compare B+ Tree performance against sortedcontainers.SortedDict.
This test will show the performance gap we need to close.
"""

import time
import random
import gc
from typing import Dict, List, Tuple
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bplus_tree import BPlusTreeMap

import pytest

try:
    from sortedcontainers import SortedDict
except ImportError:
    pytest.skip(
        "sortedcontainers not installed, skipping performance_vs_sortedcontainers tests",
        allow_module_level=True
    )


class PerformanceComparison:
    """Compare B+ Tree and SortedDict performance."""
    
    def __init__(self, size: int = 10000):
        self.size = size
        self.keys = list(range(size))
        self.random_keys = self.keys.copy()
        random.shuffle(self.random_keys)
        
    def measure_operation(self, operation, iterations: int = 1) -> float:
        """Measure operation time and return per-operation time in nanoseconds."""
        gc.collect()
        gc.disable()
        
        start = time.perf_counter()
        for _ in range(iterations):
            operation()
        end = time.perf_counter()
        
        gc.enable()
        total_time = end - start
        return (total_time * 1e9) / (iterations * self.size)
    
    def compare_lookup(self) -> Dict[str, float]:
        """Compare lookup performance."""
        # Build both structures
        btree = BPlusTreeMap(capacity=128)
        sdict = SortedDict()
        
        for key in self.keys:
            btree[key] = key * 2
            sdict[key] = key * 2
        
        # Measure B+ Tree lookup
        def btree_lookup():
            for key in self.random_keys:
                _ = btree[key]
        
        btree_time = self.measure_operation(btree_lookup, 10)
        
        # Measure SortedDict lookup
        def sdict_lookup():
            for key in self.random_keys:
                _ = sdict[key]
        
        sdict_time = self.measure_operation(sdict_lookup, 10)
        
        return {
            'btree_ns': btree_time,
            'sorteddict_ns': sdict_time,
            'ratio': btree_time / sdict_time if sdict_time > 0 else float('inf')
        }
    
    def compare_insert(self) -> Dict[str, float]:
        """Compare insertion performance."""
        # Random insert
        def btree_insert():
            btree = BPlusTreeMap(capacity=128)
            for key in self.random_keys:
                btree[key] = key * 2
        
        def sdict_insert():
            sdict = SortedDict()
            for key in self.random_keys:
                sdict[key] = key * 2
        
        btree_time = self.measure_operation(btree_insert)
        sdict_time = self.measure_operation(sdict_insert)
        
        return {
            'btree_ns': btree_time,
            'sorteddict_ns': sdict_time,
            'ratio': btree_time / sdict_time if sdict_time > 0 else float('inf')
        }
    
    def compare_range_query(self) -> Dict[str, float]:
        """Compare range query performance."""
        # Build both structures
        btree = BPlusTreeMap(capacity=128)
        sdict = SortedDict()
        
        for key in self.keys:
            btree[key] = key * 2
            sdict[key] = key * 2
        
        range_size = self.size // 10
        
        # B+ Tree range query
        def btree_range():
            count = 0
            for k, v in btree.items(self.size // 4, self.size // 4 + range_size):
                count += 1
        
        # SortedDict range query
        def sdict_range():
            count = 0
            for k in sdict.irange(self.size // 4, self.size // 4 + range_size):
                count += 1
        
        btree_time = self.measure_operation(btree_range, 100)
        sdict_time = self.measure_operation(sdict_range, 100)
        
        # Adjust for per-item time
        btree_time = btree_time * self.size / range_size
        sdict_time = sdict_time * self.size / range_size
        
        return {
            'btree_ns': btree_time,
            'sorteddict_ns': sdict_time,
            'ratio': btree_time / sdict_time if sdict_time > 0 else float('inf')
        }


def test_performance_comparison():
    """Run performance comparison tests."""
    print("B+ Tree vs SortedDict Performance Comparison")
    print("=" * 60)
    
    sizes = [1000, 10000, 100000]
    
    for size in sizes:
        print(f"\nData Size: {size:,} items")
        print("-" * 40)
        
        comp = PerformanceComparison(size)
        
        # Lookup comparison
        lookup = comp.compare_lookup()
        print(f"\nLookup Performance:")
        print(f"  B+ Tree:      {lookup['btree_ns']:.1f} ns/op")
        print(f"  SortedDict:   {lookup['sorteddict_ns']:.1f} ns/op")
        print(f"  Ratio:        {lookup['ratio']:.1f}x slower")
        
        # Insert comparison
        insert = comp.compare_insert()
        print(f"\nInsert Performance:")
        print(f"  B+ Tree:      {insert['btree_ns']:.1f} ns/op")
        print(f"  SortedDict:   {insert['sorteddict_ns']:.1f} ns/op")
        print(f"  Ratio:        {insert['ratio']:.1f}x slower")
        
        # Range query comparison
        range_query = comp.compare_range_query()
        print(f"\nRange Query Performance:")
        print(f"  B+ Tree:      {range_query['btree_ns']:.1f} ns/op")
        print(f"  SortedDict:   {range_query['sorteddict_ns']:.1f} ns/op")
        print(f"  Ratio:        {range_query['ratio']:.1f}x slower")
    
    print("\n" + "=" * 60)
    print("Performance gaps identified. Target: < 2x slower for all operations.")


if __name__ == "__main__":
    test_performance_comparison()