#!/usr/bin/env python3
"""
Benchmarks designed to find scenarios where B+ Tree outperforms SortedDict.

Focus on operations that play to B+ Tree strengths:
- Sequential access patterns
- Range queries
- Batch operations
- Memory-constrained scenarios
- Write-heavy workloads with locality
"""

import random
import time
import statistics
from typing import List, Tuple
from sortedcontainers import SortedDict
from bplus_tree import BPlusTreeMap


def benchmark_sequential_insertions():
    """Sequential insertions should favor B+ Tree due to no rebalancing"""
    print("🔄 Sequential Insertion Benchmark")
    print("=" * 50)
    
    sizes = [1000, 5000, 10000]
    
    for size in sizes:
        print(f"\nTesting {size:,} sequential insertions...")
        
        # B+ Tree
        btree_times = []
        for _ in range(3):
            tree = BPlusTreeMap(capacity=128)
            start = time.perf_counter()
            for i in range(size):
                tree[i] = f"value_{i}"
            end = time.perf_counter()
            btree_times.append(end - start)
        
        # SortedDict
        sorted_dict_times = []
        for _ in range(3):
            sd = SortedDict()
            start = time.perf_counter()
            for i in range(size):
                sd[i] = f"value_{i}"
            end = time.perf_counter()
            sorted_dict_times.append(end - start)
        
        btree_avg = statistics.mean(btree_times) * 1000
        sd_avg = statistics.mean(sorted_dict_times) * 1000
        
        if btree_avg < sd_avg:
            winner = f"B+Tree WINS! {sd_avg/btree_avg:.2f}x faster"
        else:
            winner = f"SortedDict wins ({btree_avg/sd_avg:.2f}x faster)"
        
        print(f"  B+Tree: {btree_avg:.2f}ms")
        print(f"  SortedDict: {sd_avg:.2f}ms")
        print(f"  Result: {winner}")


def benchmark_large_range_queries():
    """Large range queries should favor B+ Tree's leaf chain traversal"""
    print("\n📊 Large Range Query Benchmark")
    print("=" * 50)
    
    size = 50000
    range_sizes = [100, 1000, 5000, 10000]  # Different range sizes
    
    # Pre-populate both structures
    keys = list(range(size))
    random.shuffle(keys)  # Insert in random order
    values = [f"value_{k}" for k in keys]
    
    tree = BPlusTreeMap(capacity=128)
    sd = SortedDict()
    
    for k, v in zip(keys, values):
        tree[k] = v
        sd[k] = v
    
    print(f"Pre-populated with {size:,} items")
    
    for range_size in range_sizes:
        print(f"\nTesting range queries of size {range_size:,}...")
        
        # Generate random start points
        start_keys = random.sample(range(0, size - range_size, 100), 10)
        
        # B+ Tree range queries
        btree_times = []
        for start_key in start_keys:
            end_key = start_key + range_size
            start_time = time.perf_counter()
            result = list(tree.items(start_key=start_key, end_key=end_key))
            end_time = time.perf_counter()
            btree_times.append(end_time - start_time)
        
        # SortedDict range queries
        sd_times = []
        for start_key in start_keys:
            end_key = start_key + range_size
            start_time = time.perf_counter()
            result = [(k, sd[k]) for k in sd.irange(start_key, end_key, inclusive=(True, False))]
            end_time = time.perf_counter()
            sd_times.append(end_time - start_time)
        
        btree_avg = statistics.mean(btree_times) * 1000
        sd_avg = statistics.mean(sd_times) * 1000
        
        if btree_avg < sd_avg:
            winner = f"B+Tree WINS! {sd_avg/btree_avg:.2f}x faster"
        else:
            winner = f"SortedDict wins ({btree_avg/sd_avg:.2f}x faster)"
        
        print(f"  B+Tree: {btree_avg:.2f}ms")
        print(f"  SortedDict: {sd_avg:.2f}ms")
        print(f"  Result: {winner}")


def benchmark_full_iteration():
    """Full iteration should favor B+ Tree's linked leaf structure"""
    print("\n🔄 Full Iteration Benchmark")
    print("=" * 50)
    
    sizes = [10000, 50000, 100000]
    
    for size in sizes:
        print(f"\nTesting full iteration over {size:,} items...")
        
        # Pre-populate with random insertion order
        keys = list(range(size))
        random.shuffle(keys)
        values = [f"value_{k}" for k in keys]
        
        tree = BPlusTreeMap(capacity=128)
        sd = SortedDict()
        
        for k, v in zip(keys, values):
            tree[k] = v
            sd[k] = v
        
        # B+ Tree iteration
        btree_times = []
        for _ in range(3):
            start_time = time.perf_counter()
            result = list(tree.items())
            end_time = time.perf_counter()
            btree_times.append(end_time - start_time)
        
        # SortedDict iteration
        sd_times = []
        for _ in range(3):
            start_time = time.perf_counter()
            result = list(sd.items())
            end_time = time.perf_counter()
            sd_times.append(end_time - start_time)
        
        btree_avg = statistics.mean(btree_times) * 1000
        sd_avg = statistics.mean(sd_times) * 1000
        
        if btree_avg < sd_avg:
            winner = f"B+Tree WINS! {sd_avg/btree_avg:.2f}x faster"
        else:
            winner = f"SortedDict wins ({btree_avg/sd_avg:.2f}x faster)"
        
        print(f"  B+Tree: {btree_avg:.2f}ms")
        print(f"  SortedDict: {sd_avg:.2f}ms")
        print(f"  Result: {winner}")


