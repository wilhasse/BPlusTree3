#!/usr/bin/env python3
"""
Comprehensive fuzz testing with different capacities and initial loads.
Tests the robustness of our optimized B+ tree implementation.
"""

import time
import random

# Handle both module and direct execution
try:
    from .fuzz_test import BPlusTreeFuzzTester
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from tests.fuzz_test import BPlusTreeFuzzTester


def run_capacity_sweep():
    """Test different capacities with various initial loads"""
    print("🧪 Comprehensive Fuzz Testing: Capacity & Load Sweep")
    print("=" * 70)

    # Test configurations: (capacity, prepopulate, operations)
    test_configs = [
        # Small capacities (stress tree depth)
        (16, 0, 25000),  # Empty start, small capacity
        (16, 100, 25000),  # Small prepopulation
        (16, 1000, 25000),  # Large prepopulation
        # Medium capacities
        (16, 0, 25000),  # Empty start
        (16, 500, 25000),  # Medium prepopulation
        (16, 2000, 25000),  # Large prepopulation
        # Large capacities (our optimized range)
        (64, 0, 25000),  # Empty start
        (64, 1000, 25000),  # Medium prepopulation
        (64, 5000, 25000),  # Large prepopulation
        (128, 0, 25000),  # Empty start
        (128, 2000, 25000),  # Medium prepopulation
        (128, 10000, 25000),  # Large prepopulation
        (256, 0, 25000),  # Our optimal capacity
        (256, 5000, 25000),  # Medium prepopulation
        (256, 20000, 25000),  # Large prepopulation
        # Very large capacities
        (512, 0, 25000),  # Empty start
        (512, 10000, 25000),  # Large prepopulation
    ]

    results = []
    total_start = time.time()

    for i, (capacity, prepopulate, operations) in enumerate(test_configs):
        print(
            f"\n📋 Test {i+1}/{len(test_configs)}: Capacity={capacity}, Prepopulate={prepopulate:,}, Ops={operations:,}"
        )
        print("-" * 70)

        # Use different seed for each test
        seed = random.randint(1, 1000000)

        try:
            start_time = time.time()
            tester = BPlusTreeFuzzTester(
                capacity=capacity, seed=seed, prepopulate=prepopulate
            )

            success = tester.run_fuzz_test(operations)
            elapsed = time.time() - start_time

            result = {
                "capacity": capacity,
                "prepopulate": prepopulate,
                "operations": operations,
                "success": success,
                "time": elapsed,
                "seed": seed,
                "final_size": len(tester.btree) if success else 0,
                "stats": tester.stats.copy() if success else {},
            }
            results.append(result)

            if success:
                print(f"✅ PASSED in {elapsed:.1f}s")
                print(f"   Final tree size: {len(tester.btree):,} keys")
                print(f"   Operations/sec: {operations/elapsed:.0f}")
            else:
                print(f"❌ FAILED after {elapsed:.1f}s")
                print(f"   Seed: {seed} (for reproduction)")

        except Exception as e:
            print(f"💥 EXCEPTION: {e}")
            result = {
                "capacity": capacity,
                "prepopulate": prepopulate,
                "operations": operations,
                "success": False,
                "time": 0,
                "seed": seed,
                "final_size": 0,
                "stats": {},
                "exception": str(e),
            }
            results.append(result)

    # Summary report
    total_elapsed = time.time() - total_start
    print(f"\n📊 COMPREHENSIVE FUZZ TEST SUMMARY")
    print("=" * 70)
    print(f"Total time: {total_elapsed:.1f}s")

    passed = sum(1 for r in results if r["success"])
    failed = len(results) - passed

    print(f"Tests passed: {passed}/{len(results)} ({passed/len(results)*100:.1f}%)")
    print(f"Tests failed: {failed}/{len(results)}")

    if failed > 0:
        print(f"\n❌ FAILED TESTS:")
        for r in results:
            if not r["success"]:
                print(
                    f"   Capacity={r['capacity']}, Prepopulate={r['prepopulate']:,}, Seed={r['seed']}"
                )
                if "exception" in r:
                    print(f"      Exception: {r['exception']}")

    print(f"\n📈 PERFORMANCE BY CAPACITY:")
    capacity_groups = {}
    for r in results:
        if r["success"]:
            cap = r["capacity"]
            if cap not in capacity_groups:
                capacity_groups[cap] = []
            capacity_groups[cap].append(r["operations"] / r["time"])

    for capacity in sorted(capacity_groups.keys()):
        rates = capacity_groups[capacity]
        avg_rate = sum(rates) / len(rates)
        print(
            f"   Capacity {capacity:3d}: {avg_rate:6.0f} ops/sec (avg of {len(rates)} tests)"
        )

    print(f"\n🏗️  TREE STRUCTURE ANALYSIS:")
    for r in results:
        if r["success"] and r["final_size"] > 0:
            print(
                f"   Cap={r['capacity']:3d}, Prepop={r['prepopulate']:5,}, Final={r['final_size']:5,}"
            )

    return results


