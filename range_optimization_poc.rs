// Proof of Concept: Optimized Range Query Implementation
// This demonstrates the key concepts from the optimization plan

use std::collections::BTreeMap;

// Simplified B+ Tree structures for demonstration
type NodeId = usize;
const NULL_NODE: NodeId = usize::MAX;

#[derive(Debug)]
struct LeafNode<K, V> {
    keys: Vec<K>,
    values: Vec<V>,
    next: NodeId,
}

#[derive(Debug)]
struct BranchNode<K> {
    keys: Vec<K>,
    children: Vec<NodeId>,
}

// Core optimization: ItemIterator that can start from any position
#[derive(Debug)]
pub struct ItemIterator<'a, K, V> {
    tree: &'a SimpleBPlusTree<K, V>,
    current_leaf_id: Option<NodeId>,
    current_leaf_index: usize,
}

impl<'a, K: Ord + Clone, V: Clone> ItemIterator<'a, K, V> {
    // Existing constructor (starts from beginning)
    fn new(tree: &'a SimpleBPlusTree<K, V>) -> Self {
        Self {
            tree,
            current_leaf_id: tree.first_leaf_id(),
            current_leaf_index: 0,
        }
    }
    
    // NEW: Start from specific leaf and index - this is the key innovation!
    fn new_from_position(
        tree: &'a SimpleBPlusTree<K, V>,
        start_leaf_id: NodeId,
        start_index: usize
    ) -> Self {
        Self {
            tree,
            current_leaf_id: Some(start_leaf_id),
            current_leaf_index: start_index,
        }
    }
}

impl<'a, K: Ord + Clone, V: Clone> Iterator for ItemIterator<'a, K, V> {
    type Item = (&'a K, &'a V);

    fn next(&mut self) -> Option<Self::Item> {
        while let Some(leaf_id) = self.current_leaf_id {
            if let Some(leaf) = self.tree.get_leaf(leaf_id) {
                // Check if we have more items in the current leaf
                if self.current_leaf_index < leaf.keys.len() {
                    let key = &leaf.keys[self.current_leaf_index];
                    let value = &leaf.values[self.current_leaf_index];
                    self.current_leaf_index += 1;
                    return Some((key, value));
                } else {
                    // Move to next leaf - this is where the magic happens!
                    self.current_leaf_id = if leaf.next != NULL_NODE {
                        Some(leaf.next)
                    } else {
                        None
                    };
                    self.current_leaf_index = 0;
                    // Continue loop to try next leaf
                }
            } else {
                // Invalid leaf ID
                return None;
            }
        }
        None
    }
}

// Bounds-aware iterator wrapper
#[derive(Debug)]
pub struct BoundedItemIterator<'a, K, V> {
    inner: ItemIterator<'a, K, V>,
    end_key: Option<&'a K>,
    finished: bool,
}

impl<'a, K: Ord + Clone, V: Clone> BoundedItemIterator<'a, K, V> {
    fn new(
        tree: &'a SimpleBPlusTree<K, V>,
        start_leaf_id: NodeId,
        start_index: usize,
        end_key: Option<&'a K>
    ) -> Self {
        Self {
            inner: ItemIterator::new_from_position(tree, start_leaf_id, start_index),
            end_key,
            finished: false,
        }
    }
}

impl<'a, K: Ord + Clone, V: Clone> Iterator for BoundedItemIterator<'a, K, V> {
    type Item = (&'a K, &'a V);

    fn next(&mut self) -> Option<Self::Item> {
        if self.finished {
            return None;
        }

        if let Some((key, value)) = self.inner.next() {
            // Check if we've reached the end bound
            if let Some(end) = self.end_key {
                if key >= end {
                    self.finished = true;
                    return None;
                }
            }
            Some((key, value))
        } else {
            self.finished = true;
            None
        }
    }
}

// Optimized range iterator - the final product
#[derive(Debug)]
pub struct OptimizedRangeIterator<'a, K, V> {
    iterator: Option<BoundedItemIterator<'a, K, V>>,
}

impl<'a, K: Ord + Clone, V: Clone> OptimizedRangeIterator<'a, K, V> {
    fn new(
        tree: &'a SimpleBPlusTree<K, V>, 
        start_key: Option<&K>, 
        end_key: Option<&'a K>
    ) -> Self {
        let iterator = if let Some(start) = start_key {
            // Find the starting position using tree navigation
            if let Some((leaf_id, index)) = tree.find_range_start(start) {
                Some(BoundedItemIterator::new(tree, leaf_id, index, end_key))
            } else {
                None // No items in range
            }
        } else {
            // Start from beginning
            if let Some(first_leaf) = tree.first_leaf_id() {
                Some(BoundedItemIterator::new(tree, first_leaf, 0, end_key))
            } else {
                None // Empty tree
            }
        };

        Self { iterator }
    }
}

impl<'a, K: Ord + Clone, V: Clone> Iterator for OptimizedRangeIterator<'a, K, V> {
    type Item = (&'a K, &'a V);

    fn next(&mut self) -> Option<Self::Item> {
        self.iterator.as_mut()?.next()
    }
}

// Simplified B+ Tree for demonstration
#[derive(Debug)]
pub struct SimpleBPlusTree<K, V> {
    leaves: Vec<LeafNode<K, V>>,
    first_leaf: Option<NodeId>,
}

impl<K: Ord + Clone, V: Clone> SimpleBPlusTree<K, V> {
    fn new() -> Self {
        Self {
            leaves: Vec::new(),
            first_leaf: None,
        }
    }

