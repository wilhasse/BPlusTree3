#!/usr/bin/env python3
"""
Background Rust benchmark runner.
Runs Rust benchmarks in the background and updates results when complete.
"""

import subprocess
import os
import json
import time
from datetime import datetime
import sys

def run_background_rust_benchmark():
    """Run Rust benchmarks in background and update results."""
    print("🦀 Starting Background Rust Benchmark")
    print("=" * 50)
    print("This will run Rust benchmarks in the background.")
    print("The process may take 5-10 minutes to complete.")
    print("Results will be saved when finished.")
    print("=" * 50)
    
    # Check if cargo is available
    cargo_cmd = None
    cargo_paths = ['cargo', os.path.expanduser('~/.cargo/bin/cargo')]
    
    for path in cargo_paths:
        try:
            subprocess.run([path, '--version'], check=True, capture_output=True)
            cargo_cmd = path
            print(f"✅ Found Rust/Cargo at: {path}")
            break
        except:
            continue
    
    if not cargo_cmd:
        print("❌ Rust/Cargo not found. Please install Rust first.")
        return False
    
    # Start the benchmark
    start_time = time.time()
    print(f"\n🚀 Starting Rust benchmarks at {datetime.now().strftime('%H:%M:%S')}")
    print("⏱️  Estimated completion: 5-10 minutes")
    print("📊 Running: Sequential Insert, Lookup, Iteration, Range Query")
    
    try:
        os.chdir('rust')
        
        # Run with live output so user can see progress
        print("\n" + "─" * 50)
        print("📈 BENCHMARK PROGRESS (live output):")
        print("─" * 50)
        
        process = subprocess.Popen(
            [cargo_cmd, 'bench', '--bench', 'simple_comparison'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Show live output with progress indicators
        output_lines = []
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                line = output.strip()
                output_lines.append(line)
                
                # Show interesting lines
                if any(keyword in line for keyword in [
                    'Benchmarking', 'time:', 'Found', 'Analyzing', 'Warming up'
                ]):
                    print(f"  {line}")
                    
                # Show completion status
                if 'time:' in line and any(op in line for op in ['SequentialInsert', 'Lookup', 'Iteration', 'RangeQuery']):
                    elapsed = time.time() - start_time
                    print(f"    ⏱️  {elapsed/60:.1f} minutes elapsed")
        
        # Wait for completion
        return_code = process.poll()
        
        if return_code == 0:
            elapsed = time.time() - start_time
            print(f"\n✅ Rust benchmarks completed in {elapsed/60:.1f} minutes!")
            
            # Parse and save results
            full_output = '\n'.join(output_lines)
            parse_and_save_rust_results(full_output)
            
            print("📊 Results have been parsed and saved to benchmark files.")
            print("🔄 Run './scripts/run_all_benchmarks.py' to generate updated cross-language report.")
            
            return True
        else:
            print(f"❌ Benchmark failed with return code: {return_code}")
            return False
            
    except KeyboardInterrupt:
        print("\n⚠️  Benchmark interrupted by user")
        if process:
            process.terminate()
        return False
    except Exception as e:
        print(f"❌ Error running benchmark: {e}")
        return False
    finally:
        os.chdir('..')

def parse_and_save_rust_results(output: str):
    """Parse Rust benchmark output and update results files."""
    print("\n🔍 Parsing Rust benchmark results...")
    
    rust_results = {}
    
    # Parse criterion output format
    # Pattern: OperationName/ImplType/Size  time: [X.XX µs Y.YY µs Z.ZZ µs]
    import re
    patterns = [
        r'(\w+)/(BTreeMap|BPlusTree)/(\d+)\s+time:\s+\[([0-9.]+)\s*(µs|us|ns)',
    ]
    
    for pattern in patterns:
        for match in re.finditer(pattern, output):
            operation = match.group(1).lower()
            impl_type = match.group(2).lower()
            size = int(match.group(3))
            
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
                time_us = time_value
            
            # Normalize names
            if impl_type == 'btreemap':
                impl_type = 'btreemap'
            elif impl_type == 'bplustree':
                impl_type = 'bplustree'
            
            # Store result
            if operation not in rust_results:
                rust_results[operation] = {}
            if size not in rust_results[operation]:
                rust_results[operation][size] = {}
            
            rust_results[operation][size][impl_type] = time_us
            print(f"  📊 {operation}/{impl_type}/{size}: {time_us:.2f} µs")
    
    # Load existing results if available
    try:
        with open('../benchmark_results.json', 'r') as f:
            all_results = json.load(f)
    except:
        all_results = {
            "rust": {},
            "go": {},
            "zig": {},
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "system_info": {"os": "Unknown", "cpu": "Unknown", "memory": "Unknown"}
            }
        }
    
    # Update with Rust results
    all_results["rust"] = rust_results
    all_results["metadata"]["timestamp"] = datetime.now().isoformat()
    
    # Save updated results
    with open('../benchmark_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"✅ Saved {len(rust_results)} operation types with Rust results")
    
    # Create a summary
    print("\n📋 RUST BENCHMARK SUMMARY:")
    print("─" * 40)
    for operation in sorted(rust_results.keys()):
        print(f"\n{operation.upper()}:")
        for size in sorted(rust_results[operation].keys()):
            data = rust_results[operation][size]
            if 'bplustree' in data and 'btreemap' in data:
                ratio = data['bplustree'] / data['btreemap']
                winner = "BTreeMap" if ratio > 1.2 else "B+ Tree" if ratio < 0.8 else "Similar"
                print(f"  Size {size:6}: B+ {data['bplustree']:8.2f}µs vs BTree {data['btreemap']:8.2f}µs → {winner}")

def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("""
Background Rust Benchmark Runner

Usage:
  ./background_rust_bench.py          # Run benchmarks in foreground with live output
  nohup ./background_rust_bench.py &  # Run truly in background
  
This script:
1. Runs Rust benchmarks (takes 5-10 minutes)
2. Shows live progress updates
3. Parses and saves results automatically
4. Updates benchmark_results.json when complete

After completion, run:
  ./scripts/run_all_benchmarks.py     # To generate updated report
        """)
        return
    
    success = run_background_rust_benchmark()
    
    if success:
        print("\n🎉 Background Rust benchmark completed successfully!")
        print("📝 Next steps:")
        print("   1. Check benchmark_results.json for raw data")
        print("   2. Run: ./scripts/run_all_benchmarks.py")
        print("   3. View: benchmark_report.md for updated 3-language comparison")
    else:
        print("\n❌ Background Rust benchmark failed")
        print("🔧 Try running manually: cd rust && cargo bench --bench simple_comparison")

if __name__ == "__main__":
    main()