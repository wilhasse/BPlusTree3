"""
Private invariant checker for B+ Tree validation.

This module contains the internal validation logic for ensuring B+ tree
structural integrity and invariants are maintained. This is an internal
implementation detail and should not be imported directly by external code.

The invariant checker validates:
- All leaves are at the same depth
- Keys are in ascending order throughout the tree
- Minimum occupancy constraints (except for root)
- Maximum occupancy constraints
- Branch node structure (n children have n-1 keys)
- Leaf linked list ordering
"""

from typing import List, Tuple, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    # Import only for type checking to avoid circular imports
    from .bplus_tree import Node, LeafNode, BranchNode


class BPlusTreeInvariantChecker:
    """
    Private class for validating B+ tree invariants.

    This class encapsulates all the complex logic for checking that a B+ tree
    maintains its structural properties and ordering constraints.
    """

    def __init__(self, capacity: int):
        self.capacity = capacity

    def check_invariants(
        self, root: "Node", leaves: Optional["LeafNode"] = None
    ) -> bool:
        """
        Check all B+ tree invariants.

        Args:
            root: The root node of the tree
            leaves: Optional head of the leaf linked list

        Returns:
            True if all invariants are satisfied, False otherwise
        """
        try:
            if not root:
                return True

            # Check structural invariants
            if not self._check_keys_ascending(root):
                print("Invariant violated: Keys not in ascending order")
                return False

            if not self._check_min_occupancy(root, is_root=True):
                print("Invariant violated: Minimum occupancy constraint")
                return False

            if not self._check_max_occupancy(root):
                print("Invariant violated: Maximum occupancy constraint")
                return False

            if not self._check_branch_structure(root):
                print("Invariant violated: Branch node structure")
                return False

            # Check leaf-specific invariants
            if not self._check_leaf_consistency(root):
                print("Invariant violated: Leaf consistency")
                return False

            if leaves and not self._check_leaf_ordering(leaves):
                print("Invariant violated: Leaf ordering in linked list")
                return False

            # Check depth consistency
            if not self._check_uniform_depth(root):
                print("Invariant violated: Non-uniform leaf depths")
                return False

            return True

        except Exception as e:
            print(f"Error during invariant checking: {type(e).__name__}: {e}")
            return False

    def _check_keys_ascending(self, node: "Node") -> bool:
        """Check if keys are in ascending order throughout the tree"""
        try:
            if node.is_leaf():
                for i in range(1, len(node.keys)):
                    if node.keys[i - 1] >= node.keys[i]:
                        return False
            else:
                branch = node
                for i in range(1, len(branch.keys)):
                    if branch.keys[i - 1] >= branch.keys[i]:
                        return False

                for i, child in enumerate(branch.children):
                    if child is None:
                        print(
                            f"Invariant violated: None child at index {i} in _check_keys_ascending"
                        )
                        return False
                    if not self._check_keys_ascending(child):
                        return False

            return True

        except Exception as e:
            print(f"Error in _check_keys_ascending: {e}")
            return False

    def _check_min_occupancy(self, node: "Node", is_root: bool = False) -> bool:
        """Check minimum occupancy constraints"""
        if is_root:
            if not node.is_leaf():
                branch = node
                if len(branch.children) < 2:
                    return False
        else:
            min_keys = (self.capacity - 1) // 2
            if len(node.keys) < min_keys:
                return False

            if not node.is_leaf():
                branch = node
                min_children = min_keys + 1
                if len(branch.children) < min_children:
                    return False

        if not node.is_leaf():
            branch = node
            for child in branch.children:
                if not self._check_min_occupancy(child, False):
                    return False

        return True

    def _check_max_occupancy(self, node: "Node") -> bool:
        """Check maximum occupancy constraints"""
        if len(node.keys) > self.capacity:
            return False

        if not node.is_leaf():
            branch = node  # Type: BranchNode
            if len(branch.children) > self.capacity + 1:
                return False

            # Check children recursively
            for child in branch.children:
                if not self._check_max_occupancy(child):
                    return False

        return True

    def _check_branch_structure(self, node: "Node") -> bool:
        """Check that branch nodes have correct key-to-children ratio"""
        if node.is_leaf():
            return True

        branch = node  # Type: BranchNode

        # Branch with n children should have n-1 keys
        if len(branch.keys) != len(branch.children) - 1:
            print(
                f"Branch structure invalid: {len(branch.keys)} keys but {len(branch.children)} children"
            )
            return False

        # Check children recursively
        for child in branch.children:
            if child is None:
                print("Branch has None child")
                return False
            if not self._check_branch_structure(child):
                return False

        return True

    def _check_leaf_consistency(self, node: "Node") -> bool:
        """Check leaf-specific consistency rules"""
        if not node.is_leaf():
            branch = node  # Type: BranchNode
            # Recursively check all leaves
            for child in branch.children:
                if not self._check_leaf_consistency(child):
                    return False
            return True

        leaf = node  # Type: LeafNode

        # Leaf should have equal number of keys and values
        # (This check would need access to the values, assuming they exist)
        # For now, we just check that keys exist
        if len(leaf.keys) == 0 and leaf != self._find_root(leaf):
            # Empty leaves are only allowed if they're the root
            return False

        return True

    def _check_leaf_ordering(self, leaves_head: "LeafNode") -> bool:
        """Check that the leaf linked list maintains ordering"""
        current = leaves_head
        while current and current.next:
            if not current.keys or not current.next.keys:
                # Skip empty leaves
                current = current.next
                continue

            # Last key of current should be <= first key of next
            if current.keys[-1] >= current.next.keys[0]:
                return False

            current = current.next

        return True

    def _check_uniform_depth(self, node: "Node") -> bool:
        """Check that all leaves are at the same depth"""
        depths = self._get_leaf_depths(node)
        if not depths:
            return True

        # All depths should be the same
        first_depth = depths[0][1]
        for _, depth in depths:
            if depth != first_depth:
                return False

        return True

    def _get_leaf_depths(
        self, node: "Node", depth: int = 0
    ) -> List[Tuple["LeafNode", int]]:
        """Get all leaves with their depths"""
        try:
            if node.is_leaf():
                return [(node, depth)]

            leaves = []
            branch = node  # Type: BranchNode
            for i, child in enumerate(branch.children):
                if child is None:
                    print(f"Invariant violated: None child at index {i}")
                    return []
                leaves.extend(self._get_leaf_depths(child, depth + 1))
            return leaves

        except Exception as e:
            print(f"Error traversing tree in _get_leaf_depths: {e}")
            return []

    def _find_root(self, node: "Node") -> "Node":
        """Helper to find root (simplified - would need parent pointers in real implementation)"""
        # This is a placeholder - in practice you'd traverse up parent pointers
        return node

    def count_nodes_per_level(self, node: "Node") -> List[int]:
        """Count nodes at each level of the tree"""
        if node.is_leaf():
            return [1]

        # Count this level
        counts = [1]
        branch = node  # Type: BranchNode

        # Get counts from all children
        child_level_counts = []
        for child in branch.children:
            child_counts = self.count_nodes_per_level(child)
            child_level_counts.append(child_counts)

        # Aggregate counts by level
        if child_level_counts:
            max_child_levels = max(len(counts) for counts in child_level_counts)
            for level in range(max_child_levels):
                level_count = sum(
                    counts[level] if level < len(counts) else 0
                    for counts in child_level_counts
                )
                counts.append(level_count)

        return counts

    def get_tree_stats(self, node: "Node") -> dict:
        """Get comprehensive tree statistics"""
        if not node:
            return {
                "total_nodes": 0,
                "leaf_count": 0,
                "branch_count": 0,
                "max_depth": 0,
                "min_keys": 0,
                "max_keys": 0,
                "avg_keys": 0,
                "levels": [],
            }

        leaf_depths = self._get_leaf_depths(node)
        total_keys = self._count_total_keys(node)
        total_nodes = self._count_total_nodes(node)

        return {
            "total_nodes": total_nodes,
            "leaf_count": len(leaf_depths),
            "branch_count": total_nodes - len(leaf_depths),
            "max_depth": max(depth for _, depth in leaf_depths) if leaf_depths else 0,
            "min_keys": min(len(n.keys) for n, _ in leaf_depths) if leaf_depths else 0,
            "max_keys": max(len(n.keys) for n, _ in leaf_depths) if leaf_depths else 0,
            "avg_keys": total_keys / total_nodes if total_nodes > 0 else 0,
            "levels": self.count_nodes_per_level(node),
        }

    def _count_total_keys(self, node: "Node") -> int:
        """Count total keys in the tree"""
        if node.is_leaf():
            return len(node.keys)

        total = len(node.keys)
        branch = node  # Type: BranchNode
        for child in branch.children:
            total += self._count_total_keys(child)

        return total

    def _count_total_nodes(self, node: "Node") -> int:
        """Count total nodes in the tree"""
        if node.is_leaf():
            return 1

        total = 1
        branch = node  # Type: BranchNode
        for child in branch.children:
            total += self._count_total_nodes(child)

        return total
