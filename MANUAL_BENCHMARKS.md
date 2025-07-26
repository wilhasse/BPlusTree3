# Manual Benchmark Guide

This guide shows you how to run benchmarks for each language implementation manually, without using the automated runner.

## 🦀 Rust Benchmarks

### Prerequisites
Install Rust if not already installed:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
```

### Run Rust Benchmarks
```bash
cd rust/

# Run the simple comparison benchmark (fast)
cargo bench --bench simple_comparison

# Run all benchmarks (slower, more comprehensive)
cargo bench

# Run specific benchmark with custom duration
cargo bench --bench simple_comparison -- --sample-size 10

# Run with release optimizations (recommended)
cargo bench --release
```

### Rust Benchmark Output Format
```
SequentialInsert/BPlusTree/100  time: [5.23 µs 5.47 µs 5.71 µs]
SequentialInsert/BTreeMap/100   time: [2.89 µs 3.12 µs 3.35 µs]
```

---

## 🐹 Go Benchmarks

### Prerequisites
Install Go if not already installed:
```bash
# On Ubuntu/Debian
sudo apt update && sudo apt install golang-go

# Or download from https://golang.org/dl/
wget https://go.dev/dl/go1.21.0.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
```

### Run Go Benchmarks
```bash
cd go/

# Run comparison benchmarks
go test -bench=Comparison ./benchmark

# Run with longer duration for more accuracy
go test -bench=Comparison ./benchmark -benchtime=10s

# Run all benchmarks
go test -bench=. ./benchmark ./test

# Run with CPU profiling
go test -bench=Comparison ./benchmark -cpuprofile=cpu.prof

# Run with memory profiling  
go test -bench=Comparison ./benchmark -memprofile=mem.prof
```

### Go Benchmark Output Format
```
BenchmarkComparison/Size-100/SequentialInsert/BPlusTree-8    100000    12345 ns/op
BenchmarkComparison/Size-100/SequentialInsert/Map-8         500000     2345 ns/op
```

---

## ⚡ Zig Benchmarks

### Prerequisites
Install Zig if not already installed:
```bash
# Download latest Zig
wget https://ziglang.org/download/0.11.0/zig-linux-x86_64-0.11.0.tar.xz
tar -xf zig-linux-x86_64-0.11.0.tar.xz
sudo mv zig-linux-x86_64-0.11.0 /usr/local/zig
export PATH=$PATH:/usr/local/zig

# Or install via package manager
sudo snap install zig --classic --beta
```

### Run Zig Benchmarks
```bash
cd zig/

# Run comparison benchmark
zig build compare

# Run performance benchmark
zig build benchmark

# Run with release optimizations
zig build compare -Doptimize=ReleaseFast

# Run specific benchmark
zig build compare -- --filter="Sequential"
```

### Zig Benchmark Output Format
```
Sequential Insertion:
  B+ Tree    100 ops in  3.99e-2ms |   3e6 ops/sec |  3.99e2 ns/op
  HashMap    100 ops in  2.55e-2ms |   4e6 ops/sec |  2.55e2 ns/op
```

---

## 📊 Collecting and Comparing Results

### Manual Data Collection

#### 1. Run Each Language
```bash
# Rust (save output)
cd rust && cargo bench --bench simple_comparison > ../rust_results.txt 2>&1

# Go (save output)  
cd go && go test -bench=Comparison ./benchmark > ../go_results.txt 2>&1

# Zig (save output)
cd zig && zig build compare > ../zig_results.txt 2>&1
```

#### 2. Parse Results Manually
Look for timing data in each output:

**Rust**: Look for `time: [X.XX µs Y.YY µs Z.ZZ µs]`
**Go**: Look for `XXXX ns/op`  
**Zig**: Look for `X.XXeY ns/op`

#### 3. Create Comparison Table
```bash
# Use the analysis script on saved results
python scripts/cross_language_comparison.py rust_results.txt go_results.txt zig_results.txt
```

### Automated Collection (if languages are installed)
```bash
# Run the full automated suite
./scripts/run_all_benchmarks.py

# Or run individual languages
./scripts/run_all_benchmarks.py --rust-only
./scripts/run_all_benchmarks.py --go-only  
./scripts/run_all_benchmarks.py --zig-only
```

---

## 🔧 Troubleshooting

### Common Issues

#### Rust Issues
```bash
# If cargo not found
source ~/.cargo/env

# If compilation fails
cargo clean && cargo build

# If benchmark doesn't exist
cargo bench --list
```

#### Go Issues
```bash
# If go command not found
export PATH=$PATH:/usr/local/go/bin

# If module issues
go mod tidy
go mod download

# Check Go version
go version
```

#### Zig Issues
```bash
# If zig not found
export PATH=$PATH:/usr/local/zig

# Check Zig version
zig version

# Clean build cache
rm -rf .zig-cache
```

### Performance Considerations

#### For Accurate Results
- Close other applications
- Run multiple times and average results
- Use longer benchmark durations (`-benchtime=30s` for Go)
- Use release builds (`cargo bench --release`, `-Doptimize=ReleaseFast`)

#### System Configuration
```bash
# Disable CPU frequency scaling for consistent results
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Check CPU info
lscpu

# Check memory
free -h
```

---

## 📈 Understanding Results

### Key Metrics

#### Time per Operation
- **Lower is better**
- Usually measured in nanoseconds (ns) or microseconds (µs)
- 1 µs = 1,000 ns

#### Operations per Second  
- **Higher is better**
- Inverse of time per operation
- Good for understanding throughput

#### Comparative Analysis
- **Ratio < 1.0**: B+ tree is faster
- **Ratio > 1.0**: Native structure is faster
- **Ratio ≈ 1.0**: Similar performance

### Language-Specific Notes

#### Rust Results
- Look for both average time and confidence intervals
- Criterion provides statistical analysis
- Range shown as `[min avg max]`

#### Go Results  
- Results show nanoseconds per operation
- Number before `ns/op` is the timing
- Higher iteration count means more reliable results

#### Zig Results
- Uses scientific notation (e.g., `3.99e2` = 399)
- Shows operations per second and time per operation
- Very precise timing measurements

---

## 🎯 Quick Start Commands

If you just want to run one benchmark to test:

```bash
# Quick Rust test (if installed)
cd rust && cargo bench --bench simple_comparison -- --sample-size 10

# Quick Go test (if installed)  
cd go && go test -bench=Comparison/Size-100 ./benchmark -benchtime=1s

# Quick Zig test
cd zig && zig build compare
```

These commands will run smaller, faster benchmarks to verify everything works before running the full test suite.