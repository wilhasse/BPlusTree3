#!/usr/bin/env python3
"""
Check which languages are available and run their benchmarks.
"""

import subprocess
import os

def check_language_availability():
    """Check which languages are installed and working."""
    languages = {}
    
    # Check Rust
    try:
        result = subprocess.run(['cargo', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            languages['rust'] = f"✅ {result.stdout.strip()}"
        else:
            languages['rust'] = "❌ Cargo found but not working"
    except FileNotFoundError:
        languages['rust'] = "❌ Rust/Cargo not installed"
    
    # Check Go
    try:
        result = subprocess.run(['go', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            languages['go'] = f"✅ {result.stdout.strip()}"
        else:
            languages['go'] = "❌ Go found but not working"
    except FileNotFoundError:
        languages['go'] = "❌ Go not installed"
    
    # Check Zig
    try:
        result = subprocess.run(['zig', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            languages['zig'] = f"✅ Zig {result.stdout.strip()}"
        else:
            languages['zig'] = "❌ Zig found but not working"
    except FileNotFoundError:
        languages['zig'] = "❌ Zig not installed"
    
    return languages

def run_available_benchmarks():
    """Run benchmarks for available languages."""
    print("🔍 Checking language availability...\n")
    
    languages = check_language_availability()
    
    for lang, status in languages.items():
        print(f"{lang.title():8} {status}")
    
    print("\n" + "="*50)
    
    available = [lang for lang, status in languages.items() if "✅" in status]
    
    if not available:
        print("❌ No languages available for benchmarking!")
        print("\n📖 See MANUAL_BENCHMARKS.md for installation instructions")
        return
    
    print(f"🚀 Running benchmarks for: {', '.join(available)}")
    print("="*50)
    
    for lang in available:
        print(f"\n🔄 Running {lang.title()} benchmarks...")
        
        try:
            if lang == 'rust':
                run_rust_benchmark()
            elif lang == 'go':
                run_go_benchmark()
            elif lang == 'zig':
                run_zig_benchmark()
        except Exception as e:
            print(f"❌ Error running {lang} benchmark: {e}")

def run_rust_benchmark():
    """Run Rust benchmark."""
    os.chdir('rust')
    try:
        # Try the simple benchmark first
        result = subprocess.run(['cargo', 'bench', '--bench', 'simple_comparison', '--', '--sample-size', '10'], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ Rust benchmark completed")
            print("Sample output:")
            lines = result.stdout.split('\n')
            for line in lines[-10:]:
                if 'time:' in line and ('BPlusTree' in line or 'BTreeMap' in line):
                    print(f"  {line.strip()}")
        else:
            print(f"❌ Rust benchmark failed: {result.stderr}")
    finally:
        os.chdir('..')

def run_go_benchmark():
    """Run Go benchmark."""
    os.chdir('go')
    try:
        result = subprocess.run(['go', 'test', '-bench=Comparison/Size-100', './benchmark', '-benchtime=1s'], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ Go benchmark completed")
            print("Sample output:")
            lines = result.stdout.split('\n')
            for line in lines:
                if 'BenchmarkComparison' in line and 'ns/op' in line:
                    print(f"  {line.strip()}")
                    break
        else:
            print(f"❌ Go benchmark failed: {result.stderr}")
    finally:
        os.chdir('..')

def run_zig_benchmark():
    """Run Zig benchmark."""
    os.chdir('zig')
    try:
        result = subprocess.run(['zig', 'build', 'compare'], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ Zig benchmark completed")
            print("Sample output:")
            lines = result.stderr.split('\n')  # Zig outputs to stderr
            for line in lines:
                if 'B+ Tree' in line and 'ns/op' in line:
                    print(f"  {line.strip()}")
                    break
        else:
            print(f"❌ Zig benchmark failed: {result.stderr}")
    finally:
        os.chdir('..')

def main():
    """Main function."""
    print("B+ Tree Language Availability Checker")
    print("====================================\n")
    
    run_available_benchmarks()
    
    print(f"\n📖 For detailed benchmark instructions, see:")
    print("   - MANUAL_BENCHMARKS.md")
    print("   - scripts/run_all_benchmarks.py (full automation)")

if __name__ == "__main__":
    main()