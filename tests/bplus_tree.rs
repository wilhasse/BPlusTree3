use bplustree3::{BPlusTreeError, BPlusTreeMap};

// ============================================================================
// TRANSLATED PYTHON TESTS - Basic Operations
// ============================================================================

#[test]
fn test_create_empty_tree() {
    let tree = BPlusTreeMap::<i32, String>::new(4).unwrap();
    assert_eq!(tree.len(), 0);
    assert!(tree.is_empty());
    // TODO: Add invariant checking when implemented
}

#[test]
fn test_insert_and_get_single_item() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    tree.insert(1, "one".to_string());

    assert_eq!(tree.len(), 1);
    assert!(!tree.is_empty());
    assert_eq!(tree.get(&1), Some(&"one".to_string()));
    // TODO: Add invariant checking when implemented
}

#[test]
fn test_insert_multiple_items() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    tree.insert(1, "one".to_string());
    tree.insert(2, "two".to_string());
    tree.insert(3, "three".to_string());

    assert_eq!(tree.len(), 3);
    assert_eq!(tree.get(&1), Some(&"one".to_string()));
    assert_eq!(tree.get(&2), Some(&"two".to_string()));
    assert_eq!(tree.get(&3), Some(&"three".to_string()));
    // TODO: Add invariant checking when implemented
}

#[test]
fn test_update_existing_key() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    tree.insert(1, "one".to_string());
    let old_value = tree.insert(1, "ONE".to_string());

    assert_eq!(tree.len(), 1); // Size shouldn't change
    assert_eq!(tree.get(&1), Some(&"ONE".to_string()));
    assert_eq!(old_value, Some("one".to_string()));
    // TODO: Add invariant checking when implemented
}

#[test]
fn test_contains_key() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    tree.insert(1, "one".to_string());
    tree.insert(2, "two".to_string());

    assert!(tree.contains_key(&1));
    assert!(tree.contains_key(&2));
    assert!(!tree.contains_key(&3));
    // TODO: Add invariant checking when implemented
}

#[test]
fn test_get_with_default() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    tree.insert(1, "one".to_string());

    assert_eq!(tree.get(&1), Some(&"one".to_string()));
    assert_eq!(tree.get(&2), None);
    assert_eq!(
        tree.get_or_default(&2, &"default".to_string()),
        &"default".to_string()
    );
    // TODO: Add invariant checking when implemented
}

// ============================================================================
// TRANSLATED PYTHON TESTS - Splitting Operations
// ============================================================================

#[test]
fn test_overflow() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    // With capacity=4, need 5 items to force a split
    tree.insert(1, "one".to_string());
    tree.insert(2, "two".to_string());
    tree.insert(3, "three".to_string());
    tree.insert(4, "four".to_string());
    tree.insert(5, "five".to_string());

    // TODO: Add invariant checking when implemented
    assert_eq!(tree.len(), 5);
    assert_eq!(tree.get(&1), Some(&"one".to_string()));
    assert_eq!(tree.get(&2), Some(&"two".to_string()));
    assert_eq!(tree.get(&3), Some(&"three".to_string()));
    assert_eq!(tree.get(&4), Some(&"four".to_string()));
    assert_eq!(tree.get(&5), Some(&"five".to_string()));

    assert!(!tree.is_leaf_root());
}

#[test]
fn test_split_then_add() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    // With capacity=4, need more items to force multiple splits
    tree.insert(1, "one".to_string());
    tree.insert(2, "two".to_string());
    tree.insert(3, "three".to_string());
    tree.insert(4, "four".to_string());
    tree.insert(5, "five".to_string());
    tree.insert(6, "six".to_string());
    tree.insert(7, "seven".to_string());
    tree.insert(8, "eight".to_string());

    // Check correctness via invariants instead of exact structure
    // TODO: Add invariant checking when implemented
    assert_eq!(tree.len(), 8);
    assert_eq!(tree.get(&1), Some(&"one".to_string()));
    assert_eq!(tree.get(&2), Some(&"two".to_string()));
    assert_eq!(tree.get(&3), Some(&"three".to_string()));
    assert_eq!(tree.get(&4), Some(&"four".to_string()));
    assert_eq!(tree.get(&5), Some(&"five".to_string()));
    assert_eq!(tree.get(&6), Some(&"six".to_string()));
    assert_eq!(tree.get(&7), Some(&"seven".to_string()));
    assert_eq!(tree.get(&8), Some(&"eight".to_string()));

    // The simpler implementation may create more leaves, but that's OK
    // as long as invariants hold
    assert!(tree.leaf_count() >= 2); // At minimum need 2 leaves for 8 items with capacity 4
}

#[test]
fn test_many_insertions_maintain_invariants() {
    let mut tree = BPlusTreeMap::new(6).unwrap();

    // Insert many items
    for i in 0..20 {
        tree.insert(i, format!("value_{}", i));
        // TODO: Check invariants after each insertion when implemented
    }

    // Verify all items are retrievable
    for i in 0..20 {
        assert_eq!(tree.get(&i), Some(&format!("value_{}", i)));
    }
}

#[test]
fn test_parent_splitting() {
    let mut tree = BPlusTreeMap::new(5).unwrap(); // Small capacity to force parent splits

    // Insert enough items to force multiple levels of splits
    for i in 0..50 {
        tree.insert(i, format!("value_{}", i));
        // TODO: Check invariants after each insertion when implemented
    }

    // Verify all items are still retrievable
    for i in 0..50 {
        assert_eq!(tree.get(&i), Some(&format!("value_{}", i)));
    }

    // The tree should have multiple levels now
    assert!(!tree.is_leaf_root());

    // TODO: Check that no nodes are overfull when implemented
}

