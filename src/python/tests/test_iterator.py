"""Tests for B+ Tree iterator functionality"""

import pytest
from ..bplus_tree import BPlusTreeMap


class TestBPlusTreeIterator:
    """Test cases for B+ tree iteration"""

    def test_iterate_empty_tree(self):
        """Test iterating over an empty tree"""
        tree = BPlusTreeMap(capacity=4)
        items = list(tree.items())
        assert items == []

    def test_iterate_single_item(self):
        """Test iterating over a tree with one item"""
        tree = BPlusTreeMap(capacity=4)
        tree[5] = "value5"

        items = list(tree.items())
        assert items == [(5, "value5")]

    def test_iterate_multiple_items_single_leaf(self):
        """Test iterating over multiple items in a single leaf"""
        tree = BPlusTreeMap(capacity=4)
        tree[1] = "value1"
        tree[3] = "value3"
        tree[2] = "value2"
        tree[4] = "value4"

        items = list(tree.items())
        assert items == [(1, "value1"), (2, "value2"), (3, "value3"), (4, "value4")]

    def test_iterate_multiple_leaves(self):
        """Test iterating across multiple leaves"""
        tree = BPlusTreeMap(capacity=4)
        # Insert enough to create multiple leaves
        for i in range(1, 10):
            tree[i] = f"value{i}"

        items = list(tree.items())
        expected = [(i, f"value{i}") for i in range(1, 10)]
        assert items == expected

    def test_iterate_large_tree(self):
        """Test iterating over a large tree"""
        tree = BPlusTreeMap(capacity=4)
        n = 100
        for i in range(n):
            tree[i] = f"value{i}"

        items = list(tree.items())
        assert len(items) == n
        assert items[0] == (0, "value0")
        assert items[-1] == (99, "value99")
        # Check ordering
        for i in range(1, n):
            assert items[i][0] > items[i - 1][0]

    def test_keys_iterator(self):
        """Test iterating over just keys"""
        tree = BPlusTreeMap(capacity=4)
        for i in [5, 2, 8, 1, 9, 3]:
            tree[i] = f"value{i}"

        keys = list(tree.keys())
        assert keys == [1, 2, 3, 5, 8, 9]

    def test_values_iterator(self):
        """Test iterating over just values"""
        tree = BPlusTreeMap(capacity=4)
        for i in [5, 2, 8]:
            tree[i] = f"value{i}"

        values = list(tree.values())
        assert sorted(values) == ["value2", "value5", "value8"]


class TestBPlusTreeRangeIterator:
    """Test cases for range-based iteration"""

    def test_iterate_from_key(self):
        """Test iterating starting from a specific key"""
        tree = BPlusTreeMap(capacity=4)
        for i in range(10):
            tree[i] = f"value{i}"

        items = list(tree.items(start_key=5))
        expected = [(i, f"value{i}") for i in range(5, 10)]
        assert items == expected

    def test_iterate_until_key(self):
        """Test iterating until a specific key"""
        tree = BPlusTreeMap(capacity=4)
        for i in range(10):
            tree[i] = f"value{i}"

        items = list(tree.items(end_key=5))
        expected = [(i, f"value{i}") for i in range(5)]
        assert items == expected

    def test_iterate_range(self):
        """Test iterating over a key range"""
        tree = BPlusTreeMap(capacity=4)
        for i in range(20):
            tree[i] = f"value{i}"

        items = list(tree.items(start_key=5, end_key=15))
        expected = [(i, f"value{i}") for i in range(5, 15)]
        assert items == expected

    def test_iterate_from_nonexistent_key(self):
        """Test iterating from a key that doesn't exist"""
        tree = BPlusTreeMap(capacity=4)
        for i in [1, 3, 5, 7, 9]:
            tree[i] = f"value{i}"

        # Start from 4 (doesn't exist, should start from 5)
        items = list(tree.items(start_key=4))
        expected = [(5, "value5"), (7, "value7"), (9, "value9")]
        assert items == expected

    def test_iterate_empty_range(self):
        """Test iterating over an empty range"""
        tree = BPlusTreeMap(capacity=4)
        for i in range(10):
            tree[i] = f"value{i}"

        # Start after end
        items = list(tree.items(start_key=7, end_key=3))
        assert items == []

    def test_iterate_range_beyond_tree(self):
        """Test range that extends beyond tree contents"""
        tree = BPlusTreeMap(capacity=4)
        for i in range(5):
            tree[i] = f"value{i}"

        items = list(tree.items(start_key=2, end_key=10))
        expected = [(i, f"value{i}") for i in range(2, 5)]
        assert items == expected

    def test_iterate_from_middle_of_leaf(self):
        """Test starting iteration from the middle of a leaf node"""
        tree = BPlusTreeMap(capacity=6)  # Larger capacity for more items per leaf
        for i in range(20):
            tree[i * 2] = f"value{i*2}"  # Even numbers only

        # Start from 11 (doesn't exist, should start from 12)
        items = list(tree.items(start_key=11))
        assert items[0] == (12, "value12")
        assert len(items) == 14  # From 12 to 38 (inclusive)