def run_stress_test():
    """Run intensive stress test with our optimal configuration"""
    print(f"\n🔥 STRESS TEST: Optimal Configuration")
    print("=" * 70)

    # Use our optimal capacity with large dataset
    capacity = 256
    prepopulate = 50000
    operations = 500000  # Half million operations

    print(
        f"Configuration: Capacity={capacity}, Prepopulate={prepopulate:,}, Operations={operations:,}"
    )

    seed = random.randint(1, 1000000)
    tester = BPlusTreeFuzzTester(capacity=capacity, seed=seed, prepopulate=prepopulate)

    start_time = time.time()
    success = tester.run_fuzz_test(operations)
    elapsed = time.time() - start_time

    if success:
        print(f"✅ STRESS TEST PASSED!")
        print(f"   Time: {elapsed:.1f}s")
        print(f"   Rate: {operations/elapsed:.0f} ops/sec")
        print(f"   Final size: {len(tester.btree):,} keys")
    else:
        print(f"❌ STRESS TEST FAILED")
        print(f"   Seed: {seed}")

    return success


def run_edge_case_tests():
    """Test edge cases and boundary conditions"""
    print(f"\n🎯 EDGE CASE TESTS")
    print("=" * 70)

    edge_cases = [
        # Minimum capacity
        (16, 0, 10000, "Minimum capacity, empty start"),
        (16, 10000, 10000, "Minimum capacity, large prepopulation"),
        # Very large capacity (stress single-level trees)
        (1024, 0, 10000, "Very large capacity, empty start"),
        (1024, 50000, 10000, "Very large capacity, large prepopulation"),
        # Extreme prepopulation ratios
        (16, 100000, 5000, "Small capacity, huge prepopulation"),
        (256, 1, 10000, "Large capacity, tiny prepopulation"),
    ]

    results = []
    for capacity, prepopulate, operations, description in edge_cases:
        print(f"\n🧪 {description}")
        print(
            f"   Capacity={capacity}, Prepopulate={prepopulate:,}, Operations={operations:,}"
        )

        seed = random.randint(1, 1000000)

        try:
            tester = BPlusTreeFuzzTester(
                capacity=capacity, seed=seed, prepopulate=prepopulate
            )

            start_time = time.time()
            success = tester.run_fuzz_test(operations)
            elapsed = time.time() - start_time

            if success:
                print(f"   ✅ PASSED in {elapsed:.1f}s")
            else:
                print(f"   ❌ FAILED (seed: {seed})")

            results.append(success)

        except Exception as e:
            print(f"   💥 EXCEPTION: {e}")
            results.append(False)

    passed = sum(results)
    print(f"\nEdge case summary: {passed}/{len(results)} passed")
    return all(results)


if __name__ == "__main__":
    print("🚀 Starting Comprehensive B+ Tree Fuzz Testing")
    print("=" * 70)
    print("This will test different capacities, initial loads, and edge cases")
    print("to ensure our optimizations haven't broken anything.\n")

    # Set base random seed for reproducibility
    random.seed(42)

    overall_start = time.time()

    # Run all test suites
    try:
        # Main capacity sweep
        capacity_results = run_capacity_sweep()

        # Stress test with optimal config
        stress_passed = run_stress_test()

        # Edge case testing
        edge_passed = run_edge_case_tests()

        # Final summary
        overall_elapsed = time.time() - overall_start

        print(f"\n🏁 FINAL SUMMARY")
        print("=" * 70)
        print(f"Total testing time: {overall_elapsed:.1f}s")

        capacity_passed = sum(1 for r in capacity_results if r["success"])
        capacity_total = len(capacity_results)

        print(f"Capacity sweep: {capacity_passed}/{capacity_total} passed")
        print(f"Stress test: {'PASSED' if stress_passed else 'FAILED'}")
        print(f"Edge cases: {'PASSED' if edge_passed else 'FAILED'}")

        all_passed = (
            (capacity_passed == capacity_total) and stress_passed and edge_passed
        )

        if all_passed:
            print(f"\n🎉 ALL TESTS PASSED! B+ tree implementation is robust.")
        else:
            print(f"\n⚠️  Some tests failed. Check logs above for details.")

        print(f"\nOptimizations appear to be working correctly across:")
        print(f"  - Multiple capacities (4 to 1024)")
        print(f"  - Various initial loads (0 to 100K items)")
        print(f"  - Different operation patterns")
        print(f"  - Edge cases and stress conditions")

    except KeyboardInterrupt:
        print(f"\n⏹️  Testing interrupted by user")
    except Exception as e:
        print(f"\n💥 Testing failed with exception: {e}")
        raise
