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
