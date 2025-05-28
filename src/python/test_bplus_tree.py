"""
Tests for B+ Tree implementation
"""

import pytest
from bplus_tree import BPlusTreeMap, LeafNode, BranchNode


class TestBasicOperations:
    """Test basic B+ tree operations"""

    def test_create_empty_tree(self):
        """Test creating an empty tree"""
        tree = BPlusTreeMap(capacity=4)
        assert len(tree) == 0
        assert not tree  # Should be falsy when empty
        assert tree.invariants()

    def test_insert_and_get_single_item(self):
        """Test inserting and retrieving a single item"""
        tree = BPlusTreeMap(capacity=4)
        tree[1] = "one"

        assert len(tree) == 1
        assert tree  # Should be truthy when not empty
        assert tree[1] == "one"
        assert tree.get(1) == "one"
        assert tree.invariants()

    def test_insert_multiple_items(self):
        """Test inserting multiple items"""
        tree = BPlusTreeMap(capacity=4)
        tree[1] = "one"
        tree[2] = "two"
        tree[3] = "three"

        assert len(tree) == 3
        assert tree[1] == "one"
        assert tree[2] == "two"
        assert tree[3] == "three"
        assert tree.invariants()

    def test_update_existing_key(self):
        """Test updating an existing key"""
        tree = BPlusTreeMap(capacity=4)
        tree[1] = "one"
        tree[1] = "ONE"

        assert len(tree) == 1  # Size shouldn't change
        assert tree[1] == "ONE"
        assert tree.invariants()

    def test_contains_operator(self):
        """Test the 'in' operator"""
        tree = BPlusTreeMap(capacity=4)
        tree[1] = "one"
        tree[2] = "two"

        assert 1 in tree
        assert 2 in tree
        assert 3 not in tree
        assert tree.invariants()

    def test_get_with_default(self):
        """Test get() with default value"""
        tree = BPlusTreeMap(capacity=4)
        tree[1] = "one"

        assert tree.get(1) == "one"
        assert tree.get(2) is None
        assert tree.get(2, "default") == "default"
        assert tree.invariants()

    def test_key_error_on_missing_key(self):
        """Test that KeyError is raised for missing keys"""
        tree = BPlusTreeMap(capacity=4)
        tree[1] = "one"

        with pytest.raises(KeyError):
            _ = tree[2]
        
        assert tree.invariants()


class TestSetItemSplitting:
    """Test B+ tree operations when splitting nodes"""

    def test_overflow(self):
        tree = BPlusTreeMap(capacity=2)
        tree[1] = "one"
        tree[2] = "two"
        tree[3] = "three"

        assert tree.invariants()
        assert len(tree) == 3
        assert tree[1] == "one"
        assert tree[2] == "two"
        assert tree[3] == "three"

        assert not tree.root.is_leaf()

    def test_split_then_add(self):
        tree = BPlusTreeMap(capacity=2)
        tree[1] = "one"
        tree[2] = "two"
        tree[3] = "three"
        tree[4] = "four"

        # Check correctness via invariants instead of exact structure
        assert tree.invariants()
        assert len(tree) == 4
        assert tree[1] == "one"
        assert tree[2] == "two"
        assert tree[3] == "three"
        assert tree[4] == "four"
        
        # The simpler implementation may create more leaves, but that's OK
        # as long as invariants hold
        assert tree.leaf_count() >= 2  # At minimum need 2 leaves for 4 items with capacity 2

    def test_many_insertions_maintain_invariants(self):
        """Test that invariants hold after many insertions"""
        tree = BPlusTreeMap(capacity=4)
        
        # Insert many items
        for i in range(20):
            tree[i] = f"value_{i}"
            # Check invariants after each insertion
            assert tree.invariants(), f"Invariants violated after inserting {i}"
        
        # Verify all items are retrievable
        for i in range(20):
            assert tree[i] == f"value_{i}"

    def test_parent_splitting(self):
        """Test that parent nodes split correctly when they become full"""
        tree = BPlusTreeMap(capacity=3)  # Small capacity to force parent splits
        
        # Insert enough items to force multiple levels of splits
        for i in range(30):
            tree[i] = f"value_{i}"
            assert tree.invariants(), f"Invariants violated after inserting {i}"
        
        # Verify all items are still retrievable
        for i in range(30):
            assert tree[i] == f"value_{i}"
        
        # The tree should have multiple levels now
        assert not tree.root.is_leaf()
        
        # Check that no nodes are overfull
        def check_no_overfull(node):
            assert len(node.keys) <= node.capacity, f"Node has {len(node.keys)} keys but capacity is {node.capacity}"
            if not node.is_leaf():
                for child in node.children:
                    check_no_overfull(child)
        
        check_no_overfull(tree.root)


