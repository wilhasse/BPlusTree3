use bplustree3::BPlusTree;

#[test]
fn all_keys_exist_after_multiple_inserts_with_split() {
    let mut tree: BPlusTree<i32, i32> = BPlusTree::new(4);
    
    // Insert 5 keys (more than branching factor)
    let keys = [15, 7, 42, 23, 31];
    let values = [150, 70, 420, 230, 310];
    
    // Insert all keys
    for i in 0..keys.len() {
        tree.insert(keys[i], values[i]);
    }
    
    // Verify all keys exist and return the correct values
    for i in 0..keys.len() {
        let value = tree.get(&keys[i]);
        assert_eq!(value, Some(&values[i]), "Key {} should have value {}", keys[i], values[i]);
    }
    
    // Verify total element count
    assert_eq!(tree.len(), 5);
    
    // Verify node structure (should be split into two nodes)
    assert_eq!(tree.leaf_count(), 2);
}

#[test]
fn adding_more_than_branching_factor_keys_causes_split() {
    let mut tree: BPlusTree<i32, i32> = BPlusTree::new(4);
    
    // Insert up to branching factor
    tree.insert(10, 100);
    tree.insert(20, 200);
    tree.insert(30, 300);
    tree.insert(40, 400);
    
    // At this point we should have one leaf node with 4 entries
    assert_eq!(tree.leaf_count(), 1);
    assert_eq!(tree.leaf_sizes(), vec![4]);
    
    // This fifth insert should trigger a split
    tree.insert(50, 500);
    
    // We should now have two leaf nodes
    assert_eq!(tree.leaf_count(), 2);
    
    // Nodes should be split approximately evenly
    let sizes = tree.leaf_sizes();
    assert_eq!(sizes.len(), 2);
    
    // Verify that the split is reasonable (within 1 element of each other)
    assert!(sizes[0] >= 2 && sizes[0] <= 3);
    assert!(sizes[1] >= 2 && sizes[1] <= 3);
    assert_eq!(sizes[0] + sizes[1], 5);
    
    // All keys should be retrievable
    assert_eq!(tree.get(&10), Some(&100));
    assert_eq!(tree.get(&20), Some(&200));
    assert_eq!(tree.get(&30), Some(&300));
    assert_eq!(tree.get(&40), Some(&400));
    assert_eq!(tree.get(&50), Some(&500));
}

#[test]
fn create_empty_tree() {
    let _tree: BPlusTree<i32, i32> = BPlusTree::new(4);
}

#[test]
fn empty_tree_has_len_zero() {
    let tree: BPlusTree<i32, i32> = BPlusTree::new(4);
    assert_eq!(tree.len(), 0);
    assert!(tree.is_empty());
}

#[test]
fn create_tree_with_branching_factor() {
    let tree: BPlusTree<i32, i32> = BPlusTree::new(16);
    assert_eq!(tree.branching_factor(), 16);
}

#[test]
fn insert_increases_length() {
    let mut tree: BPlusTree<i32, i32> = BPlusTree::new(4);
    assert_eq!(tree.len(), 0);
    
    tree.insert(42, 100);
    assert_eq!(tree.len(), 1);
}

#[test]
fn get_returns_value_when_key_exists() {
    let mut tree: BPlusTree<i32, i32> = BPlusTree::new(4);
    
    tree.insert(42, 100);
    
    let value = tree.get(&42);
    assert_eq!(value, Some(&100));
}

#[test]
fn get_returns_none_when_key_missing() {
    let mut tree: BPlusTree<i32, i32> = BPlusTree::new(4);
    
    tree.insert(42, 100);
    
    let missing = tree.get(&50);
    assert_eq!(missing, None);
}

#[test]
fn inserting_multiple_items_works() {
    let mut tree: BPlusTree<i32, i32> = BPlusTree::new(4);
    
    tree.insert(10, 100);
    tree.insert(20, 200);
    tree.insert(30, 300);
    
    assert_eq!(tree.len(), 3);
    assert_eq!(tree.get(&10), Some(&100));
    assert_eq!(tree.get(&20), Some(&200));
    assert_eq!(tree.get(&30), Some(&300));
}

#[test]
fn insert_maintains_sorted_order() {
    let mut tree: BPlusTree<i32, i32> = BPlusTree::new(4);
    
    // Insert in non-sorted order
    tree.insert(30, 300);
    tree.insert(10, 100);
    tree.insert(20, 200);
    
    // Verify retrieval works for all keys
    assert_eq!(tree.len(), 3);
    assert_eq!(tree.get(&10), Some(&100));
    assert_eq!(tree.get(&20), Some(&200));
    assert_eq!(tree.get(&30), Some(&300));
}

#[test]
fn insert_at_beginning() {
    let mut tree: BPlusTree<i32, i32> = BPlusTree::new(5);
    
    // Insert some values first
    tree.insert(20, 200);
    tree.insert(30, 300);
    tree.insert(40, 400);
    
    // Now insert at beginning
    tree.insert(10, 100);
    
    // Verify correct order and values
    let entries = tree.slice();
    assert_eq!(entries.len(), 4);
    assert_eq!(entries[0], (&10, &100));  // New first entry
    assert_eq!(entries[1], (&20, &200));
    assert_eq!(entries[2], (&30, &300));
    assert_eq!(entries[3], (&40, &400));
}

