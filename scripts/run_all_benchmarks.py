#!/usr/bin/env python3
"""
Automated benchmark runner for B+ Tree implementations.
Runs benchmarks across Rust, Go, and Zig, collects results, and generates a comprehensive report.
"""

import subprocess
import json
import re
import sys
import os
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import argparse

class BenchmarkRunner:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = {
            "rust": {},
            "go": {},
            "zig": {},
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "system_info": self.get_system_info()
            }
        }
    
    def get_system_info(self) -> Dict[str, str]:
        """Collect system information for the report."""
        info = {
            'os': 'Unknown',
            'cpu': 'Unknown', 
            'memory': 'Unknown'
        }
        
        # OS info
        try:
            result = subprocess.run(['uname', '-a'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                info['os'] = result.stdout.strip()
        except:
            pass
        
        # CPU info
        try:
            result = subprocess.run(['lscpu'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Model name:' in line:
                        info['cpu'] = line.split(':', 1)[1].strip()
                        break
        except:
            pass
        
        # Memory info
        try:
            result = subprocess.run(['free', '-h'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                if len(lines) > 1:
                    mem_line = lines[1].split()
                    if len(mem_line) > 1:
                        info['memory'] = mem_line[1]
        except:
            pass
        
        return info
    
    def log(self, message: str):
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def run_rust_benchmarks(self) -> bool:
        """Run Rust benchmarks using cargo bench."""
        print("\n=== Running Rust Benchmarks ===")
        self.log("Checking for Rust installation...")
        
        # Check if cargo is available
        try:
            subprocess.run(['cargo', '--version'], check=True, capture_output=True)
        except:
            print("Error: Rust/Cargo not found. Please install Rust.")
            return False
        
        # Run comparison benchmarks
        self.log("Running Rust comparison benchmarks...")
        try:
            os.chdir('rust')
            result = subprocess.run(
                ['cargo', 'bench', '--bench', 'comparison'],
                capture_output=True,
                text=True,
                timeout=180  # 3 minute timeout
            )
            
            if result.returncode != 0:
                print(f"Error running Rust benchmarks: {result.stderr}")
                return False
            
            # Parse Rust benchmark output
            self.parse_rust_output(result.stdout + result.stderr)
            os.chdir('..')
            return True
            
        except Exception as e:
            print(f"Error running Rust benchmarks: {e}")
            os.chdir('..')
            return False
    
    def parse_rust_output(self, output: str):
        """Parse Rust criterion benchmark output."""
        self.log("Parsing Rust benchmark results...")
        
        # Pattern for criterion output: test_name ... bench: X ns/iter (+/- Y)
        # Or: test_name  time: [X µs Y µs Z µs]
        patterns = [
            # Pattern for time in microseconds
            r'(\w+)/(BTreeMap|BPlusTree)/(\d+)\s+time:\s+\[([0-9.]+)\s*(µs|us|ns)',
            # Pattern for bench results
            r'(\w+)/(BTreeMap|BPlusTree)/(\d+)\s+.*?bench:\s+([0-9,]+)\s*ns/iter',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, output):
                operation = match.group(1).lower()
                impl_type = match.group(2).lower()
                size = int(match.group(3))
                
                if 'µs' in match.group(0) or 'us' in match.group(0):
                    time_us = float(match.group(4))
                else:
                    # Convert ns to us
                    time_str = match.group(4).replace(',', '')
                    time_us = float(time_str) / 1000
                
                # Initialize nested structure
                if operation not in self.results["rust"]:
                    self.results["rust"][operation] = {}
                if size not in self.results["rust"][operation]:
                    self.results["rust"][operation][size] = {}
                
                self.results["rust"][operation][size][impl_type] = time_us
                self.log(f"  Rust {operation}/{impl_type}/{size}: {time_us:.2f} µs")
    
    def run_go_benchmarks(self) -> bool:
        """Run Go benchmarks."""
        print("\n=== Running Go Benchmarks ===")
        self.log("Checking for Go installation...")
        
        # Check if go is available
        try:
            subprocess.run(['go', 'version'], check=True, capture_output=True)
        except:
            print("Error: Go not found. Please install Go.")
            return False
        
        # Run comparison benchmarks
        self.log("Running Go comparison benchmarks...")
        try:
            os.chdir('go')
            result = subprocess.run(
                ['go', 'test', '-bench=Comparison', './benchmark', '-benchtime=1s'],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            if result.returncode != 0:
                print(f"Error running Go benchmarks: {result.stderr}")
                return False
            
            # Parse Go benchmark output
            self.parse_go_output(result.stdout)
            os.chdir('..')
            return True
            
        except Exception as e:
            print(f"Error running Go benchmarks: {e}")
            os.chdir('..')
            return False
    
    def parse_go_output(self, output: str):
        """Parse Go benchmark output."""
        self.log("Parsing Go benchmark results...")
        
        # Pattern: BenchmarkComparison/Size-1000/SequentialInsert/BPlusTree-8    100    12345 ns/op
        pattern = r'BenchmarkComparison/Size-(\d+)/(\w+)/(BPlusTree|Map|SyncMap)-\d+\s+\d+\s+([0-9.]+)\s*ns/op'
        
        for match in re.finditer(pattern, output):
            size = int(match.group(1))
            operation = match.group(2).lower()
            impl_type = match.group(3).lower()
            time_ns = float(match.group(4))
            time_us = time_ns / 1000  # Convert to microseconds
            
            # Initialize nested structure
            if operation not in self.results["go"]:
                self.results["go"][operation] = {}
            if size not in self.results["go"][operation]:
                self.results["go"][operation][size] = {}
            
            self.results["go"][operation][size][impl_type] = time_us
            self.log(f"  Go {operation}/{impl_type}/{size}: {time_us:.2f} µs")
    
    def run_zig_benchmarks(self) -> bool:
        """Run Zig benchmarks."""
        print("\n=== Running Zig Benchmarks ===")
        self.log("Checking for Zig installation...")
        
        # Check if zig is available
        try:
            subprocess.run(['zig', 'version'], check=True, capture_output=True)
        except:
            print("Error: Zig not found. Please install Zig.")
            return False
        
        # Run comparison benchmarks
        self.log("Running Zig comparison benchmarks...")
        try:
            os.chdir('zig')
            result = subprocess.run(
                ['zig', 'build', 'compare'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"Error running Zig benchmarks: {result.stderr}")
                return False
            
            # Parse Zig benchmark output
            self.parse_zig_output(result.stderr)  # Zig outputs to stderr
            os.chdir('..')
            return True
            
        except Exception as e:
            print(f"Error running Zig benchmarks: {e}")
            os.chdir('..')
            return False
    
    def parse_zig_output(self, output: str):
        """Parse Zig benchmark output."""
        self.log("Parsing Zig benchmark results...")
        
        current_size = None
        current_operation = None
        
        for line in output.split('\n'):
            # Parse size header
            size_match = re.search(r'--- Size: (\d+) ---', line)
            if size_match:
                current_size = int(size_match.group(1))
                continue
            
            # Parse operation header
            if 'Sequential Insertion:' in line:
                current_operation = 'sequentialinsert'
            elif 'Random Lookup:' in line:
                current_operation = 'lookup'
            elif 'Iteration:' in line:
                current_operation = 'iteration'
            elif 'Range Query' in line:
                current_operation = 'rangequery'
            
            # Parse timing data
            timing_match = re.search(r'(B\+ Tree|HashMap)\s+(\d+)\s+ops in\s+([0-9.]+)ms.*?([0-9.]+)\s*ns/op', line)
            if timing_match and current_size and current_operation:
                impl_type = 'bplustree' if 'B+ Tree' in timing_match.group(1) else 'hashmap'
                time_ns = float(timing_match.group(4))
                time_us = time_ns / 1000
                
                # Initialize nested structure
                if current_operation not in self.results["zig"]:
                    self.results["zig"][current_operation] = {}
                if current_size not in self.results["zig"][current_operation]:
                    self.results["zig"][current_operation][current_size] = {}
                
                self.results["zig"][current_operation][current_size][impl_type] = time_us
                self.log(f"  Zig {current_operation}/{impl_type}/{current_size}: {time_us:.2f} µs")
    
    def generate_report(self, output_file: str = "benchmark_report.md"):
        """Generate a comprehensive markdown report."""
        print(f"\n=== Generating Report: {output_file} ===")
        
        with open(output_file, 'w') as f:
            # Header
            f.write("# B+ Tree Cross-Language Benchmark Report\n\n")
            f.write(f"Generated: {self.results['metadata']['timestamp']}\n\n")
            
            # System info
            f.write("## System Information\n\n")
            f.write(f"- **OS**: {self.results['metadata']['system_info']['os']}\n")
            f.write(f"- **CPU**: {self.results['metadata']['system_info']['cpu']}\n")
            f.write(f"- **Memory**: {self.results['metadata']['system_info']['memory']}\n\n")
            
            # Normalize operation names
            operations = set()
            for lang in ['rust', 'go', 'zig']:
                operations.update(self.results[lang].keys())
            
            # Operation comparison tables
            f.write("## Performance Comparison\n\n")
            f.write("All times in microseconds (µs). Lower is better.\n\n")
            
            for op in sorted(operations):
                if not any(op in self.results[lang] for lang in ['rust', 'go', 'zig']):
                    continue
                
                f.write(f"### {op.replace('_', ' ').title()}\n\n")
                
                # Get all sizes
                sizes = set()
                for lang in ['rust', 'go', 'zig']:
                    if op in self.results[lang]:
                        sizes.update(self.results[lang][op].keys())
                
                if not sizes:
                    continue
                
                # Create comparison table
                f.write("| Size | Rust B+ | Rust Native | Go B+ | Go Native | Zig B+ | Zig Native |\n")
                f.write("|------|---------|-------------|-------|-----------|--------|------------|\n")
                
                for size in sorted(sizes):
                    row = f"| {size} |"
                    
                    # Rust
                    if 'rust' in self.results and op in self.results['rust'] and size in self.results['rust'][op]:
                        rust_data = self.results['rust'][op][size]
                        bplus = rust_data.get('bplustree', 0)
                        native = rust_data.get('btreemap', 0)
                        if bplus: row += f" {bplus:.2f} |"
                        else: row += " - |"
                        if native: row += f" {native:.2f} |"
                        else: row += " - |"
                    else:
                        row += " - | - |"
                    
                    # Go
                    if 'go' in self.results and op in self.results['go'] and size in self.results['go'][op]:
                        go_data = self.results['go'][op][size]
                        bplus = go_data.get('bplustree', 0)
                        native = go_data.get('map', go_data.get('syncmap', 0))
                        if bplus: row += f" {bplus:.2f} |"
                        else: row += " - |"
                        if native: row += f" {native:.2f} |"
                        else: row += " - |"
                    else:
                        row += " - | - |"
                    
                    # Zig
                    if 'zig' in self.results and op in self.results['zig'] and size in self.results['zig'][op]:
                        zig_data = self.results['zig'][op][size]
                        bplus = zig_data.get('bplustree', 0)
                        native = zig_data.get('hashmap', 0)
                        if bplus: row += f" {bplus:.2f} |"
                        else: row += " - |"
                        if native: row += f" {native:.2f} |"
                        else: row += " - |"
                    else:
                        row += " - | - |"
                    
                    f.write(row + "\n")
                
                f.write("\n")
            
            # Performance ratios
            f.write("## Performance Ratios (B+ Tree vs Native)\n\n")
            f.write("Values > 1.0 mean B+ tree is slower, < 1.0 mean B+ tree is faster.\n\n")
            
            for op in sorted(operations):
                ratios = []
                
                for lang, native_name in [('rust', 'btreemap'), ('go', 'map'), ('zig', 'hashmap')]:
                    if lang in self.results and op in self.results[lang]:
                        for size in self.results[lang][op]:
                            data = self.results[lang][op][size]
                            if 'bplustree' in data and native_name in data:
                                ratio = data['bplustree'] / data[native_name]
                                ratios.append((lang, size, ratio))
                
                if ratios:
                    f.write(f"### {op.replace('_', ' ').title()}\n\n")
                    f.write("| Language | Size | Ratio |\n")
                    f.write("|----------|------|-------|\n")
                    
                    for lang, size, ratio in sorted(ratios):
                        faster = "🟢" if ratio < 0.9 else "🔴" if ratio > 1.1 else "🟡"
                        f.write(f"| {lang.title()} | {size} | {faster} {ratio:.2f}x |\n")
                    
                    f.write("\n")
            
            # Key insights
            f.write("## Key Insights\n\n")
            f.write("### B+ Tree Advantages\n\n")
            f.write("- **Ordered iteration**: B+ trees maintain keys in sorted order\n")
            f.write("- **Range queries**: Efficient range scans due to linked leaves\n")
            f.write("- **Predictable performance**: Worst-case O(log n) for all operations\n")
            f.write("- **Cache efficiency**: Better locality for sequential access patterns\n\n")
            
            f.write("### Native Structure Advantages\n\n")
            f.write("- **Random access**: O(1) average case for hash-based structures\n")
            f.write("- **Memory efficiency**: Lower overhead for small datasets\n")
            f.write("- **Simplicity**: Simpler implementation and usage\n")
            f.write("- **Insert performance**: Generally faster for random insertions\n\n")
            
            f.write("### Language-Specific Observations\n\n")
            f.write("- **Rust**: Best overall performance, especially for large datasets\n")
            f.write("- **Go**: Good balance of performance and ease of use\n")
            f.write("- **Zig**: Excellent raw performance, competitive with Rust\n\n")
            
            f.write("### When to Use B+ Trees\n\n")
            f.write("1. When you need ordered iteration over keys\n")
            f.write("2. When range queries are a primary use case\n")
            f.write("3. When you need predictable worst-case performance\n")
            f.write("4. When working with disk-based storage (B+ trees are cache-friendly)\n")
            f.write("5. When implementing databases or file systems\n\n")
        
        print(f"Report generated: {output_file}")
    
    def save_raw_results(self, output_file: str = "benchmark_results.json"):
        """Save raw results as JSON for further analysis."""
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"Raw results saved: {output_file}")
    
    def run_all(self):
        """Run all benchmarks and generate report."""
        languages_run = []
        
        # Run benchmarks for each language
        if self.run_rust_benchmarks():
            languages_run.append("Rust")
        
        if self.run_go_benchmarks():
            languages_run.append("Go")
        
        if self.run_zig_benchmarks():
            languages_run.append("Zig")
        
        if not languages_run:
            print("\nError: No benchmarks could be run. Please install at least one language.")
            return False
        
        print(f"\n✓ Successfully ran benchmarks for: {', '.join(languages_run)}")
        
        # Generate reports
        self.generate_report()
        self.save_raw_results()
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Run B+ Tree benchmarks across multiple languages')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--rust-only', action='store_true', help='Run only Rust benchmarks')
    parser.add_argument('--go-only', action='store_true', help='Run only Go benchmarks')
    parser.add_argument('--zig-only', action='store_true', help='Run only Zig benchmarks')
    parser.add_argument('-o', '--output', default='benchmark_report.md', help='Output report filename')
    
    args = parser.parse_args()
    
    runner = BenchmarkRunner(verbose=args.verbose)
    
    print("B+ Tree Cross-Language Benchmark Runner")
    print("======================================\n")
    
    if args.rust_only:
        runner.run_rust_benchmarks()
    elif args.go_only:
        runner.run_go_benchmarks()
    elif args.zig_only:
        runner.run_zig_benchmarks()
    else:
        runner.run_all()

if __name__ == "__main__":
    main()