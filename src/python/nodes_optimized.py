"""
Optimized B+ Tree node implementations with single array layout.
These use a single contiguous array for better cache locality.
"""

import bisect
from abc import ABC, abstractmethod
from typing import Any, Optional, List, Tuple, Union


class Node(ABC):
    """Abstract base class for B+ tree nodes."""

    def __init__(self, capacity: int):
        """Initialize node with given capacity.

        Args:
            capacity: Maximum number of keys this node can hold.
        """
        self.capacity = capacity
        self.min_keys = capacity // 2

    @abstractmethod
    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        pass

    @abstractmethod
    def is_full(self) -> bool:
        """Check if node is full."""
        pass

    @abstractmethod
    def is_underfull(self) -> bool:
        """Check if node has too few keys."""
        pass

    @abstractmethod
    def find_child_index(self, key: Any) -> int:
        """Find index of child that should contain the key."""
        pass

    @abstractmethod
    def get_child(self, key: Any) -> "Node":
        """Get the child node that should contain the key."""
        pass


class OptimizedLeafNode(Node):
    """Leaf node with single array for better cache locality.
    
    Array layout: [keys..., values...]
    Keys are stored in data[0:capacity]
    Values are stored in data[capacity:capacity*2]
    """

    def __init__(self, capacity: int):
        """Initialize optimized leaf node."""
        super().__init__(capacity)
        self.num_keys = 0
        self.data = [None] * (capacity * 2)
        self.next: Optional["OptimizedLeafNode"] = None

    @property
    def keys(self) -> List[Any]:
        """Compatibility property for keys access."""
        return self.data[:self.num_keys]

    @property
    def values(self) -> List[Any]:
        """Compatibility property for values access."""
        return self.data[self.capacity:self.capacity + self.num_keys]

    def is_leaf(self) -> bool:
        """Leaf nodes are always leaves."""
        return True

    def is_full(self) -> bool:
        """Check if leaf is full."""
        return self.num_keys >= self.capacity

    def is_underfull(self) -> bool:
        """Check if leaf has too few keys."""
        return self.num_keys < self.min_keys

    def find_child_index(self, key: Any) -> int:
        """Find position where key should be inserted."""
        return bisect.bisect_right(self.data, key, 0, self.num_keys)

    def get_child(self, key: Any) -> "OptimizedLeafNode":
        """Leaf nodes return themselves as they have no children."""
        return self

    def _get_key(self, index: int) -> Any:
        """Get key at index."""
        return self.data[index]

    def _get_value(self, index: int) -> Any:
        """Get value at index."""
        return self.data[self.capacity + index]

    def _set_key(self, index: int, key: Any):
        """Set key at index."""
        self.data[index] = key

    def _set_value(self, index: int, value: Any):
        """Set value at index."""
        self.data[self.capacity + index] = value

    def insert(self, key: Any, value: Any) -> Optional[Tuple[Any, "OptimizedLeafNode"]]:
        """Insert key-value pair into leaf."""
        index = bisect.bisect_left(self.data, key, 0, self.num_keys)

        # Update existing key
        if index < self.num_keys and self.data[index] == key:
            self.data[self.capacity + index] = value
            return None

        # Check if split is needed
        if self.num_keys >= self.capacity:
            # Create new node
            new_leaf = OptimizedLeafNode(self.capacity)
            mid_index = self.capacity // 2

            # Build sorted arrays with new element
            all_keys = []
            all_values = []

            # Add elements before insertion point
            for i in range(index):
                all_keys.append(self.data[i])
                all_values.append(self.data[self.capacity + i])

            # Add new element
            all_keys.append(key)
            all_values.append(value)

            # Add remaining elements
            for i in range(index, self.num_keys):
                all_keys.append(self.data[i])
                all_values.append(self.data[self.capacity + i])

            # Distribute to nodes
            self.num_keys = mid_index
            for i in range(mid_index):
                self.data[i] = all_keys[i]
                self.data[self.capacity + i] = all_values[i]

            # Clear unused slots in current node
            for i in range(mid_index, self.capacity):
                self.data[i] = None
                self.data[self.capacity + i] = None

            # Fill new node
            new_leaf.num_keys = len(all_keys) - mid_index
            for i in range(new_leaf.num_keys):
                new_leaf.data[i] = all_keys[mid_index + i]
                new_leaf.data[new_leaf.capacity + i] = all_values[mid_index + i]

            # Update linked list pointers
            new_leaf.next = self.next
            self.next = new_leaf

            # Return split key and new node
            return (new_leaf.data[0], new_leaf)

        # Normal insert - shift elements
        for i in range(self.num_keys, index, -1):
            self.data[i] = self.data[i - 1]
            self.data[self.capacity + i] = self.data[self.capacity + i - 1]

        # Insert new element
        self.data[index] = key
        self.data[self.capacity + index] = value
        self.num_keys += 1
        return None

    def delete(self, key: Any) -> bool:
        """Delete key from leaf node."""
        index = bisect.bisect_left(self.data, key, 0, self.num_keys)

        if index >= self.num_keys or self.data[index] != key:
            return False

        # Shift elements left
        for i in range(index, self.num_keys - 1):
            self.data[i] = self.data[i + 1]
            self.data[self.capacity + i] = self.data[self.capacity + i + 1]

        # Clear last slot
        self.num_keys -= 1
        self.data[self.num_keys] = None
        self.data[self.capacity + self.num_keys] = None

        return True

    def get(self, key: Any) -> Optional[Any]:
        """Get value for key in leaf node."""
        index = bisect.bisect_left(self.data, key, 0, self.num_keys)
        if index < self.num_keys and self.data[index] == key:
            return self.data[self.capacity + index]
        return None

    def merge_with_right(self, right_sibling: "OptimizedLeafNode"):
        """Merge this node with its right sibling."""
        # Copy keys and values from right sibling
        for i in range(right_sibling.num_keys):
            self.data[self.num_keys + i] = right_sibling.data[i]
            self.data[self.capacity + self.num_keys + i] = right_sibling.data[self.capacity + i]

        self.num_keys += right_sibling.num_keys
        self.next = right_sibling.next

    def redistribute_from_right(self, right_sibling: "OptimizedLeafNode", parent_key: Any) -> Any:
        """Redistribute keys from right sibling to this node."""
        # Take first key-value from right sibling
        self.data[self.num_keys] = right_sibling.data[0]
        self.data[self.capacity + self.num_keys] = right_sibling.data[self.capacity]
        self.num_keys += 1

        # Shift right sibling left
        right_sibling.num_keys -= 1
        for i in range(right_sibling.num_keys):
            right_sibling.data[i] = right_sibling.data[i + 1]
            right_sibling.data[self.capacity + i] = right_sibling.data[self.capacity + i + 1]

        # Clear last slot in right sibling
        right_sibling.data[right_sibling.num_keys] = None
        right_sibling.data[self.capacity + right_sibling.num_keys] = None

        # Return new separator
        return right_sibling.data[0]