#[test]
fn insert_in_middle() {
    let mut tree: BPlusTree<i32, i32> = BPlusTree::new(5);
    
    // Insert values with a gap
    tree.insert(10, 100);
    tree.insert(30, 300);
    tree.insert(40, 400);
    
    // Now insert in the middle
    tree.insert(20, 200);
    
    // Verify correct order and values
    let entries = tree.slice();
    assert_eq!(entries.len(), 4);
    assert_eq!(entries[0], (&10, &100));
    assert_eq!(entries[1], (&20, &200));  // New middle entry
    assert_eq!(entries[2], (&30, &300));
    assert_eq!(entries[3], (&40, &400));
}

#[test]
fn insert_at_end() {
    let mut tree: BPlusTree<i32, i32> = BPlusTree::new(5);
    
    // Insert some values first
    tree.insert(10, 100);
    tree.insert(20, 200);
    tree.insert(30, 300);
    
    // Now insert at end
    tree.insert(40, 400);
    
    // Verify correct order and values
    let entries = tree.slice();
    assert_eq!(entries.len(), 4);
    assert_eq!(entries[0], (&10, &100));
    assert_eq!(entries[1], (&20, &200));
    assert_eq!(entries[2], (&30, &300));
    assert_eq!(entries[3], (&40, &400));  // New last entry
}

#[test]
fn update_existing_key() {
    let mut tree: BPlusTree<i32, i32> = BPlusTree::new(5);
    
    // Insert some values
    tree.insert(10, 100);
    tree.insert(20, 200);
    tree.insert(30, 300);
    
    // Update middle value
    let old_value = tree.insert(20, 250);
    
    // Verify update was successful
    assert_eq!(old_value, Some(200));
    assert_eq!(tree.len(), 3);  // Length unchanged
    
    // Verify correct order and updated value
    let entries = tree.slice();
    assert_eq!(entries.len(), 3);
    assert_eq!(entries[0], (&10, &100));
    assert_eq!(entries[1], (&20, &250));  // Updated value
    assert_eq!(entries[2], (&30, &300));
}

#[test]
fn slice_returns_entries_in_sorted_order() {
    let mut tree: BPlusTree<i32, i32> = BPlusTree::new(5); // Increased branching factor to 5
    
    // Insert in non-sorted order
    tree.insert(30, 300);
    tree.insert(10, 100);
    tree.insert(50, 500);
    tree.insert(20, 200);
    tree.insert(40, 400);
    
    // Get all entries as a slice
    let entries = tree.slice();
    
    // Verify the entries are in sorted order by key
    assert_eq!(entries.len(), 5);
    assert_eq!(entries[0], (&10, &100));
    assert_eq!(entries[1], (&20, &200));
    assert_eq!(entries[2], (&30, &300));
    assert_eq!(entries[3], (&40, &400));
    assert_eq!(entries[4], (&50, &500));
}

#[test]
fn range_returns_entries_in_given_range() {
    let mut tree: BPlusTree<i32, i32> = BPlusTree::new(5); // Increased branching factor to 5
    
    // Insert entries
    tree.insert(10, 100);
    tree.insert(20, 200);
    tree.insert(30, 300);
    tree.insert(40, 400);
    tree.insert(50, 500);
    
    // Get entries in range [20, 40]
    let entries = tree.range(Some(&20), Some(&40));
    
    // Verify the correct range is returned in sorted order
    assert_eq!(entries.len(), 3);
    assert_eq!(entries[0], (&20, &200));
    assert_eq!(entries[1], (&30, &300));
    assert_eq!(entries[2], (&40, &400));
}

#[test]
fn multi_level_node_chain_bug() {
    // Create a tree with small branching factor to force multiple splits
    let mut tree: BPlusTree<i32, i32> = BPlusTree::new(2);
    
    // Insert keys in order
    println!("\nInserting keys in ascending order:");
    for i in 10..=80 {
        if i % 10 == 0 {
            tree.insert(i, i * 10);
            println!("After inserting {}: {} nodes, sizes: {:?}", 
                     i, tree.leaf_count(), tree.leaf_sizes());
        }
    }
    
    // Verify all keys can be found
    let mut missing_keys = Vec::new();
    for i in 10..=80 {
        if i % 10 == 0 {
            let value = tree.get(&i);
            if value != Some(&(i * 10)) {
                missing_keys.push(i);
                println!("Missing key: {}, expected value: {}", i, i * 10);
            }
        }
    }
    
    if !missing_keys.is_empty() {
        println!("\nBUG DETECTED: Keys were inserted but cannot be found!");
        println!("Missing keys: {:?}", missing_keys);
        println!("This indicates that either:");
        println!("1. The LeafFinder is not correctly traversing more than 2 nodes, or");
        println!("2. The BPlusTree.insert method is not handling node splits correctly beyond the root.");
        println!("\nCurrent node structure:");
        println!("Number of nodes: {}", tree.leaf_count());
        println!("Node sizes: {:?}", tree.leaf_sizes());
        
        // Debugging output - manually traverse nodes to see what's happening
        println!("\nManually traversing nodes:");
        tree.print_node_chain();
        
        // Here we are assuming that the keys are in order - if they aren't, our get method 
        // will fail to find them, which is what we're seeing
        assert!(missing_keys.is_empty(), "Failed to find keys: {:?}", missing_keys);
    }
}
