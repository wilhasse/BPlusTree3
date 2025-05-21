use bplustree3::BPlusTree;

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
