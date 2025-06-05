use bplustree3::BPlusTreeMap;

#[test]
fn test_with_helpers_branch_leaf() {
    let mut tree = BPlusTreeMap::<i32, i32>::new(5).unwrap();
    // Leaf at id=0 exists and is initially empty
    assert_eq!(tree.with_leaf(0, |leaf| leaf.keys().len()), Some(0));
    assert_eq!(tree.with_leaf_mut(0, |leaf| leaf.keys().len()), Some(0));
    // No branch at id=0, closures should not execute
    assert_eq!(tree.with_branch(0, |_| panic!("should not run")), None);
    assert_eq!(tree.with_branch_mut(0, |_| panic!("should not run")), None);
}

#[test]
fn test_find_child_helpers() {
    let mut tree = BPlusTreeMap::<i32, i32>::new(4).unwrap();
    // No branch at id=0, should return None
    assert!(tree.find_child(0, &0).is_none());
    assert!(tree.find_child_mut(0, &0).is_none());
}