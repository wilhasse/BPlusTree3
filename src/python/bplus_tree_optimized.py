"""
Optimized B+ Tree implementation with switchable node implementations.

This module extends the original B+ tree with performance optimizations:
- Single array node layout for better cache locality
- Switchable between original and optimized node implementations
- Compatible API with the original BPlusTreeMap
"""

import bisect
from abc import ABC, abstractmethod
from typing import Any, Optional, List, Tuple, Union, Iterator, Literal

from bplus_tree import (
    BPlusTreeMap, Node, LeafNode, BranchNode,
    MIN_CAPACITY, DEFAULT_CAPACITY, InvalidCapacityError
)

__all__ = ["OptimizedBPlusTreeMap", "OptimizedLeafNode", "OptimizedBranchNode"]


class OptimizedLeafNode(Node):
    """Leaf node with single array optimization for better cache locality."""
    
    def __init__(self, capacity: int):
        super().__init__(capacity)
        self.num_keys = 0
        # Single array: keys[0:capacity], values[capacity:capacity*2]
        self.data = [None] * (capacity * 2)
        self.next: Optional['OptimizedLeafNode'] = None
    
    @property
    def keys(self) -> List[Any]:
        """Compatibility property for keys access."""
        return self.data[:self.num_keys]
    
    @property
    def values(self) -> List[Any]:
        """Compatibility property for values access."""
        return self.data[self.capacity:self.capacity + self.num_keys]
    
    def is_leaf(self) -> bool:
        return True
    
    def is_full(self) -> bool:
        return self.num_keys >= self.capacity
    
    def is_underfull(self) -> bool:
        return self.num_keys < self.min_keys
    
    def find_child_index(self, key: Any) -> int:
        """Binary search in keys portion of data array."""
        return bisect.bisect_right(self.data, key, 0, self.num_keys)
    
    def get_child(self, key: Any) -> 'OptimizedLeafNode':
        """Leaf nodes return themselves."""
        return self
    
    def insert(self, key: Any, value: Any) -> Optional[Tuple[Any, 'OptimizedLeafNode']]:
        """Insert key-value pair with single array optimization."""
        pos = bisect.bisect_left(self.data, key, 0, self.num_keys)
        
        # Update existing key
        if pos < self.num_keys and self.data[pos] == key:
            self.data[self.capacity + pos] = value
            return None
        
        # Check if split needed
        if self.num_keys >= self.capacity:
            # Split and insert
            new_node = OptimizedLeafNode(self.capacity)
            mid = self.capacity // 2
            
            # Build sorted arrays with new element
            all_keys = []
            all_values = []
            
            for i in range(pos):
                all_keys.append(self.data[i])
                all_values.append(self.data[self.capacity + i])
            
            all_keys.append(key)
            all_values.append(value)
            
            for i in range(pos, self.num_keys):
                all_keys.append(self.data[i])
                all_values.append(self.data[self.capacity + i])
            
            # Distribute to nodes
            self.num_keys = mid
            for i in range(mid):
                self.data[i] = all_keys[i]
                self.data[self.capacity + i] = all_values[i]
            
            # Clear unused slots
            for i in range(mid, self.capacity):
                self.data[i] = None
                self.data[self.capacity + i] = None
            
            new_node.num_keys = len(all_keys) - mid
            for i in range(new_node.num_keys):
                new_node.data[i] = all_keys[mid + i]
                new_node.data[new_node.capacity + i] = all_values[mid + i]
            
            # Update links
            new_node.next = self.next
            self.next = new_node
            
            return (new_node.data[0], new_node)
        
        # Regular insert - shift elements
        if pos < self.num_keys:
            # Shift keys
            for i in range(self.num_keys, pos, -1):
                self.data[i] = self.data[i - 1]
            # Shift values
            for i in range(self.num_keys, pos, -1):
                self.data[self.capacity + i] = self.data[self.capacity + i - 1]
        
        # Insert
        self.data[pos] = key
        self.data[self.capacity + pos] = value
        self.num_keys += 1
        return None
    
    def delete(self, key: Any) -> bool:
        """Delete key from leaf node."""
        pos = bisect.bisect_left(self.data, key, 0, self.num_keys)
        
        if pos >= self.num_keys or self.data[pos] != key:
            return False
        
        # Shift elements left
        for i in range(pos, self.num_keys - 1):
            self.data[i] = self.data[i + 1]
            self.data[self.capacity + i] = self.data[self.capacity + i + 1]
        
        # Clear last slot
        self.num_keys -= 1
        self.data[self.num_keys] = None
        self.data[self.capacity + self.num_keys] = None
        
        return True
    
    def get(self, key: Any) -> Optional[Any]:
        """Get value for key."""
        pos = bisect.bisect_left(self.data, key, 0, self.num_keys)
        if pos < self.num_keys and self.data[pos] == key:
            return self.data[self.capacity + pos]
        return None
    
    def merge_with_right(self, right_sibling: 'OptimizedLeafNode'):
        """Merge with right sibling."""
        # Copy from right sibling
        for i in range(right_sibling.num_keys):
            self.data[self.num_keys + i] = right_sibling.data[i]
            self.data[self.capacity + self.num_keys + i] = right_sibling.data[self.capacity + i]
        
        self.num_keys += right_sibling.num_keys
        self.next = right_sibling.next
    
    def redistribute_from_right(self, right_sibling: 'OptimizedLeafNode', parent_key: Any) -> Any:
        """Borrow from right sibling."""
        # Take first key-value from right
        self.data[self.num_keys] = right_sibling.data[0]
        self.data[self.capacity + self.num_keys] = right_sibling.data[self.capacity]
        self.num_keys += 1
        
        # Shift right sibling left
        right_sibling.num_keys -= 1
        for i in range(right_sibling.num_keys):
            right_sibling.data[i] = right_sibling.data[i + 1]
            right_sibling.data[self.capacity + i] = right_sibling.data[self.capacity + i + 1]
        
        # Clear last slot
        right_sibling.data[right_sibling.num_keys] = None
        right_sibling.data[self.capacity + right_sibling.num_keys] = None
        
        return right_sibling.data[0]


