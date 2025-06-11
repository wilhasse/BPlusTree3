#![allow(dead_code)] // Allow unused utility functions for future tests

/// Comprehensive test utilities to eliminate massive test duplication
/// This module provides reusable patterns for adversarial testing and common operations
use bplustree::BPlusTreeMap;

/// Create a tree for adversarial testing with common setup
pub fn create_attack_tree(capacity: usize) -> BPlusTreeMap<i32, String> {
    BPlusTreeMap::new(capacity).expect("Failed to create attack tree")
}

/// Create a tree with integer keys and values for simple testing
pub fn create_simple_tree(capacity: usize) -> BPlusTreeMap<i32, i32> {
    BPlusTreeMap::new(capacity).expect("Failed to create simple tree")
}

/// Execute a stress test cycle with automatic invariant checking
pub fn stress_test_cycle<F>(tree: &mut BPlusTreeMap<i32, String>, cycles: usize, attack_fn: F)
where
    F: Fn(&mut BPlusTreeMap<i32, String>, usize),
{
    for cycle in 0..cycles {
        attack_fn(tree, cycle);

        // Unified invariant checking with context
        if let Err(e) = tree.check_invariants_detailed() {
            panic!("ATTACK SUCCESSFUL at cycle {}: {}", cycle, e);
        }
    }
}

/// Standard arena exhaustion attack pattern
pub fn arena_exhaustion_attack(tree: &mut BPlusTreeMap<i32, String>, cycle: usize) {
    let cycle_i32 = cycle as i32;

    // Fill tree to create many nodes
    for i in 0..100 {
        tree.insert(cycle_i32 * 1000 + i, format!("v{}-{}", cycle, i));
    }

    // Delete most items to free nodes
    for i in 0..95 {
        tree.remove(&(cycle_i32 * 1000 + i));
    }

    println!(
        "Cycle {}: Free leaves={}, Free branches={}",
        cycle,
        tree.free_leaf_count(),
        tree.free_branch_count()
    );
}

/// Standard fragmentation attack pattern
pub fn fragmentation_attack(tree: &mut BPlusTreeMap<i32, String>, base_key: i32) {
    // Insert in a pattern that creates and frees nodes in specific order
    for i in 0..500 {
        tree.insert(base_key + i * 10, format!("fragmented-{}", i));
    }

    // Delete every other item
    for i in (0..500).step_by(2) {
        tree.remove(&(base_key + i * 10));
    }

    // Reinsert to reuse freed slots
    for i in 0..250 {
        tree.insert(base_key + i * 10 + 5, format!("reused-{}", i * 1000));
    }
}

/// Deep tree creation attack pattern
pub fn deep_tree_attack(tree: &mut BPlusTreeMap<i32, i32>, capacity: usize) {
    let mut key = 0;
    for level in 0..5 {
        let count = capacity.pow(level as u32);
        for _ in 0..count * 10 {
            tree.insert(key, key);
            key += 100; // Large gaps to force deep structure
        }
    }
}

/// Alternating operations attack pattern
pub fn alternating_operations_attack(tree: &mut BPlusTreeMap<i32, String>, round: usize) {
    // Delete from left side
    let left_key = (round * 6) as i32;
    if tree.contains_key(&left_key) {
        tree.remove(&left_key);
    }

    // Insert in middle
    let mid_key = 30 + round as i32;
    tree.insert(mid_key * 2 + 1, format!("mid{}", round));

    // Delete from right side
    let right_key = 118 - (round * 6) as i32;
    if tree.contains_key(&right_key) {
        tree.remove(&right_key);
    }
}

/// Verify attack failed (tree is still valid)
pub fn assert_attack_failed(tree: &BPlusTreeMap<i32, String>, context: &str) {
    if let Err(e) = tree.check_invariants_detailed() {
        panic!("ATTACK SUCCESSFUL in {}: {}", context, e);
    }
}

/// Verify attack failed for integer trees
pub fn assert_attack_failed_int(tree: &BPlusTreeMap<i32, i32>, context: &str) {
    if let Err(e) = tree.check_invariants_detailed() {
        panic!("ATTACK SUCCESSFUL in {}: {}", context, e);
    }
}

/// Verify tree ordering after attack
pub fn verify_ordering(tree: &BPlusTreeMap<i32, String>) {
    let items: Vec<_> = tree.items().collect();
    for i in 1..items.len() {
        if items[i - 1].0 >= items[i].0 {
            panic!("ATTACK SUCCESSFUL: Items out of order after attack!");
        }
    }
}

/// Verify tree ordering for integer trees
pub fn verify_ordering_int(tree: &BPlusTreeMap<i32, i32>) {
    let items: Vec<_> = tree.items().collect();
    for i in 1..items.len() {
        if items[i - 1].0 >= items[i].0 {
            panic!("ATTACK SUCCESSFUL: Items out of order after attack!");
        }
    }
}

/// Populate tree with sequential data for testing
pub fn populate_sequential(tree: &mut BPlusTreeMap<i32, String>, count: usize) {
    for i in 0..count {
        tree.insert(i as i32, format!("value_{}", i));
    }
}

