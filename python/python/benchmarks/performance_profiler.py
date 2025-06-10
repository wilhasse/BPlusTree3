"""
Performance profiling tool for B+ Tree implementation.

This module provides detailed profiling including:
- Function call analysis
- Line-by-line profiling
- Memory profiling
- Cache miss analysis
"""

import cProfile
import pstats
import io
import sys
import os
import time
from typing import Dict, List, Tuple, Any
from functools import wraps

try:
    from line_profiler import LineProfiler
    HAS_LINE_PROFILER = True
except ImportError:
    HAS_LINE_PROFILER = False
    print("Note: Install line_profiler for detailed line-by-line analysis: pip install line_profiler")

try:
    from memory_profiler import memory_usage
    HAS_MEMORY_PROFILER = True
except ImportError:
    HAS_MEMORY_PROFILER = False
    print("Note: Install memory_profiler for memory analysis: pip install memory-profiler")

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bplus_tree import BPlusTreeMap


class PerformanceProfiler:
    """Comprehensive performance profiler for B+ Tree operations."""
    
    def __init__(self):
        self.results = {}
        
    def profile_operation(self, name: str):
        """Decorator to profile a function."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # CPU profiling
                profiler = cProfile.Profile()
                profiler.enable()
                
                start_time = time.perf_counter()
                result = func(*args, **kwargs)
                end_time = time.perf_counter()
                
                profiler.disable()
                
                # Store results
                self.results[name] = {
                    'elapsed_time': end_time - start_time,
                    'profile': profiler
                }
                
                return result
            return wrapper
        return decorator
    
    def profile_insertions(self, size: int = 10000, capacity: int = 32):
        """Profile insertion operations."""
        print(f"\nProfiling insertions ({size:,} items, capacity={capacity})...")
        
        @self.profile_operation('sequential_insert')
        def sequential_insert():
            tree = BPlusTreeMap(capacity=capacity)
            for i in range(size):
                tree[i] = f'value_{i}'
            return tree
        
        @self.profile_operation('random_insert')
        def random_insert():
            import random
            tree = BPlusTreeMap(capacity=capacity)
            keys = list(range(size))
            random.shuffle(keys)
            for k in keys:
                tree[k] = f'value_{k}'
            return tree
        
        @self.profile_operation('bulk_insert')
        def bulk_insert():
            data = [(i, f'value_{i}') for i in range(size)]
            tree = BPlusTreeMap.from_sorted_items(data, capacity=capacity)
            return tree
        
        # Run profiled functions
        tree1 = sequential_insert()
        tree2 = random_insert()
        tree3 = bulk_insert()
        
        return tree1  # Return one for further testing
    
    def profile_lookups(self, tree: BPlusTreeMap, lookup_count: int = 10000):
        """Profile lookup operations."""
        print(f"\nProfiling lookups ({lookup_count:,} operations)...")
        
        import random
        size = len(tree)
        lookup_keys = [random.randint(0, size - 1) for _ in range(lookup_count)]
        
        @self.profile_operation('lookups')
        def perform_lookups():
            hits = 0
            for k in lookup_keys:
                if k in tree:
                    _ = tree[k]
                    hits += 1
            return hits
        
        hits = perform_lookups()
        print(f"  Hit rate: {hits / lookup_count * 100:.1f}%")
    
    def profile_range_queries(self, tree: BPlusTreeMap, query_count: int = 100):
        """Profile range query operations."""
        print(f"\nProfiling range queries ({query_count} queries)...")
        
        import random
        size = len(tree)
        
        @self.profile_operation('range_queries')
        def perform_ranges():
            total_items = 0
            for _ in range(query_count):
                start = random.randint(0, size - 100)
                end = start + random.randint(10, 100)
                for k, v in tree.range(start, end):
                    total_items += 1
            return total_items
        
        total = perform_ranges()
        print(f"  Total items retrieved: {total:,}")
    
    def profile_deletions(self, tree: BPlusTreeMap, delete_count: int = 1000):
        """Profile deletion operations."""
        print(f"\nProfiling deletions ({delete_count:,} operations)...")
        
        import random
        size = len(tree)
        delete_keys = random.sample(range(size), min(delete_count, size))
        
        @self.profile_operation('deletions')
        def perform_deletions():
            deleted = 0
            for k in delete_keys:
                try:
                    del tree[k]
                    deleted += 1
                except KeyError:
                    pass
            return deleted
        
        deleted = perform_deletions()
        print(f"  Items deleted: {deleted:,}")
    
    def analyze_results(self):
        """Analyze and print profiling results."""
        print("\n" + "=" * 60)
        print("PROFILING RESULTS")
        print("=" * 60)
        
        for operation, data in self.results.items():
            print(f"\n{operation.upper()}:")
            print(f"  Total time: {data['elapsed_time']:.4f} seconds")
            
            # Get top functions by cumulative time
            s = io.StringIO()
            ps = pstats.Stats(data['profile'], stream=s).sort_stats('cumulative')
            ps.print_stats(10)  # Top 10 functions
            
            output = s.getvalue()
            lines = output.split('\n')
            
            # Print relevant lines
            print("\n  Top functions by cumulative time:")
            in_table = False
            for line in lines:
                if 'ncalls' in line:
                    in_table = True
                    print("  " + line)
                elif in_table and line.strip():
                    # Skip if it's a header line
                    if not line.startswith(' '):
                        print("  " + line)
                elif in_table and not line.strip():
                    break
    
    def profile_memory_usage(self, size: int = 10000, capacity: int = 32):
        """Profile memory usage during operations."""
        if not HAS_MEMORY_PROFILER:
            print("\nMemory profiling skipped (install memory-profiler)")
            return
        
        print(f"\nProfiling memory usage ({size:,} items)...")
        
        def build_tree():
            tree = BPlusTreeMap(capacity=capacity)
            for i in range(size):
                tree[i] = f'value_{i}'
            return tree
        
        # Measure memory usage
        mem_usage = memory_usage(build_tree, interval=0.1)
        
        print(f"  Peak memory usage: {max(mem_usage):.1f} MB")
        print(f"  Memory overhead per item: {(max(mem_usage) - min(mem_usage)) / size * 1024:.1f} KB")
    
    def line_profile_critical_functions(self, size: int = 1000):
        """Profile critical functions line by line."""
        if not HAS_LINE_PROFILER:
            print("\nLine profiling skipped (install line_profiler)")
            return
        
        print(f"\nLine profiling critical functions ({size:,} items)...")
        
        # Create line profiler
        lp = LineProfiler()
        
        # Add functions to profile
        from bplus_tree import BPlusTreeMap, LeafNode, BranchNode
        
        lp.add_function(BPlusTreeMap.__setitem__)
        lp.add_function(BPlusTreeMap.__getitem__)
        lp.add_function(BPlusTreeMap._insert_recursive)
        lp.add_function(LeafNode.find_position)
        lp.add_function(BranchNode.find_child_index)
        
        # Run test workload
        lp.enable()
        
        tree = BPlusTreeMap(capacity=32)
        for i in range(size):
            tree[i] = f'value_{i}'
        
        for i in range(0, size, 10):
            _ = tree[i]
        
        lp.disable()
        
        # Print results
        lp.print_stats()
    
    def generate_optimization_report(self):
        """Generate optimization recommendations based on profiling."""
        print("\n" + "=" * 60)
        print("OPTIMIZATION RECOMMENDATIONS")
        print("=" * 60)
        
        recommendations = []
        
        # Analyze insertion patterns
        if 'sequential_insert' in self.results and 'random_insert' in self.results:
            seq_time = self.results['sequential_insert']['elapsed_time']
            rand_time = self.results['random_insert']['elapsed_time']
            
            if rand_time > seq_time * 2:
                recommendations.append(
                    "Random insertions are significantly slower than sequential. "
                    "Consider pre-sorting data when possible."
                )
        
        # Check bulk loading performance
        if 'sequential_insert' in self.results and 'bulk_insert' in self.results:
            seq_time = self.results['sequential_insert']['elapsed_time']
            bulk_time = self.results['bulk_insert']['elapsed_time']
            
            if bulk_time < seq_time * 0.5:
                recommendations.append(
                    "Bulk loading is much faster. Use from_sorted_items() when loading large datasets."
                )
        
        # Analyze function call overhead
        for operation, data in self.results.items():
            profile = data['profile']
            stats = pstats.Stats(profile)
            
            # Check for excessive function calls
            total_calls = sum(stats.stats[func][0] for func in stats.stats)
            time_ratio = total_calls / data['elapsed_time'] if data['elapsed_time'] > 0 else 0
            
            if time_ratio > 1000000:  # More than 1M calls per second
                recommendations.append(
                    f"{operation}: High function call overhead detected ({total_calls:,} calls). "
                    "Consider reducing function call depth or implementing critical paths in C."
                )
        
        # Print recommendations
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"\n{i}. {rec}")
        else:
            print("\nNo specific optimizations recommended at this time.")
        
        print("\n" + "=" * 60)


def main():
    """Run comprehensive performance profiling."""
    profiler = PerformanceProfiler()
    
    # Profile different operations
    tree = profiler.profile_insertions(size=10000, capacity=32)
    profiler.profile_lookups(tree, lookup_count=10000)
    profiler.profile_range_queries(tree, query_count=100)
    profiler.profile_deletions(tree, delete_count=1000)
    
    # Memory profiling
    profiler.profile_memory_usage(size=10000)
    
    # Line profiling
    profiler.line_profile_critical_functions(size=1000)
    
    # Analyze results
    profiler.analyze_results()
    
    # Generate recommendations
    profiler.generate_optimization_report()


if __name__ == '__main__':
    main()