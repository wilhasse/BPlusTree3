#!/usr/bin/env python3
"""
Profiler for B+ tree lookup performance to identify actual bottlenecks.
Uses cProfile and line_profiler to understand where time is spent.
"""

import cProfile
import pstats
import io
import time
import random
from bplus_tree import BPlusTreeMap
from sortedcontainers import SortedDict


def create_large_tree(size=50000, capacity=256):
    """Create a large B+ tree for profiling"""
    print(f"Creating B+ tree with {size:,} items (capacity={capacity})...")
    
    keys = list(range(size))
    random.shuffle(keys)
    values = [f"value_{k}" for k in keys]
    
    tree = BPlusTreeMap(capacity=capacity)
    for k, v in zip(keys, values):
        tree[k] = v
    
    return tree, keys


def profile_btree_lookups():
    """Profile B+ tree lookups using cProfile"""
    print("🔍 Profiling B+ Tree Lookups")
    print("=" * 50)
    
    # Create large tree
    tree, all_keys = create_large_tree(50000, 256)
    
    # Select random keys for lookup
    lookup_keys = random.sample(all_keys, 5000)
    
    print(f"Profiling {len(lookup_keys):,} lookups...")
    
    # Profile the lookup operations
    profiler = cProfile.Profile()
    
    def lookup_test():
        for key in lookup_keys:
            _ = tree[key]
    
    profiler.enable()
    lookup_test()
    profiler.disable()
    
    # Analyze results
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s)
    ps.sort_stats('cumulative')
    ps.print_stats(20)  # Top 20 functions
    
    print("Top functions by cumulative time:")
    print(s.getvalue())
    
    return profiler


def profile_sorteddict_lookups():
    """Profile SortedDict lookups for comparison"""
    print("\n🔍 Profiling SortedDict Lookups (for comparison)")
    print("=" * 50)
    
    # Create SortedDict with same data
    size = 50000
    keys = list(range(size))
    random.shuffle(keys)
    values = [f"value_{k}" for k in keys]
    
    sd = SortedDict()
    for k, v in zip(keys, values):
        sd[k] = v
    
    # Select random keys for lookup
    lookup_keys = random.sample(keys, 5000)
    
    print(f"Profiling {len(lookup_keys):,} SortedDict lookups...")
    
    # Profile the lookup operations
    profiler = cProfile.Profile()
    
    def lookup_test():
        for key in lookup_keys:
            _ = sd[key]
    
    profiler.enable()
    lookup_test()
    profiler.disable()
    
    # Analyze results
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s)
    ps.sort_stats('cumulative')
    ps.print_stats(10)  # Top 10 functions
    
    print("Top functions by cumulative time:")
    print(s.getvalue())


def detailed_timing_analysis():
    """Break down lookup timing by operation"""
    print("\n⏱️  Detailed Timing Analysis")
    print("=" * 50)
    
    tree, all_keys = create_large_tree(50000, 256)
    lookup_keys = random.sample(all_keys, 1000)
    
    # Time individual components
    print("Timing individual lookup components...")
    
    # 1. Tree traversal time
    traversal_times = []
    leaf_lookup_times = []
    
    for key in lookup_keys[:100]:  # Sample subset for detailed timing
        # Time tree traversal
        start = time.perf_counter()
        node = tree.root
        while not node.is_leaf():
            child_index = node.find_child_index(key)
            node = node.children[child_index]
        traversal_time = time.perf_counter() - start
        traversal_times.append(traversal_time * 1000000)  # microseconds
        
        # Time leaf lookup
        start = time.perf_counter()
        _ = node.get(key)
        leaf_time = time.perf_counter() - start
        leaf_lookup_times.append(leaf_time * 1000000)  # microseconds
    
    print(f"Average tree traversal time: {sum(traversal_times)/len(traversal_times):.2f}μs")
    print(f"Average leaf lookup time: {sum(leaf_lookup_times)/len(leaf_lookup_times):.2f}μs")
    
    # 2. Compare with optimized version
    optimized_times = []
    for key in lookup_keys[:100]:
        start = time.perf_counter()
        _ = tree.get(key)  # Uses our optimized version
        opt_time = time.perf_counter() - start
        optimized_times.append(opt_time * 1000000)
    
    print(f"Average optimized lookup time: {sum(optimized_times)/len(optimized_times):.2f}μs")
    
    # 3. Analyze tree structure
    print(f"\nTree structure analysis:")
    depth = 0
    node = tree.root
    while not node.is_leaf():
        depth += 1
        node = node.children[0]
    
    print(f"  Tree depth: {depth}")
    print(f"  Node capacity: {tree.capacity}")
    
    # Count nodes at each level
    if depth > 0:
        level_counts = []
        nodes_to_visit = [tree.root]
        
        for level in range(depth + 1):
            level_count = len(nodes_to_visit)
            level_counts.append(level_count)
            
            if level < depth:  # Not at leaf level
                next_level = []
                for node in nodes_to_visit:
                    if not node.is_leaf():
                        next_level.extend(node.children)
                nodes_to_visit = next_level
        
        for i, count in enumerate(level_counts):
            node_type = "leaf" if i == depth else "branch"
            print(f"  Level {i} ({node_type}): {count} nodes")


def memory_access_analysis():
    """Analyze memory access patterns"""
    print("\n💾 Memory Access Pattern Analysis")
    print("=" * 50)
    
    tree, all_keys = create_large_tree(10000, 256)  # Smaller for detailed analysis
    
    # Analyze node sizes and memory layout
    print("Node memory analysis:")
    
    # Sample a few nodes
    sample_leaf = tree.leaves
    print(f"  Leaf node:")
    print(f"    Keys: {len(sample_leaf.keys)} items")
    print(f"    Memory estimate: ~{len(sample_leaf.keys) * 8 * 2} bytes (keys + values)")
    
    if not tree.root.is_leaf():
        sample_branch = tree.root
        print(f"  Branch node:")
        print(f"    Keys: {len(sample_branch.keys)} items")
        print(f"    Children: {len(sample_branch.children)} items")
        print(f"    Memory estimate: ~{len(sample_branch.keys) * 8 + len(sample_branch.children) * 8} bytes")
    
    # Test cache effects with sequential vs random access
    print("\nCache effect analysis:")
    
    # Sequential access
    sequential_keys = sorted(random.sample(all_keys, 1000))
    start = time.perf_counter()
    for key in sequential_keys:
        _ = tree[key]
    sequential_time = time.perf_counter() - start
    
    # Random access
    random_keys = random.sample(all_keys, 1000)
    start = time.perf_counter()
    for key in random_keys:
        _ = tree[key]
    random_time = time.perf_counter() - start
    
    print(f"  Sequential access: {sequential_time*1000:.2f}ms")
    print(f"  Random access: {random_time*1000:.2f}ms")
    print(f"  Random penalty: {random_time/sequential_time:.2f}x slower")


if __name__ == "__main__":
    print("🔬 B+ Tree Lookup Performance Profiler")
    print("=" * 60)
    
    # Set random seed for reproducible results
    random.seed(42)
    
    # Run profiling
    profile_btree_lookups()
    profile_sorteddict_lookups()
    detailed_timing_analysis()
    memory_access_analysis()
    
    print("\n💡 Analysis Summary:")
    print("=" * 60)
    print("Check the profiling output above to identify:")
    print("1. Which functions consume the most time")
    print("2. How tree traversal vs leaf lookup compare")
    print("3. Memory access pattern effects")
    print("4. Comparison with SortedDict's performance profile")