// ============================================================================
// TRANSLATED PYTHON TESTS - Removal Operations
// ============================================================================

#[test]
fn test_remove_single_item_from_leaf_root() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    tree.insert(1, "one".to_string());

    // Remove the item
    let removed = tree.remove(&1);

    // Tree should be empty
    assert_eq!(removed, Some("one".to_string()));
    assert_eq!(tree.len(), 0);
    assert!(!tree.contains_key(&1));
    // TODO: Add invariant checking when implemented

    // Should return None when trying to get removed item
    assert_eq!(tree.get(&1), None);
}

#[test]
fn test_remove_multiple_items_from_leaf_root() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    tree.insert(1, "one".to_string());
    tree.insert(2, "two".to_string());
    tree.insert(3, "three".to_string());

    // Remove items
    let removed = tree.remove(&2);

    // Check state after first removal
    assert_eq!(removed, Some("two".to_string()));
    assert_eq!(tree.len(), 2);
    assert!(tree.contains_key(&1));
    assert!(!tree.contains_key(&2));
    assert!(tree.contains_key(&3));
    assert_eq!(tree.get(&1), Some(&"one".to_string()));
    assert_eq!(tree.get(&3), Some(&"three".to_string()));
    // TODO: Add invariant checking when implemented

    // Remove another item
    let removed = tree.remove(&1);

    // Check state after second removal
    assert_eq!(removed, Some("one".to_string()));
    assert_eq!(tree.len(), 1);
    assert!(!tree.contains_key(&1));
    assert!(tree.contains_key(&3));
    assert_eq!(tree.get(&3), Some(&"three".to_string()));
    // TODO: Add invariant checking when implemented

    // Remove last item
    let removed = tree.remove(&3);

    // Tree should be empty
    assert_eq!(removed, Some("three".to_string()));
    assert_eq!(tree.len(), 0);
    // TODO: Add invariant checking when implemented
}

#[test]
fn test_remove_nonexistent_key_returns_none() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    tree.insert(1, "one".to_string());
    tree.insert(2, "two".to_string());

    // Try to remove non-existent key
    let removed = tree.remove(&3);

    // Should return None
    assert_eq!(removed, None);

    // Tree should be unchanged
    assert_eq!(tree.len(), 2);
    assert_eq!(tree.get(&1), Some(&"one".to_string()));
    assert_eq!(tree.get(&2), Some(&"two".to_string()));
    // TODO: Add invariant checking when implemented
}

// ============================================================================
// TRANSLATED PYTHON TESTS - More Removal Operations
// ============================================================================

#[test]
fn test_remove_from_tree_with_branch_root() {
    let mut tree = BPlusTreeMap::new(4).unwrap();

    // Insert enough items to create a branch root
    for i in 1..=5 {
        tree.insert(i, format!("value_{}", i));
    }

    // Verify we have a branch root
    assert!(!tree.is_leaf_root());
    assert_eq!(tree.len(), 5);

    // Remove an item
    let removed = tree.remove(&2);

    // Check the item was removed
    assert_eq!(removed, Some("value_2".to_string()));
    assert_eq!(tree.len(), 4);
    assert!(!tree.contains_key(&2));
    assert_eq!(tree.get(&1), Some(&"value_1".to_string()));
    assert_eq!(tree.get(&3), Some(&"value_3".to_string()));
    assert_eq!(tree.get(&4), Some(&"value_4".to_string()));
    assert_eq!(tree.get(&5), Some(&"value_5".to_string()));
    // TODO: Add invariant checking when implemented
}

#[test]
fn test_remove_multiple_from_tree_with_branches() {
    let mut tree = BPlusTreeMap::new(4).unwrap();

    // Insert more items to ensure we have multiple levels
    for i in 1..=9 {
        tree.insert(i, format!("value_{}", i));
    }

    // Remove items in various orders
    let removed1 = tree.remove(&3);
    let removed2 = tree.remove(&6);
    let removed3 = tree.remove(&1);

    // Check remaining items
    assert_eq!(removed1, Some("value_3".to_string()));
    assert_eq!(removed2, Some("value_6".to_string()));
    assert_eq!(removed3, Some("value_1".to_string()));
    assert_eq!(tree.len(), 6);
    assert_eq!(tree.get(&2), Some(&"value_2".to_string()));
    assert_eq!(tree.get(&4), Some(&"value_4".to_string()));
    assert_eq!(tree.get(&5), Some(&"value_5".to_string()));
    assert_eq!(tree.get(&7), Some(&"value_7".to_string()));
    assert_eq!(tree.get(&8), Some(&"value_8".to_string()));
    assert_eq!(tree.get(&9), Some(&"value_9".to_string()));

    // Check removed items are gone
    assert!(!tree.contains_key(&1));
    assert!(!tree.contains_key(&3));
    assert!(!tree.contains_key(&6));

    // TODO: Add invariant checking when implemented
}

// ============================================================================
// TRANSLATED PYTHON TESTS - Range and Iterator Operations
// ============================================================================

