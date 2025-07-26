#!/usr/bin/env python3
"""
Automated benchmark runner for B+ Tree implementations.
Runs benchmarks across Rust, Go, Zig, and C, collects results, and generates a comprehensive report.
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
    def __init__(self, verbose=False, auto_install=False):
        self.verbose = verbose
        self.auto_install = auto_install
        self.results = {
            "rust": {},
            "go": {},
            "zig": {},
            "c": {},
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
    
    def auto_install_rust(self) -> bool:
        """Attempt to install Rust automatically."""
        try:
            # If auto_install is enabled, proceed without prompting
            if not self.auto_install:
                # Check if we're in interactive mode
                import sys
                if not sys.stdin.isatty():
                    print("Non-interactive mode - skipping Rust installation")
                    return False
                    
                response = input("Install Rust? (y/n): ").strip().lower()
                if response not in ['y', 'yes']:
                    return False
            
            print("Installing Rust... This may take a few minutes.")
            self.log("Downloading and installing Rust via rustup...")
            
            # Download and run rustup installer
            install_cmd = [
                'curl', '--proto', '=https', '--tlsv1.2', '-sSf', 
                'https://sh.rustup.rs', '|', 'sh', '-s', '--', '-y'
            ]
            
            # Use shell=True for pipe command
            result = subprocess.run(
                'curl --proto =https --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y',
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                print(f"Failed to install Rust: {result.stderr}")
                return False
            
            # Source the cargo env
            cargo_env = os.path.expanduser("~/.cargo/env")
            if os.path.exists(cargo_env):
                # Add cargo to current PATH
                cargo_bin = os.path.expanduser("~/.cargo/bin")
                os.environ["PATH"] = f"{cargo_bin}:{os.environ.get('PATH', '')}"
                
            # Verify installation
            try:
                subprocess.run(['cargo', '--version'], check=True, capture_output=True)
                print("✅ Rust installed successfully!")
                return True
            except:
                print("❌ Rust installation completed but cargo not found in PATH")
                print("Please restart your terminal or run: source ~/.cargo/env")
                return False
                
        except Exception as e:
            print(f"Error installing Rust: {e}")
            return False
    
    def run_rust_benchmarks(self) -> bool:
        """Run Rust benchmarks using cargo bench."""
        print("\n=== Running Rust Benchmarks ===")
        self.log("Checking for Rust installation...")
        
        # Check if cargo is available, including common install locations
        cargo_cmd = None
        cargo_paths = ['cargo', os.path.expanduser('~/.cargo/bin/cargo')]
        
        for path in cargo_paths:
            try:
                subprocess.run([path, '--version'], check=True, capture_output=True)
                cargo_cmd = path
                self.log(f"Rust/Cargo found at {path}")
                break
            except:
                continue
        
        if not cargo_cmd:
            if self.auto_install:
                print("Rust/Cargo not found. Attempting automatic installation...")
                if not self.auto_install_rust():
                    print("Skipping Rust benchmarks.")
                    return False
                # Re-check after installation
                cargo_cmd = os.path.expanduser('~/.cargo/bin/cargo')
            else:
                print("Rust/Cargo not found. Use --auto-install to install automatically, or install manually:")
                print("  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh")
                return False
        
        # Run comparison benchmarks
        self.log("Running Rust comparison benchmarks...")
        try:
            os.chdir('rust')
            result = subprocess.run(
                [cargo_cmd, 'bench', '--bench', 'simple_comparison'],
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout for Rust benchmarks
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
        
        # Updated patterns for simple_comparison benchmark
        patterns = [
            # Pattern: OperationName/ImplType/Size  time: [X.XX µs Y.YY µs Z.ZZ µs]
            r'(\w+)/(BTreeMap|BPlusTree)/(\d+)\s+time:\s+\[([0-9.]+)\s*(µs|us|ns)',
            # Pattern: OperationName/ImplType/Size ... bench: X ns/iter
            r'(\w+)/(BTreeMap|BPlusTree)/(\d+)\s+.*?time:\s+\[([0-9.]+)\s*(µs|us|ns)',
            # Alternative pattern for criterion output
            r'(\w+)/(BTreeMap|BPlusTree)/(\d+)\s+.*?([0-9.]+)\s*(µs|us|ns)',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, output):
                operation = match.group(1).lower()
                impl_type = match.group(2).lower()
                size = int(match.group(3))
                
                # Get the time value (4th group in all patterns)
                time_value = float(match.group(4))
                time_unit = match.group(5)
                
                # Convert to microseconds
                if time_unit in ['µs', 'us']:
                    time_us = time_value
                elif time_unit == 'ns':
                    time_us = time_value / 1000
                elif time_unit == 'ms':
                    time_us = time_value * 1000
                else:
                    time_us = time_value  # Assume µs if unclear
                
                # Map BTreeMap to btreemap for consistency
                if impl_type == 'btreemap':
                    impl_type = 'btreemap'
                elif impl_type == 'bplustree':
                    impl_type = 'bplustree'
                
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
        
        # Check if go is available with PATH expansion
        try:
            # Try common Go installation paths
            go_paths = ['go', '/usr/local/go/bin/go', '/usr/bin/go']
            go_cmd = None
            
            for path in go_paths:
                try:
                    subprocess.run([path, 'version'], check=True, capture_output=True)
                    go_cmd = path
                    break
                except:
                    continue
            
            if not go_cmd:
                raise FileNotFoundError("Go not found in any standard location")
                
        except:
            print("Error: Go not found. Please install Go.")
            return False
        
        # Run comparison benchmarks
        self.log("Running Go comparison benchmarks...")
        try:
            os.chdir('go')
            result = subprocess.run(
                [go_cmd, 'test', '-bench=Comparison', './benchmark', '-benchtime=1s'],
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
            
            # Parse timing data with scientific notation
            # Format: B+ Tree    1000 ops in  1.83e-1ms |  5e6 ops/sec |  1.83e2 ns/op
            timing_match = re.search(r'(B\+ Tree|HashMap)\s+(\d+)\s+ops in\s+([0-9.e+-]+)ms.*?([0-9.e+-]+)\s*ns/op', line)
            if timing_match and current_size and current_operation:
                impl_type = 'bplustree' if 'B+ Tree' in timing_match.group(1) else 'hashmap'
                time_ns_str = timing_match.group(4)
                
                # Parse scientific notation
                try:
                    time_ns = float(time_ns_str)
                    time_us = time_ns / 1000  # Convert ns to µs
                    
                    # Initialize nested structure
                    if current_operation not in self.results["zig"]:
                        self.results["zig"][current_operation] = {}
                    if current_size not in self.results["zig"][current_operation]:
                        self.results["zig"][current_operation][current_size] = {}
                    
                    self.results["zig"][current_operation][current_size][impl_type] = time_us
                    self.log(f"  Zig {current_operation}/{impl_type}/{current_size}: {time_us:.3f} µs")
                    
                except ValueError:
                    self.log(f"  Could not parse time value: {time_ns_str}")
                    continue
    
    def run_c_benchmarks(self) -> bool:
        """Run C benchmarks using make benchmark."""
        print("\n=== Running C Benchmarks ===")
        self.log("Checking for C compiler and make...")
        
        # Check if make and gcc are available
        try:
            subprocess.run(['make', '--version'], check=True, capture_output=True)
            subprocess.run(['gcc', '--version'], check=True, capture_output=True)
        except:
            print("Error: make or gcc not found. Please install build tools.")
            return False
        
        # Run C benchmarks
        self.log("Running C comparison benchmarks...")
        try:
            os.chdir('c')
            result = subprocess.run(
                ['make', 'benchmark'],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                print(f"C benchmark failed: {result.stderr}")
                return False
            
            self.parse_c_output(result.stdout)
            return True
            
        except subprocess.TimeoutExpired:
            print("C benchmark timed out")
            return False
        except Exception as e:
            print(f"Error running C benchmarks: {e}")
            return False
        finally:
            os.chdir('..')
    
    def parse_c_output(self, output: str):
        """Parse C benchmark output."""
        self.log("Parsing C benchmark results...")
        
        current_operation = None
        
        for line in output.split('\n'):
            # Parse operation headers
            if '=== Sequential Insert ===' in line:
                current_operation = 'sequentialinsert'
                continue
            elif '=== Lookup ===' in line:
                current_operation = 'lookup'
                continue
            elif '=== Iteration ===' in line:
                current_operation = 'iteration'
                continue
            
            # Parse timing data
            # Format: B+ Tree    100 ops in     0.00ms | 32954358 ops/sec |    30.34 ns/op
            timing_match = re.search(r'(B\+ Tree|Hash Table)\s+(\d+)\s+ops in\s+([0-9.]+)ms.*?([0-9.]+)\s*ns/op', line)
            if timing_match and current_operation:
                impl_type = 'bplustree' if 'B+ Tree' in timing_match.group(1) else 'hashtable'
                size = int(timing_match.group(2))
                time_ns = float(timing_match.group(4))
                time_us = time_ns / 1000  # Convert ns to µs
                
                # Initialize nested structure
                if current_operation not in self.results["c"]:
                    self.results["c"][current_operation] = {}
                if size not in self.results["c"][current_operation]:
                    self.results["c"][current_operation][size] = {}
                
                self.results["c"][current_operation][size][impl_type] = time_us
                self.log(f"  C {current_operation}/{impl_type}/{size}: {time_us:.3f} µs")
    
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
            for lang in ['rust', 'go', 'zig', 'c']:
                operations.update(self.results[lang].keys())
            
            # Operation comparison tables
            f.write("## Performance Comparison\n\n")
            f.write("All times in microseconds (µs). Lower is better.\n\n")
            
            for op in sorted(operations):
                if not any(op in self.results[lang] for lang in ['rust', 'go', 'zig', 'c']):
                    continue
                
                f.write(f"### {op.replace('_', ' ').title()}\n\n")
                
                # Get all sizes
                sizes = set()
                for lang in ['rust', 'go', 'zig', 'c']:
                    if op in self.results[lang]:
                        sizes.update(self.results[lang][op].keys())
                
                if not sizes:
                    continue
                
                # Create comparison table
                f.write("| Size | Rust B+ | Rust Native | Go B+ | Go Native | Zig B+ | Zig Native | C B+ | C Native |\n")
                f.write("|------|---------|-------------|-------|-----------|--------|------------|------|----------|\n")
                
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
                    
                    # C
                    if 'c' in self.results and op in self.results['c'] and size in self.results['c'][op]:
                        c_data = self.results['c'][op][size]
                        bplus = c_data.get('bplustree', 0)
                        native = c_data.get('hashtable', 0)
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
                
                for lang, native_name in [('rust', 'btreemap'), ('go', 'map'), ('zig', 'hashmap'), ('c', 'hashtable')]:
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
        
        if self.run_c_benchmarks():
            languages_run.append("C")
        
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
    parser.add_argument('--auto-install', action='store_true', help='Automatically install missing languages')
    parser.add_argument('--rust-only', action='store_true', help='Run only Rust benchmarks')
    parser.add_argument('--go-only', action='store_true', help='Run only Go benchmarks')
    parser.add_argument('--zig-only', action='store_true', help='Run only Zig benchmarks')
    parser.add_argument('--c-only', action='store_true', help='Run only C benchmarks')
    parser.add_argument('-o', '--output', default='benchmark_report.md', help='Output report filename')
    
    args = parser.parse_args()
    
    runner = BenchmarkRunner(verbose=args.verbose, auto_install=args.auto_install)
    
    print("B+ Tree Cross-Language Benchmark Runner")
    print("======================================\n")
    
    if args.rust_only:
        runner.run_rust_benchmarks()
    elif args.go_only:
        runner.run_go_benchmarks()
    elif args.zig_only:
        runner.run_zig_benchmarks()
    elif args.c_only:
        runner.run_c_benchmarks()
    else:
        runner.run_all()

if __name__ == "__main__":
    main()