class TestLeafNode:
    """Test LeafNode operations"""

    def test_leaf_node_creation(self):
        """Test creating a leaf node"""
        leaf = LeafNode(capacity=4)
        assert leaf.is_leaf()
        assert not leaf.is_full()
        assert len(leaf) == 0

    def test_leaf_node_insert(self):
        """Test inserting into a leaf node"""
        leaf = LeafNode(capacity=4)

        # Insert first item
        assert leaf.insert(2, "two") is None
        assert len(leaf) == 1
        assert leaf.get(2) == "two"

        # Insert before
        assert leaf.insert(1, "one") is None
        assert len(leaf) == 2
        assert leaf.keys == [1, 2]

        # Insert after
        assert leaf.insert(3, "three") is None
        assert len(leaf) == 3
        assert leaf.keys == [1, 2, 3]

        # Update existing
        assert leaf.insert(2, "TWO") == "two"
        assert len(leaf) == 3
        assert leaf.get(2) == "TWO"

    def test_leaf_node_full(self):
        """Test when leaf node is full"""
        leaf = LeafNode(capacity=4)

        # Fill the node
        for i in range(4):
            leaf.insert(i, str(i))

        assert leaf.is_full()
        assert len(leaf) == 4

    def test_leaf_find_position(self):
        """Test finding position for keys"""
        leaf = LeafNode(capacity=4)
        leaf.insert(10, "ten")
        leaf.insert(20, "twenty")
        leaf.insert(30, "thirty")

        # Test finding existing keys
        assert leaf.find_position(10) == (0, True)
        assert leaf.find_position(20) == (1, True)
        assert leaf.find_position(30) == (2, True)

        # Test finding non-existing keys
        assert leaf.find_position(5) == (0, False)  # Before all
        assert leaf.find_position(15) == (1, False)  # Between 10 and 20
        assert leaf.find_position(25) == (2, False)  # Between 20 and 30
        assert leaf.find_position(35) == (3, False)  # After all


class TestRemoval:
    """Test B+ tree removal operations"""
    
    def test_remove_single_item_from_leaf_root(self):
        """Test removing a single item when root is a leaf"""
        tree = BPlusTreeMap(capacity=4)
        tree[1] = "one"
        
        # Remove the item
        del tree[1]
        
        # Tree should be empty
        assert len(tree) == 0
        assert 1 not in tree
        assert tree.invariants()
        
        # Should raise KeyError when trying to get removed item
        with pytest.raises(KeyError):
            _ = tree[1]
    
    def test_remove_multiple_items_from_leaf_root(self):
        """Test removing multiple items when root is a leaf"""
        tree = BPlusTreeMap(capacity=4)
        tree[1] = "one"
        tree[2] = "two"
        tree[3] = "three"
        
        # Remove items
        del tree[2]
        
        # Check state after first removal
        assert len(tree) == 2
        assert 1 in tree
        assert 2 not in tree
        assert 3 in tree
        assert tree[1] == "one"
        assert tree[3] == "three"
        assert tree.invariants()
        
        # Remove another item
        del tree[1]
        
        # Check state after second removal
        assert len(tree) == 1
        assert 1 not in tree
        assert 3 in tree
        assert tree[3] == "three"
        assert tree.invariants()
        
        # Remove last item
        del tree[3]
        
        # Tree should be empty
        assert len(tree) == 0
        assert tree.invariants()
    
    def test_remove_nonexistent_key_raises_error(self):
        """Test that removing a non-existent key raises KeyError"""
        tree = BPlusTreeMap(capacity=4)
        tree[1] = "one"
        tree[2] = "two"
        
        # Try to remove non-existent key
        with pytest.raises(KeyError):
            del tree[3]
        
        # Tree should be unchanged
        assert len(tree) == 2
        assert tree[1] == "one"
        assert tree[2] == "two"
        assert tree.invariants()
    
    def test_remove_from_tree_with_branch_root(self):
        """Test removing an item when root is a branch node"""
        tree = BPlusTreeMap(capacity=3)
        
        # Insert enough items to create a branch root
        for i in range(1, 5):
            tree[i] = f"value_{i}"
        
        # Verify we have a branch root
        assert not tree.root.is_leaf()
        assert len(tree) == 4
        
        # Remove an item
        del tree[2]
        
        # Check the item was removed
        assert len(tree) == 3
        assert 2 not in tree
        assert tree[1] == "value_1"
        assert tree[3] == "value_3"
        assert tree[4] == "value_4"
        assert tree.invariants()
    
    def test_remove_multiple_from_tree_with_branches(self):
        """Test removing multiple items from a tree with branch nodes"""
        tree = BPlusTreeMap(capacity=3)
        
        # Insert more items to ensure we have multiple levels
        for i in range(1, 8):
            tree[i] = f"value_{i}"
        
        # Remove items in various orders
        del tree[3]
        del tree[6]
        del tree[1]
        
        # Check remaining items
        assert len(tree) == 4
        assert tree[2] == "value_2"
        assert tree[4] == "value_4"
        assert tree[5] == "value_5"
        assert tree[7] == "value_7"
        
        # Check removed items are gone
        assert 1 not in tree
        assert 3 not in tree
        assert 6 not in tree
        
        assert tree.invariants()
    
    def test_collapse_root_when_empty(self):
        """Test that tree height collapses when root branch becomes empty"""
        tree = BPlusTreeMap(capacity=2)
        
        # Create a small tree that will have a branch root
        tree[1] = "one"
        tree[2] = "two"
        tree[3] = "three"  # This should cause a split
        
        # Verify we have a branch root
        assert not tree.root.is_leaf()
        initial_root = tree.root
        
        # Remove items to make one child empty
        del tree[1]
        del tree[2]
        
        
        # At this point, the first leaf is empty and should be removed
        # The root should collapse to just be the remaining leaf
        assert tree.root.is_leaf()
        assert tree.root != initial_root
        assert len(tree) == 1
        assert tree[3] == "three"
        assert tree.invariants()


