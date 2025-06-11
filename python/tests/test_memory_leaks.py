"""
Memory leak detection tests for B+ Tree implementation.

These tests ensure that the implementation properly manages memory
and doesn't leak references during various operations.
"""

import pytest
import gc
import weakref
import sys
from typing import List, Any

from bplustree import BPlusTreeMap


@pytest.mark.slow
class TestMemoryLeaks:
    """Test for memory leaks in various operations."""

    def test_insertion_deletion_cycle_no_leak(self):
        """Test that insertion/deletion cycles don't leak memory."""
        tree = BPlusTreeMap()

        # Track object count before operations
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Perform multiple insertion/deletion cycles
        for cycle in range(5):
            # Insert items
            for i in range(1000):
                tree[i] = f"value_{i}_{cycle}"

            # Delete all items
            for i in range(1000):
                del tree[i]

        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())

        # Object count should not grow significantly
        # Allow some variance for internal Python operations
        growth = final_objects - initial_objects
        assert (
            growth < 100
        ), f"Too many objects leaked: {growth} new objects after cycles"

    def test_deleted_values_are_released(self):
        """Test that deleted values are properly released."""
        tree = BPlusTreeMap()

        # Create objects that we can track
        class TrackedObject:
            def __init__(self, value):
                self.value = value

        # Insert tracked objects
        objects = []
        weak_refs = []
        for i in range(100):
            obj = TrackedObject(f"value_{i}")
            objects.append(obj)
            weak_refs.append(weakref.ref(obj))
            tree[i] = obj

        # Clear our references but keep weak references
        objects.clear()

        # Delete from tree
        for i in range(100):
            del tree[i]

        # Force garbage collection
        gc.collect()

        # All objects should be released
        alive_count = sum(1 for ref in weak_refs if ref() is not None)
        assert alive_count == 0, f"{alive_count} objects still alive after deletion"

    def test_clear_releases_all_references(self):
        """Test that clear() properly releases all references."""
        tree = BPlusTreeMap()

        # Create tracked objects
        weak_refs = []
        for i in range(100):
            obj = object()
            weak_refs.append(weakref.ref(obj))
            tree[i] = obj

        # Clear the tree
        tree.clear()

        # Force garbage collection
        gc.collect()

        # All objects should be released
        alive_count = sum(1 for ref in weak_refs if ref() is not None)
        assert alive_count == 0, f"{alive_count} objects still alive after clear()"

    def test_tree_destruction_releases_nodes(self):
        """Test that destroying the tree releases all nodes."""
        # Create tree in a function scope
        weak_refs = []

        def create_and_track_tree():
            tree = BPlusTreeMap()

            # Insert enough items to create multiple nodes
            for i in range(1000):
                tree[i] = f"value_{i}"

            # Track the tree itself
            weak_refs.append(weakref.ref(tree))

            # Track some values
            for i in range(0, 1000, 100):
                if i in tree:
                    weak_refs.append(weakref.ref(tree))

        create_and_track_tree()

        # Force garbage collection
        gc.collect()

        # Tree and all its contents should be released
        alive_count = sum(1 for ref in weak_refs if ref() is not None)
        assert (
            alive_count == 0
        ), f"{alive_count} objects still alive after tree destruction"

    def test_update_operations_no_leak(self):
        """Test that update operations don't leak the old values."""
        tree = BPlusTreeMap()

        # Track memory before operations
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Insert initial values
        for i in range(500):
            tree[i] = f"initial_value_{i}"

        # Update values multiple times
        for round in range(10):
            for i in range(500):
                tree[i] = f"updated_value_{i}_{round}"

        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())

        # Should not have significant growth
        # (some growth is expected for string interning etc.)
        growth = final_objects - initial_objects
        assert (
            growth < 1000
        ), f"Too many objects leaked during updates: {growth} new objects"

    def test_copy_creates_independent_references(self):
        """Test that copy() creates proper independent references."""
        tree1 = BPlusTreeMap()

        # Create tracked objects
        objects = []
        for i in range(50):
            obj = [f"value_{i}"]  # Mutable object
            objects.append(obj)
            tree1[i] = obj

        # Create a copy
        tree2 = tree1.copy()

        # Modify objects through tree1
        for i in range(50):
            tree1[i].append("modified")

        # Changes should be visible in tree2 (shallow copy)
        for i in range(50):
            assert len(tree2[i]) == 2, "Shallow copy should share references"

        # Clear tree1
        tree1.clear()

        # tree2 should still have all references
        for i in range(50):
            assert tree2[i] == [f"value_{i}", "modified"]

    def test_large_tree_memory_usage(self):
        """Test memory usage with large trees."""
        tree = BPlusTreeMap()

        # Get initial memory usage
        initial_size = sys.getsizeof(tree)

        # Insert many items
        for i in range(10000):
            tree[i] = i

        # The tree itself should not grow too large
        # (the nodes are separate objects)
        final_size = sys.getsizeof(tree)

        # Tree object itself should remain small
        assert (
            final_size < initial_size * 2
        ), f"Tree object grew too much: {initial_size} -> {final_size}"

    def test_iterator_cleanup(self):
        """Test that iterators don't prevent garbage collection."""
        tree = BPlusTreeMap()

        # Insert items
        for i in range(100):
            tree[i] = f"value_{i}"

        # Create multiple iterators but don't exhaust them
        iterators = []
        for _ in range(10):
            it = iter(tree.items())
            next(it)  # Advance once
            iterators.append(it)

        # Track tree with weak reference
        tree_ref = weakref.ref(tree)

        # Delete tree reference
        del tree

        # Tree should still be alive (held by iterators)
        assert tree_ref() is not None

        # Clear iterators
        iterators.clear()
        gc.collect()

        # Now tree should be collected
        assert tree_ref() is None, "Tree not collected after clearing iterators"

    def test_circular_reference_handling(self):
        """Test handling of circular references in stored values."""
        tree = BPlusTreeMap()

        # Create objects with circular references
        for i in range(50):
            obj1 = {"id": i}
            obj2 = {"ref": obj1}
            obj1["ref"] = obj2
            tree[i] = obj1

        # Track with weak references
        weak_refs = []
        for i in range(50):
            weak_refs.append(weakref.ref(tree[i]))

        # Clear the tree
        tree.clear()

        # Force garbage collection (may need multiple passes for cycles)
        for _ in range(3):
            gc.collect()

        # Circular references should be collected
        alive_count = sum(1 for ref in weak_refs if ref() is not None)
        assert alive_count == 0, f"{alive_count} circular references still alive"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
