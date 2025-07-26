#!/usr/bin/env python3
"""
Cross-language B+ Tree benchmark comparison script.
Analyzes and visualizes performance across Rust, Go, and Zig implementations.
"""

import json
import sys
from typing import Dict, List, Tuple
import re

# Sample benchmark results (to be replaced with actual parsing)
# These are example values - you should parse actual output
SAMPLE_RESULTS = {
    "rust": {
        "sequential_insert": {
            100: {"bplustree": 6.03, "btreemap": 3.07},
            1000: {"bplustree": 86.2, "btreemap": 49.8},
            10000: {"bplustree": 1072, "btreemap": 640},
        },
        "lookup": {
            100: {"bplustree": 12.7, "btreemap": 8.43},
            1000: {"bplustree": 14.8, "btreemap": 11.3},
            10000: {"bplustree": 24.3, "btreemap": 29.5},
        },
        "iteration": {
            100: {"bplustree": 0.267, "btreemap": 0.107},
            1000: {"bplustree": 2.69, "btreemap": 2.25},
            10000: {"bplustree": 29.8, "btreemap": 22.7},
        }
    },
    "go": {
        "sequential_insert": {
            100: {"bplustree": 3.66, "map": 1.20},
            1000: {"bplustree": 36.6, "map": 12.0},
            10000: {"bplustree": 366, "map": 120},
        },
        "lookup": {
            100: {"bplustree": 0.175, "map": 0.050},
            1000: {"bplustree": 1.75, "map": 0.50},
            10000: {"bplustree": 17.5, "map": 5.0},
        },
        "iteration": {
            100: {"bplustree": 0.133, "map": 0.200},
            1000: {"bplustree": 1.33, "map": 2.00},
            10000: {"bplustree": 13.3, "map": 20.0},
        }
    },
    "zig": {
        "sequential_insert": {
            100: {"bplustree": 0.441, "hashmap": 0.150},
            1000: {"bplustree": 4.41, "hashmap": 1.50},
            10000: {"bplustree": 44.1, "hashmap": 15.0},
        },
        "lookup": {
            100: {"bplustree": 0.163, "hashmap": 0.040},
            1000: {"bplustree": 1.63, "hashmap": 0.40},
            10000: {"bplustree": 16.3, "hashmap": 4.0},
        },
        "iteration": {
            100: {"bplustree": 0.315, "hashmap": 0.500},
            1000: {"bplustree": 3.15, "hashmap": 5.00},
            10000: {"bplustree": 31.5, "hashmap": 50.0},
        }
    }
}

def parse_rust_output(output: str) -> Dict:
    """Parse Rust criterion benchmark output."""
    results = {}
    # Implement actual parsing logic based on criterion output format
    # This is a placeholder
    return results

def parse_go_output(output: str) -> Dict:
    """Parse Go benchmark output."""
    results = {}
    # Pattern: BenchmarkComparison/Size-1000/SequentialInsert/BPlusTree-10    1000    1234 ns/op
    pattern = r'BenchmarkComparison/Size-(\d+)/(\w+)/(\w+)-\d+\s+\d+\s+(\d+\.?\d*)\s*ns/op'
    
    for match in re.finditer(pattern, output):
        size = int(match.group(1))
        operation = match.group(2).lower()
        impl = match.group(3).lower()
        time_ns = float(match.group(4))
        time_us = time_ns / 1000  # Convert to microseconds
        
        # Initialize nested dicts if needed
        if operation not in results:
            results[operation] = {}
        if size not in results[operation]:
            results[operation][size] = {}
        
        results[operation][size][impl] = time_us
    
    return results

def parse_zig_output(output: str) -> Dict:
    """Parse Zig benchmark output."""
    results = {}
    # Implement actual parsing logic based on Zig output format
    # This is a placeholder
    return results