    fn get_leaf(&self, id: NodeId) -> Option<&LeafNode<K, V>> {
        self.leaves.get(id)
    }

    fn first_leaf_id(&self) -> Option<NodeId> {
        self.first_leaf
    }

    // Key method: Find where a range should start
    fn find_range_start(&self, start_key: &K) -> Option<(NodeId, usize)> {
        // Simplified: just search through leaves (in real implementation, use tree navigation)
        let mut current_id = self.first_leaf?;
        
        loop {
            if let Some(leaf) = self.get_leaf(current_id) {
                // Find the first key >= start_key in this leaf
                if let Some(index) = leaf.keys.iter().position(|k| k >= start_key) {
                    return Some((current_id, index));
                }
                
                // All keys in this leaf are < start_key, try next leaf
                if leaf.next != NULL_NODE {
                    current_id = leaf.next;
                } else {
                    return None; // No valid start position
                }
            } else {
                return None;
            }
        }
    }

    // Public API
    pub fn range<'a>(
        &'a self,
        start_key: Option<&K>,
        end_key: Option<&'a K>,
    ) -> OptimizedRangeIterator<'a, K, V> {
        OptimizedRangeIterator::new(self, start_key, end_key)
    }

    pub fn items(&self) -> ItemIterator<K, V> {
        ItemIterator::new(self)
    }
}

// Performance comparison demonstration
#[cfg(test)]
mod tests {
    use super::*;
    use std::time::Instant;

    #[test]
    fn demonstrate_optimization_concept() {
        // This test shows the conceptual difference between approaches
        
        println!("=== Range Query Optimization Demonstration ===\n");
        
        // Simulate current approach: collect all items first
        fn current_approach_simulation<K: Ord + Clone, V: Clone>(
            tree: &SimpleBPlusTree<K, V>,
            start: Option<&K>,
            end: Option<&K>
        ) -> Vec<(K, V)> {
            println!("Current Approach:");
            println!("1. Traverse entire tree structure");
            println!("2. Collect all items in range into Vec");
            println!("3. Return iterator over Vec");
            
            // Simulate the overhead
            let mut items = Vec::new();
            for (k, v) in tree.items() {
                let include = start.map_or(true, |s| k >= s) && 
                             end.map_or(true, |e| k < e);
                if include {
                    items.push((k.clone(), v.clone()));
                }
            }
            items
        }
        
        // Simulate optimized approach: navigate then iterate
        fn optimized_approach_simulation<K: Ord + Clone, V: Clone>(
            tree: &SimpleBPlusTree<K, V>,
            start: Option<&K>,
            end: Option<&K>
        ) -> Vec<(K, V)> {
            println!("\nOptimized Approach:");
            println!("1. Navigate tree to find start position O(log n)");
            println!("2. Follow leaf next pointers O(k) where k = range size");
            println!("3. Lazy evaluation - no upfront collection");
            
            tree.range(start, end)
                .map(|(k, v)| (k.clone(), v.clone()))
                .collect()
        }
        
        // The key insight: we transform O(n) tree traversal into O(log n + k)
        println!("\nKey Performance Insight:");
        println!("Current:   O(n) tree traversal + O(k) collection");
        println!("Optimized: O(log n) navigation + O(k) linked list traversal");
        println!("Where n = total items, k = items in range");
        println!("\nFor small ranges (k << n), this is a massive improvement!");
    }

    #[test]
    fn test_iterator_starting_positions() {
        // This demonstrates the core innovation: starting iteration from any position
        
        let mut tree = SimpleBPlusTree::new();
        
        // Add some test data (simplified setup)
        tree.leaves.push(LeafNode {
            keys: vec![1, 3, 5],
            values: vec!["one", "three", "five"],
            next: 1,
        });
        tree.leaves.push(LeafNode {
            keys: vec![7, 9, 11],
            values: vec!["seven", "nine", "eleven"],
            next: NULL_NODE,
        });
        tree.first_leaf = Some(0);
        
        // Test 1: Start from beginning (traditional)
        let full_iter = ItemIterator::new(&tree);
        let full_items: Vec<_> = full_iter.collect();
        assert_eq!(full_items.len(), 6);
        
        // Test 2: Start from middle of first leaf (NEW CAPABILITY!)
        let mid_iter = ItemIterator::new_from_position(&tree, 0, 1);
        let mid_items: Vec<_> = mid_iter.collect();
        assert_eq!(mid_items.len(), 5); // Should skip first item
        assert_eq!(mid_items[0], (&3, &"three"));
        
        // Test 3: Start from second leaf (NEW CAPABILITY!)
        let second_leaf_iter = ItemIterator::new_from_position(&tree, 1, 0);
        let second_items: Vec<_> = second_leaf_iter.collect();
        assert_eq!(second_items.len(), 3);
        assert_eq!(second_items[0], (&7, &"seven"));
        
        println!("✅ Iterator can now start from any position!");
        println!("   This enables efficient range queries without tree traversal.");
    }
}

// Usage example showing the API
fn example_usage() {
    let tree = SimpleBPlusTree::<i32, String>::new();
    
    // Optimized range query - uses tree navigation + linked list traversal
    let range_items: Vec<_> = tree.range(Some(&5), Some(&15)).collect();
    
    // Full iteration - uses linked list traversal from beginning  
    let all_items: Vec<_> = tree.items().collect();
    
    println!("Range query found {} items", range_items.len());
    println!("Full iteration found {} items", all_items.len());
}