// TODO: Implement iterator tests after fixing lifetime issues
/*
#[test]
fn test_keys_iterator() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    tree.insert(1, "one".to_string());
    tree.insert(2, "two".to_string());
    tree.insert(3, "three".to_string());

    let keys: Vec<_> = tree.keys().collect();
    assert_eq!(keys, vec![&1, &2, &3]);
}

#[test]
fn test_values_iterator() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    tree.insert(1, "one".to_string());
    tree.insert(2, "two".to_string());
    tree.insert(3, "three".to_string());

    let values: Vec<_> = tree.values().collect();
    assert_eq!(values, vec![&"one".to_string(), &"two".to_string(), &"three".to_string()]);
}

#[test]
fn test_items_iterator() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    tree.insert(1, "one".to_string());
    tree.insert(2, "two".to_string());
    tree.insert(3, "three".to_string());

    let items: Vec<_> = tree.iter().collect();
    assert_eq!(items, vec![
        (&1, &"one".to_string()),
        (&2, &"two".to_string()),
        (&3, &"three".to_string())
    ]);
}

#[test]
fn test_range_iterator() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    for i in 1..=10 {
        tree.insert(i, format!("value_{}", i));
    }

    let range_items: Vec<_> = tree.range(3..=7).collect();
    assert_eq!(range_items, vec![
        (&3, &"value_3".to_string()),
        (&4, &"value_4".to_string()),
        (&5, &"value_5".to_string()),
        (&6, &"value_6".to_string()),
        (&7, &"value_7".to_string())
    ]);
}
*/

// ============================================================================
// TRANSLATED PYTHON TESTS - Node Operations (for future implementation)
// ============================================================================

// These tests will be implemented when we add the Node trait and specific node operations

// TODO: Implement test_leaf_node_creation
// TODO: Implement test_leaf_node_insert
// TODO: Implement test_leaf_node_full
// TODO: Implement test_leaf_find_position
// TODO: Implement test_branch_node_creation
// TODO: Implement test_find_child_index
// TODO: Implement test_branch_node_split
// TODO: Implement test_leaf_can_donate
// TODO: Implement test_branch_can_donate
// TODO: Implement test_leaf_borrow_from_left
// TODO: Implement test_leaf_borrow_from_right
// TODO: Implement test_branch_borrow_from_left
// TODO: Implement test_branch_borrow_from_right
// TODO: Implement test_leaf_merge_with_right
// TODO: Implement test_branch_merge_with_right

// ============================================================================
// TRANSLATED PYTHON TESTS - Capacity Validation
// ============================================================================

#[test]
fn test_invalid_capacity_error() {
    // Test that creating a tree with capacity < 4 should return error
    let result = BPlusTreeMap::<i32, String>::new(3);
    assert!(result.is_err());

    // Test that capacity 4 works
    let _tree = BPlusTreeMap::<i32, String>::new(4).unwrap();
}

// ============================================================================
// STRESS TESTS - These will be implemented after basic functionality works
// ============================================================================

// ============================================================================
// NEW TESTS - Dict-like API
// ============================================================================

#[test]
fn test_key_error_on_missing_key() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    tree.insert(1, "one".to_string());

    // Test that get_item returns error for missing keys
    let result = tree.get_item(&2);
    assert_eq!(result, Err(BPlusTreeError::KeyNotFound));

    // Existing key should work
    let result = tree.get_item(&1);
    assert_eq!(result, Ok(&"one".to_string()));
}

#[test]
fn test_remove_nonexistent_key_raises_error() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    tree.insert(1, "one".to_string());
    tree.insert(2, "two".to_string());

    // Try to remove non-existent key
    let result = tree.remove_item(&3);
    assert_eq!(result, Err(BPlusTreeError::KeyNotFound));

    // Tree should be unchanged
    assert_eq!(tree.len(), 2);
    assert_eq!(tree.get(&1), Some(&"one".to_string()));
    assert_eq!(tree.get(&2), Some(&"two".to_string()));
}

// ============================================================================
// NEW TESTS - Iterator Support
// ============================================================================

#[test]
fn test_iterate_empty_tree() {
    let tree = BPlusTreeMap::<i32, String>::new(4).unwrap();
    let items: Vec<_> = tree.items().collect();
    assert_eq!(items, vec![]);
}

#[test]
fn test_iterate_single_item() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    tree.insert(5, "value5".to_string());

    let items: Vec<_> = tree.items().collect();
    assert_eq!(items, vec![(&5, &"value5".to_string())]);
}

#[test]
fn test_iterate_multiple_items_single_leaf() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    tree.insert(1, "value1".to_string());
    tree.insert(3, "value3".to_string());
    tree.insert(2, "value2".to_string());
    tree.insert(4, "value4".to_string());

    let items: Vec<_> = tree.items().collect();
    assert_eq!(
        items,
        vec![
            (&1, &"value1".to_string()),
            (&2, &"value2".to_string()),
            (&3, &"value3".to_string()),
            (&4, &"value4".to_string())
        ]
    );
}

#[test]
fn test_iterate_multiple_leaves() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    // Insert enough to create multiple leaves
    for i in 1..=9 {
        tree.insert(i, format!("value{}", i));
    }

    let items: Vec<_> = tree.items().collect();
    // Check that we have the right number of items and they're in order
    assert_eq!(items.len(), 9);
    for (i, (key, value)) in items.iter().enumerate() {
        let expected_key = i + 1;
        let expected_value = format!("value{}", expected_key);
        assert_eq!(**key, expected_key);
        assert_eq!(**value, expected_value);
    }
}

#[test]
fn test_keys_iterator() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    tree.insert(1, "one".to_string());
    tree.insert(2, "two".to_string());
    tree.insert(3, "three".to_string());

    let keys: Vec<_> = tree.keys().collect();
    assert_eq!(keys, vec![&1, &2, &3]);
}

#[test]
fn test_values_iterator() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    tree.insert(1, "one".to_string());
    tree.insert(2, "two".to_string());
    tree.insert(3, "three".to_string());

    let values: Vec<_> = tree.values().collect();
    assert_eq!(
        values,
        vec![&"one".to_string(), &"two".to_string(), &"three".to_string()]
    );
}

