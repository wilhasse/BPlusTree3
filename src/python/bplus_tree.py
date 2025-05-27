"""
B+ Tree implementation in Python with dict-like API
"""

from typing import Any, Optional, List, Tuple, Union
from abc import ABC, abstractmethod


class BPlusTreeMap:
    """B+ Tree with Python dict-like API"""

    def __init__(self, capacity: int = 4):
        """Create a B+ tree with specified node capacity"""
        self.capacity = capacity
        original = LeafNode(capacity)
        self.leaves: LeafNode = original
        self.root: Node = original
        self._size = 0

    def __setitem__(self, key: Any, value: Any) -> None:
        """Set a key-value pair (dict-like API)"""
        # For now, just handle the simple case of inserting into a leaf root
        if self.root.is_leaf():
            leaf = self.root
            
            # Check if we need to split before inserting
            if leaf.is_full():
                # Find position for the new key
                pos, exists = leaf.find_position(key)
                
                # If key exists, just update (no split needed)
                if exists:
                    leaf.values[pos] = value
                    return
                
                # Split the leaf
                new_leaf = leaf.split()
                
                # Determine which leaf should receive the new key
                if new_leaf.keys and key >= new_leaf.keys[0]:
                    # Insert into new leaf
                    new_leaf.insert(key, value)
                else:
                    # Insert into original leaf
                    leaf.insert(key, value)
                
                self._size += 1
            else:
                # Normal insertion
                old_value = leaf.insert(key, value)
                if old_value is None:
                    self._size += 1

    def __getitem__(self, key: Any) -> Any:
        """Get value for a key (dict-like API)"""
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value

    def get(self, key: Any, default: Any = None) -> Any:
        """Get value for a key with optional default"""
        # For now, since we only have leaf nodes at the root level,
        # search through the linked list of leaves
        current = self.leaves
        while current is not None:
            value = current.get(key)
            if value is not None:
                return value
            # If this leaf's keys are all smaller than our key, check next
            if current.keys and key > current.keys[-1]:
                current = current.next
            else:
                # Key would be in this leaf if it existed
                break
        return default

    def __contains__(self, key: Any) -> bool:
        """Check if key exists (for 'in' operator)"""
        return self.get(key) is not None

    def __len__(self) -> int:
        """Return number of key-value pairs"""
        return self._size

    def __bool__(self) -> bool:
        """Return True if tree is not empty"""
        return len(self) > 0

    def __delitem__(self, key: Any) -> None:
        """Delete a key (dict-like API)"""
        # TODO: Implement deletion
        raise NotImplementedError("Deletion not yet implemented")

    def keys(self):
        """Return an iterator over keys"""
        # TODO: Implement key iteration
        raise NotImplementedError("Key iteration not yet implemented")

    def values(self):
        """Return an iterator over values"""
        # TODO: Implement value iteration
        raise NotImplementedError("Value iteration not yet implemented")

    def items(self):
        """Return an iterator over (key, value) pairs"""
        # TODO: Implement item iteration
        raise NotImplementedError("Item iteration not yet implemented")

    """Testing only"""

    def leaf_count(self) -> int:
        """Return the number of leaf nodes"""
        count = 0
        node = self.leaves
        while node is not None:
            count += 1
            node = node.next
        return count


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

    def find_position(self, key: Any) -> Tuple[int, bool]:
        """
        Find where a key should be inserted.
        Returns (position, exists) where exists is True if key already exists.
        """
        # Binary search for the position
        left, right = 0, len(self.keys)
        while left < right:
            mid = (left + right) // 2
            if self.keys[mid] < key:
                left = mid + 1
            else:
                right = mid

        # Check if key exists at this position
        exists = left < len(self.keys) and self.keys[left] == key
        return left, exists

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
    
    def split(self) -> 'LeafNode':
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

    def find_child_index(self, key: Any) -> int:
        """Find which child a key should go to"""
        # Binary search for the child
        left, right = 0, len(self.keys)
        while left < right:
            mid = (left + right) // 2
            if key < self.keys[mid]:
                right = mid
            else:
                left = mid + 1
        return left

    def get_child(self, key: Any) -> Node:
        """Get the child node where a key would be found"""
        index = self.find_child_index(key)
        return self.children[index]
