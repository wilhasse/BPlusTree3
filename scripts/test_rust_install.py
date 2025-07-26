#!/usr/bin/env python3
"""
Test Rust installation and benchmark compilation.
"""

import subprocess
import os

def test_rust_installation():
    """Test if Rust can be installed and benchmarks work."""
    print("🔧 Testing Rust Installation and Benchmark Compilation")
    print("="*60)
    
    # Test 1: Check if Rust is already installed
    print("\n1️⃣ Checking existing Rust installation...")
    try:
        result = subprocess.run(['cargo', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Rust already installed: {result.stdout.strip()}")
            rust_available = True
        else:
            print("❌ Rust found but not working")
            rust_available = False
    except FileNotFoundError:
        print("❌ Rust not installed")
        rust_available = False
    
    # Test 2: Try to compile the benchmark
    if rust_available:
        print("\n2️⃣ Testing benchmark compilation...")
        try:
            os.chdir('rust')
            result = subprocess.run(['cargo', 'check', '--benches'], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print("✅ Rust benchmarks compile successfully")
                
                # Test 3: Try a quick benchmark run
                print("\n3️⃣ Testing quick benchmark run...")
                result = subprocess.run([
                    'cargo', 'bench', '--bench', 'simple_comparison', 
                    '--', '--sample-size', '5'
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print("✅ Rust benchmarks run successfully")
                    print("\nSample output:")
                    lines = result.stdout.split('\n')
                    for line in lines[-10:]:
                        if 'time:' in line and ('BPlusTree' in line or 'BTreeMap' in line):
                            print(f"  {line.strip()}")
                else:
                    print(f"❌ Benchmark run failed: {result.stderr}")
            else:
                print(f"❌ Compilation failed: {result.stderr}")
                print("\n🔧 This indicates the simple_comparison.rs benchmark needs fixing")
                
        except Exception as e:
            print(f"❌ Error testing benchmarks: {e}")
        finally:
            os.chdir('..')
    
    # Test 4: Show what the automated installer would do
    print("\n4️⃣ Automated Installation Test")
    if not rust_available:
        print("The automated installer would run:")
        print("  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y")
        print("  source ~/.cargo/env")
        print("\nTo test manually:")
        print("  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh")
        print("  source ~/.cargo/env")
        print("  cd rust && cargo bench --bench simple_comparison")
    else:
        print("✅ Rust already available - automated installer would skip")
    
    print(f"\n{'='*60}")
    print("🎯 Summary:")
    if rust_available:
        print("✅ Rust is ready for benchmarking")
        print("✅ You can run: ./scripts/run_all_benchmarks.py")
    else:
        print("🔧 Rust needs installation")
        print("🚀 Run: ./scripts/run_all_benchmarks.py --auto-install")
        print("📖 Or install manually and then run benchmarks")

if __name__ == "__main__":
    test_rust_installation()