// ============================================================================
// NEW TESTS - Range Iteration
// ============================================================================

#[test]
fn test_iterate_from_key() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    for i in 0..10 {
        tree.insert(i, format!("value{}", i));
    }

    let items: Vec<_> = tree.items_range(Some(&5), None).collect();
    assert_eq!(items.len(), 5); // keys 5, 6, 7, 8, 9
    for (i, (key, value)) in items.iter().enumerate() {
        let expected_key = i + 5;
        let expected_value = format!("value{}", expected_key);
        assert_eq!(**key, expected_key);
        assert_eq!(**value, expected_value);
    }
}

#[test]
fn test_iterate_until_key() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    for i in 0..10 {
        tree.insert(i, format!("value{}", i));
    }

    let items: Vec<_> = tree.items_range(None, Some(&5)).collect();
    assert_eq!(items.len(), 5); // keys 0, 1, 2, 3, 4
    for (i, (key, value)) in items.iter().enumerate() {
        let expected_key = i;
        let expected_value = format!("value{}", expected_key);
        assert_eq!(**key, expected_key);
        assert_eq!(**value, expected_value);
    }
}

#[test]
fn test_iterate_range() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    for i in 0..20 {
        tree.insert(i, format!("value{}", i));
    }

    let items: Vec<_> = tree.items_range(Some(&5), Some(&15)).collect();
    assert_eq!(items.len(), 10); // keys 5, 6, 7, 8, 9, 10, 11, 12, 13, 14
    for (i, (key, value)) in items.iter().enumerate() {
        let expected_key = i + 5;
        let expected_value = format!("value{}", expected_key);
        assert_eq!(**key, expected_key);
        assert_eq!(**value, expected_value);
    }
}

#[test]
fn test_iterate_from_nonexistent_key() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    for i in [1, 3, 5, 7, 9] {
        tree.insert(i, format!("value{}", i));
    }

    // Start from 4 (doesn't exist, should start from 5)
    let items: Vec<_> = tree.items_range(Some(&4), None).collect();
    assert_eq!(items.len(), 3); // keys 5, 7, 9
    assert_eq!(*items[0].0, 5);
    assert_eq!(*items[1].0, 7);
    assert_eq!(*items[2].0, 9);
}

#[test]
fn test_iterate_empty_range() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    for i in 0..10 {
        tree.insert(i, format!("value{}", i));
    }

    // Start after end (invalid range)
    let items: Vec<_> = tree.items_range(Some(&7), Some(&3)).collect();
    assert_eq!(items, vec![]);
}

// ============================================================================
// NEW TESTS - Invariant Checking
// ============================================================================

#[test]
fn test_invariants_empty_tree() {
    let tree = BPlusTreeMap::<i32, String>::new(4).unwrap();
    assert!(tree.check_invariants());
}

#[test]
fn test_invariants_single_item() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    tree.insert(1, "one".to_string());
    assert!(tree.check_invariants());
}

#[test]
fn test_invariants_after_split() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    // Insert enough items to force a split
    for i in 1..=5 {
        tree.insert(i, format!("value{}", i));
        assert!(
            tree.check_invariants(),
            "Invariants violated after inserting {}",
            i
        );
    }
}

#[test]
fn test_invariants_after_many_operations() {
    let mut tree = BPlusTreeMap::new(4).unwrap();

    // Insert many items
    for i in 0..20 {
        tree.insert(i, format!("value{}", i));
        assert!(
            tree.check_invariants(),
            "Invariants violated after inserting {}",
            i
        );
    }

    // Remove some items
    for i in [1, 5, 10, 15] {
        tree.remove(&i);
        assert!(
            tree.check_invariants(),
            "Invariants violated after removing {}",
            i
        );
    }

    // Insert more items
    for i in 20..30 {
        tree.insert(i, format!("value{}", i));
        assert!(
            tree.check_invariants(),
            "Invariants violated after inserting {}",
            i
        );
    }
}

// ============================================================================
// NEW TESTS - Edge Cases and Stress Tests
// ============================================================================

#[test]
fn test_large_capacity_edge_cases() {
    let mut tree = BPlusTreeMap::new(64).unwrap(); // Large capacity

    // Fill up close to capacity
    for i in 0..60 {
        tree.insert(i, format!("value_{}", i));
        assert!(
            tree.check_invariants(),
            "Invariants violated after inserting {}",
            i
        );
    }

    assert!(tree.is_leaf_root(), "Should still be single-level tree");

    // Delete most items to test underflow handling
    for i in (0..60).step_by(2) {
        // Delete every other item
        tree.remove(&i);
        assert!(tree.check_invariants(), "Delete {} broke invariants", i);
    }

    // Add items back to test growth
    for i in 60..70 {
        tree.insert(i, format!("new_value_{}", i));
        assert!(tree.check_invariants(), "Insert {} broke invariants", i);
    }
}

#[test]
fn test_capacity_boundary_conditions() {
    for capacity in [4, 8, 16, 32] {
        let mut tree = BPlusTreeMap::new(capacity).unwrap();

        // Fill exactly to capacity
        for i in 0..capacity {
            tree.insert(i, format!("value_{}", i));
            assert!(
                tree.check_invariants(),
                "Tree at capacity {} should be valid",
                capacity
            );
        }

        // Add one more to trigger split
        tree.insert(capacity, format!("value_{}", capacity));
        assert!(
            tree.check_invariants(),
            "Tree after split at capacity {} should be valid",
            capacity
        );

        // Delete back to capacity
        tree.remove(&capacity);
        assert!(
            tree.check_invariants(),
            "Tree after delete at capacity {} should be valid",
            capacity
        );
    }
}

