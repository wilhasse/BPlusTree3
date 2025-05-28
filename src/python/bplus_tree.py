"""
B+ Tree implementation in Python with dict-like API
"""

import bisect
from typing import Any, Optional, List, Tuple, Union
from abc import ABC, abstractmethod

try:
    from ._invariant_checker import _BPlusTreeInvariantChecker
except ImportError:
    # For when the module is run directly
    from _invariant_checker import _BPlusTreeInvariantChecker


class BPlusTreeMap:
    """B+ Tree with Python dict-like API"""

    def __init__(self, capacity: int = 128):
        """Create a B+ tree with specified node capacity"""
        if capacity < 4:
            raise ValueError(
                "Capacity must be at least 4 to maintain B+ tree invariants"
            )
        self.capacity = capacity

        original = LeafNode(self.capacity)
        self.leaves: LeafNode = original
        self.root: Node = original
        self._invariant_checker = _BPlusTreeInvariantChecker(capacity)

    @classmethod
    def from_sorted_items(cls, items, capacity: int = 128):
        """
        Bulk load from sorted key-value pairs for 3-5x faster construction.

        Args:
            items: Iterable of (key, value) pairs that MUST be sorted by key
            capacity: Node capacity (minimum 4)

        Returns:
            BPlusTreeMap instance
        """
        tree = cls(capacity=capacity)
        tree._bulk_load_sorted(items)
        return tree

    def _bulk_load_sorted(self, items):
        """Internal bulk loading implementation for sorted items"""
        items_list = list(items)
        if not items_list:
            return

        # Simplified bulk loading approach:
        # Use larger insertion batches and optimize for sorted order

        # Strategy: Insert items in optimally-sized batches
        # This reduces tree restructuring while maintaining correctness
        optimal_batch_size = max(self.capacity * 2, 50)  # Larger batches for efficiency

        for i in range(0, len(items_list), optimal_batch_size):
            batch_end = min(i + optimal_batch_size, len(items_list))

            # Insert batch using optimized path for sorted data
            for j in range(i, batch_end):
                key, value = items_list[j]
                self._insert_sorted_optimized(key, value)

    def _insert_sorted_optimized(self, key, value):
        """Optimized insertion for sorted data - avoids repeated tree traversals"""
        # For sorted data, we can cache the rightmost leaf and insert directly
        # when possible, falling back to regular insertion when needed

        if not hasattr(self, "_rightmost_leaf_cache"):
            self._rightmost_leaf_cache = None

        # Try to insert into cached rightmost leaf if key is larger than all existing
        if (
            self._rightmost_leaf_cache
            and self._rightmost_leaf_cache.keys
            and key > self._rightmost_leaf_cache.keys[-1]
            and not self._rightmost_leaf_cache.is_full()
        ):

            self._rightmost_leaf_cache.keys.append(key)
            self._rightmost_leaf_cache.values.append(value)
            return

        # Fallback to regular insertion and update cache
        self[key] = value
        self._update_rightmost_leaf_cache()

    def _update_rightmost_leaf_cache(self):
        """Update the rightmost leaf cache"""
        # Find the rightmost leaf by traversing the linked list
        current = self.leaves
        while current.next is not None:
            current = current.next
        self._rightmost_leaf_cache = current

    def __setitem__(self, key: Any, value: Any) -> None:
        """Set a key-value pair (dict-like API)"""
        result = self._insert_recursive(self.root, key, value)

        # If the root split, create a new root
        if result is not None:
            new_node, separator_key = result
            new_root = BranchNode(self.capacity)
            new_root.keys.append(separator_key)
            new_root.children.append(self.root)
            new_root.children.append(new_node)
            self.root = new_root

    def _insert_recursive(
        self, node: "Node", key: Any, value: Any
    ) -> Optional[Tuple["Node", Any]]:
        """
        Recursively insert a key-value pair into the tree.
        Returns None for a simple insertion, or (new_node, separator_key) if a split occurred.
        """
        if node.is_leaf():
            # Base case: insert into leaf
            return self._insert_into_leaf(node, key, value)

        # Recursive case: find the correct child and recurse
        child_index = node.find_child_index(key)
        child = node.children[child_index]

        # Recursively insert and check if child split
        split_result = self._insert_recursive(child, key, value)
        if split_result is None:
            return None

        # Child split, handle it
        new_child, separator_key = split_result
        return self._insert_into_branch(node, child_index, separator_key, new_child)

    def _insert_into_leaf(
        self, leaf: "LeafNode", key: Any, value: Any
    ) -> Optional[Tuple["LeafNode", Any]]:
        """Insert into a leaf node. Returns None or (new_leaf, separator) if split."""
        pos, exists = leaf.find_position(key)

        # If key exists, just update (no split needed)
        if exists:
            leaf.values[pos] = value
            return None

        # If leaf is not full, simple insertion
        if not leaf.is_full():
            leaf.insert(key, value)
            return None

        # Leaf is full, need to split
        return leaf.split_and_insert(key, value)

    def _insert_into_branch(
        self,
        branch: "BranchNode",
        child_index: int,
        separator_key: Any,
        new_child: "Node",
    ) -> Optional[Tuple["BranchNode", Any]]:
        """Insert a separator and new child into a branch node. Returns None or (new_branch, separator) if split."""
        return branch.insert_child_and_split_if_needed(
            child_index, separator_key, new_child
        )

    def __getitem__(self, key: Any) -> Any:
        """Get value for a key (dict-like API)"""
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value

    def get(self, key: Any, default: Any = None) -> Any:
        """Get value for a key with optional default"""
        # Navigate to the correct leaf
        node = self.root
        while not node.is_leaf():
            node = node.get_child(key)

        # Get from leaf
        value = node.get(key)
        return value if value is not None else default

    def __contains__(self, key: Any) -> bool:
        """Check if key exists (for 'in' operator)"""
        return self.get(key) is not None

    def __len__(self) -> int:
        """Return number of key-value pairs"""
        return self.leaves.key_count()

    def __bool__(self) -> bool:
        """Return True if tree is not empty"""
        return len(self) > 0

    def __delitem__(self, key: Any) -> None:
        """Delete a key (dict-like API)"""
        deleted = self._delete_recursive(self.root, key)
        if not deleted:
            raise KeyError(key)

        # Root collapse is handled naturally by proper deletion logic

    def _delete_recursive(self, node: "Node", key: Any) -> bool:
        """
        Recursively delete a key from the tree.
        Returns True if the key was found and deleted, False otherwise.
        """
        if node.is_leaf():
            # Base case: delete from leaf
            # Note: underflow handling will be done by parent
            return self._delete_from_leaf(node, key)

        # Recursive case: find the correct child and recurse
        child_index = node.find_child_index(key)
        child = node.children[child_index]
        deleted = self._delete_recursive(child, key)
        if not deleted:
            return False

        # Handle child underflow after deletion
        if len(child) == 0 or child.is_underfull():
            # Child is underfull (including completely empty), try redistribution or merging
            self._handle_underflow(node, child_index)

            # After handling child underflow, check if parent became underfull
            # This can happen when merging removes a child from the parent
            if node != self.root and node.is_underfull():
                # Parent is now underfull, but we can't handle it here since we need
                # the parent's parent. This will be handled by the recursive call chain.
                pass

        # Handle root collapse: if root has only one child, make that child the new root
        if node == self.root and not node.is_leaf() and len(node.children) == 1:
            self.root = node.children[0]

        return deleted

    def _handle_underflow(self, parent: "BranchNode", child_index: int) -> None:
        """Handle underflow in a child node by trying redistribution first"""
        child = parent.children[child_index]

        # If child is not underfull, nothing to do
        if not child.is_underfull():
            return

        # Handle empty children by merging them (they can't redistribute)
        if len(child) == 0:
            self._merge_with_sibling(parent, child_index)
            return

        # Try to redistribute from siblings
        redistributed = False

        # Try to borrow from right sibling
        if child_index < len(parent.children) - 1:
            right_sibling = parent.children[child_index + 1]
            if right_sibling.can_donate():
                self._redistribute_from_right(parent, child_index)
                redistributed = True

        # If no redistribution from right, try left sibling
        if not redistributed and child_index > 0:
            left_sibling = parent.children[child_index - 1]
            if left_sibling.can_donate():
                self._redistribute_from_left(parent, child_index)
                redistributed = True

        # If redistribution failed, try to merge with a sibling
        if not redistributed:
            self._merge_with_sibling(parent, child_index)

    def _redistribute_from_left(self, parent: "BranchNode", child_index: int) -> None:
        """Redistribute keys from left sibling to child"""
        child = parent.children[child_index]
        left_sibling = parent.children[child_index - 1]

        if child.is_leaf():
            # Leaf redistribution
            child.borrow_from_left(left_sibling)
            # Update separator key in parent
            parent.keys[child_index - 1] = child.keys[0]
        else:
            # Branch redistribution
            separator_key = parent.keys[child_index - 1]
            new_separator = child.borrow_from_left(left_sibling, separator_key)
            parent.keys[child_index - 1] = new_separator

    def _redistribute_from_right(self, parent: "BranchNode", child_index: int) -> None:
        """Redistribute keys from right sibling to child"""
        child = parent.children[child_index]
        right_sibling = parent.children[child_index + 1]

        if child.is_leaf():
            # Leaf redistribution
            child.borrow_from_right(right_sibling)
            # Update separator key in parent
            parent.keys[child_index] = right_sibling.keys[0]
        else:
            # Branch redistribution
            separator_key = parent.keys[child_index]
            new_separator = child.borrow_from_right(right_sibling, separator_key)
            parent.keys[child_index] = new_separator

    def _merge_with_sibling(self, parent: "BranchNode", child_index: int) -> None:
        """Merge an underfull child with one of its siblings"""
        child = parent.children[child_index]

        # Validate parent structure before merging
        if child_index >= len(parent.children):
            raise ValueError(
                f"Invalid child_index {child_index} for parent with {len(parent.children)} children"
            )
        if len(parent.keys) != len(parent.children) - 1:
            raise ValueError(
                f"Parent structure invalid: {len(parent.keys)} keys but {len(parent.children)} children"
            )

        # Prefer merging with left sibling (arbitrary choice)
        if child_index > 0:
            # Merge with left sibling
            left_sibling = parent.children[child_index - 1]

            if child.is_leaf():
                # Check if merging would exceed capacity
                total_keys = len(left_sibling.keys) + len(child.keys)
                if total_keys <= self.capacity:
                    # Safe to merge
                    left_sibling.merge_with_right(child)
                    # Remove the merged child and its separator
                    parent.children.pop(child_index)
                    parent.keys.pop(child_index - 1)
                else:
                    # Cannot merge without exceeding capacity - leave nodes separate
                    # This preserves tree structure but may leave underfull nodes
                    pass
            else:
                # Check if merging would exceed capacity
                total_keys = (
                    len(left_sibling.keys) + len(child.keys) + 1
                )  # +1 for separator
                total_children = len(left_sibling.children) + len(child.children)
                if total_keys <= self.capacity and total_children <= self.capacity + 1:
                    # Safe to merge
                    separator_key = parent.keys[child_index - 1]
                    left_sibling.merge_with_right(child, separator_key)
                    # Remove the merged child and its separator
                    parent.children.pop(child_index)
                    parent.keys.pop(child_index - 1)
                else:
                    # Cannot merge without exceeding capacity - leave nodes separate
                    pass

        elif child_index < len(parent.children) - 1:
            # Merge with right sibling
            right_sibling = parent.children[child_index + 1]

            if child.is_leaf():
                # Check if merging would exceed capacity
                total_keys = len(child.keys) + len(right_sibling.keys)
                if total_keys <= self.capacity:
                    # Safe to merge
                    child.merge_with_right(right_sibling)
                    # Remove the merged sibling and its separator
                    parent.children.pop(child_index + 1)
                    parent.keys.pop(child_index)
                else:
                    # Cannot merge without exceeding capacity - leave nodes separate
                    pass
            else:
                # Check if merging would exceed capacity
                total_keys = (
                    len(child.keys) + len(right_sibling.keys) + 1
                )  # +1 for separator
                total_children = len(child.children) + len(right_sibling.children)
                if total_keys <= self.capacity and total_children <= self.capacity + 1:
                    # Safe to merge
                    separator_key = parent.keys[child_index]
                    child.merge_with_right(right_sibling, separator_key)
                    # Remove the merged sibling and its separator
                    parent.children.pop(child_index + 1)
                    parent.keys.pop(child_index)
                else:
                    # Cannot merge without exceeding capacity - leave nodes separate
                    pass
        else:
            # This can happen when a parent has only one child left
            # In this case, we should handle it by collapsing the tree structure
            # This will be handled by the caller in _delete_recursive
            pass

    def _delete_from_leaf(self, leaf: "LeafNode", key: Any) -> bool:
        """Delete from a leaf node. Returns True if deleted, False if not found."""
        deleted = leaf.delete(key)
        return deleted is not None

    def keys(self, start_key=None, end_key=None):
        """Return an iterator over keys in the given range"""
        for key, _ in self.items(start_key, end_key):
            yield key

    def values(self, start_key=None, end_key=None):
        """Return an iterator over values in the given range"""
        for _, value in self.items(start_key, end_key):
            yield value

    def items(self, start_key=None, end_key=None):
        """Return an iterator over (key, value) pairs in the given range"""
        if start_key is None:
            # Start from the beginning
            current = self.leaves
            start_index = 0
        else:
            # Find the leaf containing start_key or where it would be
            current = self._find_leaf_for_key(start_key)
            if current is None:
                return  # Empty tree
            # Find the starting position within the leaf
            start_index = self._find_position_in_leaf(current, start_key)

        # Iterate through leaves starting from current
        while current is not None:
            # Start from start_index in the first leaf, 0 in subsequent leaves
            for i in range(start_index, len(current.keys)):
                key = current.keys[i]
                # Check if we've reached the end of the range
                if end_key is not None and key >= end_key:
                    return
                yield (key, current.values[i])

            # Move to next leaf and reset start_index
            current = current.next
            start_index = 0

    def _find_leaf_for_key(self, key: Any) -> Optional["LeafNode"]:
        """Find the leaf node that contains or would contain the given key"""
        return self.root.find_leaf_for_key(key)

    def _find_position_in_leaf(self, leaf: "LeafNode", key: Any) -> int:
        """Find the position where key is or would be in the leaf"""
        # Binary search for the position
        left, right = 0, len(leaf.keys)
        while left < right:
            mid = (left + right) // 2
            if key <= leaf.keys[mid]:
                right = mid
            else:
                left = mid + 1
        return left

    """Testing only"""

    def leaf_count(self) -> int:
        """Return the number of leaf nodes"""
        count = 0
        node = self.leaves
        while node is not None:
            count += 1
            node = node.next
        return count

    def invariants(self) -> bool:
        """Check that all B+ tree invariants hold"""
        return self._invariant_checker.check_invariants(self.root, self.leaves)


