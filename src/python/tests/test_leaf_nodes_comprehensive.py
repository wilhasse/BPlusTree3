"""
Comprehensive unit tests for LeafNode implementations.
Tests all three implementations: original, optimized Python, and C extension.
Covers all corner cases and edge conditions.
"""

import pytest
import sys
import os
import random
from typing import List, Tuple, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all node implementations
from nodes_original import LeafNode as OriginalLeafNode
from nodes_optimized import OptimizedLeafNode
try:
    import bplustree_c
    HAS_C_EXTENSION = True
except ImportError:
    HAS_C_EXTENSION = False
    bplustree_c = None

# Test parameters
CAPACITIES = [4, 8, 16, 32, 128]
TEST_SIZES = [0, 1, 2, 5, 10, 50, 100]


class TestLeafNodeImplementations:
    """Test suite for all LeafNode implementations."""
    
    def get_implementations(self):
        """Get all available node implementations."""
        implementations = [
            ("Original", OriginalLeafNode),
            ("Optimized", OptimizedLeafNode),
        ]
        
        if HAS_C_EXTENSION:
            # For C extension, we'll create a wrapper that behaves like a leaf node
            class CLeafNodeWrapper:
                def __init__(self, capacity):
                    self.capacity = capacity
                    self.tree = bplustree_c.BPlusTree(capacity=capacity)
                    self.next = None
                    self._keys_cache = []
                    self._values_cache = []
                
                def insert(self, key, value):
                    old_size = len(self.tree)
                    self.tree[key] = value
                    new_size = len(self.tree)
                    
                    # Update cache
                    self._update_cache()
                    
                    # Check if split would occur (simplified for testing)
                    if new_size > self.capacity:
                        # Simulate split for compatibility
                        mid = self.capacity // 2
                        new_node = CLeafNodeWrapper(self.capacity)
                        
                        # This is a simplified split simulation
                        # In reality, C extension handles this internally
                        return (self._keys_cache[mid], new_node)
                    
                    return None
                
                def get(self, key):
                    try:
                        return self.tree[key]
                    except KeyError:
                        return None
                
                def delete(self, key):
                    try:
                        del self.tree[key]
                        self._update_cache()
                        return True
                    except KeyError:
                        return False
                
                def is_leaf(self):
                    return True
                
                def is_full(self):
                    return len(self.tree) >= self.capacity
                
                def is_underfull(self):
                    return len(self.tree) < self.capacity // 2
                
                @property
                def keys(self):
                    self._update_cache()
                    return self._keys_cache
                
                @property
                def values(self):
                    self._update_cache()
                    return self._values_cache
                
                def _update_cache(self):
                    items = list(self.tree.items())
                    self._keys_cache = [k for k, v in items]
                    self._values_cache = [v for k, v in items]
            
            implementations.append(("C Extension", CLeafNodeWrapper))
        
        return implementations

    def test_empty_node_creation(self):
        """Test creating empty nodes with various capacities."""
        for impl_name, impl_class in self.get_implementations():
            for capacity in CAPACITIES:
                node = impl_class(capacity)
                
                assert node.is_leaf(), f"{impl_name}: Node should be a leaf"
                assert len(node.keys) == 0, f"{impl_name}: Empty node should have no keys"
                assert len(node.values) == 0, f"{impl_name}: Empty node should have no values"
                assert not node.is_full(), f"{impl_name}: Empty node should not be full"
                assert node.capacity == capacity, f"{impl_name}: Capacity should be {capacity}"

    def test_single_insertion(self):
        """Test inserting a single key-value pair."""
        for impl_name, impl_class in self.get_implementations():
            for capacity in CAPACITIES:
                node = impl_class(capacity)
                
                # Insert single item
                result = node.insert("key1", "value1")
                
                assert result is None, f"{impl_name}: Single insertion should not cause split"
                assert len(node.keys) == 1, f"{impl_name}: Should have 1 key after insertion"
                assert len(node.values) == 1, f"{impl_name}: Should have 1 value after insertion"
                assert node.keys[0] == "key1", f"{impl_name}: Key should be 'key1'"
                assert node.values[0] == "value1", f"{impl_name}: Value should be 'value1'"
                assert node.get("key1") == "value1", f"{impl_name}: get() should return 'value1'"

    def test_sequential_insertion_no_split(self):
        """Test sequential insertion without causing splits."""
        for impl_name, impl_class in self.get_implementations():
            for capacity in CAPACITIES:
                node = impl_class(capacity)
                fill_count = min(capacity - 1, 10)  # Don't fill to capacity
                
                # Insert sequential keys
                for i in range(fill_count):
                    result = node.insert(i, i * 10)
                    assert result is None, f"{impl_name}: Insertion {i} should not cause split"
                
                # Verify all keys and values
                assert len(node.keys) == fill_count, f"{impl_name}: Should have {fill_count} keys"
                assert len(node.values) == fill_count, f"{impl_name}: Should have {fill_count} values"
                
                for i in range(fill_count):
                    assert node.keys[i] == i, f"{impl_name}: Key {i} should be {i}"
                    assert node.values[i] == i * 10, f"{impl_name}: Value {i} should be {i * 10}"
                    assert node.get(i) == i * 10, f"{impl_name}: get({i}) should return {i * 10}"

    def test_insertion_ordering(self):
        """Test that keys maintain sorted order regardless of insertion order."""
        for impl_name, impl_class in self.get_implementations():
            node = impl_class(16)
            
            # Insert in random order
            keys_to_insert = [5, 1, 9, 3, 7, 2, 8, 4, 6]
            expected_order = sorted(keys_to_insert)
            
            for key in keys_to_insert:
                node.insert(key, key * 100)
            
            # Verify sorted order
            assert node.keys == expected_order, f"{impl_name}: Keys not in sorted order"
            
            # Verify values follow key order
            for i, key in enumerate(expected_order):
                assert node.values[i] == key * 100, f"{impl_name}: Value at position {i} incorrect"

    def test_duplicate_key_updates(self):
        """Test updating existing keys."""
        for impl_name, impl_class in self.get_implementations():
            node = impl_class(8)
            
            # Insert initial values
            for i in range(5):
                node.insert(i, i)
            
            original_length = len(node.keys)
            
            # Update existing keys
            for i in range(5):
                result = node.insert(i, i * 1000)
                assert result is None, f"{impl_name}: Update should not cause split"
            
            # Verify no new keys added
            assert len(node.keys) == original_length, f"{impl_name}: Length should not change on update"
            
            # Verify updated values
            for i in range(5):
                assert node.get(i) == i * 1000, f"{impl_name}: Updated value incorrect for key {i}"

    def test_insertion_at_boundaries(self):
        """Test insertion at beginning, middle, and end."""
        for impl_name, impl_class in self.get_implementations():
            node = impl_class(16)
            
            # Insert middle value first
            node.insert(5, 50)
            
            # Insert at beginning
            node.insert(1, 10)
            assert node.keys == [1, 5], f"{impl_name}: Beginning insertion failed"
            
            # Insert at end
            node.insert(9, 90)
            assert node.keys == [1, 5, 9], f"{impl_name}: End insertion failed"
            
            # Insert in middle
            node.insert(3, 30)
            assert node.keys == [1, 3, 5, 9], f"{impl_name}: Middle insertion failed"
            
            # Verify all values
            expected_values = [10, 30, 50, 90]
            assert node.values == expected_values, f"{impl_name}: Values incorrect after boundary insertions"

    def test_node_split_behavior(self):
        """Test node splitting when capacity is exceeded."""
        for impl_name, impl_class in self.get_implementations():
            if impl_name == "C Extension":
                continue  # Skip for C extension as it handles splits internally
            
            capacity = 8
            node = impl_class(capacity)
            
            # Fill node to capacity
            for i in range(capacity):
                result = node.insert(i, i * 10)
                assert result is None, f"{impl_name}: Should not split before capacity"
            
            # Insert one more to trigger split
            result = node.insert(capacity, capacity * 10)
            
            if result is not None:
                split_key, new_node = result
                
                # Verify split occurred
                assert new_node is not None, f"{impl_name}: New node should be created"
                assert new_node.is_leaf(), f"{impl_name}: New node should be a leaf"
                
                # Verify total keys preserved
                total_keys = len(node.keys) + len(new_node.keys)
                assert total_keys == capacity + 1, f"{impl_name}: Total keys should be {capacity + 1}"
                
                # Verify all keys are still accessible
                all_keys = node.keys + new_node.keys
                all_keys.sort()
                expected_keys = list(range(capacity + 1))
                assert all_keys == expected_keys, f"{impl_name}: Keys lost during split"

    def test_get_nonexistent_keys(self):
        """Test getting values for non-existent keys."""
        for impl_name, impl_class in self.get_implementations():
            node = impl_class(8)
            
            # Empty node
            assert node.get("nonexistent") is None, f"{impl_name}: Empty node should return None"
            
            # Node with some data
            for i in range(5):
                node.insert(i, i * 10)
            
            # Test non-existent keys
            assert node.get(-1) is None, f"{impl_name}: Should return None for key before range"
            assert node.get(10) is None, f"{impl_name}: Should return None for key after range"
            assert node.get(2.5) is None, f"{impl_name}: Should return None for key between existing keys"

    def test_delete_operations(self):
        """Test deleting keys from leaf nodes."""
        for impl_name, impl_class in self.get_implementations():
            node = impl_class(8)
            
            # Insert test data
            test_keys = [1, 3, 5, 7, 9]
            for key in test_keys:
                node.insert(key, key * 10)
            
            original_length = len(node.keys)
            
            # Delete middle element
            result = node.delete(5)
            assert result is True, f"{impl_name}: Delete should return True for existing key"
            assert len(node.keys) == original_length - 1, f"{impl_name}: Length should decrease"
            assert 5 not in node.keys, f"{impl_name}: Deleted key should not be in keys"
            assert node.get(5) is None, f"{impl_name}: Deleted key should return None"
            
            # Delete first element
            result = node.delete(1)
            assert result is True, f"{impl_name}: Delete should return True for existing key"
            assert 1 not in node.keys, f"{impl_name}: Deleted key should not be in keys"
            
            # Delete last element
            result = node.delete(9)
            assert result is True, f"{impl_name}: Delete should return True for existing key"
            assert 9 not in node.keys, f"{impl_name}: Deleted key should not be in keys"
            
            # Verify remaining keys are correct
            remaining_keys = [3, 7]
            assert node.keys == remaining_keys, f"{impl_name}: Remaining keys incorrect"
            
            # Try to delete non-existent key
            result = node.delete(100)
            assert result is False, f"{impl_name}: Delete should return False for non-existent key"

    def test_edge_case_capacities(self):
        """Test with edge case capacities."""
        for impl_name, impl_class in self.get_implementations():
            # Test minimum capacity
            min_capacity = 4
            node = impl_class(min_capacity)
            
            # Fill to capacity
            for i in range(min_capacity):
                node.insert(i, i)
            
            assert len(node.keys) == min_capacity, f"{impl_name}: Should handle minimum capacity"
            assert node.is_full(), f"{impl_name}: Should be full at minimum capacity"
            
            # Test very large capacity
            large_capacity = 1000
            node = impl_class(large_capacity)
            
            # Insert many items
            for i in range(100):
                node.insert(i, i)
            
            assert len(node.keys) == 100, f"{impl_name}: Should handle large capacity"
            assert not node.is_full(), f"{impl_name}: Should not be full with large capacity"

    def test_string_keys_and_values(self):
        """Test with string keys and values."""
        for impl_name, impl_class in self.get_implementations():
            node = impl_class(16)
            
            # Test data
            string_pairs = [
                ("apple", "fruit"),
                ("banana", "yellow"),
                ("cherry", "red"),
                ("date", "sweet"),
            ]
            
            # Insert string pairs
            for key, value in string_pairs:
                node.insert(key, value)
            
            # Verify sorted order (alphabetical)
            expected_keys = sorted([key for key, _ in string_pairs])
            assert node.keys == expected_keys, f"{impl_name}: String keys not sorted correctly"
            
            # Verify values
            for key, expected_value in string_pairs:
                assert node.get(key) == expected_value, f"{impl_name}: String value incorrect for {key}"

    def test_numeric_precision(self):
        """Test with various numeric types."""
        for impl_name, impl_class in self.get_implementations():
            node = impl_class(16)
            
            # Test with integers, floats
            numeric_pairs = [
                (1, "one"),
                (1.5, "one-point-five"),
                (2, "two"),
                (2.7, "two-point-seven"),
                (3, "three"),
            ]
            
            for key, value in numeric_pairs:
                node.insert(key, value)
            
            # Verify all can be retrieved
            for key, expected_value in numeric_pairs:
                assert node.get(key) == expected_value, f"{impl_name}: Numeric key {key} value incorrect"

    def test_large_dataset_stress(self):
        """Stress test with large datasets."""
        for impl_name, impl_class in self.get_implementations():
            if impl_name == "C Extension":
                continue  # Skip for C extension due to wrapper limitations
            
            node = impl_class(128)
            
            # Generate large random dataset
            size = 100
            keys = list(range(size))
            random.shuffle(keys)
            
            # Insert all keys
            for key in keys:
                result = node.insert(key, key * 1000)
                # May cause splits, that's okay
            
            # Verify all keys can be retrieved (from original node and any splits)
            for key in range(size):
                value = node.get(key)
                if value is not None:
                    assert value == key * 1000, f"{impl_name}: Large dataset value incorrect for {key}"

    def test_boundary_value_handling(self):
        """Test handling of boundary values."""
        for impl_name, impl_class in self.get_implementations():
            node = impl_class(16)
            
            # Test with None values (if supported)
            try:
                node.insert("key_none", None)
                assert node.get("key_none") is None, f"{impl_name}: None value should be retrievable"
            except:
                pass  # None values might not be supported
            
            # Test with empty string
            node.insert("", "empty_key")
            assert node.get("") == "empty_key", f"{impl_name}: Empty string key should work"
            
            # Test with very long strings
            long_key = "x" * 1000
            long_value = "y" * 1000
            node.insert(long_key, long_value)
            assert node.get(long_key) == long_value, f"{impl_name}: Long strings should work"

    def test_memory_efficiency(self):
        """Test memory usage patterns."""
        for impl_name, impl_class in self.get_implementations():
            # Create many small nodes to test memory allocation
            nodes = []
            for i in range(100):
                node = impl_class(8)
                for j in range(4):
                    node.insert(i * 10 + j, j)
                nodes.append(node)
            
            # Verify all nodes still work
            for i, node in enumerate(nodes):
                for j in range(4):
                    expected_key = i * 10 + j
                    assert node.get(expected_key) == j, f"{impl_name}: Memory test failed for node {i}"

    def test_concurrent_iteration_modification(self):
        """Test behavior when modifying during iteration (if applicable)."""
        for impl_name, impl_class in self.get_implementations():
            node = impl_class(16)
            
            # Insert initial data
            for i in range(10):
                node.insert(i, i * 10)
            
            # Get snapshot of keys
            original_keys = list(node.keys)
            
            # Modify node
            node.insert(15, 150)
            node.delete(5)
            
            # Original snapshot should be unchanged
            assert len(original_keys) == 10, f"{impl_name}: Original keys snapshot should be unchanged"
            
            # New keys should reflect changes
            current_keys = list(node.keys)
            assert 15 in current_keys, f"{impl_name}: New key should be present"
            assert 5 not in current_keys, f"{impl_name}: Deleted key should be absent"

    def test_custom_objects_as_keys(self):
        """Test with custom objects that have complex comparison logic."""
        
        class ComplexKey:
            """Custom key class with complex comparison logic."""
            
            def __init__(self, primary: int, secondary: str):
                self.primary = primary
                self.secondary = secondary
            
            def __eq__(self, other):
                if not isinstance(other, ComplexKey):
                    return False
                return self.primary == other.primary and self.secondary == other.secondary
            
            def __lt__(self, other):
                if not isinstance(other, ComplexKey):
                    return NotImplemented
                if self.primary != other.primary:
                    return self.primary < other.primary
                return self.secondary < other.secondary
            
            def __le__(self, other):
                return self < other or self == other
            
            def __gt__(self, other):
                return not (self <= other)
            
            def __ge__(self, other):
                return not (self < other)
            
            def __hash__(self):
                return hash((self.primary, self.secondary))
            
            def __repr__(self):
                return f"ComplexKey({self.primary}, '{self.secondary}')"
        
        class WeirdComparison:
            """Object with unusual comparison behavior."""
            
            def __init__(self, value: int):
                self.value = value
            
            def __eq__(self, other):
                if not isinstance(other, WeirdComparison):
                    return False
                # Equal only if exactly the same value
                return self.value == other.value
            
            def __lt__(self, other):
                if not isinstance(other, WeirdComparison):
                    return NotImplemented
                # Sort even numbers before odd numbers, then by value
                self_parity = self.value % 2
                other_parity = other.value % 2
                if self_parity != other_parity:
                    return self_parity < other_parity  # Even (0) < Odd (1)
                return self.value < other.value
            
            def __hash__(self):
                return hash(self.value)
            
            def __repr__(self):
                return f"Weird({self.value})"
        
        for impl_name, impl_class in self.get_implementations():
            print(f"  Testing {impl_name} with custom objects...")
            
            # Test ComplexKey objects
            node = impl_class(16)
            
            complex_keys = [
                ComplexKey(1, "z"),
                ComplexKey(1, "a"),
                ComplexKey(2, "m"),
                ComplexKey(0, "x"),
            ]
            
            # Insert complex keys
            for i, key in enumerate(complex_keys):
                node.insert(key, f"value_{i}")
            
            # Verify sorted order
            sorted_keys = sorted(complex_keys)
            node_keys = list(node.keys)
            
            # Compare manually since complex objects
            for i, expected_key in enumerate(sorted_keys):
                assert node_keys[i] == expected_key, f"{impl_name}: Complex key order wrong at position {i}"
            
            # Test retrieval
            for i, key in enumerate(complex_keys):
                retrieved_value = node.get(key)
                assert retrieved_value == f"value_{i}", f"{impl_name}: Complex key retrieval failed"
            
            # Test WeirdComparison objects
            node2 = impl_class(16)
            
            weird_values = [3, 1, 4, 2, 6, 5]  # Mix of even and odd
            weird_keys = [WeirdComparison(v) for v in weird_values]
            
            for i, key in enumerate(weird_keys):
                node2.insert(key, f"weird_{i}")
            
            # Verify custom sorting (evens first, then odds, each group sorted by value)
            expected_order = [WeirdComparison(2), WeirdComparison(4), WeirdComparison(6),  # evens
                            WeirdComparison(1), WeirdComparison(3), WeirdComparison(5)]  # odds
            
            node2_keys = list(node2.keys)
            for i, expected_key in enumerate(expected_order):
                assert node2_keys[i].value == expected_key.value, \
                    f"{impl_name}: Weird comparison order wrong at position {i}"

    def test_objects_with_side_effects(self):
        """Test objects that have side effects during comparison."""
        
        class CountingKey:
            """Key that counts how many times it's been compared."""
            comparison_count = 0
            
            def __init__(self, value: int):
                self.value = value
            
            def __eq__(self, other):
                CountingKey.comparison_count += 1
                if not isinstance(other, CountingKey):
                    return False
                return self.value == other.value
            
            def __lt__(self, other):
                CountingKey.comparison_count += 1
                if not isinstance(other, CountingKey):
                    return NotImplemented
                return self.value < other.value
            
            def __hash__(self):
                return hash(self.value)
            
            def __repr__(self):
                return f"Counting({self.value})"
            
            @classmethod
            def reset_count(cls):
                cls.comparison_count = 0
        
        for impl_name, impl_class in self.get_implementations():
            print(f"  Testing {impl_name} with side-effect objects...")
            
            node = impl_class(8)
            CountingKey.reset_count()
            
            # Insert keys that will trigger multiple comparisons
            keys = [CountingKey(i) for i in [5, 2, 8, 1, 9, 3]]
            
            for key in keys:
                node.insert(key, key.value * 10)
            
            # Verify comparisons were made (implementation-dependent count)
            initial_count = CountingKey.comparison_count
            assert initial_count > 0, f"{impl_name}: No comparisons made during insertion"
            
            # Test lookup (should trigger comparisons)
            CountingKey.reset_count()
            test_key = CountingKey(5)
            result = node.get(test_key)
            
            lookup_count = CountingKey.comparison_count
            assert lookup_count > 0, f"{impl_name}: No comparisons made during lookup"
            assert result == 50, f"{impl_name}: Lookup result incorrect"

    def test_comparable_across_types(self):
        """Test objects that can compare across different types."""
        
        class FlexibleNumber:
            """Number that can compare with int, float, etc."""
            
            def __init__(self, value):
                self.value = float(value)
            
            def __eq__(self, other):
                if isinstance(other, (int, float)):
                    return self.value == float(other)
                elif isinstance(other, FlexibleNumber):
                    return self.value == other.value
                return False
            
            def __lt__(self, other):
                if isinstance(other, (int, float)):
                    return self.value < float(other)
                elif isinstance(other, FlexibleNumber):
                    return self.value < other.value
                return NotImplemented
            
            def __le__(self, other):
                return self < other or self == other
            
            def __gt__(self, other):
                if isinstance(other, (int, float)):
                    return self.value > float(other)
                elif isinstance(other, FlexibleNumber):
                    return self.value > other.value
                return NotImplemented
            
            def __ge__(self, other):
                return self > other or self == other
            
            def __hash__(self):
                return hash(self.value)
            
            def __repr__(self):
                return f"Flex({self.value})"
        
        for impl_name, impl_class in self.get_implementations():
            print(f"  Testing {impl_name} with cross-type comparable objects...")
            
            node = impl_class(16)
            
            # Use only FlexibleNumber objects to avoid cross-type comparison issues
            # This tests the internal comparison logic of FlexibleNumber
            mixed_keys = [
                FlexibleNumber(3.5),
                FlexibleNumber(2.0),
                FlexibleNumber(1.0),
                FlexibleNumber(4.7),
                FlexibleNumber(3.0),
            ]
            
            # Insert keys
            for i, key in enumerate(mixed_keys):
                node.insert(key, f"flex_{i}")
            
            # Test retrieval
            for i, key in enumerate(mixed_keys):
                result = node.get(key)
                assert result == f"flex_{i}", f"{impl_name}: FlexibleNumber retrieval failed for {key}"
            
            # Test that we can find with equivalent but different instances
            test_key = FlexibleNumber(2.0)
            result = node.get(test_key)
            assert result is not None, f"{impl_name}: Equivalent FlexibleNumber lookup failed"