class OptimizedBranchNode(Node):
    """Branch node with single array for better cache locality.
    
    Array layout: [keys..., children...]
    Keys are stored in data[0:capacity]
    Children are stored in data[capacity:capacity*2+1]
    Note: There's always one more child than keys
    """

    def __init__(self, capacity: int):
        """Initialize optimized branch node."""
        super().__init__(capacity)
        self.num_keys = 0
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
        """Branch nodes are never leaves."""
        return False

    def is_full(self) -> bool:
        """Check if branch is full."""
        return self.num_keys >= self.capacity

    def is_underfull(self) -> bool:
        """Check if branch has too few keys."""
        return self.num_keys < self.min_keys

    def find_child_index(self, key: Any) -> int:
        """Find index of child that should contain the key."""
        return bisect.bisect_right(self.data, key, 0, self.num_keys)

    def get_child(self, key: Any) -> Node:
        """Get the child node that should contain the key."""
        index = self.find_child_index(key)
        return self.data[self.capacity + index]

    def _get_key(self, index: int) -> Any:
        """Get key at index."""
        return self.data[index]

    def _get_child(self, index: int) -> Node:
        """Get child at index."""
        return self.data[self.capacity + index]

    def _set_key(self, index: int, key: Any):
        """Set key at index."""
        self.data[index] = key

    def _set_child(self, index: int, child: Node):
        """Set child at index."""
        self.data[self.capacity + index] = child

    def insert(self, key: Any, right_child: Node) -> Optional[Tuple[Any, "OptimizedBranchNode"]]:
        """Insert key and right child into branch node."""
        index = bisect.bisect_left(self.data, key, 0, self.num_keys)

        # Check if split is needed
        if self.num_keys >= self.capacity:
            # Create new node
            new_branch = OptimizedBranchNode(self.capacity)
            mid_index = self.capacity // 2

            # Collect all keys and children
            all_keys = []
            all_children = [self.data[self.capacity]]  # First child

            # Add existing elements
            for i in range(index):
                all_keys.append(self.data[i])
                all_children.append(self.data[self.capacity + i + 1])

            # Add new element
            all_keys.append(key)
            all_children.append(right_child)

            # Add remaining elements
            for i in range(index, self.num_keys):
                all_keys.append(self.data[i])
                all_children.append(self.data[self.capacity + i + 1])

            # Get promoted key
            promoted_key = all_keys[mid_index]

            # Update current node
            self.num_keys = mid_index
            for i in range(mid_index):
                self.data[i] = all_keys[i]
            for i in range(mid_index + 1):
                self.data[self.capacity + i] = all_children[i]

            # Clear unused slots
            for i in range(mid_index, self.capacity):
                self.data[i] = None
            for i in range(mid_index + 1, self.capacity + 1):
                self.data[self.capacity + i] = None

            # Fill new node
            new_branch.num_keys = len(all_keys) - mid_index - 1
            for i in range(new_branch.num_keys):
                new_branch.data[i] = all_keys[mid_index + 1 + i]
            for i in range(new_branch.num_keys + 1):
                new_branch.data[new_branch.capacity + i] = all_children[mid_index + 1 + i]

            return (promoted_key, new_branch)

        # Normal insert - shift elements
        for i in range(self.num_keys, index, -1):
            self.data[i] = self.data[i - 1]
        for i in range(self.num_keys + 1, index + 1, -1):
            self.data[self.capacity + i] = self.data[self.capacity + i - 1]

        # Insert new element
        self.data[index] = key
        self.data[self.capacity + index + 1] = right_child
        self.num_keys += 1
        return None

    def delete_key_at_index(self, index: int):
        """Delete key at given index and merge children."""
        # Shift keys left
        for i in range(index, self.num_keys - 1):
            self.data[i] = self.data[i + 1]

        # Shift children left (remove right child of deleted key)
        for i in range(index + 1, self.num_keys):
            self.data[self.capacity + i] = self.data[self.capacity + i + 1]

        # Clear last slots
        self.num_keys -= 1
        self.data[self.num_keys] = None
        self.data[self.capacity + self.num_keys + 1] = None

    def merge_with_right(self, right_sibling: "OptimizedBranchNode", separator_key: Any):
        """Merge this node with its right sibling using the separator key."""
        # Add separator key
        self.data[self.num_keys] = separator_key
        self.num_keys += 1

        # Copy keys from right sibling
        for i in range(right_sibling.num_keys):
            self.data[self.num_keys + i] = right_sibling.data[i]

        # Copy children from right sibling
        for i in range(right_sibling.num_keys + 1):
            self.data[self.capacity + self.num_keys + i] = right_sibling.data[self.capacity + i]

        self.num_keys += right_sibling.num_keys

    def redistribute_from_right(self, right_sibling: "OptimizedBranchNode", separator_key: Any) -> Any:
        """Redistribute keys from right sibling to this node."""
        # Move separator key down to this node
        self.data[self.num_keys] = separator_key
        self.num_keys += 1

        # Move first child from right sibling
        self.data[self.capacity + self.num_keys] = right_sibling.data[self.capacity]

        # New separator is first key from right sibling
        new_separator = right_sibling.data[0]

        # Shift right sibling left
        right_sibling.num_keys -= 1
        for i in range(right_sibling.num_keys):
            right_sibling.data[i] = right_sibling.data[i + 1]
        for i in range(right_sibling.num_keys + 1):
            right_sibling.data[self.capacity + i] = right_sibling.data[self.capacity + i + 1]

        # Clear last slots in right sibling
        right_sibling.data[right_sibling.num_keys] = None
        right_sibling.data[self.capacity + right_sibling.num_keys + 1] = None

        return new_separator