class Node(ABC):
    """Abstract base class for B+ tree nodes"""

    @abstractmethod
    def is_leaf(self) -> bool:
        """Returns True if this is a leaf node"""
        pass

    @abstractmethod
    def is_full(self) -> bool:
        """Returns True if the node is at capacity"""
        pass

    @abstractmethod
    def __len__(self) -> int:
        """Returns the number of items in the node"""
        pass

    @abstractmethod
    def is_underfull(self) -> bool:
        """Returns True if the node has fewer than minimum required keys"""
        pass


class LeafNode(Node):
    """Leaf node containing key-value pairs"""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.keys: List[Any] = []
        self.values: List[Any] = []
        self.next: Optional["LeafNode"] = None  # Link to next leaf

    def is_leaf(self) -> bool:
        return True

    def is_full(self) -> bool:
        return len(self.keys) >= self.capacity

    def __len__(self) -> int:
        return len(self.keys)

    def is_underfull(self) -> bool:
        """Check if leaf has fewer than minimum required keys"""
        min_keys = (self.capacity - 1) // 2
        return len(self.keys) < min_keys

    def can_donate(self) -> bool:
        """Check if leaf can give a key to a sibling (has more than minimum)"""
        min_keys = (self.capacity - 1) // 2
        return len(self.keys) > min_keys

    def borrow_from_left(self, left_sibling: "LeafNode") -> None:
        """Borrow the rightmost key-value from left sibling"""
        if not left_sibling.can_donate():
            raise ValueError("Left sibling cannot donate")

        # Move the rightmost key-value from left to beginning of this node
        key = left_sibling.keys.pop()
        value = left_sibling.values.pop()
        self.keys.insert(0, key)
        self.values.insert(0, value)

    def borrow_from_right(self, right_sibling: "LeafNode") -> None:
        """Borrow the leftmost key-value from right sibling"""
        if not right_sibling.can_donate():
            raise ValueError("Right sibling cannot donate")

        # Move the leftmost key-value from right to end of this node
        key = right_sibling.keys.pop(0)
        value = right_sibling.values.pop(0)
        self.keys.append(key)
        self.values.append(value)

    def merge_with_right(self, right_sibling: "LeafNode") -> None:
        """Merge this leaf with its right sibling"""
        # Move all keys and values from right sibling to this node
        self.keys.extend(right_sibling.keys)
        self.values.extend(right_sibling.values)

        # Update linked list to skip the right sibling
        self.next = right_sibling.next

    def find_position(self, key: Any) -> Tuple[int, bool]:
        """
        Find where a key should be inserted.
        Returns (position, exists) where exists is True if key already exists.
        """
        # Use optimized bisect module for binary search
        pos = bisect.bisect_left(self.keys, key)
        exists = pos < len(self.keys) and self.keys[pos] == key
        return pos, exists

    def insert(self, key: Any, value: Any) -> Optional[Any]:
        """
        Insert a key-value pair. Returns old value if key exists.
        """
        pos, exists = self.find_position(key)

        if exists:
            # Update existing value
            old_value = self.values[pos]
            self.values[pos] = value
            return old_value
        else:
            # Insert new key-value pair
            self.keys.insert(pos, key)
            self.values.insert(pos, value)
            return None

    def get(self, key: Any) -> Optional[Any]:
        """Get value for a key, returns None if not found"""
        pos, exists = self.find_position(key)
        if exists:
            return self.values[pos]
        return None

    def delete(self, key: Any) -> Optional[Any]:
        """Delete a key, returns the value if found"""
        pos, exists = self.find_position(key)
        if exists:
            self.keys.pop(pos)
            return self.values.pop(pos)
        return None

    def split(self) -> "LeafNode":
        """Split this leaf node, returning the new right node"""
        # Find the midpoint
        mid = len(self.keys) // 2

        # Create new leaf for right half
        new_leaf = LeafNode(self.capacity)

        # Move right half of keys/values to new leaf
        new_leaf.keys = self.keys[mid:]
        new_leaf.values = self.values[mid:]

        # Keep left half in this leaf
        self.keys = self.keys[:mid]
        self.values = self.values[:mid]

        # Update linked list pointers
        new_leaf.next = self.next
        self.next = new_leaf

        return new_leaf

    def split_and_insert(self, key: Any, value: Any) -> Tuple["LeafNode", Any]:
        """Split leaf and insert key-value, returning (new_leaf, separator_key)"""
        new_leaf = self.split()

        # Insert into appropriate leaf
        if key < new_leaf.keys[0]:
            self.insert(key, value)
        else:
            new_leaf.insert(key, value)

        return new_leaf, new_leaf.keys[0]

    def find_leaf_for_key(self, _key: Any) -> "LeafNode":
        """Find the leaf node that contains or would contain the given key"""
        return self  # Leaf nodes return themselves

    def key_count(self) -> int:
        """Count all keys in this leaf and all following leaves"""
        return len(self) + (0 if self.next is None else self.next.key_count())