/// Populate tree with sequential integer data
pub fn populate_sequential_int(tree: &mut BPlusTreeMap<i32, i32>, count: usize) {
    for i in 0..count {
        tree.insert(i as i32, i as i32);
    }
}

/// Populate tree with sequential integer data where value = key * 10
pub fn populate_sequential_int_x10(tree: &mut BPlusTreeMap<i32, i32>, count: usize) {
    for i in 0..count {
        tree.insert(i as i32, (i as i32) * 10);
    }
}

/// Create a tree with specific structure for branch testing
pub fn create_branch_test_tree(capacity: usize) -> BPlusTreeMap<i32, String> {
    let mut tree = create_attack_tree(capacity);

    // Build specific tree structure where branches are at minimum
    let keys = vec![
        10, 20, 30, 40, 15, 25, 35, 45, 12, 18, 22, 28, 32, 38, 42, 48,
    ];
    for key in keys {
        tree.insert(key, format!("v{}", key));
    }

    // Delete strategically to make siblings exactly at minimum
    for key in vec![18, 28, 38, 48] {
        tree.remove(&key);
    }

    tree
}

/// Standard setup for concurrent access simulation
pub fn setup_concurrent_simulation() -> (Vec<(bool, i32)>, Vec<(bool, i32)>) {
    let thread1_ops = vec![
        (true, 1),
        (true, 3),
        (true, 5),
        (false, 3),
        (true, 7),
        (false, 1),
    ];
    let thread2_ops = vec![
        (true, 2),
        (true, 4),
        (false, 2),
        (true, 6),
        (true, 8),
        (false, 4),
    ];
    (thread1_ops, thread2_ops)
}

/// Execute interleaved operations for concurrent simulation
pub fn execute_interleaved_ops(
    tree: &mut BPlusTreeMap<i32, String>,
    thread1_ops: &[(bool, i32)],
    thread2_ops: &[(bool, i32)],
) {
    for i in 0..thread1_ops.len() {
        // Thread 1 operation
        let (is_insert, key) = thread1_ops[i];
        if is_insert {
            tree.insert(key * 10, format!("t1-{}", key));
        } else {
            tree.remove(&(key * 10));
        }

        // Check invariants after each operation
        if let Err(e) = tree.check_invariants_detailed() {
            panic!("ATTACK SUCCESSFUL after thread1 op {}: {}", i, e);
        }

        // Thread 2 operation
        let (is_insert, key) = thread2_ops[i];
        if is_insert {
            tree.insert(key * 10 + 1, format!("t2-{}", key));
        } else {
            tree.remove(&(key * 10 + 1));
        }

        // Check invariants after each operation
        if let Err(e) = tree.check_invariants_detailed() {
            panic!("ATTACK SUCCESSFUL after thread2 op {}: {}", i, e);
        }
    }
}

/// Verify tree has expected number of items
pub fn verify_item_count(tree: &BPlusTreeMap<i32, String>, expected: usize, context: &str) {
    let actual = tree.len();
    if actual != expected {
        panic!(
            "ATTACK SUCCESSFUL in {}: Expected {} items, got {}",
            context, expected, actual
        );
    }
}

/// Verify tree has expected number of items (integer version)
pub fn verify_item_count_int(tree: &BPlusTreeMap<i32, i32>, expected: usize, context: &str) {
    let actual = tree.len();
    if actual != expected {
        panic!(
            "ATTACK SUCCESSFUL in {}: Expected {} items, got {}",
            context, expected, actual
        );
    }
}

/// Print tree statistics for debugging
pub fn print_tree_stats(tree: &BPlusTreeMap<i32, String>, label: &str) {
    println!(
        "{}: {} items, Free leaves={}, Free branches={}",
        label,
        tree.len(),
        tree.free_leaf_count(),
        tree.free_branch_count()
    );
    println!("Leaf sizes: {:?}", tree.leaf_sizes());
}

/// Print tree statistics for integer trees
pub fn print_tree_stats_int(tree: &BPlusTreeMap<i32, i32>, label: &str) {
    println!(
        "{}: {} items, Free leaves={}, Free branches={}",
        label,
        tree.len(),
        tree.free_leaf_count(),
        tree.free_branch_count()
    );
    println!("Leaf sizes: {:?}", tree.leaf_sizes());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_utilities_basic_functionality() {
        let mut tree = create_attack_tree(4);
        populate_sequential(&mut tree, 10);

        assert_eq!(tree.len(), 10);
        verify_ordering(&tree);
        assert_attack_failed(&tree, "basic functionality test");
    }

    #[test]
    fn test_stress_cycle_utility() {
        let mut tree = create_attack_tree(4);

        // Test that stress_test_cycle works correctly
        stress_test_cycle(&mut tree, 5, |tree, cycle| {
            tree.insert(cycle as i32, format!("cycle_{}", cycle));
        });

        assert_eq!(tree.len(), 5);
    }
}
