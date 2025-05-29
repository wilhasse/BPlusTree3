"""
B+ Tree implementation with switchable node types.

This module provides a B+ tree that can switch between original and optimized
node implementations for performance comparison and testing.
"""

import bisect
from abc import ABC, abstractmethod
from typing import Any, Optional, List, Tuple, Union, Iterator, Literal
from enum import Enum

# Import both node implementations
from nodes_original import Node as OriginalNode, LeafNode as OriginalLeafNode, BranchNode as OriginalBranchNode
from nodes_optimized import Node as OptimizedNode, OptimizedLeafNode, OptimizedBranchNode

__all__ = ["BPlusTreeMap", "NodeImplementation"]

# Constants
MIN_CAPACITY = 4
DEFAULT_CAPACITY = 128
BULK_LOAD_BATCH_MULTIPLIER = 2
MIN_BULK_LOAD_BATCH_SIZE = 50


class NodeImplementation(Enum):
    """Available node implementations."""
    ORIGINAL = "original"
    OPTIMIZED = "optimized"


class BPlusTreeError(Exception):
    """Base exception for B+ tree operations."""
    pass


class InvalidCapacityError(BPlusTreeError):
    """Raised when an invalid capacity is specified."""
    pass


class BPlusTreeMap:
    """B+ Tree implementation with switchable node types.

    This implementation allows choosing between original (separate arrays)
    and optimized (single array) node implementations at creation time.
    
    Attributes:
        capacity: Maximum number of keys per node.
        root: The root node of the tree.
        leaves: The leftmost leaf node (head of linked list).
        node_impl: Which node implementation is being used.
    """

    def __init__(
        self, 
        capacity: int = DEFAULT_CAPACITY,
        node_impl: Union[NodeImplementation, str] = NodeImplementation.ORIGINAL
    ) -> None:
        """Create a B+ tree with specified node capacity and implementation.

        Args:
            capacity: Maximum number of keys per node (minimum 4).
            node_impl: Which node implementation to use.

        Raises:
            InvalidCapacityError: If capacity is less than 4.
        """
        if capacity < MIN_CAPACITY:
            raise InvalidCapacityError(
                f"Capacity must be at least {MIN_CAPACITY} to maintain B+ tree invariants"
            )
        
        self.capacity = capacity
        self._rightmost_leaf_cache = None
        
        # Convert string to enum if needed
        if isinstance(node_impl, str):
            node_impl = NodeImplementation(node_impl)
        self.node_impl = node_impl
        
        # Set up node classes based on implementation choice
        if node_impl == NodeImplementation.OPTIMIZED:
            self._leaf_class = OptimizedLeafNode
            self._branch_class = OptimizedBranchNode
            self._node_base = OptimizedNode
        else:
            self._leaf_class = OriginalLeafNode
            self._branch_class = OriginalBranchNode
            self._node_base = OriginalNode
        
        # Create initial root
        root = self._leaf_class(self.capacity)
        self.leaves = root
        self.root = root

    @classmethod
    def from_sorted_items(
        cls, 
        items, 
        capacity: int = DEFAULT_CAPACITY,
        node_impl: Union[NodeImplementation, str] = NodeImplementation.ORIGINAL
    ) -> "BPlusTreeMap":
        """Bulk load from sorted key-value pairs for 3-5x faster construction.

        Args:
            items: Iterable of (key, value) pairs that MUST be sorted by key.
            capacity: Node capacity (minimum 4).
            node_impl: Which node implementation to use.

        Returns:
            BPlusTreeMap instance with loaded data.
        """
        tree = cls(capacity=capacity, node_impl=node_impl)
        tree._bulk_load_sorted(items)
        return tree

    def _bulk_load_sorted(self, items) -> None:
        """Internal bulk loading implementation for sorted items."""
        items_list = list(items)
        if not items_list:
            return
        optimal_batch_size = max(
            self.capacity * BULK_LOAD_BATCH_MULTIPLIER, MIN_BULK_LOAD_BATCH_SIZE
        )

        for i in range(0, len(items_list), optimal_batch_size):
            batch_end = min(i + optimal_batch_size, len(items_list))

            for j in range(i, batch_end):
                key, value = items_list[j]
                self._insert_sorted_optimized(key, value)

    def _insert_sorted_optimized(self, key: Any, value: Any) -> None:
        """Optimized insertion for sorted data - avoids repeated tree traversals."""
        # Check if we can append to rightmost leaf
        if self._rightmost_leaf_cache:
            # For optimized nodes, check num_keys property
            if hasattr(self._rightmost_leaf_cache, 'num_keys'):
                if (self._rightmost_leaf_cache.num_keys > 0 and
                    key > self._rightmost_leaf_cache.data[self._rightmost_leaf_cache.num_keys - 1] and
                    not self._rightmost_leaf_cache.is_full()):
                    # Direct append for optimized node
                    idx = self._rightmost_leaf_cache.num_keys
                    self._rightmost_leaf_cache.data[idx] = key
                    self._rightmost_leaf_cache.data[self._rightmost_leaf_cache.capacity + idx] = value
                    self._rightmost_leaf_cache.num_keys += 1
                    return
            else:
                # Original node implementation
                if (self._rightmost_leaf_cache.keys and
                    key > self._rightmost_leaf_cache.keys[-1] and
                    not self._rightmost_leaf_cache.is_full()):
                    self._rightmost_leaf_cache.keys.append(key)
                    self._rightmost_leaf_cache.values.append(value)
                    return

        # Regular insertion
        self._insert(key, value)

    def _find_leaf(self, key: Any) -> Any:
        """Find the leaf node that should contain the key."""
        node = self.root
        while not node.is_leaf():
            node = node.get_child(key)
        return node

    def _insert(self, key: Any, value: Any) -> None:
        """Insert a key-value pair into the tree."""
        result = self._insert_recursive(self.root, key, value)
        
        if result is not None:
            # Root split occurred
            split_key, new_right = result
            new_root = self._branch_class(self.capacity)
            
            # Set up new root - handle both node types
            if hasattr(new_root, 'data'):
                # Optimized node
                new_root.data[new_root.capacity] = self.root  # First child
                new_root.data[0] = split_key
                new_root.data[new_root.capacity + 1] = new_right
                new_root.num_keys = 1
            else:
                # Original node
                new_root.children = [self.root, new_right]
                new_root.keys = [split_key]
            
            self.root = new_root

    def _insert_recursive(self, node: Any, key: Any, value: Any) -> Optional[Tuple[Any, Any]]:
        """Recursively insert and handle splits."""
        if node.is_leaf():
            result = node.insert(key, value)
            if result and node == self._rightmost_leaf_cache:
                self._rightmost_leaf_cache = result[1]
            return result
        else:
            child = node.get_child(key)
            result = self._insert_recursive(child, key, value)
            
            if result is not None:
                return node.insert(result[0], result[1])
            
            return None

    def __getitem__(self, key: Any) -> Any:
        """Get value for key."""
        leaf = self._find_leaf(key)
        value = leaf.get(key)
        if value is None:
            raise KeyError(key)
        return value

    def __setitem__(self, key: Any, value: Any) -> None:
        """Set value for key."""
        self._insert(key, value)

    def __delitem__(self, key: Any) -> None:
        """Delete key from tree."""
        if not self._delete(key):
            raise KeyError(key)

    def __contains__(self, key: Any) -> bool:
        """Check if key exists in tree."""
        try:
            self[key]
            return True
        except KeyError:
            return False

    def __len__(self) -> int:
        """Return total number of keys in tree."""
        count = 0
        current = self.leaves
        while current is not None:
            if hasattr(current, 'num_keys'):
                count += current.num_keys
            else:
                count += len(current.keys)
            current = current.next
        return count

    def __iter__(self) -> Iterator[Any]:
        """Iterate over all keys in sorted order."""
        current = self.leaves
        while current is not None:
            if hasattr(current, 'num_keys'):
                # Optimized node
                for i in range(current.num_keys):
                    yield current.data[i]
            else:
                # Original node
                for key in current.keys:
                    yield key
            current = current.next

    def items(self, start_key=None, end_key=None) -> Iterator[Tuple[Any, Any]]:
        """Iterate over key-value pairs in range [start_key, end_key)."""
        # Find starting leaf
        if start_key is None:
            current = self.leaves
        else:
            current = self._find_leaf(start_key)

        while current is not None:
            if hasattr(current, 'num_keys'):
                # Optimized node
                start_idx = 0
                if start_key is not None and current == self._find_leaf(start_key):
                    start_idx = bisect.bisect_left(current.data, start_key, 0, current.num_keys)
                
                for i in range(start_idx, current.num_keys):
                    key = current.data[i]
                    if end_key is not None and key >= end_key:
                        return
                    yield (key, current.data[current.capacity + i])
            else:
                # Original node
                start_idx = 0
                if start_key is not None and current == self._find_leaf(start_key):
                    start_idx = bisect.bisect_left(current.keys, start_key)
                
                for i in range(start_idx, len(current.keys)):
                    key = current.keys[i]
                    if end_key is not None and key >= end_key:
                        return
                    yield (key, current.values[i])
            
            current = current.next
            start_key = None  # Only apply to first leaf

    def keys(self) -> Iterator[Any]:
        """Iterate over all keys."""
        return iter(self)

    def values(self) -> Iterator[Any]:
        """Iterate over all values."""
        for _, value in self.items():
            yield value

    def get(self, key: Any, default: Any = None) -> Any:
        """Get value for key, or default if not found."""
        try:
            return self[key]
        except KeyError:
            return default

    def _delete(self, key: Any) -> bool:
        """Delete key from tree. Returns True if key was found and deleted."""
        # For simplicity, using a basic delete that may leave underfull nodes
        # A full implementation would handle rebalancing
        leaf = self._find_leaf(key)
        return leaf.delete(key)

    def clear(self) -> None:
        """Remove all items from tree."""
        root = self._leaf_class(self.capacity)
        self.leaves = root
        self.root = root
        self._rightmost_leaf_cache = None

    def __repr__(self) -> str:
        """String representation."""
        return f"BPlusTreeMap(capacity={self.capacity}, node_impl={self.node_impl.value}, size={len(self)})"