class OptimizedBranchNode(Node):
    """Branch node with single array optimization."""
    
    def __init__(self, capacity: int):
        super().__init__(capacity)
        self.num_keys = 0
        # Single array: keys[0:capacity], children[capacity:capacity*2+1]
        self.data = [None] * (capacity * 2 + 1)
    
    @property
    def keys(self) -> List[Any]:
        """Compatibility property for keys access."""
        return self.data[:self.num_keys]
    
    @property
    def children(self) -> List[Node]:
        """Compatibility property for children access."""
        return self.data[self.capacity:self.capacity + self.num_keys + 1]
    
    def is_leaf(self) -> bool:
        return False
    
    def is_full(self) -> bool:
        return self.num_keys >= self.capacity
    
    def is_underfull(self) -> bool:
        return self.num_keys < self.min_keys
    
    def find_child_index(self, key: Any) -> int:
        """Binary search for child index."""
        return bisect.bisect_right(self.data, key, 0, self.num_keys)
    
    def get_child(self, key: Any) -> Node:
        """Get child node for key."""
        index = self.find_child_index(key)
        return self.data[self.capacity + index]
    
    def insert(self, key: Any, right_child: Node) -> Optional[Tuple[Any, 'OptimizedBranchNode']]:
        """Insert key and right child."""
        pos = bisect.bisect_left(self.data, key, 0, self.num_keys)
        
        # Check if split needed
        if self.num_keys >= self.capacity:
            # Split and insert
            new_node = OptimizedBranchNode(self.capacity)
            mid = self.capacity // 2
            
            # Collect all elements
            all_keys = []
            all_children = [self.data[self.capacity]]  # First child
            
            for i in range(pos):
                all_keys.append(self.data[i])
                all_children.append(self.data[self.capacity + i + 1])
            
            all_keys.append(key)
            all_children.append(right_child)
            
            for i in range(pos, self.num_keys):
                all_keys.append(self.data[i])
                all_children.append(self.data[self.capacity + i + 1])
            
            # Split key
            split_key = all_keys[mid]
            
            # Update current node
            self.num_keys = mid
            for i in range(mid):
                self.data[i] = all_keys[i]
            for i in range(mid + 1):
                self.data[self.capacity + i] = all_children[i]
            
            # Clear unused
            for i in range(mid, self.capacity):
                self.data[i] = None
            for i in range(mid + 1, self.capacity + 1):
                self.data[self.capacity + i] = None
            
            # Fill new node
            new_node.num_keys = len(all_keys) - mid - 1
            for i in range(new_node.num_keys):
                new_node.data[i] = all_keys[mid + 1 + i]
            for i in range(new_node.num_keys + 1):
                new_node.data[new_node.capacity + i] = all_children[mid + 1 + i]
            
            return (split_key, new_node)
        
        # Regular insert - shift elements
        if pos < self.num_keys:
            # Shift keys
            for i in range(self.num_keys, pos, -1):
                self.data[i] = self.data[i - 1]
            # Shift children
            for i in range(self.num_keys + 1, pos + 1, -1):
                self.data[self.capacity + i] = self.data[self.capacity + i - 1]
        
        # Insert
        self.data[pos] = key
        self.data[self.capacity + pos + 1] = right_child
        self.num_keys += 1
        return None
    
    def delete_key_at_index(self, index: int):
        """Delete key at index."""
        # Shift keys left
        for i in range(index, self.num_keys - 1):
            self.data[i] = self.data[i + 1]
        
        # Shift children left
        for i in range(index + 1, self.num_keys):
            self.data[self.capacity + i] = self.data[self.capacity + i + 1]
        
        # Clear last slots
        self.num_keys -= 1
        self.data[self.num_keys] = None
        self.data[self.capacity + self.num_keys + 1] = None
    
    def merge_with_right(self, right_sibling: 'OptimizedBranchNode', separator_key: Any):
        """Merge with right sibling."""
        # Add separator key
        self.data[self.num_keys] = separator_key
        self.num_keys += 1
        
        # Copy keys from right
        for i in range(right_sibling.num_keys):
            self.data[self.num_keys + i] = right_sibling.data[i]
        
        # Copy children from right
        for i in range(right_sibling.num_keys + 1):
            self.data[self.capacity + self.num_keys + i] = right_sibling.data[self.capacity + i]
        
        self.num_keys += right_sibling.num_keys
    
    def redistribute_from_right(self, right_sibling: 'OptimizedBranchNode', separator_key: Any) -> Any:
        """Borrow from right sibling."""
        # Add separator as last key
        self.data[self.num_keys] = separator_key
        self.num_keys += 1
        
        # Take first child from right
        self.data[self.capacity + self.num_keys] = right_sibling.data[self.capacity]
        
        # New separator is first key from right
        new_separator = right_sibling.data[0]
        
        # Shift right sibling left
        right_sibling.num_keys -= 1
        for i in range(right_sibling.num_keys):
            right_sibling.data[i] = right_sibling.data[i + 1]
        for i in range(right_sibling.num_keys + 1):
            right_sibling.data[self.capacity + i] = right_sibling.data[self.capacity + i + 1]
        
        # Clear last slots
        right_sibling.data[right_sibling.num_keys] = None
        right_sibling.data[self.capacity + right_sibling.num_keys + 1] = None
        
        return new_separator


class OptimizedBPlusTreeMap(BPlusTreeMap):
    """B+ Tree with switchable node implementation."""
    
    def __init__(self, capacity: int = DEFAULT_CAPACITY, 
                 node_type: Literal["original", "optimized"] = "optimized"):
        """Initialize with specified node implementation.
        
        Args:
            capacity: Maximum keys per node
            node_type: Which node implementation to use
        """
        if capacity < MIN_CAPACITY:
            raise InvalidCapacityError(
                f"Capacity must be at least {MIN_CAPACITY}, got {capacity}"
            )
        
        self.capacity = capacity
        self.node_type = node_type
        
        # Create root with appropriate type
        if node_type == "optimized":
            self.root = OptimizedLeafNode(capacity)
            self._leaf_class = OptimizedLeafNode
            self._branch_class = OptimizedBranchNode
        else:
            self.root = LeafNode(capacity)
            self._leaf_class = LeafNode
            self._branch_class = BranchNode
        
        self.leaves = self.root
    
    def _create_leaf_node(self) -> Node:
        """Create a new leaf node of the appropriate type."""
        return self._leaf_class(self.capacity)
    
    def _create_branch_node(self) -> Node:
        """Create a new branch node of the appropriate type."""
        return self._branch_class(self.capacity)