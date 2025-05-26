use bplustree3::BPlusTree;

#[test]
fn test_bplus_tree_remove_existing_key() {
    let mut tree = BPlusTree::new(4);

    // Insert some test data
    tree.insert(10, 100);
    tree.insert(20, 200);
    tree.insert(30, 300);

    // Test removing existing key
    assert_eq!(tree.remove(&20), Some(200));
    assert_eq!(tree.get(&20), None);

    // Verify other keys still exist
    assert_eq!(tree.get(&10), Some(&100));
    assert_eq!(tree.get(&30), Some(&300));

    // Validate tree invariants
    tree.validate()
        .expect("Tree should maintain invariants after remove");
}

#[test]
fn test_bplus_tree_remove_with_underflow() {
    let mut tree = BPlusTree::new(2); // Small branching factor, min_keys = 1

    // Insert enough keys to create multiple nodes
    tree.insert(10, 100);
    tree.insert(20, 200);
    tree.insert(30, 300);
    tree.insert(40, 400);
    tree.insert(50, 500);

    // Verify we have multiple nodes
    assert!(tree.leaf_count() > 1, "Should have multiple nodes");

    // Remove a key from the first node to cause underflow
    tree.remove(&10);

    // Tree should still be valid and accessible
    assert_eq!(tree.get(&10), None);
    assert_eq!(tree.get(&20), Some(&200));
    assert_eq!(tree.get(&30), Some(&300));
    assert_eq!(tree.get(&40), Some(&400));
    assert_eq!(tree.get(&50), Some(&500));

    // The tree should have handled underflow through redistribution or merge
    // All remaining keys should still be accessible
    for &key in &[20, 30, 40, 50] {
        assert!(
            tree.get(&key).is_some(),
            "Key {} should still be accessible",
            key
        );
    }

    // Validate tree invariants
    tree.validate()
        .expect("Tree should maintain invariants after underflow handling");
}

#[test]
fn test_bplus_tree_remove_last_key_from_tree() {
    let mut tree = BPlusTree::new(4);

    // Insert a single key
    tree.insert(42, 420);
    assert_eq!(tree.get(&42), Some(&420));
    assert_eq!(tree.len(), 1);

    // Remove the last (and only) key
    assert_eq!(tree.remove(&42), Some(420));

    // Tree should be empty but still valid
    assert_eq!(tree.len(), 0);
    assert!(tree.is_empty());
    assert_eq!(tree.get(&42), None);

    // Tree should still be in a valid state for future operations
    tree.insert(100, 1000);
    assert_eq!(tree.get(&100), Some(&1000));
    assert_eq!(tree.len(), 1);

    // Validate tree invariants
    tree.validate()
        .expect("Tree should maintain invariants after removing last key");
}

#[test]
fn test_bplus_tree_remove_all_keys_from_single_node() {
    let mut tree = BPlusTree::new(4);

    // Insert multiple keys in a single node
    tree.insert(10, 100);
    tree.insert(20, 200);
    tree.insert(30, 300);

    // Verify we have one node with 3 keys
    assert_eq!(tree.leaf_count(), 1);
    assert_eq!(tree.len(), 3);

    // Remove all keys one by one
    assert_eq!(tree.remove(&20), Some(200));
    assert_eq!(tree.len(), 2);
    tree.validate()
        .expect("Tree should be valid after first removal");

    assert_eq!(tree.remove(&10), Some(100));
    assert_eq!(tree.len(), 1);
    tree.validate()
        .expect("Tree should be valid after second removal");

    assert_eq!(tree.remove(&30), Some(300));
    assert_eq!(tree.len(), 0);
    assert!(tree.is_empty());

    // Tree should still be valid and usable
    tree.insert(50, 500);
    assert_eq!(tree.get(&50), Some(&500));
    assert_eq!(tree.len(), 1);

    // Validate tree invariants
    tree.validate()
        .expect("Tree should maintain invariants after removing all keys");
}

#[test]
fn test_bplus_tree_remove_from_first_node_causing_empty() {
    let mut tree = BPlusTree::new(2); // Small branching factor

    // Create a scenario with multiple nodes where first node becomes empty
    tree.insert(10, 100);
    tree.insert(20, 200);
    tree.insert(30, 300);
    tree.insert(40, 400);

    // Verify we have multiple nodes
    assert!(tree.leaf_count() > 1, "Should have multiple nodes");

    // Remove all keys from what should be the first node
    // This should trigger special handling for empty first node
    tree.remove(&10);

    // Tree should still be valid and all remaining keys accessible
    assert_eq!(tree.get(&10), None);
    assert_eq!(tree.get(&20), Some(&200));
    assert_eq!(tree.get(&30), Some(&300));
    assert_eq!(tree.get(&40), Some(&400));

    // The tree structure should be valid even if first node is empty/removed
    tree.validate()
        .expect("Tree should handle empty first node correctly");
}

#[test]
fn test_bplus_tree_remove_with_root_node_empty_validation() {
    let mut tree = BPlusTree::new(4);

    // Insert a single key and remove it
    tree.insert(42, 420);
    tree.remove(&42);

    // The root node should now be empty (count = 0)
    // But our validation should handle this correctly
    assert_eq!(tree.len(), 0);
    assert!(tree.is_empty());

    // Check that validation passes for empty root
    tree.validate().expect("Empty root should be valid");

    // Check that the tree is still usable
    tree.insert(100, 1000);
    assert_eq!(tree.get(&100), Some(&1000));
    tree.validate().expect("Tree should be valid after reuse");
}

#[test]
fn test_remove_nonexistent_key() {
    let mut tree = BPlusTree::new(4);

    // Insert some test data
    tree.insert(10, 100);
    tree.insert(20, 200);
    tree.insert(30, 300);

    // Test removing non-existing key
    assert_eq!(tree.remove(&99), None);
    assert_eq!(tree.len(), 3); // Length should remain unchanged

    // All original keys should still exist
    assert_eq!(tree.get(&10), Some(&100));
    assert_eq!(tree.get(&20), Some(&200));
    assert_eq!(tree.get(&30), Some(&300));

    // Validate tree invariants
    tree.validate()
        .expect("Tree should maintain invariants after failed remove");
}
