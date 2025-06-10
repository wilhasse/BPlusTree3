"""
Comprehensive performance benchmarking suite for B+ Tree.

This module provides detailed performance analysis including:
- Operation benchmarks (insert, lookup, delete, range)
- Comparison with dict and sortedcontainers.SortedDict
- Memory usage profiling
- Cache performance analysis
- Scalability testing
"""

import time
import gc
import json
import statistics
import tracemalloc
from typing import Dict, List, Tuple, Any, Optional
import random
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bplus_tree import BPlusTreeMap

try:
    from sortedcontainers import SortedDict
    HAS_SORTEDDICT = True
except ImportError:
    HAS_SORTEDDICT = False
    print("Warning: sortedcontainers not installed. Install with: pip install sortedcontainers")

class BenchmarkResult:
    """Container for benchmark results."""
    
    def __init__(self, name: str):
        self.name = name
        self.times: List[float] = []
        self.memory_start: Optional[int] = None
        self.memory_peak: Optional[int] = None
        self.iterations: int = 0
        
    def add_time(self, elapsed: float):
        """Add a timing measurement."""
        self.times.append(elapsed)
        self.iterations += 1
        
    def set_memory(self, start: int, peak: int):
        """Set memory usage statistics."""
        self.memory_start = start
        self.memory_peak = peak
        
    def get_stats(self) -> Dict[str, Any]:
        """Get statistical summary."""
        if not self.times:
            return {}
            
        return {
            'name': self.name,
            'iterations': self.iterations,
            'total_time': sum(self.times),
            'mean_time': statistics.mean(self.times),
            'median_time': statistics.median(self.times),
            'stdev_time': statistics.stdev(self.times) if len(self.times) > 1 else 0,
            'min_time': min(self.times),
            'max_time': max(self.times),
            'memory_used_mb': (self.memory_peak - self.memory_start) / 1024 / 1024 if self.memory_peak else None,
            'ops_per_second': self.iterations / sum(self.times) if self.times else 0
        }

