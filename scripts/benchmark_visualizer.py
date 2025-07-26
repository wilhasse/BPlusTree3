#!/usr/bin/env python3
"""
Benchmark result visualizer for B+ Tree implementations.
Creates charts and graphs from benchmark data.
"""

import json
import sys
import os
from typing import Dict, List, Optional

def create_charts(results_file: str = "benchmark_results.json"):
    """Create visual charts from benchmark results."""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("matplotlib not installed. Install with: pip install matplotlib")
        return False
    
    # Load results
    try:
        with open(results_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Results file not found: {results_file}")
        print("Run './run_all_benchmarks.py' first to generate results.")
        return False
    
    # Create figure with subplots
    operations = ['sequentialinsert', 'lookup', 'iteration']
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('B+ Tree Cross-Language Performance Comparison', fontsize=16)
    
    # Color scheme for languages
    colors = {
        'rust': '#CE422B',
        'go': '#00ADD8', 
        'zig': '#F7A41D'
    }
    
    # Process each operation
    for idx, op in enumerate(operations):
        ax = axes[idx // 2, idx % 2]
        
        # Collect data for this operation
        sizes = set()
        for lang in ['rust', 'go', 'zig']:
            if lang in data and op in data[lang]:
                sizes.update(data[lang][op].keys())
        
        if not sizes:
            continue
        
        sizes = sorted(list(sizes))
        x = np.arange(len(sizes))
        width = 0.25
        
        # Plot bars for each language
        for i, lang in enumerate(['rust', 'go', 'zig']):
            if lang not in data or op not in data[lang]:
                continue
            
            values = []
            for size in sizes:
                if size in data[lang][op] and 'bplustree' in data[lang][op][size]:
                    values.append(data[lang][op][size]['bplustree'])
                else:
                    values.append(0)
            
            if values:
                ax.bar(x + (i-1)*width, values, width, label=lang.title(), color=colors[lang])
        
        ax.set_xlabel('Dataset Size')
        ax.set_ylabel('Time (μs)')
        ax.set_title(f'{op.replace("_", " ").title()}')
        ax.set_xticks(x)
        ax.set_xticklabels(sizes)
        ax.legend()
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3)
    
    # Create ratio comparison in the fourth subplot
    ax = axes[1, 1]
    
    # Calculate average ratios across all operations
    lang_ratios = {}
    for lang in ['rust', 'go', 'zig']:
        if lang not in data:
            continue
        
        ratios = []
        native_key = {'rust': 'btreemap', 'go': 'map', 'zig': 'hashmap'}[lang]
        
        for op in data[lang]:
            for size in data[lang][op]:
                if 'bplustree' in data[lang][op][size] and native_key in data[lang][op][size]:
                    bplus = data[lang][op][size]['bplustree']
                    native = data[lang][op][size][native_key]
                    if native > 0:
                        ratios.append(bplus / native)
        
        if ratios:
            lang_ratios[lang] = {
                'mean': np.mean(ratios),
                'min': np.min(ratios),
                'max': np.max(ratios)
            }
    
    # Plot ratio comparison
    if lang_ratios:
        langs = list(lang_ratios.keys())
        means = [lang_ratios[l]['mean'] for l in langs]
        mins = [lang_ratios[l]['min'] for l in langs]
        maxs = [lang_ratios[l]['max'] for l in langs]
        
        x = np.arange(len(langs))
        ax.bar(x, means, color=[colors[l] for l in langs])
        ax.errorbar(x, means, yerr=[np.array(means) - np.array(mins), np.array(maxs) - np.array(means)], 
                   fmt='none', color='black', capsize=5)
        
        ax.axhline(y=1.0, color='red', linestyle='--', alpha=0.5, label='Equal performance')
        ax.set_xlabel('Language')
        ax.set_ylabel('B+ Tree / Native Ratio')
        ax.set_title('Average Performance Ratio\n(B+ Tree vs Native Structure)')
        ax.set_xticks(x)
        ax.set_xticklabels([l.title() for l in langs])
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_file = 'benchmark_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Chart saved: {output_file}")
    
    # Create additional detailed charts
    create_operation_comparison_chart(data)
    create_scalability_chart(data)
    
    return True

def create_operation_comparison_chart(data: Dict):
    """Create a chart comparing different operations."""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        return
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    operations = ['sequentialinsert', 'lookup', 'iteration']
    languages = ['rust', 'go', 'zig']
    
    # Use 10000 size as reference
    reference_size = 10000
    
    # Prepare data
    op_data = {op: [] for op in operations}
    
    for op in operations:
        for lang in languages:
            if (lang in data and op in data[lang] and 
                reference_size in data[lang][op] and 
                'bplustree' in data[lang][op][reference_size]):
                op_data[op].append(data[lang][op][reference_size]['bplustree'])
            else:
                op_data[op].append(0)
    
    # Create grouped bar chart
    x = np.arange(len(operations))
    width = 0.25
    
    for i, lang in enumerate(languages):
        values = [op_data[op][i] for op in operations]
        ax.bar(x + (i-1)*width, values, width, label=lang.title())
    
    ax.set_xlabel('Operation Type')
    ax.set_ylabel('Time (μs) - Log Scale')
    ax.set_title(f'Operation Performance Comparison (Size={reference_size})')
    ax.set_xticks(x)
    ax.set_xticklabels([op.replace('_', ' ').title() for op in operations])
    ax.legend()
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('operation_comparison.png', dpi=300, bbox_inches='tight')
    print("Chart saved: operation_comparison.png")

def create_scalability_chart(data: Dict):
    """Create a chart showing scalability characteristics."""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        return
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('B+ Tree Scalability Analysis', fontsize=16)
    
    languages = ['rust', 'go', 'zig']
    colors = {'rust': '#CE422B', 'go': '#00ADD8', 'zig': '#F7A41D'}
    
    for lang_idx, lang in enumerate(languages):
        ax = axes[lang_idx]
        
        if lang not in data:
            continue
        
        # Plot lines for each operation
        for op in ['sequentialinsert', 'lookup', 'iteration']:
            if op not in data[lang]:
                continue
            
            sizes = []
            times = []
            
            for size in sorted(data[lang][op].keys()):
                if 'bplustree' in data[lang][op][size]:
                    sizes.append(size)
                    times.append(data[lang][op][size]['bplustree'])
            
            if sizes and times:
                ax.plot(sizes, times, 'o-', label=op.replace('_', ' ').title(), linewidth=2, markersize=8)
        
        ax.set_xlabel('Dataset Size')
        ax.set_ylabel('Time (μs)')
        ax.set_title(f'{lang.title()} B+ Tree Scalability')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('scalability_analysis.png', dpi=300, bbox_inches='tight')
    print("Chart saved: scalability_analysis.png")

def main():
    """Generate visualizations from benchmark results."""
    if len(sys.argv) > 1:
        results_file = sys.argv[1]
    else:
        results_file = "benchmark_results.json"
    
    print("Generating benchmark visualizations...")
    create_charts(results_file)

if __name__ == "__main__":
    main()