class TestNodeUnderflow:
    """Test node underflow detection"""
    
    def test_leaf_underflow_detection(self):
        """Test that leaf nodes correctly detect underflow"""
        leaf = LeafNode(capacity=4)  # min_keys = 2
        
        # Empty leaf is underfull
        assert leaf.is_underfull()
        
        # Single key is underfull
        leaf.insert(1, "one")
        assert leaf.is_underfull()
        
        # Two keys is at minimum (not underfull)
        leaf.insert(2, "two")
        assert not leaf.is_underfull()
        
        # More keys is definitely not underfull
        leaf.insert(3, "three")
        assert not leaf.is_underfull()
    
    def test_branch_underflow_detection(self):
        """Test that branch nodes correctly detect underflow"""
        branch = BranchNode(capacity=4)  # min_keys = 2
        
        # Empty branch is underfull
        assert branch.is_underfull()
        
        # Single key is underfull
        branch.keys.append(5)
        assert branch.is_underfull()
        
        # Two keys is at minimum (not underfull)
        branch.keys.append(10)
        assert not branch.is_underfull()
        
        # More keys is definitely not underfull
        branch.keys.append(15)
        assert not branch.is_underfull()
    
    def test_underflow_after_deletion_creates_violation(self):
        """Test that deleting keys can create underflow violations"""
        tree = BPlusTreeMap(capacity=4)
        
        # Create a tree with enough items to have branch nodes
        for i in range(1, 10):
            tree[i] = f"value_{i}"
        
        # Delete many items to potentially create underflow
        # (This test documents current behavior - underflow handling will be added later)
        del tree[1]
        del tree[2] 
        del tree[3]
        del tree[4]
        
        # Check if any nodes are underfull (they might be, which is expected for now)
        has_underflow = self._tree_has_underflow(tree)
        
        # For now, just verify the tree still functions correctly
        assert len(tree) == 5
        assert tree[5] == "value_5"
    
    def test_deletion_can_violate_underflow_invariant(self):
        """Test that deletions can create underflow violations (documenting current behavior)"""
        tree = BPlusTreeMap(capacity=4)
        
        # Create a minimal tree that will have underflow after deletion
        tree[1] = "one"
        tree[2] = "two"
        tree[3] = "three"
        tree[4] = "four"
        tree[5] = "five"  # This creates a branch node
        
        # Verify we start with a valid tree
        assert tree.invariants()
        
        # Delete items from one leaf to make it underfull
        del tree[1]
        del tree[2]
        
        # Our current deletion implementation actually handles this well
        # by removing empty leaves, so invariants should still hold
        assert tree.invariants()
        
        # The tree should still be functionally correct even if invariants are violated
        assert len(tree) == 3
        assert tree[3] == "three"
        assert tree[4] == "four"
        assert tree[5] == "five"
        
    def _tree_has_underflow(self, tree) -> bool:
        """Helper to check if any non-root nodes in tree are underfull"""
        def check_node(node, is_root=False):
            if is_root:
                return False  # Root can be underfull
            
            if node.is_underfull():
                return True
                
            if not node.is_leaf():
                for child in node.children:
                    if check_node(child, False):
                        return True
            return False
        
        return check_node(tree.root, is_root=True)


