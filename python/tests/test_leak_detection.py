import tracemalloc
import gc

import pytest

from ..bplus_tree import BPlusTreeMap as BPlusTree


def test_no_memory_leak_on_insert_delete():
    """
    Leak-detection test using tracemalloc: after 1K inserts and deletes,
    memory usage should not grow excessively (allowing for Python GC overhead).
    """
    tracemalloc.start()

    # Baseline measurement with empty tree
    tree = BPlusTree(capacity=16)
    gc.collect()
    snapshot_before = tracemalloc.take_snapshot()

    # Perform operations
    for i in range(1000):
        tree[i] = i
    for i in range(1000):
        del tree[i]

    # Clean up and measure
    del tree
    gc.collect()
    snapshot_after = tracemalloc.take_snapshot()
    tracemalloc.stop()

    total_before = sum(stat.size for stat in snapshot_before.statistics("filename"))
    total_after = sum(stat.size for stat in snapshot_after.statistics("filename"))

    # Allow for reasonable overhead (10KB) due to Python's memory management
    max_allowed_growth = 10 * 1024  # 10KB
    growth = total_after - total_before

    assert growth <= max_allowed_growth, (
        f"Excessive memory growth detected: before={total_before} bytes, "
        f"after={total_after} bytes, growth={growth} bytes (max allowed: {max_allowed_growth})"
    )
