#!/usr/bin/env python3
"""
Benchmark bulk loading optimization for BPlusTreeMap
Tests construction time for sorted data insertion
"""

import time
import random
from bplus_tree import BPlusTreeMap

def benchmark_bulk_loading():
    """Compare regular insertion vs bulk loading for sorted data"""
    sizes = [1000, 5000, 10000, 50000]
    results = []
    
    print("Bulk Loading Benchmark")
    print("=" * 50)
    print(f"{'Size':<8} {'Regular':<12} {'Bulk Load':<12} {'Speedup':<10}")
    print("-" * 50)
    
    for size in sizes:
        # Generate sorted data
        items = [(i, f"value_{i}") for i in range(size)]
        
        # Benchmark regular insertion (sorted order)
        start_time = time.perf_counter()
        tree1 = BPlusTreeMap()
        for key, value in items:
            tree1[key] = value
        regular_time = time.perf_counter() - start_time
        
        # Benchmark bulk loading
        start_time = time.perf_counter()
        tree2 = BPlusTreeMap.from_sorted_items(items)
        bulk_time = time.perf_counter() - start_time
        
        # Verify both trees are identical
        assert len(tree1) == len(tree2) == size
        for key, value in items:
            assert tree1[key] == tree2[key] == value
        
        speedup = regular_time / bulk_time if bulk_time > 0 else float('inf')
        results.append((size, regular_time, bulk_time, speedup))
        
        print(f"{size:<8} {regular_time*1000:<11.1f}ms {bulk_time*1000:<11.1f}ms {speedup:<9.1f}x")
    
    return results

def benchmark_unsorted_vs_sorted():
    """Compare performance difference between sorted and unsorted data"""
    size = 10000
    
    # Generate data
    sorted_items = [(i, f"value_{i}") for i in range(size)]
    unsorted_items = sorted_items.copy()
    random.shuffle(unsorted_items)
    
    print("\nSorted vs Unsorted Data Construction")
    print("=" * 50)
    
    # Regular insertion with sorted data
    start_time = time.perf_counter()
    tree_sorted = BPlusTreeMap()
    for key, value in sorted_items:
        tree_sorted[key] = value
    sorted_time = time.perf_counter() - start_time
    
    # Regular insertion with unsorted data
    start_time = time.perf_counter()
    tree_unsorted = BPlusTreeMap()
    for key, value in unsorted_items:
        tree_unsorted[key] = value
    unsorted_time = time.perf_counter() - start_time
    
    # Bulk loading with sorted data
    start_time = time.perf_counter()
    tree_bulk = BPlusTreeMap.from_sorted_items(sorted_items)
    bulk_time = time.perf_counter() - start_time
    
    print(f"Regular insertion (sorted):   {sorted_time*1000:.1f}ms")
    print(f"Regular insertion (unsorted): {unsorted_time*1000:.1f}ms")
    print(f"Bulk loading (sorted):        {bulk_time*1000:.1f}ms")
    print(f"")
    print(f"Sorted vs Unsorted ratio:     {unsorted_time/sorted_time:.1f}x")
    print(f"Bulk vs Regular (sorted):     {sorted_time/bulk_time:.1f}x")
    print(f"Bulk vs Regular (unsorted):   {unsorted_time/bulk_time:.1f}x")

def verify_bulk_loading_correctness():
    """Verify bulk loading produces correct tree structure"""
    print("\nBulk Loading Correctness Test")
    print("=" * 50)
    
    test_cases = [
        [(1, 'a'), (2, 'b'), (3, 'c')],  # Small case
        [(i, f"val_{i}") for i in range(100)],  # Medium case
        [(i, f"value_{i}") for i in range(0, 1000, 2)],  # Sparse keys
    ]
    
    for i, items in enumerate(test_cases):
        # Build with regular insertion
        tree1 = BPlusTreeMap()
        for key, value in items:
            tree1[key] = value
        
        # Build with bulk loading
        tree2 = BPlusTreeMap.from_sorted_items(items)
        
        # Verify same contents
        assert len(tree1) == len(tree2) == len(items)
        
        # Check all key-value pairs
        for key, value in items:
            assert tree1[key] == value
            assert tree2[key] == value
            assert key in tree1
            assert key in tree2
        
        # Test iteration order
        list1 = list(tree1.items())
        list2 = list(tree2.items())
        assert list1 == list2 == items
        
        print(f"Test case {i+1} ({len(items)} items): ✓ PASSED")
    
    print("All correctness tests passed!")

if __name__ == "__main__":
    verify_bulk_loading_correctness()
    benchmark_bulk_loading()
    benchmark_unsorted_vs_sorted()