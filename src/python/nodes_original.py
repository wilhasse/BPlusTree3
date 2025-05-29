"""
Original B+ Tree node implementations.
These use separate arrays for keys, values, and children.
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


class LeafNode(Node):
    """Leaf node containing key-value pairs."""

    def __init__(self, capacity: int):
        """Initialize leaf node.

        Args:
            capacity: Maximum number of keys this node can hold.
        """
        super().__init__(capacity)
        self.keys: List[Any] = []
        self.values: List[Any] = []
        self.next: Optional["LeafNode"] = None

    def is_leaf(self) -> bool:
        """Leaf nodes are always leaves."""
        return True

    def is_full(self) -> bool:
        """Check if leaf is full."""
        return len(self.keys) >= self.capacity

    def is_underfull(self) -> bool:
        """Check if leaf has too few keys."""
        return len(self.keys) < self.min_keys

    def find_child_index(self, key: Any) -> int:
        """Find position where key should be inserted."""
        return bisect.bisect_right(self.keys, key)

    def get_child(self, key: Any) -> "LeafNode":
        """Leaf nodes return themselves as they have no children."""
        return self

    def insert(self, key: Any, value: Any) -> Optional[Tuple[Any, "LeafNode"]]:
        """Insert key-value pair into leaf.

        Returns:
            None if no split occurred, or (split_key, new_node) if split.
        """
        index = bisect.bisect_left(self.keys, key)

        # Update existing key
        if index < len(self.keys) and self.keys[index] == key:
            self.values[index] = value
            return None

        # Check if split is needed
        if len(self.keys) >= self.capacity:
            # Create new node
            new_leaf = LeafNode(self.capacity)
            mid_index = self.capacity // 2

            # Determine where to insert the new key-value pair
            if index <= mid_index:
                # Insert in current node
                self.keys.insert(index, key)
                self.values.insert(index, value)
                # Move half to new node
                new_leaf.keys = self.keys[mid_index:]
                new_leaf.values = self.values[mid_index:]
                self.keys = self.keys[:mid_index]
                self.values = self.values[:mid_index]
            else:
                # Insert in new node
                new_leaf.keys = self.keys[mid_index:]
                new_leaf.values = self.values[mid_index:]
                self.keys = self.keys[:mid_index]
                self.values = self.values[:mid_index]
                insert_index = index - mid_index
                new_leaf.keys.insert(insert_index, key)
                new_leaf.values.insert(insert_index, value)

            # Update linked list pointers
            new_leaf.next = self.next
            self.next = new_leaf

            # Return split key (first key of new node) and new node
            return (new_leaf.keys[0], new_leaf)

        # Normal insert
        self.keys.insert(index, key)
        self.values.insert(index, value)
        return None

    def delete(self, key: Any) -> bool:
        """Delete key from leaf node.

        Returns:
            True if key was found and deleted, False otherwise.
        """
        try:
            index = self.keys.index(key)
            self.keys.pop(index)
            self.values.pop(index)
            return True
        except ValueError:
            return False

    def get(self, key: Any) -> Optional[Any]:
        """Get value for key in leaf node."""
        try:
            index = self.keys.index(key)
            return self.values[index]
        except ValueError:
            return None

    def merge_with_right(self, right_sibling: "LeafNode"):
        """Merge this node with its right sibling."""
        self.keys.extend(right_sibling.keys)
        self.values.extend(right_sibling.values)
        self.next = right_sibling.next

    def redistribute_from_right(
        self, right_sibling: "LeafNode", parent_key: Any
    ) -> Any:
        """Redistribute keys from right sibling to this node.

        Returns:
            The new separator key for the parent.
        """
        # Take first key-value from right sibling
        self.keys.append(right_sibling.keys.pop(0))
        self.values.append(right_sibling.values.pop(0))

        # Return new separator (first key of right sibling)
        return right_sibling.keys[0]


class BranchNode(Node):
    """Internal node containing keys and child pointers."""

    def __init__(self, capacity: int):
        """Initialize branch node.

        Args:
            capacity: Maximum number of keys this node can hold.
        """
        super().__init__(capacity)
        self.keys: List[Any] = []
        self.children: List[Node] = []

    def is_leaf(self) -> bool:
        """Branch nodes are never leaves."""
        return False

    def is_full(self) -> bool:
        """Check if branch is full."""
        return len(self.keys) >= self.capacity

    def is_underfull(self) -> bool:
        """Check if branch has too few keys."""
        return len(self.keys) < self.min_keys

    def find_child_index(self, key: Any) -> int:
        """Find index of child that should contain the key."""
        return bisect.bisect_right(self.keys, key)

    def get_child(self, key: Any) -> Node:
        """Get the child node that should contain the key."""
        index = self.find_child_index(key)
        return self.children[index]

    def insert(
        self, key: Any, right_child: Node
    ) -> Optional[Tuple[Any, "BranchNode"]]:
        """Insert key and right child into branch node.

        The right_child is the node to the right of the key.

        Returns:
            None if no split occurred, or (split_key, new_node) if split.
        """
        index = bisect.bisect_left(self.keys, key)

        # Check if split is needed
        if len(self.keys) >= self.capacity:
            # Create new node
            new_branch = BranchNode(self.capacity)
            mid_index = self.capacity // 2

            # Get the key that will be promoted
            if index <= mid_index:
                # Insert new key-child pair in current node
                self.keys.insert(index, key)
                self.children.insert(index + 1, right_child)

                # Promote middle key
                promoted_key = self.keys[mid_index]

                # Split keys and children
                new_branch.keys = self.keys[mid_index + 1 :]
                new_branch.children = self.children[mid_index + 1 :]
                self.keys = self.keys[:mid_index]
                self.children = self.children[: mid_index + 1]
            else:
                # Insert new key-child pair in new node
                promoted_index = index - mid_index - 1

                # Promote middle key
                promoted_key = self.keys[mid_index]

                # Split first
                new_branch.keys = self.keys[mid_index + 1 :]
                new_branch.children = self.children[mid_index + 1 :]
                self.keys = self.keys[:mid_index]
                self.children = self.children[: mid_index + 1]

                # Then insert in new node
                new_branch.keys.insert(promoted_index, key)
                new_branch.children.insert(promoted_index + 1, right_child)

            return (promoted_key, new_branch)

        # Normal insert
        self.keys.insert(index, key)
        self.children.insert(index + 1, right_child)
        return None

    def delete_key_at_index(self, index: int):
        """Delete key at given index and merge children."""
        self.keys.pop(index)
        # Remove the right child of the deleted key
        self.children.pop(index + 1)

    def merge_with_right(self, right_sibling: "BranchNode", separator_key: Any):
        """Merge this node with its right sibling using the separator key."""
        # Add separator key
        self.keys.append(separator_key)
        # Add all keys from right sibling
        self.keys.extend(right_sibling.keys)
        # Add all children from right sibling
        self.children.extend(right_sibling.children)

    def redistribute_from_right(
        self, right_sibling: "BranchNode", separator_key: Any
    ) -> Any:
        """Redistribute keys from right sibling to this node.

        Returns:
            The new separator key for the parent.
        """
        # Move separator key down to this node
        self.keys.append(separator_key)

        # Move first child from right sibling
        self.children.append(right_sibling.children.pop(0))

        # Move first key from right sibling up as new separator
        new_separator = right_sibling.keys.pop(0)

        return new_separator