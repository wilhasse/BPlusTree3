# Complete Cross-Language Benchmark Guide

🎯 **Updated benchmark runner now supports automatic Rust installation and standardized metrics across all three languages!**

## 🚀 Quick Start - All Three Languages

### Automatic Installation & Benchmarking
```bash
# Install missing languages and run all benchmarks
./scripts/run_all_benchmarks.py --auto-install -v

# This will:
# 1. Check for Rust, Go, Zig
# 2. Install Rust automatically if missing
# 3. Run standardized benchmarks for all available languages
# 4. Generate a comprehensive report
```

### Manual Step-by-Step
```bash
# 1. Check what's available
./scripts/check_and_run.py

# 2. Install Rust manually (if needed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# 3. Run complete benchmark suite
./scripts/run_all_benchmarks.py -v

# 4. View results
cat benchmark_report.md
```

## 📊 Standardized Metrics

All three languages now use the same benchmark format:

### Operations Tested
- **Sequential Insert**: Insert keys 0, 1, 2, ... N
- **Random Insert**: Insert keys in random order
- **Lookup**: Random key lookups
- **Iteration**: Full tree traversal
- **Range Query**: Subset retrieval (B+ trees only)

### Data Sizes
- 100, 1,000, 10,000, 100,000 elements

### Output Format
All results normalized to **microseconds (µs)** for easy comparison.

## 🔧 Individual Language Commands

### Rust Benchmarks
```bash
cd rust
cargo bench --bench simple_comparison
```

### Go Benchmarks  
```bash
cd go
go test -bench=Comparison ./benchmark
```

### Zig Benchmarks
```bash
cd zig
zig build compare
```

## 🎛️ Advanced Options

### Automated Runner Options
```bash
# Verbose output with installation
./scripts/run_all_benchmarks.py --auto-install -v

# Run only specific languages
./scripts/run_all_benchmarks.py --rust-only --auto-install
./scripts/run_all_benchmarks.py --go-only
./scripts/run_all_benchmarks.py --zig-only

# Custom output file
./scripts/run_all_benchmarks.py -o my_results.md
```

### Performance Tuning
```bash
# Longer benchmark runs for accuracy
cd go && go test -bench=Comparison ./benchmark -benchtime=10s

# Release mode for Rust
cd rust && cargo bench --release

# Optimized Zig
cd zig && zig build compare -Doptimize=ReleaseFast
```

## 📈 Expected Results

Based on our analysis, you should see:

### Performance Hierarchy (B+ Trees)
1. **🥇 Zig**: 0.001-0.4 µs (blazingly fast)
2. **🥈 Go**: 1.3-50 µs (good balance)  
3. **🥉 Rust**: 2.5-80 µs (surprisingly slower)

### B+ Tree vs Native Structure
- **Iteration**: B+ trees 2-5x faster in all languages
- **Lookups**: Native structures 4-450,000x faster
- **Range Queries**: Only B+ trees support this efficiently

### Language Characteristics
- **Zig**: Extreme performance, manual control
- **Go**: Great productivity/performance balance  
- **Rust**: Memory safety with good performance

## 🛠️ Troubleshooting

### Rust Installation Issues
```bash
# Test installation
./scripts/test_rust_install.py

# Manual installation
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Fix PATH issues
echo 'source ~/.cargo/env' >> ~/.bashrc
```

### Go PATH Issues
```bash
# Check Go location
which go
go version

# Add to PATH if needed
export PATH=$PATH:/usr/local/go/bin
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
```

### Zig Issues
```bash
# Check Zig
zig version

# Clean build cache
cd zig && rm -rf .zig-cache
```

### Performance Inconsistency
```bash
# Close other applications
# Run benchmarks multiple times
./scripts/run_all_benchmarks.py -v  # Run 3 times, compare

# Use dedicated timing
go test -bench=Comparison/Size-1000 ./benchmark -benchtime=30s
```

## 📋 Files Generated

### Benchmark Reports
- `benchmark_report.md` - Main comparison report
- `benchmark_results.json` - Raw timing data
- `CROSS_LANGUAGE_ANALYSIS.md` - Detailed analysis

### Visualization (Optional)
```bash
# Generate charts (requires matplotlib)
pip install matplotlib
./scripts/benchmark_visualizer.py

# Creates:
# - benchmark_comparison.png
# - operation_comparison.png  
# - scalability_analysis.png
```

## 🎯 Use Case Recommendations

### Choose Zig When:
- Maximum performance is critical
- Embedded/systems programming
- Manual memory management is acceptable

### Choose Go When:
- Development productivity matters
- Building web services/APIs
- Good performance + simplicity

### Choose Rust When:  
- Memory safety without GC
- Concurrent systems
- Systems programming with safety guarantees

### Use B+ Trees When:
- Ordered iteration required
- Range queries needed
- Sequential access patterns
- Database/file system components

### Use Native Structures When:
- Pure key-value lookups
- Random access patterns
- Small datasets
- Simplicity preferred

## 🚀 Full Workflow Example

```bash
# 1. Clone/navigate to project
cd BPlusTree3

# 2. Run complete benchmark suite with auto-install
./scripts/run_all_benchmarks.py --auto-install -v

# 3. Check results
cat benchmark_report.md

# 4. Generate visualizations
pip install matplotlib
./scripts/benchmark_visualizer.py

# 5. Review comprehensive analysis
cat CROSS_LANGUAGE_ANALYSIS.md
```

This gives you a complete, automated system for comparing B+ tree performance across Rust, Go, and Zig with standardized metrics and automatic setup! 🎉