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
    
    def test_insert_and_get_single_item(self):
        """Test inserting and retrieving a single item"""
        tree = BPlusTreeMap(capacity=4)
        tree[1] = "one"
        
        assert len(tree) == 1
        assert tree  # Should be truthy when not empty
        assert tree[1] == "one"
        assert tree.get(1) == "one"
    
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
    
    def test_update_existing_key(self):
        """Test updating an existing key"""
        tree = BPlusTreeMap(capacity=4)
        tree[1] = "one"
        tree[1] = "ONE"
        
        assert len(tree) == 1  # Size shouldn't change
        assert tree[1] == "ONE"
    
    def test_contains_operator(self):
        """Test the 'in' operator"""
        tree = BPlusTreeMap(capacity=4)
        tree[1] = "one"
        tree[2] = "two"
        
        assert 1 in tree
        assert 2 in tree
        assert 3 not in tree
    
    def test_get_with_default(self):
        """Test get() with default value"""
        tree = BPlusTreeMap(capacity=4)
        tree[1] = "one"
        
        assert tree.get(1) == "one"
        assert tree.get(2) is None
        assert tree.get(2, "default") == "default"
    
    def test_key_error_on_missing_key(self):
        """Test that KeyError is raised for missing keys"""
        tree = BPlusTreeMap(capacity=4)
        tree[1] = "one"
        
        with pytest.raises(KeyError):
            _ = tree[2]


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
        assert leaf.find_position(5) == (0, False)   # Before all
        assert leaf.find_position(15) == (1, False)  # Between 10 and 20
        assert leaf.find_position(25) == (2, False)  # Between 20 and 30
        assert leaf.find_position(35) == (3, False)  # After all


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
        assert branch.find_child_index(5) == 0    # < 10
        assert branch.find_child_index(10) == 1   # >= 10, < 20
        assert branch.find_child_index(15) == 1   # >= 10, < 20
        assert branch.find_child_index(20) == 2   # >= 20, < 30
        assert branch.find_child_index(25) == 2   # >= 20, < 30
        assert branch.find_child_index(30) == 3   # >= 30
        assert branch.find_child_index(35) == 3   # >= 30


if __name__ == "__main__":
    pytest.main([__file__, "-v"])