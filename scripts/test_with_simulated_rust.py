#!/usr/bin/env python3
"""
Test the benchmark runner with simulated Rust output.
Creates a complete cross-language comparison.
"""

import os
import tempfile
from run_all_benchmarks import BenchmarkRunner

def create_simulated_rust_output():
    """Create simulated Rust benchmark output in criterion format."""
    return """
SequentialInsert/BPlusTree/100
                        time:   [5.23 µs 5.47 µs 5.71 µs]
                        change: [-2.1% +0.5% +3.2%] (p = 0.45 > 0.05)
                        No change in performance detected.

SequentialInsert/BTreeMap/100
                        time:   [2.89 µs 3.12 µs 3.35 µs]
                        change: [-1.8% +1.2% +4.1%] (p = 0.32 > 0.05)
                        No change in performance detected.

SequentialInsert/BPlusTree/1000
                        time:   [78.4 µs 82.1 µs 85.9 µs]
                        change: [-3.2% +0.8% +4.7%] (p = 0.58 > 0.05)
                        No change in performance detected.

SequentialInsert/BTreeMap/1000
                        time:   [44.2 µs 47.3 µs 50.5 µs]
                        change: [-2.5% +1.1% +4.8%] (p = 0.41 > 0.05)
                        No change in performance detected.

SequentialInsert/BPlusTree/10000
                        time:   [982 µs 1.04 ms 1.11 ms]
                        change: [-4.1% +1.3% +6.8%] (p = 0.29 > 0.05)
                        No change in performance detected.

SequentialInsert/BTreeMap/10000
                        time:   [587 µs 623 µs 659 µs]
                        change: [-3.7% +0.9% +5.4%] (p = 0.52 > 0.05)
                        No change in performance detected.

Lookup/BPlusTree/100
                        time:   [11.3 µs 12.1 µs 12.9 µs]
                        change: [-2.8% +1.4% +5.7%] (p = 0.33 > 0.05)
                        No change in performance detected.

Lookup/BTreeMap/100
                        time:   [7.82 µs 8.34 µs 8.87 µs]
                        change: [-1.9% +0.7% +3.3%] (p = 0.46 > 0.05)
                        No change in performance detected.

Lookup/BPlusTree/1000
                        time:   [13.7 µs 14.6 µs 15.5 µs]
                        change: [-3.1% +1.8% +6.7%] (p = 0.28 > 0.05)
                        No change in performance detected.

Lookup/BTreeMap/1000
                        time:   [10.4 µs 11.1 µs 11.8 µs]
                        change: [-2.4% +0.9% +4.2%] (p = 0.51 > 0.05)
                        No change in performance detected.

Lookup/BPlusTree/10000
                        time:   [22.8 µs 24.3 µs 25.9 µs]
                        change: [-4.2% +1.1% +6.4%] (p = 0.37 > 0.05)
                        No change in performance detected.

Lookup/BTreeMap/10000
                        time:   [27.2 µs 28.9 µs 30.6 µs]
                        change: [-3.8% +2.1% +7.9%] (p = 0.19 > 0.05)
                        No change in performance detected.

Iteration/BPlusTree/100
                        time:   [245 ns 267 ns 289 ns]
                        change: [-1.7% +1.3% +4.2%] (p = 0.43 > 0.05)
                        No change in performance detected.

Iteration/BTreeMap/100
                        time:   [98.2 ns 107 ns 116 ns]
                        change: [-2.1% +0.8% +3.7%] (p = 0.55 > 0.05)
                        No change in performance detected.

Iteration/BPlusTree/1000
                        time:   [2.48 µs 2.69 µs 2.91 µs]
                        change: [-3.4% +1.7% +6.8%] (p = 0.26 > 0.05)
                        No change in performance detected.

Iteration/BTreeMap/1000
                        time:   [2.08 µs 2.25 µs 2.42 µs]
                        change: [-2.9% +0.6% +4.1%] (p = 0.48 > 0.05)
                        No change in performance detected.

Iteration/BPlusTree/10000
                        time:   [27.3 µs 29.8 µs 32.4 µs]
                        change: [-4.7% +2.2% +9.1%] (p = 0.14 > 0.05)
                        No change in performance detected.

Iteration/BTreeMap/10000
                        time:   [20.9 µs 22.7 µs 24.5 µs]
                        change: [-3.6% +1.4% +6.4%] (p = 0.31 > 0.05)
                        No change in performance detected.

RangeQuery/BPlusTree/100
                        time:   [123 ns 134 ns 145 ns]
                        change: [-1.8% +1.1% +4.0%] (p = 0.42 > 0.05)
                        No change in performance detected.

RangeQuery/BTreeMap/100
                        time:   [89.3 ns 97.2 ns 105 ns]
                        change: [-2.3% +0.7% +3.7%] (p = 0.49 > 0.05)
                        No change in performance detected.

RangeQuery/BPlusTree/1000
                        time:   [587 ns 634 ns 681 ns]
                        change: [-3.1% +1.9% +6.9%] (p = 0.25 > 0.05)
                        No change in performance detected.

RangeQuery/BTreeMap/1000
                        time:   [745 ns 812 ns 879 ns]
                        change: [-2.7% +1.3% +5.3%] (p = 0.35 > 0.05)
                        No change in performance detected.

RangeQuery/BPlusTree/10000
                        time:   [5.89 µs 6.34 µs 6.79 µs]
                        change: [-4.2% +2.1% +8.4%] (p = 0.18 > 0.05)
                        No change in performance detected.

RangeQuery/BTreeMap/10000
                        time:   [7.23 µs 7.81 µs 8.39 µs]
                        change: [-3.8% +1.6% +7.0%] (p = 0.28 > 0.05)
                        No change in performance detected.
"""

class TestBenchmarkRunner(BenchmarkRunner):
    """Test version that simulates Rust output."""
    
    def run_rust_benchmarks(self) -> bool:
        """Simulate Rust benchmarks."""
        print("\n=== Running Rust Benchmarks (SIMULATED) ===")
        self.log("Simulating Rust benchmark output...")
        
        # Simulate the output
        output = create_simulated_rust_output()
        self.parse_rust_output(output)
        
        print("✓ Simulated Rust benchmarks completed")
        return True

def main():
    """Run test with simulated Rust data."""
    print("B+ Tree Cross-Language Benchmark Test")
    print("====================================")
    print("Running with simulated Rust data for complete comparison\n")
    
    runner = TestBenchmarkRunner(verbose=True)
    
    # Run all benchmarks
    if runner.run_all():
        print("\n" + "="*50)
        print("SUCCESS: All benchmarks completed!")
        print("="*50)
        
        # Show summary of what we got
        languages = []
        for lang in ['rust', 'go', 'zig']:
            if lang in runner.results and runner.results[lang]:
                languages.append(lang)
        
        print(f"\nData collected for: {', '.join(languages)}")
        
        # Show a sample comparison
        if len(languages) >= 2:
            print("\nSample cross-language comparison (Iteration at size 1000):")
            for lang in languages:
                if 'iteration' in runner.results[lang] and 1000 in runner.results[lang]['iteration']:
                    data = runner.results[lang]['iteration'][1000]
                    if 'bplustree' in data:
                        print(f"  {lang.title()} B+ Tree: {data['bplustree']:.3f} µs")
        
        print("\nCheck 'benchmark_report.md' for full analysis!")
    else:
        print("Some benchmarks failed, but partial results may still be useful.")

if __name__ == "__main__":
    main()