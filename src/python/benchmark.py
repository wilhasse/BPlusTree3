#!/usr/bin/env python3
"""
Performance benchmark comparing BPlusTreeMap with SortedDict from sortedcontainers.

This benchmark tests various operations across different dataset sizes to compare
the performance characteristics of our B+ Tree implementation against the
well-optimized SortedDict.

Usage:
    python benchmark.py                    # Run all benchmarks
    python benchmark.py --quick            # Quick benchmark (smaller datasets)
    python benchmark.py --operation insert # Only test insertions
    python benchmark.py --sizes 1000,10000 # Test specific sizes
    python benchmark.py --capacity 4       # Test specific B+ tree capacity
"""

import argparse
import gc
import random
import statistics
import sys
import time
from typing import List, Tuple, Dict, Callable, Any

try:
    from sortedcontainers import SortedDict
except ImportError:
    print("❌ sortedcontainers not installed. Install with: pip install sortedcontainers")
    sys.exit(1)

from bplus_tree import BPlusTreeMap


class BenchmarkRunner:
    """Manages and executes performance benchmarks"""
    
    def __init__(self, seed: int = 42, warmup_iterations: int = 3, measurement_iterations: int = 5):
        self.seed = seed
        self.warmup_iterations = warmup_iterations
        self.measurement_iterations = measurement_iterations
        random.seed(seed)
        
        # Store results for analysis
        self.results: Dict[str, Dict[str, List[float]]] = {}
    
    def time_operation(self, operation: Callable, name: str, size: int) -> Tuple[float, float]:
        """Time an operation with warmup and multiple measurements"""
        
        # Warmup runs
        for _ in range(self.warmup_iterations):
            operation()
            gc.collect()
        
        # Measurement runs
        times = []
        for _ in range(self.measurement_iterations):
            start_time = time.perf_counter()
            operation()
            end_time = time.perf_counter()
            times.append(end_time - start_time)
            gc.collect()
        
        # Store results
        if name not in self.results:
            self.results[name] = {}
        if str(size) not in self.results[name]:
            self.results[name][str(size)] = []
        self.results[name][str(size)].extend(times)
        
        mean_time = statistics.mean(times)
        std_time = statistics.stdev(times) if len(times) > 1 else 0
        return mean_time, std_time
    
    def generate_random_keys(self, size: int, key_range: int = None) -> List[int]:
        """Generate random keys for testing"""
        if key_range is None:
            key_range = size * 10  # 10x key space to reduce collisions
        
        keys = set()
        while len(keys) < size:
            keys.add(random.randint(1, key_range))
        return list(keys)
    
    def benchmark_insertions(self, size: int, capacity: int = 4) -> Dict[str, Tuple[float, float]]:
        """Benchmark insertion operations"""
        keys = self.generate_random_keys(size)
        values = [f"value_{k}" for k in keys]
        
        def insert_btree():
            tree = BPlusTreeMap(capacity=capacity)
            for k, v in zip(keys, values):
                tree[k] = v
            return tree
        
        def insert_sorted_dict():
            sd = SortedDict()
            for k, v in zip(keys, values):
                sd[k] = v
            return sd
        
        btree_time, btree_std = self.time_operation(insert_btree, f"btree_insert_cap{capacity}", size)
        sorted_dict_time, sorted_dict_std = self.time_operation(insert_sorted_dict, "sorted_dict_insert", size)
        
        return {
            'btree': (btree_time, btree_std),
            'sorted_dict': (sorted_dict_time, sorted_dict_std)
        }
    
    def benchmark_lookups(self, size: int, capacity: int = 4) -> Dict[str, Tuple[float, float]]:
        """Benchmark lookup operations"""
        keys = self.generate_random_keys(size)
        values = [f"value_{k}" for k in keys]
        
        # Pre-populate data structures
        tree = BPlusTreeMap(capacity=capacity)
        sd = SortedDict()
        for k, v in zip(keys, values):
            tree[k] = v
            sd[k] = v
        
        # Randomize lookup order
        lookup_keys = keys.copy()
        random.shuffle(lookup_keys)
        
        def lookup_btree():
            for k in lookup_keys:
                _ = tree[k]
        
        def lookup_sorted_dict():
            for k in lookup_keys:
                _ = sd[k]
        
        btree_time, btree_std = self.time_operation(lookup_btree, f"btree_lookup_cap{capacity}", size)
        sorted_dict_time, sorted_dict_std = self.time_operation(lookup_sorted_dict, "sorted_dict_lookup", size)
        
        return {
            'btree': (btree_time, btree_std),
            'sorted_dict': (sorted_dict_time, sorted_dict_std)
        }
    
    def benchmark_deletions(self, size: int, capacity: int = 4) -> Dict[str, Tuple[float, float]]:
        """Benchmark deletion operations"""
        keys = self.generate_random_keys(size)
        values = [f"value_{k}" for k in keys]
        
        # Delete 50% of keys in random order
        delete_keys = random.sample(keys, size // 2)
        
        def delete_btree():
            tree = BPlusTreeMap(capacity=capacity)
            for k, v in zip(keys, values):
                tree[k] = v
            for k in delete_keys:
                del tree[k]
            return tree
        
        def delete_sorted_dict():
            sd = SortedDict()
            for k, v in zip(keys, values):
                sd[k] = v
            for k in delete_keys:
                del sd[k]
            return sd
        
        btree_time, btree_std = self.time_operation(delete_btree, f"btree_delete_cap{capacity}", size)
        sorted_dict_time, sorted_dict_std = self.time_operation(delete_sorted_dict, "sorted_dict_delete", size)
        
        return {
            'btree': (btree_time, btree_std),
            'sorted_dict': (sorted_dict_time, sorted_dict_std)
        }
    
    def benchmark_iteration(self, size: int, capacity: int = 4) -> Dict[str, Tuple[float, float]]:
        """Benchmark full iteration operations"""
        keys = self.generate_random_keys(size)
        values = [f"value_{k}" for k in keys]
        
        # Pre-populate data structures
        tree = BPlusTreeMap(capacity=capacity)
        sd = SortedDict()
        for k, v in zip(keys, values):
            tree[k] = v
            sd[k] = v
        
        def iterate_btree():
            result = []
            for k, v in tree.items():
                result.append((k, v))
            return result
        
        def iterate_sorted_dict():
            result = []
            for k, v in sd.items():
                result.append((k, v))
            return result
        
        btree_time, btree_std = self.time_operation(iterate_btree, f"btree_iterate_cap{capacity}", size)
        sorted_dict_time, sorted_dict_std = self.time_operation(iterate_sorted_dict, "sorted_dict_iterate", size)
        
        return {
            'btree': (btree_time, btree_std),
            'sorted_dict': (sorted_dict_time, sorted_dict_std)
        }
    
    def benchmark_range_queries(self, size: int, capacity: int = 4) -> Dict[str, Tuple[float, float]]:
        """Benchmark range query operations (where our B+ tree should excel)"""
        keys = self.generate_random_keys(size)
        values = [f"value_{k}" for k in keys]
        
        # Pre-populate data structures
        tree = BPlusTreeMap(capacity=capacity)
        sd = SortedDict()
        for k, v in zip(keys, values):
            tree[k] = v
            sd[k] = v
        
        sorted_keys = sorted(keys)
        # Query 10% ranges at different positions
        range_size = max(1, size // 10)
        start_positions = [0, size // 4, size // 2, 3 * size // 4]
        
        def range_query_btree():
            results = []
            for start_pos in start_positions:
                if start_pos + range_size < len(sorted_keys):
                    start_key = sorted_keys[start_pos]
                    end_key = sorted_keys[start_pos + range_size]
                    result = list(tree.items(start_key=start_key, end_key=end_key))
                    results.extend(result)
            return results
        
        def range_query_sorted_dict():
            results = []
            for start_pos in start_positions:
                if start_pos + range_size < len(sorted_keys):
                    start_key = sorted_keys[start_pos]
                    end_key = sorted_keys[start_pos + range_size]
                    # SortedDict doesn't have built-in range queries, so we use irange
                    result = list(sd.irange(start_key, end_key, inclusive=(True, False)))
                    results.extend([(k, sd[k]) for k in result])
            return results
        
        btree_time, btree_std = self.time_operation(range_query_btree, f"btree_range_cap{capacity}", size)
        sorted_dict_time, sorted_dict_std = self.time_operation(range_query_sorted_dict, "sorted_dict_range", size)
        
        return {
            'btree': (btree_time, btree_std),
            'sorted_dict': (sorted_dict_time, sorted_dict_std)
        }
    
    def benchmark_mixed_workload(self, size: int, capacity: int = 4) -> Dict[str, Tuple[float, float]]:
        """Benchmark mixed workload (insert, lookup, delete)"""
        keys = self.generate_random_keys(size)
        values = [f"value_{k}" for k in keys]
        
        # Mixed operations: 50% inserts, 30% lookups, 20% deletes
        operations = (['insert'] * (size // 2) + 
                     ['lookup'] * (size * 3 // 10) + 
                     ['delete'] * (size // 5))
        random.shuffle(operations)
        
        def mixed_workload_btree():
            tree = BPlusTreeMap(capacity=capacity)
            inserted_keys = set()
            
            for i, op in enumerate(operations):
                if i >= len(keys):
                    break
                    
                key = keys[i]
                value = values[i]
                
                if op == 'insert':
                    tree[key] = value
                    inserted_keys.add(key)
                elif op == 'lookup' and inserted_keys:
                    lookup_key = random.choice(list(inserted_keys))
                    try:
                        _ = tree[lookup_key]
                    except KeyError:
                        pass
                elif op == 'delete' and inserted_keys:
                    delete_key = random.choice(list(inserted_keys))
                    try:
                        del tree[delete_key]
                        inserted_keys.remove(delete_key)
                    except KeyError:
                        pass
            return tree
        
        def mixed_workload_sorted_dict():
            sd = SortedDict()
            inserted_keys = set()
            
            for i, op in enumerate(operations):
                if i >= len(keys):
                    break
                    
                key = keys[i]
                value = values[i]
                
                if op == 'insert':
                    sd[key] = value
                    inserted_keys.add(key)
                elif op == 'lookup' and inserted_keys:
                    lookup_key = random.choice(list(inserted_keys))
                    try:
                        _ = sd[lookup_key]
                    except KeyError:
                        pass
                elif op == 'delete' and inserted_keys:
                    delete_key = random.choice(list(inserted_keys))
                    try:
                        del sd[delete_key]
                        inserted_keys.remove(delete_key)
                    except KeyError:
                        pass
            return sd
        
        btree_time, btree_std = self.time_operation(mixed_workload_btree, f"btree_mixed_cap{capacity}", size)
        sorted_dict_time, sorted_dict_std = self.time_operation(mixed_workload_sorted_dict, "sorted_dict_mixed", size)
        
        return {
            'btree': (btree_time, btree_std),
            'sorted_dict': (sorted_dict_time, sorted_dict_std)
        }
    
    def print_results(self, operation: str, size: int, results: Dict[str, Tuple[float, float]], capacity: int = 4):
        """Print benchmark results in a formatted way"""
        btree_time, btree_std = results['btree']
        sorted_dict_time, sorted_dict_std = results['sorted_dict']
        
        # Calculate relative performance
        if sorted_dict_time > 0:
            speedup = sorted_dict_time / btree_time
            if speedup > 1:
                relative = f"B+Tree is {speedup:.2f}x faster"
            else:
                relative = f"SortedDict is {1/speedup:.2f}x faster"
        else:
            relative = "Cannot compare (zero time)"
        
        print(f"  {operation:15} | {size:>8,} | "
              f"{btree_time*1000:>8.2f}ms ± {btree_std*1000:>5.2f} | "
              f"{sorted_dict_time*1000:>8.2f}ms ± {sorted_dict_std*1000:>5.2f} | "
              f"{relative}")
    
    def run_benchmark_suite(self, sizes: List[int], operations: List[str], capacities: List[int] = [4]):
        """Run the complete benchmark suite"""
        
        print("🚀 B+ Tree vs SortedDict Performance Benchmark")
        print("=" * 80)
        print(f"Configuration: {self.measurement_iterations} measurements, {self.warmup_iterations} warmup iterations")
        print(f"Random seed: {self.seed}")
        print()
        
        operation_map = {
            'insert': self.benchmark_insertions,
            'lookup': self.benchmark_lookups, 
            'delete': self.benchmark_deletions,
            'iterate': self.benchmark_iteration,
            'range': self.benchmark_range_queries,
            'mixed': self.benchmark_mixed_workload
        }
        
        for capacity in capacities:
            if len(capacities) > 1:
                print(f"\n📊 Results for B+ Tree capacity = {capacity}")
                print("=" * 80)
            
            print(f"{'Operation':15} | {'Size':>8} | {'B+Tree Time':>15} | {'SortedDict Time':>17} | {'Relative Performance'}")
            print("-" * 80)
            
            for operation in operations:
                if operation not in operation_map:
                    print(f"⚠️  Unknown operation: {operation}")
                    continue
                
                benchmark_func = operation_map[operation]
                
                for size in sizes:
                    try:
                        print(f"  Running {operation} benchmark for {size:,} keys... ", end="", flush=True)
                        
                        if operation in ['range']:
                            # Range queries only make sense for our B+ tree if it supports them
                            if hasattr(BPlusTreeMap(), 'items') and len(BPlusTreeMap().items.__code__.co_varnames) > 1:
                                results = benchmark_func(size, capacity)
                            else:
                                print("skipped (range queries not implemented)")
                                continue
                        else:
                            results = benchmark_func(size, capacity)
                        
                        print("✅")
                        self.print_results(operation, size, results, capacity)
                        
                    except Exception as e:
                        print(f"❌ Error: {e}")
                        continue
            
            print()
        
        # Summary statistics
        self.print_summary()
    
    def print_summary(self):
        """Print summary statistics across all benchmarks"""
        print("📈 Summary")
        print("=" * 40)
        
        btree_wins = 0
        sorted_dict_wins = 0
        total_comparisons = 0
        capacity_performance = {}  # capacity -> [relative_times]
        
        for operation, size_results in self.results.items():
            for size, times in size_results.items():
                if 'btree' in operation:
                    # Extract capacity from operation name
                    if '_cap' in operation:
                        capacity = int(operation.split('_cap')[1])
                    else:
                        capacity = 4  # default
                    
                    # Find corresponding sorted_dict operation
                    base_op = operation.replace('btree_', '').split('_cap')[0]
                    sorted_dict_op = f"sorted_dict_{base_op}"
                    
                    if sorted_dict_op in self.results and size in self.results[sorted_dict_op]:
                        btree_time = statistics.mean(times)
                        sorted_dict_time = statistics.mean(self.results[sorted_dict_op][size])
                        
                        total_comparisons += 1
                        if btree_time < sorted_dict_time:
                            btree_wins += 1
                        else:
                            sorted_dict_wins += 1
                        
                        # Track capacity performance
                        if capacity not in capacity_performance:
                            capacity_performance[capacity] = []
                        capacity_performance[capacity].append(sorted_dict_time / btree_time)
        
        if total_comparisons > 0:
            print(f"B+ Tree wins: {btree_wins}/{total_comparisons} ({btree_wins/total_comparisons*100:.1f}%)")
            print(f"SortedDict wins: {sorted_dict_wins}/{total_comparisons} ({sorted_dict_wins/total_comparisons*100:.1f}%)")
        
        # Capacity analysis
        if capacity_performance:
            print(f"\n🎛️  Capacity Performance Analysis:")
            print(f"{'Capacity':>8} | {'Avg Relative Speed':>18} | {'Best Performance'}")
            print("-" * 50)
            
            best_capacity = None
            best_performance = 0
            
            for capacity in sorted(capacity_performance.keys()):
                relative_speeds = capacity_performance[capacity]
                avg_speed = statistics.mean(relative_speeds)
                
                if avg_speed > best_performance:
                    best_performance = avg_speed
                    best_capacity = capacity
                
                status = "✅ Best" if capacity == best_capacity else ""
                print(f"{capacity:>8} | {avg_speed:>15.2f}x | {status}")
            
            print(f"\n🏆 Optimal capacity: {best_capacity} (avg {best_performance:.2f}x relative to SortedDict)")
        
        print("\n💡 Notes:")
        print("- B+ Trees excel at range queries and sequential access")
        print("- SortedDict is highly optimized and uses advanced data structures")
        print("- Performance can vary significantly based on access patterns")
        print("- Higher capacity = fewer tree levels but larger nodes")
        print("- Lower capacity = more tree levels but better cache locality")
        print("- Optimal capacity depends on workload and dataset size")


def main():
    parser = argparse.ArgumentParser(description="Benchmark B+ Tree vs SortedDict performance")
    parser.add_argument('--quick', action='store_true', 
                       help='Run quick benchmark with smaller datasets')
    parser.add_argument('--capacity-tuning', action='store_true',
                       help='Focus on capacity tuning with comprehensive capacity range')
    parser.add_argument('--sizes', type=str, default='1000,5000,10000,50000',
                       help='Comma-separated list of dataset sizes to test')
    parser.add_argument('--operations', type=str, default='insert,lookup,delete,iterate,range,mixed',
                       help='Comma-separated list of operations to benchmark')
    parser.add_argument('--capacity', type=str, default='3,4,5,8,16',
                       help='Comma-separated list of B+ tree capacities to test')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducible results')
    parser.add_argument('--iterations', type=int, default=5,
                       help='Number of measurement iterations per benchmark')
    
    args = parser.parse_args()
    
    # Parse sizes
    if args.quick:
        sizes = [100, 1000, 5000]
    elif args.capacity_tuning:
        sizes = [1000, 10000]  # Focus on medium sizes for capacity tuning
    else:
        sizes = [int(s.strip()) for s in args.sizes.split(',')]
    
    # Parse operations
    if args.capacity_tuning:
        operations = ['insert', 'lookup', 'mixed']  # Focus on key operations for tuning
    else:
        operations = [op.strip() for op in args.operations.split(',')]
    
    # Parse capacities
    if args.capacity_tuning:
        capacities = [3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32]  # Comprehensive range
    else:
        capacities = [int(c.strip()) for c in args.capacity.split(',')]
    
    # Create and run benchmark
    runner = BenchmarkRunner(seed=args.seed, measurement_iterations=args.iterations)
    runner.run_benchmark_suite(sizes, operations, capacities)


if __name__ == "__main__":
    main()