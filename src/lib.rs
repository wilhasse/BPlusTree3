//! BPlusTree library.

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
    /// Array of key-value entries for B+ tree implementation
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
            items,
            count: 0,
        }
    }
    
    /// Inserts a key-value pair into the node.
    fn insert(&mut self, key: K, value: V) -> Option<V> {
        // Check if key already exists and update it if found
        for i in 0..self.count {
            if let Some(ref mut entry) = self.items[i] {
                if entry.key == key {
                    let old_value = entry.value.clone();
                    entry.value = value;
                    return Some(old_value);
                }
            }
        }
        
        // Key doesn't exist, check if we have room for a new entry
        if self.count < self.branching_factor {
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
            
            return None;
        }
        
        // No room for a new entry
        // In a real implementation, we would handle node splitting here
        None
    }
    
    /// Returns a reference to the value corresponding to the key.
    fn get(&self, key: &K) -> Option<&V> {
        // Linear search through the sorted items
        for i in 0..self.count {
            if let Some(ref entry) = self.items[i] {
                if &entry.key == key {
                    return Some(&entry.value);
                } else if &entry.key > key {
                    // We've passed where the key would be, so it doesn't exist
                    // This early return is possible because items are kept sorted
                    return None;
                }
            }
        }
        None
    }
    
    /// Returns the number of elements in the node.
    fn len(&self) -> usize {
        self.count
    }
    
    /// Returns `true` if the node contains no elements.
    fn is_empty(&self) -> bool {
        self.count == 0
    }
    
    /// Returns all key-value pairs in the range [min_key, max_key] in sorted order.
    /// If min_key is None, starts from the smallest key.
    /// If max_key is None, goes up to the largest key.
    fn range(&self, min_key: Option<&K>, max_key: Option<&K>) -> Vec<(&K, &V)> {
        let mut result = Vec::new();
        
        // Iterate through the sorted items array
        for i in 0..self.count {
            if let Some(ref entry) = self.items[i] {
                // Check min bound
                if let Some(min) = min_key {
                    if &entry.key < min {
                        continue;
                    }
                }
                
                // Check max bound
                if let Some(max) = max_key {
                    if &entry.key > max {
                        break; // Items are ordered, so we can stop once we exceed the max
                    }
                }
                
                result.push((&entry.key, &entry.value));
            }
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