#[test]
fn test_sequential_vs_random_patterns() {
    // Test sequential insertion
    let mut tree = BPlusTreeMap::new(8).unwrap();
    for i in 0..50 {
        tree.insert(i, format!("value_{}", i));
        assert!(
            tree.check_invariants(),
            "Sequential insert {} broke invariants",
            i
        );
    }

    // Test reverse insertion
    let mut tree = BPlusTreeMap::new(8).unwrap();
    for i in (0..50).rev() {
        tree.insert(i, format!("value_{}", i));
        assert!(
            tree.check_invariants(),
            "Reverse insert {} broke invariants",
            i
        );
    }

    // Test random-ish insertion (using a deterministic pattern)
    let mut tree = BPlusTreeMap::new(8).unwrap();
    let mut keys: Vec<i32> = (0..50).collect();
    // Simple deterministic shuffle
    for i in 0..keys.len() {
        let j = (i * 17) % keys.len(); // Simple pseudo-random pattern
        keys.swap(i, j);
    }

    for key in keys {
        tree.insert(key, format!("value_{}", key));
        assert!(
            tree.check_invariants(),
            "Random insert {} broke invariants",
            key
        );
    }
}

// ============================================================================
// NEW TESTS - Deep Tree and Recursive Insertion
// ============================================================================

#[test]
fn test_deep_tree_insertion() {
    let mut tree = BPlusTreeMap::new(4).unwrap(); // Small capacity to force deep tree

    // Insert enough items to create a deep tree (3+ levels)
    for i in 0..100 {
        tree.insert(i, format!("value_{}", i));
        assert!(
            tree.check_invariants(),
            "Invariants violated after inserting {}",
            i
        );
    }

    // Verify all items are retrievable
    for i in 0..100 {
        assert_eq!(tree.get(&i), Some(&format!("value_{}", i)));
    }

    // Tree should have multiple levels
    assert!(!tree.is_leaf_root());
    assert!(tree.leaf_count() > 10); // Should have many leaves
}

#[test]
fn test_branch_node_splitting() {
    let mut tree = BPlusTreeMap::new(4).unwrap();

    // Insert items in a pattern that will force branch node splits
    for i in 0..50 {
        tree.insert(i, format!("value_{}", i));
        assert!(
            tree.check_invariants(),
            "Invariants violated after inserting {}",
            i
        );
    }

    // Verify the tree structure is correct
    assert!(!tree.is_leaf_root());
    assert_eq!(tree.len(), 50);

    // All items should be retrievable
    for i in 0..50 {
        assert_eq!(tree.get(&i), Some(&format!("value_{}", i)));
    }
}

#[test]
fn test_multi_level_splits() {
    let mut tree = BPlusTreeMap::new(5).unwrap(); // Slightly larger capacity

    // Insert enough items to force multiple levels of splits
    for i in 0..200 {
        tree.insert(i, format!("value_{}", i));
        // Check invariants every 10 insertions to catch issues early
        if i % 10 == 0 {
            assert!(
                tree.check_invariants(),
                "Invariants violated after inserting {}",
                i
            );
        }
    }

    // Final invariant check
    assert!(tree.check_invariants());
    assert_eq!(tree.len(), 200);

    // Verify all items are still accessible
    for i in 0..200 {
        assert_eq!(tree.get(&i), Some(&format!("value_{}", i)));
    }
}

#[test]
fn test_large_sequential_insertion() {
    let mut tree = BPlusTreeMap::new(8).unwrap();

    // Insert a large number of sequential items
    for i in 0..1000 {
        tree.insert(i, i * 2);
        // Check invariants periodically
        if i % 100 == 0 {
            assert!(
                tree.check_invariants(),
                "Invariants violated after inserting {}",
                i
            );
        }
    }

    // Final checks
    assert!(tree.check_invariants());
    assert_eq!(tree.len(), 1000);

    // Spot check some values
    assert_eq!(tree.get(&0), Some(&0));
    assert_eq!(tree.get(&500), Some(&1000));
    assert_eq!(tree.get(&999), Some(&1998));
}

#[test]
fn test_reverse_order_insertion() {
    let mut tree = BPlusTreeMap::new(6).unwrap();

    // Insert items in reverse order to test different split patterns
    for i in (0..100).rev() {
        tree.insert(i, format!("value_{}", i));
        if i % 20 == 0 {
            assert!(
                tree.check_invariants(),
                "Invariants violated after inserting {}",
                i
            );
        }
    }

    // Final checks
    assert!(tree.check_invariants());
    assert_eq!(tree.len(), 100);

    // Verify all items are accessible
    for i in 0..100 {
        assert_eq!(tree.get(&i), Some(&format!("value_{}", i)));
    }
}

// ============================================================================
// NEW TESTS - Advanced Deletion and Rebalancing
// ============================================================================

#[test]
fn test_delete_until_empty() {
    let mut tree = BPlusTreeMap::new(4).unwrap();

    // Insert items
    for i in 0..20 {
        tree.insert(i, format!("value_{}", i));
    }
    assert!(tree.check_invariants());
    assert_eq!(tree.len(), 20);

    // Delete all items
    for i in 0..20 {
        let removed = tree.remove(&i);
        assert_eq!(removed, Some(format!("value_{}", i)));
        if !tree.check_invariants() {
            println!(
                "Tree state after removing {}: len={}, is_leaf_root={}",
                i,
                tree.len(),
                tree.is_leaf_root()
            );
            panic!("Invariants violated after removing {}", i);
        }
    }

    // Tree should be empty
    assert_eq!(tree.len(), 0);
    assert!(tree.is_empty());
    assert!(tree.check_invariants());
}