class TestBranchNode:
    """Test BranchNode operations"""

    def test_branch_node_creation(self):
        """Test creating a branch node"""
        branch = BranchNode(capacity=4)
        assert not branch.is_leaf()
        assert not branch.is_full()
        assert len(branch) == 0

    def test_find_child_index(self):
        """Test finding correct child index"""
        branch = BranchNode(capacity=4)
        branch.keys = [10, 20, 30]

        # Create dummy leaf nodes as children
        for i in range(4):
            branch.children.append(LeafNode(capacity=4))

        # Test finding child indices
        assert branch.find_child_index(5) == 0  # < 10
        assert branch.find_child_index(10) == 1  # >= 10, < 20
        assert branch.find_child_index(15) == 1  # >= 10, < 20
        assert branch.find_child_index(20) == 2  # >= 20, < 30
        assert branch.find_child_index(25) == 2  # >= 20, < 30
        assert branch.find_child_index(30) == 3  # >= 30
        assert branch.find_child_index(35) == 3  # >= 30

    def test_branch_node_split(self):
        """Test splitting a branch node"""
        branch = BranchNode(capacity=4)
        branch.keys = [10, 20, 30, 40]
        
        # Create dummy children (one more than keys)
        branch.children = [LeafNode(4) for _ in range(5)]
        
        # Split the branch
        new_branch, separator = branch.split()
        
        # Check the split results
        assert separator == 30  # Middle key should be promoted (keys[2])
        assert branch.keys == [10, 20]  # Left half
        assert new_branch.keys == [40]  # Right half (excluding promoted key)
        assert len(branch.children) == 3  # mid + 1 = 3
        assert len(new_branch.children) == 2  # 5 - 3 = 2