class ComprehensiveBenchmark:
    """Comprehensive benchmark suite for B+ Tree performance analysis."""
    
    def __init__(self, sizes: List[int] = None, capacities: List[int] = None):
        self.sizes = sizes or [100, 1000, 10000, 100000]
        self.capacities = capacities or [8, 16, 32, 64, 128]
        self.results: Dict[str, BenchmarkResult] = {}
        
    def _prepare_data(self, size: int, pattern: str = 'sequential') -> List[Tuple[int, str]]:
        """Generate test data with different patterns."""
        if pattern == 'sequential':
            return [(i, f'value_{i}') for i in range(size)]
        elif pattern == 'random':
            keys = list(range(size))
            random.shuffle(keys)
            return [(k, f'value_{k}') for k in keys]
        elif pattern == 'reverse':
            return [(i, f'value_{i}') for i in range(size-1, -1, -1)]
        else:
            raise ValueError(f"Unknown pattern: {pattern}")
    
    def _measure_time(self, func, *args, **kwargs) -> float:
        """Measure execution time of a function."""
        gc.disable()
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        gc.enable()
        return end - start
    
    def _measure_memory(self, func, *args, **kwargs) -> Tuple[Any, int, int]:
        """Measure memory usage of a function."""
        tracemalloc.start()
        gc.collect()
        
        start_memory = tracemalloc.get_traced_memory()[0]
        result = func(*args, **kwargs)
        peak_memory = tracemalloc.get_traced_memory()[1]
        
        tracemalloc.stop()
        return result, start_memory, peak_memory
    
    def benchmark_insertions(self, size: int, capacity: int = 32) -> Dict[str, BenchmarkResult]:
        """Benchmark insertion performance."""
        results = {}
        
        # Test different insertion patterns
        for pattern in ['sequential', 'random', 'reverse']:
            data = self._prepare_data(size, pattern)
            
            # B+ Tree
            key = f'bplus_insert_{pattern}_{size}'
            result = BenchmarkResult(key)
            
            def insert_bplus():
                tree = BPlusTreeMap(capacity=capacity)
                for k, v in data:
                    tree[k] = v
                return tree
            
            # Warm up
            insert_bplus()
            
            # Time measurements
            for _ in range(3):
                elapsed = self._measure_time(insert_bplus)
                result.add_time(elapsed)
            
            # Memory measurement
            tree, start_mem, peak_mem = self._measure_memory(insert_bplus)
            result.set_memory(start_mem, peak_mem)
            
            results[key] = result
            
            # Compare with dict
            key = f'dict_insert_{pattern}_{size}'
            result = BenchmarkResult(key)
            
            def insert_dict():
                d = {}
                for k, v in data:
                    d[k] = v
                return d
            
            for _ in range(3):
                elapsed = self._measure_time(insert_dict)
                result.add_time(elapsed)
                
            results[key] = result
            
            # Compare with SortedDict if available
            if HAS_SORTEDDICT:
                key = f'sorteddict_insert_{pattern}_{size}'
                result = BenchmarkResult(key)
                
                def insert_sorted():
                    sd = SortedDict()
                    for k, v in data:
                        sd[k] = v
                    return sd
                
                for _ in range(3):
                    elapsed = self._measure_time(insert_sorted)
                    result.add_time(elapsed)
                    
                results[key] = result
        
        return results
    
    def benchmark_lookups(self, size: int, capacity: int = 32, lookup_count: int = None) -> Dict[str, BenchmarkResult]:
        """Benchmark lookup performance."""
        if lookup_count is None:
            lookup_count = min(size, 10000)
            
        results = {}
        data = self._prepare_data(size, 'sequential')
        
        # Prepare lookup keys (mix of existing and non-existing)
        lookup_keys = []
        for _ in range(lookup_count // 2):
            lookup_keys.append(random.randint(0, size - 1))  # Existing
        for _ in range(lookup_count // 2):
            lookup_keys.append(random.randint(size, size * 2))  # Non-existing
        
        # B+ Tree
        tree = BPlusTreeMap(capacity=capacity)
        for k, v in data:
            tree[k] = v
            
        key = f'bplus_lookup_{size}'
        result = BenchmarkResult(key)
        
        def lookup_bplus():
            hits = 0
            for k in lookup_keys:
                if k in tree:
                    _ = tree[k]
                    hits += 1
            return hits
        
        # Warm up
        lookup_bplus()
        
        for _ in range(3):
            elapsed = self._measure_time(lookup_bplus)
            result.add_time(elapsed)
            result.iterations = lookup_count
            
        results[key] = result
        
        # Compare with dict
        d = {k: v for k, v in data}
        
        key = f'dict_lookup_{size}'
        result = BenchmarkResult(key)
        
        def lookup_dict():
            hits = 0
            for k in lookup_keys:
                if k in d:
                    _ = d[k]
                    hits += 1
            return hits
        
        for _ in range(3):
            elapsed = self._measure_time(lookup_dict)
            result.add_time(elapsed)
            result.iterations = lookup_count
            
        results[key] = result
        
        # Compare with SortedDict
        if HAS_SORTEDDICT:
            sd = SortedDict(data)
            
            key = f'sorteddict_lookup_{size}'
            result = BenchmarkResult(key)
            
            def lookup_sorted():
                hits = 0
                for k in lookup_keys:
                    if k in sd:
                        _ = sd[k]
                        hits += 1
                return hits
            
            for _ in range(3):
                elapsed = self._measure_time(lookup_sorted)
                result.add_time(elapsed)
                result.iterations = lookup_count
                
            results[key] = result
        
        return results
    
    def benchmark_range_queries(self, size: int, capacity: int = 32) -> Dict[str, BenchmarkResult]:
        """Benchmark range query performance."""
        results = {}
        data = self._prepare_data(size, 'sequential')
        
        # Test different range sizes
        range_sizes = [10, 100, 1000, size // 10]
        
        for range_size in range_sizes:
            if range_size > size:
                continue
                
            # B+ Tree
            tree = BPlusTreeMap(capacity=capacity)
            for k, v in data:
                tree[k] = v
                
            key = f'bplus_range_{size}_size{range_size}'
            result = BenchmarkResult(key)
            
            # Generate random ranges
            ranges = []
            for _ in range(10):
                start = random.randint(0, size - range_size)
                end = start + range_size
                ranges.append((start, end))
            
            def range_bplus():
                total = 0
                for start, end in ranges:
                    for k, v in tree.range(start, end):
                        total += 1
                return total
            
            # Warm up
            range_bplus()
            
            for _ in range(3):
                elapsed = self._measure_time(range_bplus)
                result.add_time(elapsed)
                
            results[key] = result
            
            # Compare with SortedDict
            if HAS_SORTEDDICT:
                sd = SortedDict(data)
                
                key = f'sorteddict_range_{size}_size{range_size}'
                result = BenchmarkResult(key)
                
                def range_sorted():
                    total = 0
                    for start, end in ranges:
                        for k in sd.irange(start, end, inclusive=(True, False)):
                            total += 1
                    return total
                
                for _ in range(3):
                    elapsed = self._measure_time(range_sorted)
                    result.add_time(elapsed)
                    
                results[key] = result
        
        return results
    
    def benchmark_deletions(self, size: int, capacity: int = 32) -> Dict[str, BenchmarkResult]:
        """Benchmark deletion performance."""
        results = {}
        delete_count = min(size // 2, 5000)
        
        # Random deletion pattern
        delete_keys = random.sample(range(size), delete_count)
        
        # B+ Tree
        key = f'bplus_delete_{size}'
        result = BenchmarkResult(key)
        
        def delete_bplus():
            tree = BPlusTreeMap(capacity=capacity)
            for i in range(size):
                tree[i] = f'value_{i}'
            
            for k in delete_keys:
                del tree[k]
            return tree
        
        # Warm up
        delete_bplus()
        
        for _ in range(3):
            elapsed = self._measure_time(delete_bplus)
            result.add_time(elapsed)
            result.iterations = delete_count
            
        results[key] = result
        
        # Compare with dict
        key = f'dict_delete_{size}'
        result = BenchmarkResult(key)
        
        def delete_dict():
            d = {i: f'value_{i}' for i in range(size)}
            for k in delete_keys:
                del d[k]
            return d
        
        for _ in range(3):
            elapsed = self._measure_time(delete_dict)
            result.add_time(elapsed)
            result.iterations = delete_count
            
        results[key] = result
        
        # Compare with SortedDict
        if HAS_SORTEDDICT:
            key = f'sorteddict_delete_{size}'
            result = BenchmarkResult(key)
            
            def delete_sorted():
                sd = SortedDict({i: f'value_{i}' for i in range(size)})
                for k in delete_keys:
                    del sd[k]
                return sd
            
            for _ in range(3):
                elapsed = self._measure_time(delete_sorted)
                result.add_time(elapsed)
                result.iterations = delete_count
                
            results[key] = result
        
        return results
    
    def benchmark_mixed_operations(self, size: int, capacity: int = 32) -> Dict[str, BenchmarkResult]:
        """Benchmark mixed operations (realistic workload)."""
        results = {}
        
        # 60% lookups, 20% inserts, 10% deletes, 10% range queries
        op_count = 10000
        operations = []
        
        for _ in range(int(op_count * 0.6)):
            operations.append(('lookup', random.randint(0, size * 2)))
        
        for _ in range(int(op_count * 0.2)):
            operations.append(('insert', random.randint(size, size * 2), f'new_value'))
        
        for _ in range(int(op_count * 0.1)):
            operations.append(('delete', random.randint(0, size)))
        
        for _ in range(int(op_count * 0.1)):
            start = random.randint(0, size)
            operations.append(('range', start, start + 100))
        
        random.shuffle(operations)
        
        # B+ Tree
        key = f'bplus_mixed_{size}'
        result = BenchmarkResult(key)
        
        def mixed_bplus():
            tree = BPlusTreeMap(capacity=capacity)
            for i in range(size):
                tree[i] = f'value_{i}'
                
            for op in operations:
                if op[0] == 'lookup':
                    _ = tree.get(op[1])
                elif op[0] == 'insert':
                    tree[op[1]] = op[2]
                elif op[0] == 'delete':
                    try:
                        del tree[op[1]]
                    except KeyError:
                        pass
                elif op[0] == 'range':
                    list(tree.range(op[1], op[2]))
                    
            return tree
        
        # Warm up
        mixed_bplus()
        
        for _ in range(3):
            elapsed = self._measure_time(mixed_bplus)
            result.add_time(elapsed)
            result.iterations = op_count
            
        results[key] = result
        
        return results
    
    def benchmark_capacity_impact(self, size: int = 10000) -> Dict[str, BenchmarkResult]:
        """Benchmark impact of different node capacities."""
        results = {}
        
        for capacity in self.capacities:
            # Insertion benchmark
            data = self._prepare_data(size, 'random')
            
            key = f'bplus_capacity_{capacity}_insert'
            result = BenchmarkResult(key)
            
            def insert_with_capacity():
                tree = BPlusTreeMap(capacity=capacity)
                for k, v in data:
                    tree[k] = v
                return tree
            
            for _ in range(3):
                elapsed = self._measure_time(insert_with_capacity)
                result.add_time(elapsed)
                result.iterations = size
                
            results[key] = result
            
            # Lookup benchmark
            tree = insert_with_capacity()
            lookup_keys = random.sample(range(size), min(1000, size))
            
            key = f'bplus_capacity_{capacity}_lookup'
            result = BenchmarkResult(key)
            
            def lookup_with_capacity():
                for k in lookup_keys:
                    _ = tree[k]
            
            for _ in range(3):
                elapsed = self._measure_time(lookup_with_capacity)
                result.add_time(elapsed)
                result.iterations = len(lookup_keys)
                
            results[key] = result
        
        return results
    
    def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run all benchmarks and return results."""
        all_results = {}
        
        print("Running comprehensive benchmarks...")
        print("=" * 60)
        
        for size in self.sizes:
            print(f"\nBenchmarking with {size:,} items:")
            
            # Run different benchmark types
            print("  - Insertions...")
            results = self.benchmark_insertions(size)
            all_results.update(results)
            
            print("  - Lookups...")
            results = self.benchmark_lookups(size)
            all_results.update(results)
            
            print("  - Range queries...")
            results = self.benchmark_range_queries(size)
            all_results.update(results)
            
            print("  - Deletions...")
            results = self.benchmark_deletions(size)
            all_results.update(results)
            
            print("  - Mixed operations...")
            results = self.benchmark_mixed_operations(size)
            all_results.update(results)
        
        # Capacity impact (only once)
        print("\nBenchmarking capacity impact...")
        results = self.benchmark_capacity_impact()
        all_results.update(results)
        
        return all_results
    
    def generate_report(self, results: Dict[str, BenchmarkResult], output_file: str = None):
        """Generate a comprehensive benchmark report."""
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'python_version': sys.version,
            'has_sorteddict': HAS_SORTEDDICT,
            'test_sizes': self.sizes,
            'test_capacities': self.capacities,
            'results': {}
        }
        
        # Convert results to serializable format
        for key, result in results.items():
            report['results'][key] = result.get_stats()
        
        # Generate summary comparisons
        summary = self._generate_summary(results)
        report['summary'] = summary
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\nReport saved to: {output_file}")
        
        # Print summary to console
        self._print_summary(summary)
        
        return report
    
    def _generate_summary(self, results: Dict[str, BenchmarkResult]) -> Dict[str, Any]:
        """Generate performance summary comparing implementations."""
        summary = {
            'performance_ratios': {},
            'memory_usage': {},
            'recommendations': []
        }
        
        # Calculate performance ratios for each size
        for size in self.sizes:
            size_ratios = {}
            
            # Compare insertions
            bplus_key = f'bplus_insert_random_{size}'
            dict_key = f'dict_insert_random_{size}'
            sorted_key = f'sorteddict_insert_random_{size}'
            
            if bplus_key in results and dict_key in results:
                bplus_time = results[bplus_key].get_stats()['mean_time']
                dict_time = results[dict_key].get_stats()['mean_time']
                size_ratios['insert_vs_dict'] = bplus_time / dict_time
            
            if HAS_SORTEDDICT and bplus_key in results and sorted_key in results:
                bplus_time = results[bplus_key].get_stats()['mean_time']
                sorted_time = results[sorted_key].get_stats()['mean_time']
                size_ratios['insert_vs_sorteddict'] = bplus_time / sorted_time
            
            # Compare lookups
            bplus_key = f'bplus_lookup_{size}'
            dict_key = f'dict_lookup_{size}'
            sorted_key = f'sorteddict_lookup_{size}'
            
            if bplus_key in results and dict_key in results:
                bplus_time = results[bplus_key].get_stats()['mean_time']
                dict_time = results[dict_key].get_stats()['mean_time']
                size_ratios['lookup_vs_dict'] = bplus_time / dict_time
            
            if HAS_SORTEDDICT and bplus_key in results and sorted_key in results:
                bplus_time = results[bplus_key].get_stats()['mean_time']
                sorted_time = results[sorted_key].get_stats()['mean_time']
                size_ratios['lookup_vs_sorteddict'] = bplus_time / sorted_time
            
            summary['performance_ratios'][str(size)] = size_ratios
        
        # Memory usage comparison
        for size in self.sizes:
            bplus_key = f'bplus_insert_sequential_{size}'
            if bplus_key in results:
                stats = results[bplus_key].get_stats()
                if stats.get('memory_used_mb'):
                    summary['memory_usage'][str(size)] = {
                        'bplus_mb': stats['memory_used_mb'],
                        'items_per_mb': size / stats['memory_used_mb']
                    }
        
        # Generate recommendations
        avg_lookup_ratio = statistics.mean([
            ratios.get('lookup_vs_dict', 1.0)
            for ratios in summary['performance_ratios'].values()
        ])
        
        if avg_lookup_ratio > 10:
            summary['recommendations'].append(
                "Consider using C extension for better lookup performance"
            )
        
        if avg_lookup_ratio > 5:
            summary['recommendations'].append(
                "Increase node capacity for better cache utilization"
            )
        
        # Check if SortedDict is significantly faster
        if HAS_SORTEDDICT:
            avg_sorted_ratio = statistics.mean([
                ratios.get('lookup_vs_sorteddict', 1.0)
                for ratios in summary['performance_ratios'].values()
            ])
            
            if avg_sorted_ratio > 20:
                summary['recommendations'].append(
                    "Current implementation needs optimization to compete with SortedDict"
                )
        
        return summary
    
    def _print_summary(self, summary: Dict[str, Any]):
        """Print a human-readable summary."""
        print("\n" + "=" * 60)
        print("PERFORMANCE SUMMARY")
        print("=" * 60)
        
        print("\nPerformance Ratios (B+ Tree time / comparison time):")
        print("Lower is better, <1 means B+ Tree is faster")
        print("-" * 60)
        
        for size, ratios in summary['performance_ratios'].items():
            print(f"\nSize: {int(size):,} items")
            for op, ratio in ratios.items():
                print(f"  {op:.<30} {ratio:.2f}x")
        
        if summary['memory_usage']:
            print("\nMemory Usage:")
            print("-" * 60)
            for size, mem_info in summary['memory_usage'].items():
                print(f"Size {int(size):,}: {mem_info['bplus_mb']:.2f} MB "
                      f"({mem_info['items_per_mb']:.0f} items/MB)")
        
        if summary['recommendations']:
            print("\nRecommendations:")
            print("-" * 60)
            for rec in summary['recommendations']:
                print(f"• {rec}")
        
        print("\n" + "=" * 60)


def main():
    """Run comprehensive benchmarks with default settings."""
    # Configure benchmark parameters
    sizes = [100, 1000, 10000, 100000]
    capacities = [8, 16, 32, 64, 128]
    
    # Create benchmark instance
    benchmark = ComprehensiveBenchmark(sizes=sizes, capacities=capacities)
    
    # Run all benchmarks
    results = benchmark.run_all_benchmarks()
    
    # Generate report
    output_file = 'benchmark_results.json'
    benchmark.generate_report(results, output_file)
    
    print(f"\nBenchmark complete!")
    print(f"Detailed results saved to: {output_file}")


if __name__ == '__main__':
    main()