def benchmark_batch_operations():
    """Batch operations should favor B+ Tree's specialized methods"""
    print("\n📦 Batch Operations Benchmark")
    print("=" * 50)
    
    size = 10000
    batch_sizes = [10, 100, 1000]
    
    for batch_size in batch_sizes:
        print(f"\nTesting batch deletion of {batch_size} items from {size} total...")
        
        # Pre-populate
        keys = list(range(size))
        values = [f"value_{k}" for k in keys]
        
        # Test multiple times
        btree_times = []
        sd_times = []
        
        for _ in range(5):
            # Random keys to delete
            keys_to_delete = random.sample(keys, batch_size)
            
            # B+ Tree batch deletion
            tree = BPlusTreeMap(capacity=128)
            for k, v in zip(keys, values):
                tree[k] = v
            
            start_time = time.perf_counter()
            deleted_count = tree.delete_batch(keys_to_delete)
            end_time = time.perf_counter()
            btree_times.append(end_time - start_time)
            
            # SortedDict individual deletions
            sd = SortedDict()
            for k, v in zip(keys, values):
                sd[k] = v
            
            start_time = time.perf_counter()
            deleted_count = 0
            for k in keys_to_delete:
                if k in sd:
                    del sd[k]
                    deleted_count += 1
            end_time = time.perf_counter()
            sd_times.append(end_time - start_time)
        
        btree_avg = statistics.mean(btree_times) * 1000
        sd_avg = statistics.mean(sd_times) * 1000
        
        if btree_avg < sd_avg:
            winner = f"B+Tree WINS! {sd_avg/btree_avg:.2f}x faster"
        else:
            winner = f"SortedDict wins ({btree_avg/sd_avg:.2f}x faster)"
        
        print(f"  B+Tree (batch): {btree_avg:.2f}ms")
        print(f"  SortedDict (individual): {sd_avg:.2f}ms")
        print(f"  Result: {winner}")


