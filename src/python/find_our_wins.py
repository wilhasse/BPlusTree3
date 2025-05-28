#!/usr/bin/env python3
"""
Focused benchmark to explore scenarios where B+ Tree excels.
Based on initial findings, let's explore variations of winning scenarios.
"""

import random
import time
import statistics
from sortedcontainers import SortedDict
from bplus_tree import BPlusTreeMap


def explore_range_query_sweet_spot():
    """Find the range size sweet spot where B+ Tree wins"""
    print("🎯 Range Query Sweet Spot Analysis")
    print("=" * 50)
    
    size = 50000
    # Test various range sizes around our winning point (5000)
    range_sizes = [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 15000, 20000]
    
    # Pre-populate
    keys = list(range(size))
    random.shuffle(keys)
    values = [f"value_{k}" for k in keys]
    
    tree = BPlusTreeMap(capacity=128)
    sd = SortedDict()
    
    for k, v in zip(keys, values):
        tree[k] = v
        sd[k] = v
    
    print(f"Testing range queries on {size:,} items...\n")
    
    wins = 0
    total = 0
    
    for range_size in range_sizes:
        # Multiple random start points
        start_keys = [random.randint(0, size - range_size) for _ in range(10)]
        
        # B+ Tree
        btree_times = []
        for start_key in start_keys:
            end_key = start_key + range_size
            start_time = time.perf_counter()
            result = list(tree.items(start_key=start_key, end_key=end_key))
            end_time = time.perf_counter()
            btree_times.append(end_time - start_time)
        
        # SortedDict
        sd_times = []
        for start_key in start_keys:
            end_key = start_key + range_size
            start_time = time.perf_counter()
            result = [(k, sd[k]) for k in sd.irange(start_key, end_key, inclusive=(True, False))]
            end_time = time.perf_counter()
            sd_times.append(end_time - start_time)
        
        btree_avg = statistics.mean(btree_times) * 1000
        sd_avg = statistics.mean(sd_times) * 1000
        
        total += 1
        if btree_avg < sd_avg:
            wins += 1
            status = f"B+Tree WINS! {sd_avg/btree_avg:.2f}x faster 🏆"
        else:
            status = f"SortedDict wins ({btree_avg/sd_avg:.2f}x faster)"
        
        print(f"Range {range_size:>5}: B+Tree {btree_avg:>6.2f}ms, SortedDict {sd_avg:>6.2f}ms | {status}")
    
    print(f"\nB+ Tree wins: {wins}/{total} scenarios ({wins/total*100:.1f}%)")


def explore_iteration_size_scaling():
    """Find where iteration performance crosses over"""
    print("\n📈 Iteration Performance Scaling")
    print("=" * 50)
    
    sizes = [10000, 25000, 50000, 75000, 100000, 150000, 200000, 300000, 500000]
    
    wins = 0
    total = 0
    
    for size in sizes:
        print(f"Testing iteration over {size:,} items...")
        
        # Pre-populate with random order
        keys = list(range(size))
        random.shuffle(keys)
        values = [f"value_{k}" for k in keys]
        
        tree = BPlusTreeMap(capacity=128)
        sd = SortedDict()
        
        # Build time
        start_time = time.perf_counter()
        for k, v in zip(keys, values):
            tree[k] = v
        btree_build_time = time.perf_counter() - start_time
        
        start_time = time.perf_counter()
        for k, v in zip(keys, values):
            sd[k] = v
        sd_build_time = time.perf_counter() - start_time
        
        # Iteration time
        start_time = time.perf_counter()
        btree_items = list(tree.items())
        btree_iter_time = time.perf_counter() - start_time
        
        start_time = time.perf_counter()
        sd_items = list(sd.items())
        sd_iter_time = time.perf_counter() - start_time
        
        total += 1
        if btree_iter_time < sd_iter_time:
            wins += 1
            status = f"B+Tree WINS! {sd_iter_time/btree_iter_time:.2f}x faster 🏆"
        else:
            status = f"SortedDict wins ({btree_iter_time/sd_iter_time:.2f}x faster)"
        
        print(f"  Iteration: B+Tree {btree_iter_time*1000:>6.1f}ms, SortedDict {sd_iter_time*1000:>6.1f}ms | {status}")
        print(f"  Build: B+Tree {btree_build_time:>6.2f}s, SortedDict {sd_build_time:>6.2f}s")
        print()
    
    print(f"B+ Tree iteration wins: {wins}/{total} scenarios ({wins/total*100:.1f}%)")