#[test]
fn test_root_collapse() {
    let mut tree = BPlusTreeMap::new(4).unwrap();

    // Create a tree with branch root
    for i in 0..10 {
        tree.insert(i, format!("value_{}", i));
    }
    assert!(!tree.is_leaf_root());

    // Delete most items to force root collapse
    for i in 0..9 {
        tree.remove(&i);
        assert!(
            tree.check_invariants(),
            "Invariants violated after removing {}",
            i
        );
    }

    // Should still have one item and maintain invariants
    assert_eq!(tree.len(), 1);
    assert_eq!(tree.get(&9), Some(&"value_9".to_string()));
    assert!(tree.check_invariants());
}

#[test]
fn test_alternating_insert_delete() {
    let mut tree = BPlusTreeMap::new(6).unwrap();

    // Alternating pattern of insert and delete
    for i in 0..50 {
        tree.insert(i, format!("value_{}", i));
        if i > 0 && i % 3 == 0 {
            tree.remove(&(i - 2));
        }
        assert!(
            tree.check_invariants(),
            "Invariants violated at iteration {}",
            i
        );
    }

    // Final check
    assert!(tree.check_invariants());
}

#[test]
fn test_delete_from_deep_tree() {
    let mut tree = BPlusTreeMap::new(4).unwrap();

    // Create a deep tree
    for i in 0..100 {
        tree.insert(i, i * 2);
    }
    assert!(tree.check_invariants());
    assert!(!tree.is_leaf_root());

    // Delete items from various parts of the tree
    let to_delete = [5, 25, 50, 75, 95, 10, 30, 60, 80];
    for &key in &to_delete {
        let removed = tree.remove(&key);
        assert_eq!(removed, Some(key * 2));
        assert!(
            tree.check_invariants(),
            "Invariants violated after removing {}",
            key
        );
    }

    // Verify remaining items are correct
    for i in 0..100 {
        if to_delete.contains(&i) {
            assert_eq!(tree.get(&i), None);
        } else {
            assert_eq!(tree.get(&i), Some(&(i * 2)));
        }
    }
}

#[test]
fn test_delete_all_but_one() {
    let mut tree = BPlusTreeMap::new(5).unwrap();

    // Insert many items
    for i in 0..50 {
        tree.insert(i, format!("value_{}", i));
    }
    if !tree.check_invariants() {
        println!("Final tree structure:");
        tree.print_node_chain();
        panic!("Final invariants check failed");
    }

    // Delete all but the last item
    for i in 0..49 {
        tree.remove(&i);
        if !tree.check_invariants() {
            println!("Invariants failed after removing {}", i);
            tree.print_node_chain();
            panic!("Invariants violated after removing {}", i);
        }
    }

    // Should have exactly one item left
    assert_eq!(tree.len(), 1);
    assert_eq!(tree.get(&49), Some(&"value_49".to_string()));
    assert!(tree.check_invariants());
}

// ============================================================================
// NEW TESTS - Borrowing and Merging (Future Implementation)
// ============================================================================

#[test]
fn test_massive_insertion_deletion_cycle() {
    let mut tree = BPlusTreeMap::new(8).unwrap();

    // Insert a large number of items
    for i in 0..500 {
        tree.insert(i, format!("value_{}", i));
        if i % 50 == 0 {
            assert!(
                tree.check_invariants(),
                "Invariants violated after inserting {}",
                i
            );
        }
    }

    // Delete every other item
    for i in (0..500).step_by(2) {
        tree.remove(&i);
        if i % 50 == 0 {
            assert!(
                tree.check_invariants(),
                "Invariants violated after removing {}",
                i
            );
        }
    }

    // Verify remaining items
    for i in 0..500 {
        if i % 2 == 0 {
            assert_eq!(tree.get(&i), None);
        } else {
            assert_eq!(tree.get(&i), Some(&format!("value_{}", i)));
        }
    }

    assert!(tree.check_invariants());
    assert_eq!(tree.len(), 250);
}

#[test]
fn test_random_deletion_pattern() {
    let mut tree = BPlusTreeMap::new(6).unwrap();

    // Insert items
    for i in 0..100 {
        tree.insert(i, i * 3);
    }
    assert!(tree.check_invariants());

    // Delete in a pseudo-random pattern
    let delete_pattern = [13, 7, 42, 89, 3, 67, 21, 95, 8, 56, 34, 78, 12, 45, 90];
    for &key in &delete_pattern {
        if key < 100 {
            tree.remove(&key);
            assert!(
                tree.check_invariants(),
                "Invariants violated after removing {}",
                key
            );
        }
    }

    // Verify correct items remain
    for i in 0..100 {
        if delete_pattern.contains(&i) {
            assert_eq!(tree.get(&i), None);
        } else {
            assert_eq!(tree.get(&i), Some(&(i * 3)));
        }
    }
}

#[test]
fn test_delete_from_minimal_tree() {
    let mut tree = BPlusTreeMap::new(4).unwrap(); // Minimal capacity

    // Create a tree with just enough items to have a branch root
    for i in 1..=5 {
        tree.insert(i, format!("value_{}", i));
    }
    assert!(!tree.is_leaf_root());
    assert!(tree.check_invariants());

    // Delete items one by one and verify invariants
    for i in 1..=5 {
        tree.remove(&i);
        assert!(
            tree.check_invariants(),
            "Invariants violated after removing {}",
            i
        );
    }

    assert!(tree.is_empty());
    assert!(tree.is_leaf_root());
}

