"""
Continuous performance tracking for B+ Tree implementation.

This script tracks performance over time and can be integrated with CI/CD
to detect performance regressions.
"""

import json
import time
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import subprocess
import platform

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bplus_tree import BPlusTreeMap
from comprehensive_benchmark import ComprehensiveBenchmark


class PerformanceTracker:
    """Track B+ Tree performance metrics over time."""
    
    def __init__(self, history_file: str = 'performance_history.json'):
        self.history_file = history_file
        self.history = self._load_history()
        
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load performance history from file."""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_history(self):
        """Save performance history to file."""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def _get_git_info(self) -> Dict[str, str]:
        """Get current git commit and branch info."""
        try:
            commit = subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'], 
                text=True
            ).strip()
            
            branch = subprocess.check_output(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                text=True
            ).strip()
            
            message = subprocess.check_output(
                ['git', 'log', '-1', '--pretty=%B'], 
                text=True
            ).strip()
            
            return {
                'commit': commit[:8],
                'branch': branch,
                'message': message.split('\n')[0]  # First line only
            }
        except:
            return {
                'commit': 'unknown',
                'branch': 'unknown',
                'message': 'unknown'
            }
    
    def run_benchmarks(self, sizes: List[int] = None) -> Dict[str, Any]:
        """Run standard benchmark suite."""
        if sizes is None:
            sizes = [1000, 10000, 100000]
        
        benchmark = ComprehensiveBenchmark(sizes=sizes, capacities=[32])
        
        results = {}
        
        # Run specific benchmarks
        for size in sizes:
            print(f"Benchmarking size {size:,}...")
            
            # Insertions
            insert_results = benchmark.benchmark_insertions(size, capacity=32)
            results.update(insert_results)
            
            # Lookups
            lookup_results = benchmark.benchmark_lookups(size, capacity=32)
            results.update(lookup_results)
            
            # Range queries
            range_results = benchmark.benchmark_range_queries(size, capacity=32)
            results.update(range_results)
        
        return results
    
    def track_performance(self):
        """Run benchmarks and track results."""
        print("Running performance tracking...")
        print("=" * 60)
        
        # Get system info
        git_info = self._get_git_info()
        
        # Run benchmarks
        start_time = time.time()
        results = self.run_benchmarks()
        end_time = time.time()
        
        # Create tracking entry
        entry = {
            'timestamp': datetime.now().isoformat(),
            'git': git_info,
            'system': {
                'platform': platform.platform(),
                'python': platform.python_version(),
                'processor': platform.processor()
            },
            'duration': end_time - start_time,
            'metrics': {}
        }
        
        # Extract key metrics
        for key, result in results.items():
            stats = result.get_stats()
            entry['metrics'][key] = {
                'mean_time': stats['mean_time'],
                'ops_per_second': stats['ops_per_second'],
                'iterations': stats['iterations']
            }
        
        # Add to history
        self.history.append(entry)
        self._save_history()
        
        # Check for regressions
        self._check_regressions(entry)
        
        print(f"\nPerformance tracking complete. Results saved to {self.history_file}")
    
    def _check_regressions(self, current_entry: Dict[str, Any]):
        """Check for performance regressions compared to previous runs."""
        if len(self.history) < 2:
            return
        
        # Get previous entry on same branch
        previous_entry = None
        for entry in reversed(self.history[:-1]):
            if entry['git']['branch'] == current_entry['git']['branch']:
                previous_entry = entry
                break
        
        if not previous_entry:
            return
        
        print("\nRegression Analysis:")
        print("-" * 60)
        
        regressions = []
        improvements = []
        
        # Compare metrics
        for metric_name, current_metric in current_entry['metrics'].items():
            if metric_name in previous_entry['metrics']:
                prev_metric = previous_entry['metrics'][metric_name]
                
                # Calculate performance change
                if prev_metric['mean_time'] > 0:
                    change = (current_metric['mean_time'] - prev_metric['mean_time']) / prev_metric['mean_time'] * 100
                    
                    if change > 10:  # More than 10% slower
                        regressions.append({
                            'metric': metric_name,
                            'change': change,
                            'prev_time': prev_metric['mean_time'],
                            'curr_time': current_metric['mean_time']
                        })
                    elif change < -10:  # More than 10% faster
                        improvements.append({
                            'metric': metric_name,
                            'change': abs(change),
                            'prev_time': prev_metric['mean_time'],
                            'curr_time': current_metric['mean_time']
                        })
        
        # Report findings
        if regressions:
            print("\n⚠️  PERFORMANCE REGRESSIONS DETECTED:")
            for reg in regressions:
                print(f"  - {reg['metric']}: {reg['change']:.1f}% slower")
                print(f"    Previous: {reg['prev_time']:.6f}s, Current: {reg['curr_time']:.6f}s")
        
        if improvements:
            print("\n✅ PERFORMANCE IMPROVEMENTS:")
            for imp in improvements:
                print(f"  - {imp['metric']}: {imp['change']:.1f}% faster")
                print(f"    Previous: {imp['prev_time']:.6f}s, Current: {imp['curr_time']:.6f}s")
        
        if not regressions and not improvements:
            print("No significant performance changes detected (±10% threshold)")
    
    def generate_trend_report(self, metric_filter: Optional[str] = None):
        """Generate performance trend report."""
        if not self.history:
            print("No performance history available")
            return
        
        print("\nPerformance Trends")
        print("=" * 60)
        
        # Group by metric
        metrics = {}
        for entry in self.history:
            for metric_name, metric_data in entry['metrics'].items():
                if metric_filter and metric_filter not in metric_name:
                    continue
                    
                if metric_name not in metrics:
                    metrics[metric_name] = []
                
                metrics[metric_name].append({
                    'timestamp': entry['timestamp'],
                    'commit': entry['git']['commit'],
                    'mean_time': metric_data['mean_time'],
                    'ops_per_second': metric_data['ops_per_second']
                })
        
        # Print trends
        for metric_name, data_points in sorted(metrics.items()):
            print(f"\n{metric_name}:")
            print("-" * 60)
            
            # Show last 5 data points
            for point in data_points[-5:]:
                timestamp = datetime.fromisoformat(point['timestamp'])
                print(f"  {timestamp.strftime('%Y-%m-%d %H:%M')} "
                      f"(commit {point['commit']}): "
                      f"{point['mean_time']:.6f}s "
                      f"({point['ops_per_second']:.0f} ops/s)")
            
            # Calculate trend
            if len(data_points) >= 2:
                first_time = data_points[0]['mean_time']
                last_time = data_points[-1]['mean_time']
                change = (last_time - first_time) / first_time * 100
                
                if abs(change) > 1:
                    trend = "🔴 slower" if change > 0 else "🟢 faster"
                    print(f"\n  Overall trend: {abs(change):.1f}% {trend}")
    
    def export_for_ci(self, output_file: str = 'ci_performance.json'):
        """Export latest performance data for CI/CD integration."""
        if not self.history:
            print("No performance history available")
            return
        
        latest = self.history[-1]
        
        # Create CI-friendly format
        ci_data = {
            'timestamp': latest['timestamp'],
            'commit': latest['git']['commit'],
            'branch': latest['git']['branch'],
            'metrics': {}
        }
        
        # Extract key metrics for CI
        for metric_name, metric_data in latest['metrics'].items():
            # Simplify metric names
            simple_name = metric_name.replace('bplus_', '').replace('_', '.')
            ci_data['metrics'][simple_name] = {
                'value': metric_data['mean_time'] * 1000,  # Convert to ms
                'unit': 'ms'
            }
        
        with open(output_file, 'w') as f:
            json.dump(ci_data, f, indent=2)
        
        print(f"\nCI performance data exported to {output_file}")


def main():
    """Run performance tracking."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Track B+ Tree performance over time')
    parser.add_argument('--track', action='store_true', help='Run benchmarks and track results')
    parser.add_argument('--trends', action='store_true', help='Show performance trends')
    parser.add_argument('--export-ci', action='store_true', help='Export data for CI/CD')
    parser.add_argument('--filter', type=str, help='Filter metrics by name')
    parser.add_argument('--sizes', type=int, nargs='+', help='Test sizes (default: 1000 10000 100000)')
    
    args = parser.parse_args()
    
    tracker = PerformanceTracker()
    
    if args.track:
        sizes = args.sizes if args.sizes else None
        tracker.track_performance()
    
    if args.trends:
        tracker.generate_trend_report(metric_filter=args.filter)
    
    if args.export_ci:
        tracker.export_for_ci()
    
    if not any([args.track, args.trends, args.export_ci]):
        parser.print_help()


if __name__ == '__main__':
    main()