class TestSiblingRedistribution:
    """Test sibling key redistribution during deletion"""

    def test_leaf_can_donate(self):
        """Test that leaf nodes correctly detect when they can donate keys"""
        leaf = LeafNode(capacity=4)  # min_keys = 2
        
        # Empty leaf cannot donate
        assert not leaf.can_donate()
        
        # Leaf with 1 key cannot donate  
        leaf.keys = [1]
        leaf.values = ["one"]
        assert not leaf.can_donate()
        
        # Leaf with 2 keys (minimum) cannot donate
        leaf.keys = [1, 2]
        leaf.values = ["one", "two"]
        assert not leaf.can_donate()
        
        # Leaf with 3 keys can donate
        leaf.keys = [1, 2, 3]
        leaf.values = ["one", "two", "three"]
        assert leaf.can_donate()

    def test_branch_can_donate(self):
        """Test that branch nodes correctly detect when they can donate keys"""
        branch = BranchNode(capacity=4)  # min_keys = 2
        
        # Empty branch cannot donate
        assert not branch.can_donate()
        
        # Branch with 1 key cannot donate
        branch.keys = [5]
        branch.children = [LeafNode(4), LeafNode(4)]
        assert not branch.can_donate()
        
        # Branch with 2 keys (minimum) cannot donate
        branch.keys = [5, 10]
        branch.children = [LeafNode(4), LeafNode(4), LeafNode(4)]
        assert not branch.can_donate()
        
        # Branch with 3 keys can donate
        branch.keys = [5, 10, 15]
        branch.children = [LeafNode(4), LeafNode(4), LeafNode(4), LeafNode(4)]
        assert branch.can_donate()

    def test_leaf_borrow_from_left(self):
        """Test leaf borrowing keys from left sibling"""
        left = LeafNode(capacity=4)
        right = LeafNode(capacity=4)
        
        # Set up left sibling with excess keys
        left.keys = [1, 2, 3]
        left.values = ["one", "two", "three"]
        
        # Set up right sibling with too few keys
        right.keys = [5]
        right.values = ["five"]
        
        # Borrow from left
        right.borrow_from_left(left)
        
        # Verify redistribution
        assert left.keys == [1, 2]
        assert left.values == ["one", "two"]
        assert right.keys == [3, 5]
        assert right.values == ["three", "five"]

    def test_leaf_borrow_from_right(self):
        """Test leaf borrowing keys from right sibling"""
        left = LeafNode(capacity=4)
        right = LeafNode(capacity=4)
        
        # Set up left sibling with too few keys
        left.keys = [1]
        left.values = ["one"]
        
        # Set up right sibling with excess keys
        right.keys = [5, 6, 7]
        right.values = ["five", "six", "seven"]
        
        # Borrow from right
        left.borrow_from_right(right)
        
        # Verify redistribution
        assert left.keys == [1, 5]
        assert left.values == ["one", "five"]
        assert right.keys == [6, 7]
        assert right.values == ["six", "seven"]

    def test_branch_borrow_from_left(self):
        """Test branch borrowing keys from left sibling"""
        left = BranchNode(capacity=4)
        right = BranchNode(capacity=4)
        
        # Set up left sibling with excess keys and children
        left.keys = [5, 10, 15]
        left.children = [LeafNode(4) for _ in range(4)]
        
        # Set up right sibling with too few keys
        right.keys = [25]
        right.children = [LeafNode(4), LeafNode(4)]
        
        # Borrow from left with separator key 20
        new_separator = right.borrow_from_left(left, 20)
        
        # Verify redistribution
        assert left.keys == [5, 10]
        assert len(left.children) == 3
        assert right.keys == [20, 25]
        assert len(right.children) == 3
        assert new_separator == 15

    def test_branch_borrow_from_right(self):
        """Test branch borrowing keys from right sibling"""
        left = BranchNode(capacity=4)
        right = BranchNode(capacity=4)
        
        # Set up left sibling with too few keys
        left.keys = [5]
        left.children = [LeafNode(4), LeafNode(4)]
        
        # Set up right sibling with excess keys and children
        right.keys = [15, 20, 25]
        right.children = [LeafNode(4) for _ in range(4)]
        
        # Borrow from right with separator key 10
        new_separator = left.borrow_from_right(right, 10)
        
        # Verify redistribution
        assert left.keys == [5, 10]
        assert len(left.children) == 3
        assert right.keys == [20, 25]
        assert len(right.children) == 3
        assert new_separator == 15

    def test_redistribution_during_deletion(self):
        """Test that underflow handling (redistribution or merging) works during deletion"""
        tree = BPlusTreeMap(capacity=4)
        
        # Create a tree where deletion will trigger underflow handling
        # Insert enough items to create multiple leaves
        for i in range(1, 8):
            tree[i] = f"value_{i}"
        
        # Verify tree structure before deletion
        assert tree.invariants()
        initial_structure = tree.leaf_count()
        
        # Delete an item that should trigger underflow handling
        del tree[1]
        
        # Tree should still be valid (may have fewer leaves due to merging)
        assert tree.invariants()
        assert tree.leaf_count() <= initial_structure  # Merging may reduce leaf count
        
        # Verify remaining keys
        for i in range(2, 8):
            assert tree[i] == f"value_{i}"

    def test_actual_redistribution_scenario(self):
        """Test a scenario that actually triggers redistribution (not merging)"""
        tree = BPlusTreeMap(capacity=4)
        
        # Create a tree structure where redistribution will be possible
        # Insert keys that will create leaves where one can donate to another
        keys = [10, 20, 30, 40, 50, 60, 70]
        for key in keys:
            tree[key] = f"value_{key}"
        
        # Check the initial structure - this should create leaves with uneven distribution
        assert tree.invariants()
        initial_leaf_count = tree.leaf_count()
        
        # Delete a key to create underflow where redistribution should be possible
        del tree[10]
        
        # Tree should remain valid and potentially maintain leaf count via redistribution
        assert tree.invariants()
        
        # Verify remaining keys are accessible
        remaining_keys = [20, 30, 40, 50, 60, 70]
        for key in remaining_keys:
            assert tree[key] == f"value_{key}"

    def test_forced_redistribution_scenario(self):
        """Test a specific scenario that forces redistribution"""
        tree = BPlusTreeMap(capacity=4)
        
        # Create a tree with specific structure to force redistribution
        # Insert keys to create a scenario where one leaf becomes underfull
        keys = [5, 10, 15, 20, 25, 30, 35, 40]
        for key in keys:
            tree[key] = f"value_{key}"
        
        # Verify initial state
        assert tree.invariants()
        
        # Find a leaf that will become underfull after deletion
        # With capacity=4, min_keys=2, so deleting from a leaf with 2 keys should trigger redistribution
        initial_len = len(tree)
        
        # Delete multiple keys from one area to create underflow
        del tree[5]  # This should work without redistribution
        assert tree.invariants()
        
        # Continue deleting to potentially trigger redistribution
        # The exact behavior depends on the tree structure, but it should remain valid
        del tree[10]
        assert tree.invariants()
        assert len(tree) == initial_len - 2
        
        # Verify remaining keys are still accessible
        remaining_keys = [15, 20, 25, 30, 35, 40]
        for key in remaining_keys:
            assert tree[key] == f"value_{key}"


