//! BPlusTree library.

use std::collections::BTreeMap;

/// A key-value entry in a leaf node.
#[derive(Debug, Clone)]
struct Entry<K, V> {
    key: K,
    value: V,
}

/// A node in the B+ tree containing the actual key-value data.
#[derive(Debug)]
struct LeafNode<K, V> {
    /// Maximum number of entries this node can hold before splitting
    branching_factor: usize,
    /// Data stored in this leaf node (using BTreeMap for initial implementation)
    entries: BTreeMap<K, V>,
    /// Array of key-value entries, will be used for B+ tree implementation
    /// Entries are stored in order, with valid entries from 0..count and None for unused slots
    items: Vec<Option<Entry<K, V>>>,
    /// Number of valid entries in the items array
    count: usize,
}

impl<K: Ord + Clone, V: Clone> LeafNode<K, V> {
    /// Creates a new leaf node with the specified branching factor.
    fn new(branching_factor: usize) -> Self {
        // Initialize the items vector with None values up to branching_factor
        let mut items = Vec::with_capacity(branching_factor);
        for _ in 0..branching_factor {
            items.push(None);
        }
        
        Self {
            branching_factor,
            entries: BTreeMap::new(),
            items,
            count: 0,
        }
    }
    
    /// Inserts a key-value pair into the node.
    fn insert(&mut self, key: K, value: V) -> Option<V> {
        // Check if key already exists, so we can update the items array if needed
        let old_value = self.entries.insert(key.clone(), value.clone());
        
        if old_value.is_none() && self.count < self.branching_factor {
            // New key being added
            let new_entry = Entry { key, value };
            
            // Find the position to insert the new entry to maintain sorted order
            let mut insert_pos = self.count;
            for i in 0..self.count {
                if let Some(ref entry) = self.items[i] {
                    if entry.key > new_entry.key {
                        insert_pos = i;
                        break;
                    }
                }
            }
            
            // Shift elements to make room for the new entry
            for i in (insert_pos..self.count).rev() {
                self.items[i + 1] = self.items[i].clone();
            }
            
            // Insert the new entry and increment count
            self.items[insert_pos] = Some(new_entry);
            self.count += 1;
        } else if let Some(ref value) = old_value {
            // Update existing entry in the items array
            for i in 0..self.count {
                if let Some(ref mut entry) = self.items[i] {
                    if entry.key == key {
                        entry.value = value.clone();
                        break;
                    }
                }
            }
        }
        
        old_value
    }
    
    /// Returns a reference to the value corresponding to the key.
    fn get(&self, key: &K) -> Option<&V> {
        self.entries.get(key)
    }
    
    /// Returns the number of elements in the node.
    fn len(&self) -> usize {
        self.entries.len()
    }
    
    /// Returns `true` if the node contains no elements.
    fn is_empty(&self) -> bool {
        self.entries.is_empty()
    }
    
    /// Returns all key-value pairs in the range [min_key, max_key] in sorted order.
    /// If min_key is None, starts from the smallest key.
    /// If max_key is None, goes up to the largest key.
    fn range(&self, min_key: Option<&K>, max_key: Option<&K>) -> Vec<(&K, &V)> {
        // For now, let's use the entries BTreeMap directly which is already in sorted order
        // This is simpler and more reliable for the current implementation
        let mut result = Vec::new();
        
        for (key, value) in &self.entries {
            // Check min bound
            if let Some(min) = min_key {
                if key < min {
                    continue;
                }
            }
            
            // Check max bound
            if let Some(max) = max_key {
                if key > max {
                    break; // BTreeMap is ordered, so we can stop once we exceed the max
                }
            }
            
            result.push((key, value));
        }
        
        result
    }
}

#[derive(Debug)]
pub struct BPlusTree<K, V> {
    /// Maximum number of entries in each node
    branching_factor: usize,
    /// Root node of the tree (temporarily using BTreeMap until we implement proper tree structure)
    root: LeafNode<K, V>,
}

impl<K: Ord + Clone, V: Clone> BPlusTree<K, V> {
    /// Creates an empty `BPlusTree` with the specified branching factor.
    pub fn new(branching_factor: usize) -> Self {
        Self { 
            branching_factor,
            root: LeafNode::new(branching_factor),
        }
    }

    /// Returns the branching factor of the tree.
    pub fn branching_factor(&self) -> usize {
        self.branching_factor
    }

    /// Inserts a key-value pair into the tree.
    pub fn insert(&mut self, key: K, value: V) -> Option<V> {
        self.root.insert(key, value)
    }

    /// Returns a reference to the value corresponding to the key.
    pub fn get(&self, key: &K) -> Option<&V> {
        self.root.get(key)
    }
    
    /// Returns all key-value pairs in the range [min_key, max_key] in sorted order.
    /// If min_key is None, starts from the smallest key.
    /// If max_key is None, goes up to the largest key.
    pub fn range(&self, min_key: Option<&K>, max_key: Option<&K>) -> Vec<(&K, &V)> {
        self.root.range(min_key, max_key)
    }
    
    /// Returns a slice of the tree containing all key-value pairs in sorted order.
    pub fn slice(&self) -> Vec<(&K, &V)> {
        self.range(None, None)
    }

    /// Removes a key from the tree, returning the value if it existed.
    pub fn remove(&mut self, _key: &K) -> Option<V> {
        unimplemented!("not yet implemented")
    }

    /// Returns the number of elements in the tree.
    pub fn len(&self) -> usize {
        self.root.len()
    }

    /// Returns `true` if the tree contains no elements.
    pub fn is_empty(&self) -> bool {
        self.root.is_empty()
    }
}