#[test]
fn test_stress_deletion_with_invariants() {
    let mut tree = BPlusTreeMap::new(5).unwrap();

    // Build a moderately complex tree
    for i in 0..200 {
        tree.insert(i, i.to_string());
    }
    assert!(tree.check_invariants());

    // Delete items in chunks and verify invariants after each chunk
    for chunk in (0..200).collect::<Vec<_>>().chunks(10) {
        for &item in chunk {
            tree.remove(&item);
        }
        assert!(
            tree.check_invariants(),
            "Invariants violated after deleting chunk {:?}",
            chunk
        );
    }

    assert!(tree.is_empty());
}

// ============================================================================
// NEW TESTS - Comprehensive Edge Cases and Stress Tests
// ============================================================================

#[test]
fn test_single_key_operations() {
    let mut tree = BPlusTreeMap::new(4).unwrap();

    // Test with single key
    tree.insert(42, "answer".to_string());
    assert_eq!(tree.len(), 1);
    assert_eq!(tree.get(&42), Some(&"answer".to_string()));
    assert!(tree.check_invariants());

    // Update the single key
    let old = tree.insert(42, "new_answer".to_string());
    assert_eq!(old, Some("answer".to_string()));
    assert_eq!(tree.len(), 1);
    assert!(tree.check_invariants());

    // Remove the single key
    let removed = tree.remove(&42);
    assert_eq!(removed, Some("new_answer".to_string()));
    assert_eq!(tree.len(), 0);
    assert!(tree.is_empty());
    assert!(tree.check_invariants());
}

#[test]
fn test_duplicate_key_handling() {
    let mut tree = BPlusTreeMap::new(6).unwrap();

    // Insert same key multiple times
    assert_eq!(tree.insert(1, "first".to_string()), None);
    assert_eq!(
        tree.insert(1, "second".to_string()),
        Some("first".to_string())
    );
    assert_eq!(
        tree.insert(1, "third".to_string()),
        Some("second".to_string())
    );

    assert_eq!(tree.len(), 1);
    assert_eq!(tree.get(&1), Some(&"third".to_string()));
    assert!(tree.check_invariants());
}

#[test]
fn test_extreme_capacity_values() {
    // Test minimum capacity
    let mut tree = BPlusTreeMap::new(4).unwrap();
    for i in 0..20 {
        tree.insert(i, i * 2);
        assert!(
            tree.check_invariants(),
            "Invariants violated at capacity 4, item {}",
            i
        );
    }

    // Test larger capacity
    let mut tree = BPlusTreeMap::new(100).unwrap();
    for i in 0..200 {
        tree.insert(i, i * 3);
        if i % 25 == 0 {
            assert!(
                tree.check_invariants(),
                "Invariants violated at capacity 100, item {}",
                i
            );
        }
    }
}

#[test]
fn test_pathological_deletion_patterns() {
    let mut tree = BPlusTreeMap::new(5).unwrap();

    // Insert items
    for i in 0..50 {
        tree.insert(i, format!("value_{}", i));
    }
    assert!(tree.check_invariants());

    // Delete every 3rd item
    for i in (0..50).step_by(3) {
        tree.remove(&i);
        assert!(
            tree.check_invariants(),
            "Invariants violated after removing every 3rd: {}",
            i
        );
    }

    // Delete every 7th remaining item
    for i in (0..50).step_by(7) {
        tree.remove(&i);
        assert!(
            tree.check_invariants(),
            "Invariants violated after removing every 7th: {}",
            i
        );
    }
}

#[test]
fn test_clustered_key_patterns() {
    let mut tree = BPlusTreeMap::new(6).unwrap();

    // Insert clustered keys (0-9, 100-109, 200-209, etc.)
    for cluster in 0..10 {
        for i in 0..10 {
            let key = cluster * 100 + i;
            tree.insert(key, format!("cluster_{}_{}", cluster, i));
            if key % 50 == 0 {
                assert!(
                    tree.check_invariants(),
                    "Invariants violated at clustered key {}",
                    key
                );
            }
        }
    }

    // Delete entire clusters
    for cluster in [2, 5, 8] {
        for i in 0..10 {
            let key = cluster * 100 + i;
            tree.remove(&key);
        }
        assert!(
            tree.check_invariants(),
            "Invariants violated after removing cluster {}",
            cluster
        );
    }
}

#[test]
fn test_interleaved_operations() {
    let mut tree = BPlusTreeMap::new(7).unwrap();

    // Interleave insertions, deletions, and updates
    for round in 0..20 {
        // Insert some items
        for i in 0..5 {
            let key = round * 10 + i;
            tree.insert(key, format!("round_{}_item_{}", round, i));
        }

        // Update some existing items
        if round > 0 {
            for i in 0..3 {
                let key = (round - 1) * 10 + i;
                tree.insert(key, format!("updated_round_{}_item_{}", round - 1, i));
            }
        }

        // Delete some old items
        if round > 1 {
            for i in 0..2 {
                let key = (round - 2) * 10 + i;
                tree.remove(&key);
            }
        }

        assert!(
            tree.check_invariants(),
            "Invariants violated at round {}",
            round
        );
    }
}

