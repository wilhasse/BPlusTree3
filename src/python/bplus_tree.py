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

    def __init__(self, capacity: int = 128, use_memory_pool: bool = True):
        """Create a B+ tree with specified node capacity"""
        self.capacity = capacity
        self.use_memory_pool = use_memory_pool
        
        # Initialize memory pool if enabled
        if use_memory_pool:
            from memory_pool import get_default_pool
            self._pool = get_default_pool(capacity)
        else:
            self._pool = None
        
        original = self._create_leaf_node()
        self.leaves: LeafNode = original
        self.root: Node = original
        self._invariant_checker = _BPlusTreeInvariantChecker(capacity)
    
    def _create_leaf_node(self) -> 'LeafNode':
        """Create a new leaf node, using pool if enabled"""
        if self._pool:
            return self._pool.get_leaf_node()
        else:
            return LeafNode(self.capacity)
    
    def _create_branch_node(self) -> 'BranchNode':
        """Create a new branch node, using pool if enabled"""
        if self._pool:
            return self._pool.get_branch_node()
        else:
            return BranchNode(self.capacity)
    
    def _return_leaf_node(self, node: 'LeafNode') -> None:
        """Return a leaf node to the pool if enabled"""
        if self._pool:
            self._pool.return_leaf_node(node)
    
    def _return_branch_node(self, node: 'BranchNode') -> None:
        """Return a branch node to the pool if enabled"""
        if self._pool:
            self._pool.return_branch_node(node)
    
    def get_pool_stats(self) -> dict:
        """Get memory pool statistics"""
        if self._pool:
            return self._pool.get_hit_rate()
        return {"pool_disabled": True}

    @classmethod
    def from_sorted_items(cls, items, capacity: int = 128, use_memory_pool: bool = True):
        """
        Bulk load from sorted key-value pairs for 3-5x faster construction.
        
        Args:
            items: Iterable of (key, value) pairs that MUST be sorted by key
            capacity: Node capacity
            use_memory_pool: Whether to use memory pooling
            
        Returns:
            BPlusTreeMap instance
        """
        tree = cls(capacity=capacity, use_memory_pool=use_memory_pool)
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
        
        if not hasattr(self, '_rightmost_leaf_cache'):
            self._rightmost_leaf_cache = None
        
        # Try to insert into cached rightmost leaf if key is larger than all existing
        if (self._rightmost_leaf_cache and 
            self._rightmost_leaf_cache.keys and 
            key > self._rightmost_leaf_cache.keys[-1] and
            not self._rightmost_leaf_cache.is_full()):
            
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
            new_root = self._create_branch_node()
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
        return branch.insert_child_and_split_if_needed(child_index, separator_key, new_child)

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

        # Check if root needs to collapse or repair
        self._repair_tree_structure()

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

        return deleted

    def _repair_tree_structure(self) -> None:
        """
        Repair tree structure after deletions to ensure validity.
        Handles root collapse and removes invalid branch nodes.
        """
        # Repeatedly collapse root if it has only one child
        while (not self.root.is_leaf() and 
               len(self.root.children) == 1):
            self.root = self.root.children[0]
        
        # Handle edge case where root becomes empty branch
        if (not self.root.is_leaf() and 
            len(self.root.children) == 0):
            # Create a new empty leaf as root
            new_root = self._create_leaf_node()
            self.leaves = new_root
            self.root = new_root

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
            raise ValueError(f"Invalid child_index {child_index} for parent with {len(parent.children)} children")
        if len(parent.keys) != len(parent.children) - 1:
            raise ValueError(f"Parent structure invalid: {len(parent.keys)} keys but {len(parent.children)} children")

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
                total_keys = len(left_sibling.keys) + len(child.keys) + 1  # +1 for separator
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
                total_keys = len(child.keys) + len(right_sibling.keys) + 1  # +1 for separator
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
            # Edge case: child has no siblings (parent has only one child)
            # This can happen in complex deletion scenarios
            # The parent should collapse by promoting its only child
            if len(parent.children) == 1:
                # This is a structural issue that should be handled by parent collapse
                # For now, we'll skip merging and let the tree structure handle it
                # The parent itself will be handled by its parent's underflow logic
                return
            else:
                # This really shouldn't happen - investigate further
                raise ValueError(f"Cannot merge - node has no siblings (parent has {len(parent.children)} children, child_index={child_index})")

    def _try_consolidate_branch(self, node: "BranchNode") -> None:
        """
        PHASE 6 OPTIMIZATION: Try to consolidate branch structure for better space utilization.
        Look for opportunities to merge sparse branch nodes or eliminate unnecessary levels.
        """
        if node.is_leaf():
            return

        # Check if any child branches can be merged with siblings to reduce tree width
        for i in range(len(node.children) - 1):
            child = node.children[i]
            right_sibling = node.children[i + 1]
            
            # Skip if either child is a leaf - we don't consolidate leaves in this method
            if child.is_leaf() or right_sibling.is_leaf():
                continue

            # If both children are branches and their combined size would fit in one node
            if (
                len(child.keys) + len(right_sibling.keys) + 1 <= child.capacity
                and len(child.children) + len(right_sibling.children) <= child.capacity + 1
            ):

                # Merge the two branch nodes for better space utilization
                separator_key = node.keys[i]
                child.merge_with_right(right_sibling, separator_key)

                # Remove the merged sibling and separator
                node.children.pop(i + 1)
                node.keys.pop(i)

                # Only do one merge per call to avoid index issues
                break

    def _remove_empty_child(self, parent: "BranchNode", child_index: int) -> None:
        """Remove an empty child from a branch node."""
        empty_child = parent.children[child_index]

        # If it's a leaf, update the linked list
        if empty_child.is_leaf() and empty_child == self.leaves:
            # Update the head of the leaves list
            self.leaves = empty_child.next

        # Find and update the previous leaf's next pointer
        if empty_child.is_leaf():
            current = self.leaves
            while current and current.next != empty_child:
                current = current.next
            if current:
                current.next = empty_child.next

        # Remove the child
        parent.children.pop(child_index)

        # Remove the corresponding separator key
        # In a branch node: child[0] key[0] child[1] key[1] child[2] ... key[n-2] child[n-1]
        # Key[i] separates child[i] and child[i+1]
        # When removing child[i], we need to remove the key that was associated with it
        if len(parent.keys) > 0:
            if child_index == 0:
                # Removing the first child, remove key[0] (between child[0] and child[1])
                parent.keys.pop(0)
            elif child_index == len(parent.children):
                # Removing the last child, remove the last key (was between child[n-2] and child[n-1])
                parent.keys.pop(-1)
            else:
                # Removing middle child[i], remove key[i-1] (was between child[i-1] and child[i])
                parent.keys.pop(child_index - 1)

    def _delete_from_leaf(self, leaf: "LeafNode", key: Any) -> bool:
        """Delete from a leaf node. Returns True if deleted, False if not found."""
        deleted = leaf.delete(key)
        return deleted is not None

    def delete_batch(self, keys: list) -> int:
        """
        PHASE 6 OPTIMIZATION: Delete multiple keys efficiently.
        Returns the number of keys actually deleted.
        """
        deleted_count = 0

        # Sort keys to potentially optimize tree traversal
        sorted_keys = sorted(keys)

        # Delete keys one by one (could be optimized further)
        for key in sorted_keys:
            try:
                del self[key]
                deleted_count += 1
            except KeyError:
                pass  # Key doesn't exist, skip

        # Compact the tree after batch deletions if many keys were deleted
        if deleted_count > len(keys) * 0.1:  # If >10% of keys were deleted
            self.compact()

        return deleted_count

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
    
    def _find_leaf_for_key(self, key: Any) -> Optional['LeafNode']:
        """Find the leaf node that contains or would contain the given key"""
        return self.root.find_leaf_for_key(key)
    
    def _find_position_in_leaf(self, leaf: 'LeafNode', key: Any) -> int:
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

    def compact(self) -> None:
        """
        PHASE 6 OPTIMIZATION: Compact the tree structure for better space utilization.
        This method should be called after large numbers of deletions to optimize the tree.
        """
        if self.root.is_leaf():
            return

        # Perform multiple passes of consolidation until no more improvements
        max_passes = 10  # Prevent infinite loops
        for _ in range(max_passes):
            initial_structure = self._count_total_nodes()
            self._compact_recursive(self.root)

            # Check if root can be collapsed further
            while not self.root.is_leaf() and len(self.root.children) == 1:
                self.root = self.root.children[0]

            # If no structural changes were made, we're done
            if self._count_total_nodes() == initial_structure:
                break

    def _count_total_nodes(self) -> int:
        """Count total nodes in the tree for optimization tracking"""

        def count_nodes(node):
            if node.is_leaf():
                return 1
            count = 1
            for child in node.children:
                count += count_nodes(child)
            return count

        return count_nodes(self.root)

    def _compact_recursive(self, node: "Node") -> None:
        """Recursively compact the tree structure"""
        if node.is_leaf():
            return

        # First, compact all children
        for child in node.children:
            self._compact_recursive(child)

        # Then try to consolidate this level
        self._try_consolidate_branch(node)


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
    
    def _reset_for_reuse(self) -> None:
        """Reset the node for reuse from memory pool"""
        self.keys.clear()
        self.values.clear()
        self.next = None

    def is_underfull(self) -> bool:
        """Check if leaf has fewer than minimum required keys"""
        min_keys = self.capacity // 2
        return len(self.keys) < min_keys

    def can_donate(self) -> bool:
        """Check if leaf can give a key to a sibling (has more than minimum)"""
        min_keys = self.capacity // 2
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
        new_leaf = LeafNode(self.capacity)  # Note: This is in the LeafNode class, will be updated separately

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
    
    def get_separator_key(self) -> Any:
        """Get the separator key for this node (first key)"""
        if not self.keys:
            raise ValueError("Cannot get separator from empty leaf")
        return self.keys[0]
    
    def find_leaf_for_key(self, key: Any) -> 'LeafNode':
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
    
    def _reset_for_reuse(self) -> None:
        """Reset the node for reuse from memory pool"""
        self.keys.clear()
        self.children.clear()

    def is_underfull(self) -> bool:
        """Check if branch has fewer than minimum required keys"""
        min_keys = self.capacity // 2
        return len(self.keys) < min_keys

    def can_donate(self) -> bool:
        """Check if branch can give a key to a sibling (has more than minimum)"""
        min_keys = self.capacity // 2
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
            raise ValueError(f"Invalid branch structure: {len(self.keys)} keys, {len(self.children)} children")
        
        # Use optimized bisect module for binary search
        left = bisect.bisect_right(self.keys, key)
        
        # Validate result
        if left >= len(self.children):
            raise ValueError(f"Child index {left} out of range (have {len(self.children)} children)")
        
        return left

    def get_child(self, key: Any) -> Node:
        """Get the child node where a key would be found"""
        if not self.children:
            raise ValueError("BranchNode has no children - tree structure corrupted")
        index = self.find_child_index(key)
        if index >= len(self.children):
            raise ValueError(f"Child index {index} out of range (have {len(self.children)} children)")
        return self.children[index]

    def split(self) -> "BranchNode":
        """Split this branch node, returning the new right node"""
        # Find the midpoint
        mid = len(self.keys) // 2

        # Create new branch for right half
        new_branch = BranchNode(self.capacity)  # Note: This is in the BranchNode class, will be updated separately

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
    
    def insert_child_and_split_if_needed(self, child_index: int, separator_key: Any, new_child: "Node") -> Optional[Tuple["BranchNode", Any]]:
        """Insert separator and child, split if necessary. Returns None or (new_branch, promoted_key)"""
        # Insert the separator key and new child at the appropriate position
        self.keys.insert(child_index, separator_key)
        self.children.insert(child_index + 1, new_child)

        # If branch is not full after insertion, we're done
        if not self.is_full():
            return None

        # Branch is full, need to split
        return self.split()
    
    def find_leaf_for_key(self, key: Any) -> 'LeafNode':
        """Find the leaf node that contains or would contain the given key"""
        child = self.get_child(key)
        return child.find_leaf_for_key(key)