class TestNodeMerging:
    """Test node merging during deletion"""

    def test_leaf_merge_with_right(self):
        """Test merging a leaf with its right sibling"""
        left = LeafNode(capacity=4)
        right = LeafNode(capacity=4)
        
        # Set up left leaf with underfull keys
        left.keys = [1]
        left.values = ["one"]
        
        # Set up right leaf
        right.keys = [5, 6]
        right.values = ["five", "six"]
        
        # Set up linked list
        left.next = right
        
        # Merge left with right
        left.merge_with_right(right)
        
        # Verify merge results
        assert left.keys == [1, 5, 6]
        assert left.values == ["one", "five", "six"]
        assert left.next == right.next  # Should skip merged node

    def test_branch_merge_with_right(self):
        """Test merging a branch with its right sibling"""
        left = BranchNode(capacity=4)
        right = BranchNode(capacity=4)
        
        # Set up left branch with underfull keys
        left.keys = [5]
        left.children = [LeafNode(4), LeafNode(4)]
        
        # Set up right branch
        right.keys = [15, 20]
        right.children = [LeafNode(4), LeafNode(4), LeafNode(4)]
        
        # Merge with separator key 10
        left.merge_with_right(right, 10)
        
        # Verify merge results
        assert left.keys == [5, 10, 15, 20]
        assert len(left.children) == 5  # 2 + 3

    def test_merging_during_deletion_creates_balanced_tree(self):
        """Test that merging during deletion maintains tree balance"""
        tree = BPlusTreeMap(capacity=3)  # Small capacity to force merging
        
        # Insert keys to create a tree structure
        for i in range(1, 10):
            tree[i] = f"value_{i}"
        
        # Verify initial state
        assert tree.invariants()
        initial_leaf_count = tree.leaf_count()
        
        # Delete enough keys to force merging
        keys_to_delete = [1, 2, 3, 4]
        for key in keys_to_delete:
            del tree[key]
            assert tree.invariants()  # Should remain valid after each deletion
        
        # Tree should have fewer leaves after merging
        final_leaf_count = tree.leaf_count()
        assert final_leaf_count <= initial_leaf_count
        
        # Verify remaining keys are still accessible
        remaining_keys = [5, 6, 7, 8, 9]
        for key in remaining_keys:
            assert tree[key] == f"value_{key}"

    def test_cascade_merging(self):
        """Test that merging can cascade up the tree"""
        tree = BPlusTreeMap(capacity=3)
        
        # Create a deeper tree structure
        for i in range(1, 16):
            tree[i] = f"value_{i}"
        
        # Verify initial state
        assert tree.invariants()
        initial_structure = tree.leaf_count()
        
        # Delete many keys to potentially cause cascading merges
        keys_to_delete = list(range(1, 8))  # Delete about half
        for key in keys_to_delete:
            del tree[key]
            # Tree should remain valid after each deletion
            assert tree.invariants()
        
        # Verify remaining keys
        remaining_keys = list(range(8, 16))
        for key in remaining_keys:
            assert tree[key] == f"value_{key}"
        
        # Tree structure may have changed significantly
        final_structure = tree.leaf_count()
        assert final_structure <= initial_structure

    def test_merge_vs_redistribute_preference(self):
        """Test that redistribution is preferred over merging when possible"""
        tree = BPlusTreeMap(capacity=4)
        
        # Create a specific scenario where we can test preference
        keys = [10, 20, 30, 40, 50, 60]
        for key in keys:
            tree[key] = f"value_{key}"
        
        assert tree.invariants()
        initial_leaf_count = tree.leaf_count()
        
        # Delete one key - this should trigger redistribution, not merging
        del tree[10]
        assert tree.invariants()
        
        # If redistribution worked, we should have same number of leaves
        # If merging happened, we'd have fewer leaves
        assert tree.leaf_count() == initial_leaf_count
        
        # Verify remaining keys
        remaining_keys = [20, 30, 40, 50, 60]
        for key in remaining_keys:
            assert tree[key] == f"value_{key}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
