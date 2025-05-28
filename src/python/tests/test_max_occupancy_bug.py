"""Detailed tests to reproduce the maximum occupancy bug"""

import pytest
from ..bplus_tree import BPlusTreeMap
from .._invariant_checker import BPlusTreeInvariantChecker


def check_invariants(tree: BPlusTreeMap) -> bool:
    """Helper function to check tree invariants"""
    checker = BPlusTreeInvariantChecker(tree.capacity)
    return checker.check_invariants(tree.root, tree.leaves)


class TestMaxOccupancyBug:
    """Tests to isolate and understand the max occupancy violation bug"""

    def test_small_tree_deletion_pattern(self):
        """Test with a smaller tree to find minimal reproduction"""
        tree = BPlusTreeMap(capacity=4)

        # Insert just 30 keys
        for i in range(1, 31):
            tree[i] = f"value_{i}"

        assert check_invariants(tree), "Tree should be valid after insertions"

        # Delete every 3rd key and check when invariants break
        for i in range(1, 31, 3):
            del tree[i]
            if not check_invariants(tree):
                print(f"Invariants broken after deleting key {i}")
                print(f"Deleted {(i-1)//3 + 1} keys total")
                # Check root structure
                if not tree.root.is_leaf():
                    print(
                        f"Root has {len(tree.root.keys)} keys (max: {tree.root.capacity})"
                    )
                    print(
                        f"Root has {len(tree.root.children)} children (max: {tree.root.capacity + 1})"
                    )
                pytest.fail(f"Invariants violated after deleting key {i}")

    def test_specific_deletion_sequence(self):
        """Test a specific sequence that should trigger the bug"""
        tree = BPlusTreeMap(capacity=4)

        # Create a tree that will have specific structure
        keys = list(range(1, 25))  # 24 keys
        for key in keys:
            tree[key] = f"value_{key}"

        # Track tree structure
        print(f"Initial: {len(tree)} keys, root is leaf: {tree.root.is_leaf()}")

        # Delete specific keys to trigger merges
        keys_to_delete = [1, 4, 7, 10, 13, 16, 19, 22]  # Every 3rd starting from 1

        for i, key in enumerate(keys_to_delete):
            del tree[key]
            valid = check_invariants(tree)
            print(f"After deleting {key} (deletion #{i+1}): valid={valid}")

            if not valid and not tree.root.is_leaf():
                print(
                    f"  Root: {len(tree.root.keys)} keys, {len(tree.root.children)} children"
                )
                # Look at first level children
                for j, child in enumerate(tree.root.children[:3]):  # First 3 children
                    if child.is_leaf():
                        print(f"  Child {j} (leaf): {len(child.keys)} keys")
                    else:
                        print(
                            f"  Child {j} (branch): {len(child.keys)} keys, {len(child.children)} children"
                        )
                break

    def test_root_accumulation(self):
        """Test if root accumulates children without splitting"""
        tree = BPlusTreeMap(capacity=4)

        # Insert enough to create a 3-level tree
        for i in range(1, 50):
            tree[i] = f"value_{i}"

        # Count initial structure
        def count_root_growth():
            if tree.root.is_leaf():
                return 0, 0
            return len(tree.root.keys), len(tree.root.children)

        initial_keys, initial_children = count_root_growth()
        print(f"Initial root: {initial_keys} keys, {initial_children} children")

        # Delete many keys and watch root grow
        deleted = 0
        for i in range(1, 50, 2):  # Delete every other key
            del tree[i]
            deleted += 1

            keys, children = count_root_growth()
            if keys > tree.root.capacity or children > tree.root.capacity + 1:
                print(f"Root overflow after {deleted} deletions!")
                print(f"Root has {keys} keys (max: {tree.root.capacity})")
                print(f"Root has {children} children (max: {tree.root.capacity + 1})")
                pytest.fail("Root exceeded capacity")

    def test_single_deletion_trigger(self):
        """Try to find the exact deletion that breaks invariants"""
        tree = BPlusTreeMap(capacity=4)

        # Build specific tree
        for i in range(1, 40):
            tree[i] = f"value_{i}"

        # Delete keys one by one
        for i in range(1, 40, 3):
            # Check before
            was_valid = check_invariants(tree)

            # Delete
            del tree[i]

            # Check after
            is_valid = check_invariants(tree)

            if was_valid and not is_valid:
                print(f"Deletion of key {i} broke invariants!")
                print(f"Tree had {len(tree) + 1} keys before deletion")

                # Examine tree structure
                def examine_node(node, level=0, name="root"):
                    indent = "  " * level
                    if node.is_leaf():
                        print(f"{indent}{name} (leaf): {len(node.keys)} keys")
                    else:
                        over_capacity = ""
                        if len(node.keys) > node.capacity:
                            over_capacity = (
                                f" EXCEEDS CAPACITY by {len(node.keys) - node.capacity}"
                            )
                        print(
                            f"{indent}{name} (branch): {len(node.keys)} keys, {len(node.children)} children{over_capacity}"
                        )

                        # Show first few children
                        for i in range(min(3, len(node.children))):
                            examine_node(node.children[i], level + 1, f"child[{i}]")
                        if len(node.children) > 3:
                            print(
                                f"{indent}  ... and {len(node.children) - 3} more children"
                            )

                examine_node(tree.root)
                pytest.fail(f"Key {i} deletion broke invariants")


if __name__ == "__main__":
    # Run tests manually for debugging
    test = TestMaxOccupancyBug()

    print("=== Test 1: Small tree deletion pattern ===")
    try:
        test.test_small_tree_deletion_pattern()
        print("PASSED")
    except:
        pass

    print("\n=== Test 2: Specific deletion sequence ===")
    try:
        test.test_specific_deletion_sequence()
        print("PASSED")
    except:
        pass

    print("\n=== Test 3: Root accumulation ===")
    try:
        test.test_root_accumulation()
        print("PASSED")
    except:
        pass

    print("\n=== Test 4: Single deletion trigger ===")
    try:
        test.test_single_deletion_trigger()
        print("PASSED")
    except:
        pass