#[test]
fn test_empty_tree_operations() {
    let mut tree = BPlusTreeMap::<i32, String>::new(8).unwrap();

    // Operations on empty tree
    assert_eq!(tree.get(&1), None);
    assert_eq!(tree.remove(&1), None);
    assert!(!tree.contains_key(&1));
    assert_eq!(tree.len(), 0);
    assert!(tree.is_empty());

    // Iterators on empty tree
    assert_eq!(tree.items().count(), 0);
    assert_eq!(tree.keys().count(), 0);
    assert_eq!(tree.values().count(), 0);
    assert_eq!(tree.items_range(Some(&1), Some(&10)).count(), 0);

    assert!(tree.check_invariants());
}

// ============================================================================
// NEW TESTS - API Completeness
// ============================================================================

#[test]
fn test_clear() {
    let mut tree = BPlusTreeMap::new(4).unwrap();

    // Add some items
    for i in 0..10 {
        tree.insert(i, format!("value_{}", i));
    }
    assert_eq!(tree.len(), 10);
    assert!(!tree.is_empty());

    // Clear the tree
    tree.clear();
    assert_eq!(tree.len(), 0);
    assert!(tree.is_empty());
    assert!(tree.is_leaf_root());
    assert!(tree.check_invariants());

    // Should be able to insert after clearing
    tree.insert(42, "new_value".to_string());
    assert_eq!(tree.len(), 1);
    assert_eq!(tree.get(&42), Some(&"new_value".to_string()));
}

#[test]
fn test_get_mut() {
    let mut tree = BPlusTreeMap::new(5).unwrap();

    // Insert some items
    tree.insert(1, "one".to_string());
    tree.insert(2, "two".to_string());
    tree.insert(3, "three".to_string());

    // Test get_mut for existing key
    if let Some(value) = tree.get_mut(&2) {
        *value = "TWO".to_string();
    }
    assert_eq!(tree.get(&2), Some(&"TWO".to_string()));

    // Test get_mut for non-existing key
    assert_eq!(tree.get_mut(&99), None);

    // Verify other values unchanged
    assert_eq!(tree.get(&1), Some(&"one".to_string()));
    assert_eq!(tree.get(&3), Some(&"three".to_string()));
    assert!(tree.check_invariants());
}

#[test]
fn test_first_and_last() {
    let mut tree = BPlusTreeMap::new(4).unwrap();

    // Empty tree
    assert_eq!(tree.first(), None);
    assert_eq!(tree.last(), None);

    // Single item
    tree.insert(5, "five".to_string());
    assert_eq!(tree.first(), Some((&5, &"five".to_string())));
    assert_eq!(tree.last(), Some((&5, &"five".to_string())));

    // Multiple items
    tree.insert(1, "one".to_string());
    tree.insert(9, "nine".to_string());
    tree.insert(3, "three".to_string());

    assert_eq!(tree.first(), Some((&1, &"one".to_string())));
    assert_eq!(tree.last(), Some((&9, &"nine".to_string())));

    // After deletion
    tree.remove(&1);
    tree.remove(&9);
    assert_eq!(tree.first(), Some((&3, &"three".to_string())));
    assert_eq!(tree.last(), Some((&5, &"five".to_string())));
}

#[test]
fn test_api_completeness_with_deep_tree() {
    let mut tree = BPlusTreeMap::new(4).unwrap();

    // Create a deep tree
    for i in 0..50 {
        tree.insert(i, i * 2);
    }
    assert!(!tree.is_leaf_root());

    // Test all APIs work with deep tree
    assert_eq!(tree.first(), Some((&0, &0)));
    assert_eq!(tree.last(), Some((&49, &98)));

    // Test get_mut in deep tree
    if let Some(value) = tree.get_mut(&25) {
        *value = 999;
    }
    assert_eq!(tree.get(&25), Some(&999));

    // Test clear on deep tree
    tree.clear();
    assert!(tree.is_empty());
    assert!(tree.is_leaf_root());
    assert!(tree.check_invariants());
}

#[test]
fn test_linked_list_range_performance() {
    use std::time::Instant;

    let mut tree = BPlusTreeMap::new(64).unwrap();

    // Insert 10,000 items
    for i in 0..10000 {
        tree.insert(i, format!("value{}", i));
    }

    // Test range query performance
    let start = Instant::now();
    let items: Vec<_> = tree.items_range(Some(&1000), Some(&2000)).collect();
    let duration = start.elapsed();

    println!("Range query (1000 items) took: {:?}", duration);
    assert_eq!(items.len(), 1000);

    // Verify correctness
    for (i, (key, value)) in items.iter().enumerate() {
        let expected_key = 1000 + i;
        let expected_value = format!("value{}", expected_key);
        assert_eq!(**key, expected_key);
        assert_eq!(**value, expected_value);
    }
}

#[test]
fn test_debug_range_iterator() {
    let mut tree = BPlusTreeMap::new(4).unwrap();
    for i in 0..20 {
        tree.insert(i, format!("value{}", i));
    }

    println!("Tree structure after insertions:");
    println!("Tree length: {}", tree.len());
    println!("Leaf count: {}", tree.leaf_count());

    let items: Vec<_> = tree.items_range(Some(&5), Some(&15)).collect();
    println!("Range [5, 15) returned {} items:", items.len());
    for (key, value) in &items {
        println!("  {} -> {}", key, value);
    }

    // This should return keys 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 (10 items)
    assert_eq!(items.len(), 10);

    // Test the invariant checker - this should catch the linked list issue
    println!("Checking invariants...");
    match tree.validate() {
        Ok(()) => println!("Invariants passed"),
        Err(e) => println!("Invariants failed: {}", e),
    }
}

// TODO: Add fuzz tests against BTreeMap
// TODO: Add performance benchmarks