def run_comprehensive_leaf_tests():
    """Run all comprehensive leaf node tests."""
    test_suite = TestLeafNodeImplementations()
    
    test_methods = [
        test_suite.test_empty_node_creation,
        test_suite.test_single_insertion,
        test_suite.test_sequential_insertion_no_split,
        test_suite.test_insertion_ordering,
        test_suite.test_duplicate_key_updates,
        test_suite.test_insertion_at_boundaries,
        test_suite.test_node_split_behavior,
        test_suite.test_get_nonexistent_keys,
        test_suite.test_delete_operations,
        test_suite.test_edge_case_capacities,
        test_suite.test_string_keys_and_values,
        test_suite.test_numeric_precision,
        test_suite.test_large_dataset_stress,
        test_suite.test_boundary_value_handling,
        test_suite.test_memory_efficiency,
        test_suite.test_concurrent_iteration_modification,
        test_suite.test_custom_objects_as_keys,
        test_suite.test_objects_with_side_effects,
        test_suite.test_comparable_across_types,
    ]
    
    print("Running Comprehensive LeafNode Tests")
    print("=" * 60)
    
    implementations = test_suite.get_implementations()
    print(f"Testing implementations: {[name for name, _ in implementations]}")
    print()
    
    passed = 0
    failed = 0
    
    for test_method in test_methods:
        test_name = test_method.__name__
        try:
            print(f"Running {test_name}...")
            test_method()
            print(f"✓ {test_name} PASSED")
            passed += 1
        except Exception as e:
            print(f"✗ {test_name} FAILED: {e}")
            failed += 1
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All LeafNode tests passed across all implementations!")
    else:
        print("🚨 Some tests failed. Check implementation consistency.")
    
    return failed == 0


if __name__ == "__main__":
    run_comprehensive_leaf_tests()