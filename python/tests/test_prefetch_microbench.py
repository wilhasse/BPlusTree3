import pytest

pytest.skip(
    "Prefetch microbenchmark harness (requires rebuild with -DPREFETCH_HINTS); see docstring for usage",
    allow_module_level=True,
)

"""
Prefetch Microbenchmark for BPlusTree C extension.

This benchmark measures lookup performance with and without CPU prefetch hints.

Usage:
    # Baseline (no prefetch hints)
    CFLAGS='-O3 -march=native' pip install -e .
    pytest src/python/tests/test_prefetch_microbench.py::test_prefetch_microbench --capture=no

    # With prefetch hints enabled
    CFLAGS='-O3 -march=native -DPREFETCH_HINTS' pip install -e .
    pytest src/python/tests/test_prefetch_microbench.py::test_prefetch_microbench --capture=no
"""

import time
import random
import gc

from bplustree_c import BPlusTree


def test_prefetch_microbench():
    """Run lookup benchmark to compare prefetch hint impact."""
    # Prepare dataset
    size = 100_000
    keys = list(range(size))
    random.shuffle(keys)
    lookup_keys = random.sample(keys, min(10_000, size))

    # Build tree
    tree = BPlusTree(capacity=128)
    for key in keys:
        tree[key] = key * 2

    def lookup():
        for k in lookup_keys:
            _ = tree[k]

    # Warm up and measure
    iterations = 5
    gc.collect()
    gc.disable()
    start = time.perf_counter()
    for _ in range(iterations):
        lookup()
    total = time.perf_counter() - start
    gc.enable()

    ns_per_op = total * 1e9 / (iterations * len(lookup_keys))
    print(f"Lookup performance: {ns_per_op:.1f} ns/op")
