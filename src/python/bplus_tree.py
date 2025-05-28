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

    def __setitem__(self, key: Any, value: Any) -> None:
        """Set a key-value pair (dict-like API)"""
        # Navigate to the correct leaf, keeping track of path
        path = []
        node = self.root
        while not node.is_leaf():
            path.append(node)
            node = node.get_child(key)

        leaf = node

        # Try to insert
        pos, exists = leaf.find_position(key)

        # If key exists, just update (no split needed)
        if exists:
            leaf.values[pos] = value
            return

        # Check if we need to split before inserting
        if not leaf.is_full():
            # Normal insertion
            leaf.insert(key, value)
            return

        new_leaf = leaf.split()

        if key < new_leaf.keys[0]:
            leaf.insert(key, value)
        else:
            new_leaf.insert(key, value)

        separator_key = new_leaf.keys[0]

        # If this is the root, create a new branch root
        if leaf == self.root:
            branch = BranchNode(self.capacity)
            branch.keys.append(separator_key)
            branch.children.append(leaf)
            branch.children.append(new_leaf)
            self.root = branch
        else:
            # Propagate the split up the tree
            self._insert_into_parent(path, leaf, separator_key, new_leaf)

    def _insert_into_parent(
        self,
        path: List["BranchNode"],
        left_child: "Node",
        separator_key: Any,
        right_child: "Node",
    ) -> None:
        """Insert a separator key and new child into parent after a split"""
        if not path:
            # No parent exists, need to create new root
            branch = BranchNode(self.capacity)
            branch.keys.append(separator_key)
            branch.children.append(left_child)
            branch.children.append(right_child)
            self.root = branch
            return

        parent = path[-1]

        # Find where to insert the separator key
        pos = 0
        for i, key in enumerate(parent.keys):
            if separator_key < key:
                pos = i
                break
            pos = i + 1

        # Insert the separator key and new child
        parent.keys.insert(pos, separator_key)
        # The right child goes after the position of the separator key
        # Find the index of left_child in parent.children
        left_index = parent.children.index(left_child)
        parent.children.insert(left_index + 1, right_child)

        # Check if parent needs to split
        if parent.is_full():
            # Split the parent
            new_parent, promoted_key = parent.split()
            
            # Recursively insert the promoted key into the grandparent
            grandparent_path = path[:-1]
            self._insert_into_parent(grandparent_path, parent, promoted_key, new_parent)

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

    def invariants(self) -> bool:
        """Check that all B+ tree invariants hold"""

        # Helper to get all leaves with their depths
        def get_leaves_with_depth(
            node: Node, depth: int = 0
        ) -> List[Tuple[LeafNode, int]]:
            if node.is_leaf():
                return [(node, depth)]

            leaves = []
            for child in node.children:
                leaves.extend(get_leaves_with_depth(child, depth + 1))
            return leaves

        # Helper to check if keys are in ascending order
        def check_keys_ascending(node: Node) -> bool:
            if node.is_leaf():
                for i in range(1, len(node.keys)):
                    if node.keys[i - 1] >= node.keys[i]:
                        return False
            else:
                # Check branch keys
                for i in range(1, len(node.keys)):
                    if node.keys[i - 1] >= node.keys[i]:
                        return False
                # Recursively check children
                for child in node.children:
                    if not check_keys_ascending(child):
                        return False
            return True

        # Helper to check minimum occupancy
        def check_min_occupancy(node: Node, is_root: bool = False) -> bool:
            if is_root:
                # Root can have fewer entries
                return True

            min_keys = self.capacity // 2
            if len(node.keys) < min_keys:
                return False

            if not node.is_leaf():
                # Check children recursively
                for child in node.children:
                    if not check_min_occupancy(child, False):
                        return False

            return True

        # Helper to count nodes at each level of a subtree
        def count_nodes_per_level(node: Node) -> List[int]:
            if node.is_leaf():
                return [1]

            # Count this level
            counts = [1]

            # Get counts from first child to determine depth
            if node.children:
                child_counts = count_nodes_per_level(node.children[0])
                # Initialize counts for all levels below
                for i in range(len(child_counts)):
                    if i + 1 >= len(counts):
                        counts.append(0)

                # Add counts from all children
                for child in node.children:
                    child_counts = count_nodes_per_level(child)
                    for i, count in enumerate(child_counts):
                        counts[i + 1] += count

            return counts

        # 1. Check all leaves are at the same depth
        leaves_with_depth = get_leaves_with_depth(self.root)
        if leaves_with_depth:
            first_depth = leaves_with_depth[0][1]
            for leaf, depth in leaves_with_depth:
                if depth != first_depth:
                    print(
                        f"Invariant violated: Leaf at depth {depth}, expected {first_depth}"
                    )
                    return False

        # 2. Check keys ascend
        if not check_keys_ascending(self.root):
            print("Invariant violated: Keys not in ascending order")
            return False

        # Check keys ascend across leaves
        prev_key = None
        current = self.leaves
        while current:
            if current.keys:
                if prev_key is not None and prev_key >= current.keys[0]:
                    print(
                        f"Invariant violated: Keys not ascending across leaves: {prev_key} >= {current.keys[0]}"
                    )
                    return False
                if current.keys:
                    prev_key = current.keys[-1]
            current = current.next

        # 3 & 4. Check minimum occupancy (except for root)
        if not check_min_occupancy(self.root, is_root=True):
            print(
                f"Invariant violated: Node has fewer than {self.capacity // 2} entries"
            )
            return False

        # 5. Check branch balance (subtrees should have similar depths)
        if not self.root.is_leaf():
            # For B+ trees, we only need to check that all leaves are at the same depth
            # which we already did above. The exact shape of subtrees can vary
            # during insertions as long as all leaves remain at the same level.
            pass

        return True


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

    def split(self) -> "BranchNode":
        """Split this branch node, returning the new right node"""
        # Find the midpoint
        mid = len(self.keys) // 2
        
        # Create new branch for right half
        new_branch = BranchNode(self.capacity)
        
        # The middle key becomes the separator to be promoted
        separator_key = self.keys[mid]
        
        # Move right half of keys to new branch (excluding the middle key)
        new_branch.keys = self.keys[mid + 1:]
        
        # Move corresponding children to new branch
        new_branch.children = self.children[mid + 1:]
        
        # Keep left half in this branch
        self.keys = self.keys[:mid]
        self.children = self.children[:mid + 1]
        
        return new_branch, separator_key
