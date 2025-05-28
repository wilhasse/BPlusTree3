#!/usr/bin/env python3
"""
Extended capacity analysis to find true optimal capacity and identify performance bottlenecks.
"""

import time
import statistics
from typing import List, Tuple
from bplus_tree import BPlusTreeMap

def find_optimal_capacity(max_capacity: int = 128, sizes: List[int] = [1000, 10000]):
    """Find the true optimal capacity by testing a wide range"""
    
    print("🔍 Finding Optimal B+ Tree Capacity")
    print("=" * 60)
    
    # Test capacities from 3 to max_capacity
    test_capacities = [3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 48, 64, 96, 128]
    test_capacities = [c for c in test_capacities if c <= max_capacity]
    
    results = {}
    
    for capacity in test_capacities:
        print(f"Testing capacity {capacity}...")
        
        capacity_times = []
        
        for size in sizes:
            # Generate test data
            keys = list(range(size))
            values = [f"value_{k}" for k in keys]
            
            # Test insertion performance
            times = []
            for _ in range(3):  # 3 measurements
                tree = BPlusTreeMap(capacity=capacity)
                
                start_time = time.perf_counter()
                for k, v in zip(keys, values):
                    tree[k] = v
                end_time = time.perf_counter()
                
                times.append(end_time - start_time)
            
            avg_time = statistics.mean(times)
            capacity_times.append(avg_time)
        
        results[capacity] = statistics.mean(capacity_times)
        print(f"  Capacity {capacity}: {results[capacity]*1000:.2f}ms average")
    
    # Find optimal
    best_capacity = min(results.keys(), key=lambda k: results[k])
    best_time = results[best_capacity]
    
    print(f"\n🏆 Results:")
    print(f"{'Capacity':>8} | {'Avg Time (ms)':>12} | {'Relative':>10}")
    print("-" * 35)
    
    for capacity in sorted(results.keys()):
        time_ms = results[capacity] * 1000
        relative = results[capacity] / best_time
        marker = " ✅" if capacity == best_capacity else ""
        print(f"{capacity:>8} | {time_ms:>10.2f} | {relative:>8.2f}x{marker}")
    
    return best_capacity, results

def analyze_performance_bottlenecks():
    """Analyze where our B+ Tree is spending time"""
    
    print("\n🔬 Performance Bottleneck Analysis")
    print("=" * 60)
    
    import cProfile
    import pstats
    import io
    
    # Profile insertion operations
    tree = BPlusTreeMap(capacity=32)
    keys = list(range(10000))
    values = [f"value_{k}" for k in keys]
    
    pr = cProfile.Profile()
    pr.enable()
    
    for k, v in zip(keys, values):
        tree[k] = v
    
    pr.disable()
    
    # Analyze results
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)  # Top 20 functions
    
    profile_output = s.getvalue()
    
    print("Top time-consuming functions during insertion:")
    print("-" * 50)
    lines = profile_output.split('\n')
    
    # Find the actual data lines (skip headers)
    data_started = False
    for line in lines:
        if 'cumulative' in line:
            data_started = True
            continue
        if data_started and line.strip():
            if 'bplus_tree.py' in line or any(method in line for method in 
                ['insert', 'split', 'find', '__setitem__', 'merge']):
                print(line)

def memory_usage_analysis():
    """Analyze memory usage patterns"""
    
    print("\n💾 Memory Usage Analysis")
    print("=" * 60)
    
    import sys
    
    capacities = [4, 16, 32, 64, 128]
    size = 10000
    
    for capacity in capacities:
        tree = BPlusTreeMap(capacity=capacity)
        
        # Insert data
        for i in range(size):
            tree[i] = f"value_{i}"
        
        # Estimate memory usage
        def get_tree_memory(node):
            """Rough estimate of tree memory usage"""
            if node is None:
                return 0
            
            memory = sys.getsizeof(node)
            memory += sys.getsizeof(node.keys)
            
            if hasattr(node, 'values'):  # Leaf node
                memory += sys.getsizeof(node.values)
                memory += sum(sys.getsizeof(v) for v in node.values)
            else:  # Branch node
                memory += sys.getsizeof(node.children)
                for child in node.children:
                    memory += get_tree_memory(child)
            
            return memory
        
        total_memory = get_tree_memory(tree.root)
        memory_per_item = total_memory / size
        
        print(f"Capacity {capacity:>3}: {total_memory/1024:.1f}KB total, {memory_per_item:.1f}B per item")

def theoretical_performance_limits():
    """Calculate theoretical performance limits"""
    
    print("\n📐 Theoretical Performance Analysis")
    print("=" * 60)
    
    def tree_depth(capacity: int, num_items: int) -> int:
        """Calculate tree depth for given capacity and items"""
        if num_items <= capacity:
            return 1
        
        # For a B+ tree, each internal node can have up to capacity+1 children
        # and each leaf can hold up to capacity items
        items_per_leaf = capacity
        leaves_needed = (num_items + items_per_leaf - 1) // items_per_leaf
        
        depth = 1  # Start with leaf level
        nodes_at_level = leaves_needed
        
        while nodes_at_level > 1:
            nodes_at_level = (nodes_at_level + capacity) // (capacity + 1)
            depth += 1
        
        return depth
    
    sizes = [1000, 10000, 100000]
    capacities = [4, 8, 16, 32, 64, 128]
    
    print(f"{'Capacity':>8} | {'Size':>8} | {'Depth':>5} | {'Ops/Lookup':>10}")
    print("-" * 45)
    
    for capacity in capacities:
        for size in sizes:
            depth = tree_depth(capacity, size)
            # Each lookup requires approximately 'depth' comparisons
            ops_per_lookup = depth * capacity // 2  # Binary search within node
            print(f"{capacity:>8} | {size:>8} | {depth:>5} | {ops_per_lookup:>10}")

if __name__ == "__main__":
    # Find optimal capacity
    best_capacity, capacity_results = find_optimal_capacity(128)
    
    # Analyze bottlenecks
    analyze_performance_bottlenecks()
    
    # Memory analysis
    memory_usage_analysis()
    
    # Theoretical limits
    theoretical_performance_limits()
    
    print(f"\n🎯 Conclusion: Optimal capacity appears to be {best_capacity}")
    print("   But check if performance plateaus suggest even higher values might work!")