def create_comparison_table():
    """Create a detailed comparison table."""
    print("\n=== Cross-Language B+ Tree Performance Comparison ===")
    print("(All times in microseconds)")
    print("\n" + "="*100)
    
    operations = ["sequential_insert", "lookup", "iteration"]
    sizes = [100, 1000, 10000]
    
    for op in operations:
        print(f"\n{op.upper().replace('_', ' ')}:")
        print("-" * 100)
        
        # Header
        header = "Size".ljust(10)
        for lang in ["Rust", "Go", "Zig"]:
            header += f"{lang} B+Tree".rjust(15) + f"{lang} Native".rjust(15) + "Ratio".rjust(10)
        print(header)
        print("-" * 100)
        
        # Data rows
        for size in sizes:
            row = f"{size}".ljust(10)
            
            for lang in ["rust", "go", "zig"]:
                if lang in SAMPLE_RESULTS and op in SAMPLE_RESULTS[lang]:
                    data = SAMPLE_RESULTS[lang][op].get(size, {})
                    bplus = data.get("bplustree", 0)
                    native_key = {"rust": "btreemap", "go": "map", "zig": "hashmap"}[lang]
                    native = data.get(native_key, 0)
                    
                    if bplus and native:
                        ratio = bplus / native
                        row += f"{bplus:.2f}".rjust(15)
                        row += f"{native:.2f}".rjust(15)
                        row += f"{ratio:.2f}x".rjust(10)
                    else:
                        row += "N/A".rjust(15) + "N/A".rjust(15) + "N/A".rjust(10)
                else:
                    row += "N/A".rjust(15) + "N/A".rjust(15) + "N/A".rjust(10)
            
            print(row)
    
    print("\n" + "="*100)
    print("\nKEY INSIGHTS:")
    print("- B+ Trees generally slower for small datasets but scale better")
    print("- B+ Trees excel at iteration due to linked leaves")
    print("- Native structures (HashMap/Map) better for random access")
    print("- B+ Trees provide ordered iteration and range queries")
    print("- Zig shows best raw performance, Go most convenient, Rust most memory safe")

def create_visual_comparison():
    """Create visual bar charts if matplotlib is available."""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle("B+ Tree Cross-Language Performance Comparison", fontsize=16)
        
        operations = ["sequential_insert", "lookup", "iteration"]
        sizes = [100, 1000, 10000]
        
        for idx, op in enumerate(operations):
            ax = axes[idx // 2, idx % 2]
            
            # Prepare data
            rust_bplus = [SAMPLE_RESULTS["rust"][op][s]["bplustree"] for s in sizes]
            go_bplus = [SAMPLE_RESULTS["go"][op][s]["bplustree"] for s in sizes]
            zig_bplus = [SAMPLE_RESULTS["zig"][op][s]["bplustree"] for s in sizes]
            
            x = np.arange(len(sizes))
            width = 0.25
            
            # Create bars
            ax.bar(x - width, rust_bplus, width, label='Rust', color='#CE422B')
            ax.bar(x, go_bplus, width, label='Go', color='#00ADD8')
            ax.bar(x + width, zig_bplus, width, label='Zig', color='#F7A41D')
            
            ax.set_xlabel('Dataset Size')
            ax.set_ylabel('Time (μs)')
            ax.set_title(f'{op.replace("_", " ").title()}')
            ax.set_xticks(x)
            ax.set_xticklabels(sizes)
            ax.legend()
            ax.set_yscale('log')
        
        # Remove empty subplot
        fig.delaxes(axes[1, 1])
        
        plt.tight_layout()
        plt.savefig('bplustree_comparison.png', dpi=300, bbox_inches='tight')
        print("\nVisualization saved as 'bplustree_comparison.png'")
        
    except ImportError:
        print("\nNote: Install matplotlib for visual charts: pip install matplotlib")

if __name__ == "__main__":
    print("B+ Tree Cross-Language Benchmark Analysis")
    print("=========================================")
    
    # Create comparison table
    create_comparison_table()
    
    # Try to create visual comparison
    create_visual_comparison()
    
    print("\nTo use with actual benchmark data:")
    print("1. Run benchmarks in each language:")
    print("   - Rust: cargo bench")
    print("   - Go: go test -bench=Comparison ./benchmark")
    print("   - Zig: zig build compare")
    print("2. Pipe output to this script or modify to read from files")
    print("3. Update parsing functions to match actual output formats")