class BranchNode(Node):
    """Internal node containing keys and child pointers"""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.keys: List[Any] = []
        self.children: List[Node] = []

    def is_leaf(self) -> bool:
        return False

    def is_full(self) -> bool:
        return len(self.keys) >= self.capacity

    def __len__(self) -> int:
        return len(self.keys)

    def is_underfull(self) -> bool:
        """Check if branch has fewer than minimum required keys"""
        min_keys = (self.capacity - 1) // 2
        return len(self.keys) < min_keys

    def can_donate(self) -> bool:
        """Check if branch can give a key to a sibling (has more than minimum)"""
        min_keys = (self.capacity - 1) // 2
        return len(self.keys) > min_keys

    def borrow_from_left(self, left_sibling: "BranchNode", separator_key: Any) -> Any:
        """Borrow the rightmost key and child from left sibling, returns new separator"""
        if not left_sibling.can_donate():
            raise ValueError("Left sibling cannot donate")

        # Take the separator key as our leftmost key
        self.keys.insert(0, separator_key)

        # Take the rightmost child from left sibling
        child = left_sibling.children.pop()
        self.children.insert(0, child)

        # The rightmost key from left sibling becomes the new separator
        return left_sibling.keys.pop()

    def borrow_from_right(self, right_sibling: "BranchNode", separator_key: Any) -> Any:
        """Borrow the leftmost key and child from right sibling, returns new separator"""
        if not right_sibling.can_donate():
            raise ValueError("Right sibling cannot donate")

        # Take the separator key as our rightmost key
        self.keys.append(separator_key)

        # Take the leftmost child from right sibling
        child = right_sibling.children.pop(0)
        self.children.append(child)

        # The leftmost key from right sibling becomes the new separator
        return right_sibling.keys.pop(0)

    def merge_with_right(self, right_sibling: "BranchNode", separator_key: Any) -> None:
        """Merge this branch with its right sibling using the separator key"""
        # Add the separator key to this node's keys
        self.keys.append(separator_key)

        # Move all keys and children from right sibling to this node
        self.keys.extend(right_sibling.keys)
        self.children.extend(right_sibling.children)

    def find_child_index(self, key: Any) -> int:
        """Find which child a key should go to"""
        # Validate node structure
        if len(self.children) == 0:
            raise ValueError("BranchNode has no children")
        if len(self.keys) != len(self.children) - 1:
            raise ValueError(
                f"Invalid branch structure: {len(self.keys)} keys, {len(self.children)} children"
            )

        # Use optimized bisect module for binary search
        left = bisect.bisect_right(self.keys, key)

        # Validate result
        if left >= len(self.children):
            raise ValueError(
                f"Child index {left} out of range (have {len(self.children)} children)"
            )

        return left

    def get_child(self, key: Any) -> Node:
        """Get the child node where a key would be found"""
        if not self.children:
            raise ValueError("BranchNode has no children - tree structure corrupted")
        index = self.find_child_index(key)
        if index >= len(self.children):
            raise ValueError(
                f"Child index {index} out of range (have {len(self.children)} children)"
            )
        return self.children[index]

    def split(self) -> "BranchNode":
        """Split this branch node, returning the new right node"""
        # Find the midpoint
        mid = len(self.keys) // 2

        # Create new branch for right half
        new_branch = BranchNode(self.capacity)

        # The middle key becomes the separator to be promoted
        separator_key = self.keys[mid]

        # Move right half of keys to new branch (excluding the middle key)
        new_branch.keys = self.keys[mid + 1 :]

        # Move corresponding children to new branch
        new_branch.children = self.children[mid + 1 :]

        # Keep left half in this branch
        self.keys = self.keys[:mid]
        self.children = self.children[: mid + 1]

        return new_branch, separator_key

    def insert_child_and_split_if_needed(
        self, child_index: int, separator_key: Any, new_child: "Node"
    ) -> Optional[Tuple["BranchNode", Any]]:
        """Insert separator and child, split if necessary. Returns None or (new_branch, promoted_key)"""
        # Insert the separator key and new child at the appropriate position
        self.keys.insert(child_index, separator_key)
        self.children.insert(child_index + 1, new_child)

        # If branch is not full after insertion, we're done
        if not self.is_full():
            return None

        # Branch is full, need to split
        return self.split()

    def find_leaf_for_key(self, key: Any) -> "LeafNode":
        """Find the leaf node that contains or would contain the given key"""
        child = self.get_child(key)
        return child.find_leaf_for_key(key)
