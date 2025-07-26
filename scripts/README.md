# B+ Tree Benchmark Scripts

This directory contains scripts for running and analyzing benchmarks across all B+ Tree implementations.

## Scripts

### run_all_benchmarks.py
Automated benchmark runner that:
- Runs benchmarks for Rust, Go, and Zig implementations
- Collects and parses results from each language
- Generates a comprehensive markdown report
- Saves raw results as JSON for further analysis

**Usage:**
```bash
# Run all benchmarks and generate report
./run_all_benchmarks.py

# Run with verbose output
./run_all_benchmarks.py -v

# Run only specific language benchmarks
./run_all_benchmarks.py --rust-only
./run_all_benchmarks.py --go-only
./run_all_benchmarks.py --zig-only

# Specify output file
./run_all_benchmarks.py -o my_report.md
```

**Output Files:**
- `benchmark_report.md` - Comprehensive markdown report with tables and analysis
- `benchmark_results.json` - Raw benchmark data for further processing

### benchmark_visualizer.py
Creates visual charts from benchmark results:
- Performance comparison bar charts
- Scalability analysis graphs
- Operation-specific comparisons
- Language performance ratios

**Usage:**
```bash
# Generate charts from default results file
./benchmark_visualizer.py

# Use specific results file
./benchmark_visualizer.py my_results.json
```

**Requirements:**
```bash
pip install matplotlib numpy
```

**Output Files:**
- `benchmark_comparison.png` - Main comparison chart
- `operation_comparison.png` - Operation-specific performance
- `scalability_analysis.png` - Scalability characteristics

### analyze_benchmarks.py
Manual analysis script for comparing specific benchmark outputs.
Useful for quick comparisons or when automatic parsing fails.

### cross_language_comparison.py
Standalone comparison script with sample data.
Demonstrates the comparison methodology.

## Benchmark Process

1. **Preparation**: Ensure all languages are installed:
   ```bash
   # Check installations
   cargo --version  # Rust
   go version      # Go
   zig version     # Zig
   ```

2. **Run Benchmarks**: Execute the automated runner:
   ```bash
   cd /path/to/BPlusTree3
   ./scripts/run_all_benchmarks.py -v
   ```

3. **Generate Visualizations** (optional):
   ```bash
   # Install matplotlib if needed
   pip install matplotlib
   
   # Generate charts
   ./scripts/benchmark_visualizer.py
   ```

4. **Review Results**:
   - Open `benchmark_report.md` for detailed analysis
   - View PNG files for visual comparisons
   - Use `benchmark_results.json` for custom analysis

## Benchmark Metrics

The scripts measure and compare:
- **Sequential Insert**: Performance of inserting keys in order
- **Random Insert**: Performance of inserting keys randomly
- **Lookup**: Time to find existing keys
- **Iteration**: Time to traverse all elements
- **Range Query**: Time to retrieve a subset of keys (B+ Tree only)

## Interpreting Results

- **Ratio > 1.0**: B+ Tree is slower than native structure
- **Ratio < 1.0**: B+ Tree is faster than native structure
- **Ratio ≈ 1.0**: Similar performance

### When B+ Trees Excel:
- Ordered iteration (keys maintained in sorted order)
- Range queries (efficient subset retrieval)
- Predictable performance (consistent O(log n) operations)

### When Native Structures Excel:
- Random access patterns (O(1) hash maps)
- Small datasets (lower overhead)
- Simple key-value lookups

## Troubleshooting

### "Language not found" errors
Install the missing language:
- Rust: https://rustup.rs/
- Go: https://golang.org/dl/
- Zig: https://ziglang.org/download/

### Parsing errors
- Check that benchmark output format hasn't changed
- Use `-v` flag for verbose output to see raw results
- Manually inspect language-specific benchmark output

### Performance variations
- Close other applications to reduce system load
- Run benchmarks multiple times for consistency
- Use dedicated benchmark machine for best results

## Customization

### Adding New Benchmarks
1. Add benchmark to language implementation
2. Update parsing logic in `run_all_benchmarks.py`
3. Add visualization in `benchmark_visualizer.py`

### Changing Benchmark Parameters
Edit the benchmark files directly:
- Rust: `rust/benches/comparison.rs`
- Go: `go/benchmark/comparison_test.go`
- Zig: `zig/benchmarks/comparison.zig`