//! Demonstrates the centralized tree traversal algorithm in BPlusTreeMap.
//!
//! This example shows how the tree traversal logic is now contained within
//! BPlusTreeMap methods rather than being distributed across node types.

use bplustree3::BPlusTreeMap;

fn main() {
    // Create a B+ tree with capacity 4 for easy visualization
    let mut tree = BPlusTreeMap::new(4).unwrap();
    
    // Insert some values to create a multi-level tree
    for i in 0..20 {
        tree.insert(i, format!("value_{}", i));
    }
    
    println!("B+ Tree Traversal Algorithm Demo");
    println!("================================\n");
    
    // Demonstrate get operation
    let key = 15;
    println!("Looking up key: {}", key);
    
    // The traversal algorithm is now centralized in BPlusTreeMap::get()
    // It follows these steps:
    // 1. Start at root
    // 2. If leaf, search for key
    // 3. If branch, find child index and descend
    // 4. Repeat until leaf is found
    
    match tree.get(&key) {
        Some(value) => println!("Found value: {}", value),
        None => println!("Key not found"),
    }
    
    println!("\nKey points about the centralized traversal:");
    println!("1. All traversal logic is in BPlusTreeMap methods");
    println!("2. Nodes only contain data and simple operations");
    println!("3. No recursive calls through node types");
    println!("4. Easier to understand and maintain");
    
    // The same pattern is used for all operations:
    println!("\nOther operations using the same traversal pattern:");
    
    // get_mut - mutable traversal
    if let Some(value) = tree.get_mut(&10) {
        *value = "updated_value_10".to_string();
        println!("- get_mut: Updated key 10");
    }
    
    // contains_key - uses get internally
    if tree.contains_key(&5) {
        println!("- contains_key: Key 5 exists");
    }
    
    // remove - finds leaf then removes
    if let Some(old_value) = tree.remove(&8) {
        println!("- remove: Removed key 8 with value {}", old_value);
    }
    
    println!("\nTree statistics (also using centralized traversal):");
    println!("- Total items: {}", tree.len());
    println!("- Leaf count: {}", tree.leaf_count());
    println!("- Is empty: {}", tree.is_empty());
}