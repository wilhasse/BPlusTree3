import pytest

try:
    from bplustree_c import BPlusTree
except ImportError as e:
    pytest.skip(f"C extension not available: {e}", allow_module_level=True)

"""
Multithreaded Lookup Microbenchmark for BPlusTree C extension.

This benchmark measures lookup throughput across multiple threads.

Usage:
    pytest src/python/tests/test_multithreaded_lookup.py::test_multithreaded_lookup --capture=no
"""

import threading
import time
import random
import gc


def test_multithreaded_lookup():
    """Multithreaded lookup performance: measure throughput of concurrent lookups."""
    # Prepare dataset
    size = 100_000
    keys = list(range(size))
    random.shuffle(keys)
    tree = BPlusTree(capacity=128)
    for key in keys:
        tree[key] = key * 2

    lookup_keys = random.sample(keys, min(10_000, size))

    def worker(iterations):
        for _ in range(iterations):
            for k in lookup_keys:
                _ = tree[k]

    thread_count = 4
    iterations = 5

    gc.collect()
    gc.disable()
    threads = []
    start = time.perf_counter()
    for _ in range(thread_count):
        t = threading.Thread(target=worker, args=(iterations,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    total_time = time.perf_counter() - start
    gc.enable()

    total_ops = thread_count * iterations * len(lookup_keys)
    ns_per_op = total_time * 1e9 / total_ops
    ops_per_sec = total_ops / total_time
    print(
        f"Threads: {thread_count}, Multithreaded lookup: {ns_per_op:.1f} ns/op ({ops_per_sec:.0f} ops/sec)"
    )