def test_multiple_consecutive_ranges():
    """Test multiple consecutive range queries (common in analytics)"""
    print("\n🔄 Multiple Consecutive Range Queries")
    print("=" * 50)
    
    size = 100000
    range_size = 1000
    num_ranges = 50  # 50 consecutive ranges
    
    # Pre-populate
    keys = list(range(size))
    random.shuffle(keys)
    values = [f"value_{k}" for k in keys]
    
    tree = BPlusTreeMap(capacity=128)
    sd = SortedDict()
    
    for k, v in zip(keys, values):
        tree[k] = v
        sd[k] = v
    
    print(f"Testing {num_ranges} consecutive range queries of size {range_size} each...")
    
    # Generate consecutive ranges
    start_points = list(range(0, size - range_size * num_ranges, range_size))
    
    # B+ Tree - multiple ranges
    start_time = time.perf_counter()
    all_results = []
    for start_point in start_points:
        end_point = start_point + range_size
        result = list(tree.items(start_key=start_point, end_key=end_point))
        all_results.extend(result)
    btree_time = time.perf_counter() - start_time
    
    # SortedDict - multiple ranges  
    start_time = time.perf_counter()
    all_results = []
    for start_point in start_points:
        end_point = start_point + range_size
        result = [(k, sd[k]) for k in sd.irange(start_point, end_point, inclusive=(True, False))]
        all_results.extend(result)
    sd_time = time.perf_counter() - start_time
    
    if btree_time < sd_time:
        winner = f"B+Tree WINS! {sd_time/btree_time:.2f}x faster 🏆"
    else:
        winner = f"SortedDict wins ({btree_time/sd_time:.2f}x faster)"
    
    print(f"  B+Tree: {btree_time*1000:.2f}ms")
    print(f"  SortedDict: {sd_time*1000:.2f}ms")
    print(f"  Result: {winner}")


def test_range_updates():
    """Test updating all items in a range (like updating timestamps)"""
    print("\n✏️  Range Update Operations")
    print("=" * 50)
    
    size = 50000
    update_ranges = [100, 500, 1000, 2000, 5000]
    
    for range_size in update_ranges:
        print(f"\nTesting range update of {range_size} items...")
        
        # Pre-populate
        keys = list(range(size))
        random.shuffle(keys)
        values = [f"value_{k}" for k in keys]
        
        tree = BPlusTreeMap(capacity=128)
        sd = SortedDict()
        
        for k, v in zip(keys, values):
            tree[k] = v
            sd[k] = v
        
        # Choose random range to update
        start_key = random.randint(0, size - range_size)
        end_key = start_key + range_size
        
        # B+ Tree range update
        start_time = time.perf_counter()
        for k, v in tree.items(start_key=start_key, end_key=end_key):
            tree[k] = f"updated_{v}"
        btree_time = time.perf_counter() - start_time
        
        # Reset tree
        tree = BPlusTreeMap(capacity=128)
        for k, v in zip(keys, values):
            tree[k] = v
        
        # SortedDict range update
        start_time = time.perf_counter()
        for k in sd.irange(start_key, end_key, inclusive=(True, False)):
            sd[k] = f"updated_{sd[k]}"
        sd_time = time.perf_counter() - start_time
        
        if btree_time < sd_time:
            winner = f"B+Tree WINS! {sd_time/btree_time:.2f}x faster 🏆"
        else:
            winner = f"SortedDict wins ({btree_time/sd_time:.2f}x faster)"
        
        print(f"  B+Tree: {btree_time*1000:.2f}ms")
        print(f"  SortedDict: {sd_time*1000:.2f}ms")
        print(f"  Result: {winner}")


def test_partial_range_scans():
    """Test scanning ranges but stopping early (like LIMIT in SQL)"""
    print("\n🔍 Partial Range Scans (Early Termination)")
    print("=" * 50)
    
    size = 100000
    max_range = 10000
    limits = [10, 50, 100, 500, 1000]  # Stop after N items
    
    # Pre-populate
    keys = list(range(size))
    random.shuffle(keys)
    values = [f"value_{k}" for k in keys]
    
    tree = BPlusTreeMap(capacity=128)
    sd = SortedDict()
    
    for k, v in zip(keys, values):
        tree[k] = v
        sd[k] = v
    
    for limit in limits:
        print(f"\nTesting partial scan (limit {limit} items from range of {max_range})...")
        
        start_key = random.randint(0, size - max_range)
        end_key = start_key + max_range
        
        # B+ Tree partial scan
        start_time = time.perf_counter()
        result = []
        for k, v in tree.items(start_key=start_key, end_key=end_key):
            result.append((k, v))
            if len(result) >= limit:
                break
        btree_time = time.perf_counter() - start_time
        
        # SortedDict partial scan
        start_time = time.perf_counter()
        result = []
        for k in sd.irange(start_key, end_key, inclusive=(True, False)):
            result.append((k, sd[k]))
            if len(result) >= limit:
                break
        sd_time = time.perf_counter() - start_time
        
        if btree_time < sd_time:
            winner = f"B+Tree WINS! {sd_time/btree_time:.2f}x faster 🏆"
        else:
            winner = f"SortedDict wins ({btree_time/sd_time:.2f}x faster)"
        
        print(f"  B+Tree: {btree_time*1000:.3f}ms")
        print(f"  SortedDict: {sd_time*1000:.3f}ms")
        print(f"  Result: {winner}")


def main():
    print("🏆 Finding B+ Tree's Winning Scenarios")
    print("=" * 60)
    print("Exploring variations of scenarios where we showed promise...\n")
    
    explore_range_query_sweet_spot()
    explore_iteration_size_scaling()
    test_multiple_consecutive_ranges()
    test_range_updates()
    test_partial_range_scans()
    
    print("\n🎯 Summary")
    print("=" * 60)
    print("Look for scenarios marked with 🏆 - these are our competitive advantages!")


if __name__ == "__main__":
    main()