def benchmark_write_heavy_locality():
    """Write-heavy workloads with locality should favor B+ Tree"""
    print("\n✍️  Write-Heavy with Locality Benchmark")
    print("=" * 50)
    
    size = 10000
    locality_ranges = [10, 100, 1000]  # How clustered the writes are
    
    for locality_range in locality_ranges:
        print(f"\nTesting write-heavy workload with locality range {locality_range}...")
        
        # Generate clustered write pattern
        operations = []
        for _ in range(size):
            # Pick a random cluster center
            center = random.randint(0, size)
            # Pick a key within locality range of center
            key = center + random.randint(-locality_range//2, locality_range//2)
            key = max(0, min(size*2, key))  # Clamp to reasonable range
            operations.append(('write', key, f"value_{key}"))
        
        # B+ Tree
        btree_times = []
        for _ in range(3):
            tree = BPlusTreeMap(capacity=128)
            start_time = time.perf_counter()
            for op, key, value in operations:
                tree[key] = value
            end_time = time.perf_counter()
            btree_times.append(end_time - start_time)
        
        # SortedDict
        sd_times = []
        for _ in range(3):
            sd = SortedDict()
            start_time = time.perf_counter()
            for op, key, value in operations:
                sd[key] = value
            end_time = time.perf_counter()
            sd_times.append(end_time - start_time)
        
        btree_avg = statistics.mean(btree_times) * 1000
        sd_avg = statistics.mean(sd_times) * 1000
        
        if btree_avg < sd_avg:
            winner = f"B+Tree WINS! {sd_avg/btree_avg:.2f}x faster"
        else:
            winner = f"SortedDict wins ({btree_avg/sd_avg:.2f}x faster)"
        
        print(f"  B+Tree: {btree_avg:.2f}ms")
        print(f"  SortedDict: {sd_avg:.2f}ms")
        print(f"  Result: {winner}")


def benchmark_small_range_scans():
    """Small, frequent range scans"""
    print("\n🔍 Small Range Scan Benchmark")
    print("=" * 50)
    
    size = 50000
    num_queries = 1000
    range_size = 10  # Small ranges
    
    # Pre-populate
    keys = list(range(size))
    random.shuffle(keys)
    values = [f"value_{k}" for k in keys]
    
    tree = BPlusTreeMap(capacity=128)
    sd = SortedDict()
    
    for k, v in zip(keys, values):
        tree[k] = v
        sd[k] = v
    
    # Generate many small range queries
    query_starts = [random.randint(0, size - range_size) for _ in range(num_queries)]
    
    print(f"Testing {num_queries} small range queries (size {range_size}) on {size:,} items...")
    
    # B+ Tree
    btree_times = []
    for _ in range(3):
        start_time = time.perf_counter()
        for start_key in query_starts:
            end_key = start_key + range_size
            result = list(tree.items(start_key=start_key, end_key=end_key))
        end_time = time.perf_counter()
        btree_times.append(end_time - start_time)
    
    # SortedDict
    sd_times = []
    for _ in range(3):
        start_time = time.perf_counter()
        for start_key in query_starts:
            end_key = start_key + range_size
            result = [(k, sd[k]) for k in sd.irange(start_key, end_key, inclusive=(True, False))]
        end_time = time.perf_counter()
        sd_times.append(end_time - start_time)
    
    btree_avg = statistics.mean(btree_times) * 1000
    sd_avg = statistics.mean(sd_times) * 1000
    
    if btree_avg < sd_avg:
        winner = f"B+Tree WINS! {sd_avg/btree_avg:.2f}x faster"
    else:
        winner = f"SortedDict wins ({btree_avg/sd_avg:.2f}x faster)"
    
    print(f"  B+Tree: {btree_avg:.2f}ms")
    print(f"  SortedDict: {sd_avg:.2f}ms")
    print(f"  Result: {winner}")


def benchmark_memory_pressure():
    """Test under memory pressure (large datasets)"""
    print("\n💾 Memory Pressure Benchmark")
    print("=" * 50)
    
    # Use very large dataset to stress memory hierarchy
    size = 200000
    
    print(f"Testing with large dataset ({size:,} items)...")
    print("This may take a few minutes...")
    
    # Generate data
    keys = list(range(size))
    random.shuffle(keys)
    values = [f"value_{k:06d}" for k in keys]  # Longer values
    
    # B+ Tree insertion
    print("  Building B+ Tree...")
    start_time = time.perf_counter()
    tree = BPlusTreeMap(capacity=128)
    for k, v in zip(keys, values):
        tree[k] = v
    btree_build_time = time.perf_counter() - start_time
    
    # SortedDict insertion
    print("  Building SortedDict...")
    start_time = time.perf_counter()
    sd = SortedDict()
    for k, v in zip(keys, values):
        sd[k] = v
    sd_build_time = time.perf_counter() - start_time
    
    print(f"\nBuild time comparison:")
    print(f"  B+Tree: {btree_build_time:.2f}s")
    print(f"  SortedDict: {sd_build_time:.2f}s")
    
    if btree_build_time < sd_build_time:
        winner = f"B+Tree WINS! {sd_build_time/btree_build_time:.2f}x faster"
    else:
        winner = f"SortedDict wins ({btree_build_time/sd_build_time:.2f}x faster)"
    
    print(f"  Result: {winner}")
    
    # Test iteration on large dataset
    print(f"\nFull iteration over {size:,} items:")
    
    start_time = time.perf_counter()
    btree_items = list(tree.items())
    btree_iter_time = time.perf_counter() - start_time
    
    start_time = time.perf_counter()
    sd_items = list(sd.items())
    sd_iter_time = time.perf_counter() - start_time
    
    print(f"  B+Tree: {btree_iter_time:.2f}s")
    print(f"  SortedDict: {sd_iter_time:.2f}s")
    
    if btree_iter_time < sd_iter_time:
        winner = f"B+Tree WINS! {sd_iter_time/btree_iter_time:.2f}x faster"
    else:
        winner = f"SortedDict wins ({btree_iter_time/sd_iter_time:.2f}x faster)"
    
    print(f"  Result: {winner}")


def main():
    print("🏆 Competitive Benchmark: Finding B+ Tree's Strengths")
    print("=" * 60)
    print("Testing scenarios where B+ Tree might outperform SortedDict...")
    print()
    
    # Run all benchmarks
    benchmark_sequential_insertions()
    benchmark_large_range_queries() 
    benchmark_full_iteration()
    benchmark_batch_operations()
    benchmark_write_heavy_locality()
    benchmark_small_range_scans()
    benchmark_memory_pressure()
    
    print("\n🎯 Summary")
    print("=" * 60)
    print("Look for scenarios where B+Tree WINS! above.")
    print("These represent our competitive advantages that could be")
    print("marketed as use cases where B+ Tree is the better choice.")


if __name__ == "__main__":
    main()