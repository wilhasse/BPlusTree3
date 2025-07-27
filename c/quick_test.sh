#!/bin/bash

# Quick Test Runner for C B+ Tree Implementation

echo "=== C B+ Tree Quick Test Runner ==="
echo

# Ensure we're in the right directory
if [ ! -f "src/bplustree.c" ]; then
    echo "❌ Error: Run from c/ directory"
    exit 1
fi

mkdir -p build

# Test files
tests=(
    "test_enhanced_error_handling"
    "test_tree_invariant_validation"
    "test_adversarial_edge_cases"
    "test_comprehensive_memory_safety"
    "test_bug_reproduction"
    "test_critical_bug"
    "test_concurrent_modification"
    "test_fuzz"
)

passed=0
total=0

for test in "${tests[@]}"; do
    echo -n "Testing $test... "
    
    # Compile quietly
    if gcc -Wall -Wextra -std=c99 -O2 -o "build/$test" "tests/$test.c" src/bplustree.c 2>/dev/null; then
        # Run quietly
        if "./build/$test" >/dev/null 2>&1; then
            echo "✅ PASSED"
            ((passed++))
        else
            echo "❌ FAILED"
        fi
    else
        echo "❌ COMPILE ERROR"
    fi
    
    ((total++))
done

echo
echo "Results: $passed/$total tests passed"

if [ $passed -eq $total ]; then
    echo "🎉 All tests passed!"
    exit 0
else
    echo "❌ Some tests failed"
    exit 1
fi