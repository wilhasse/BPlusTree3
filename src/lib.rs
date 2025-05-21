//! BPlusTree library.

/// A key-value entry in a leaf node.
#[derive(Debug, Clone)]
struct Entry<K, V> {
    key: K,
    value: V,
}

/// A node in the B+ tree containing the actual key-value data.
#[derive(Debug, Clone)]
struct LeafNode<K, V> {
    /// Maximum number of entries this node can hold before splitting
    branching_factor: usize,
    /// Array of key-value entries for B+ tree implementation
    /// Entries are stored in order, with valid entries from 0..count and None for unused slots
    items: Vec<Option<Entry<K, V>>>,
    /// Number of valid entries in the items array
    count: usize,
    /// Reference to the next leaf node in the linked list
    next: Option<Box<LeafNode<K, V>>>,
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
            next: None,
        }
    }
    
    /// Find the position of a key in the items array.
    /// Returns (position, Some(entry_index)) if key exists, or (insert_position, None) if key doesn't exist.
    fn find_position(&self, key: &K) -> (usize, Option<usize>) {
        // Search for the key in the sorted array
        let mut insert_pos = self.count; // Default to end of array
        
        for i in 0..self.count {
            if let Some(ref entry) = self.items[i] {
                // Use match for comparison as suggested by clippy
                match entry.key.cmp(key) {
                    std::cmp::Ordering::Equal => {
                        // Key found
                        return (i, Some(i));
                    },
                    std::cmp::Ordering::Greater => {
                        // Found first key greater than target key
                        insert_pos = i;
                        break;
                    },
                    std::cmp::Ordering::Less => {
                        // Continue searching
                    }
                }
            }
        }
        
        // Key not found, return the position where it should be inserted
        (insert_pos, None)
    }
    
    /// Inserts a key-value pair into the node.
    fn insert(&mut self, key: K, value: V) -> Option<V> {
        // Find if key exists or where it should be inserted
        let (pos, maybe_existing_index) = self.find_position(&key);
        
        // If key exists, update the value
        if let Some(existing_index) = maybe_existing_index {
            if let Some(ref mut entry) = self.items[existing_index] {
                let old_value = entry.value.clone();
                entry.value = value;
                return Some(old_value);
            }
        }
        
        // Key doesn't exist, check if we have room for a new entry
        if self.count < self.branching_factor {
            let new_entry = Entry { key, value };
            
            // Shift elements to make room for the new entry
            for i in (pos..self.count).rev() {
                self.items[i + 1] = self.items[i].clone();
            }
            
            // Insert the new entry and increment count
            self.items[pos] = Some(new_entry);
            self.count += 1;
            
            return None;
        }
        
        // No room for a new entry
        // In a real implementation, we would handle node splitting here
        None
    }
    
    /// Returns a reference to the value corresponding to the key.
    fn get(&self, key: &K) -> Option<&V> {
        // Use the find_position helper to check if key exists
        let (_, maybe_index) = self.find_position(key);
        
        if let Some(index) = maybe_index {
            if let Some(ref entry) = self.items[index] {
                return Some(&entry.value);
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
    
    /// Splits this node into two nodes, keeping roughly half the entries in this node
    /// and moving the other half to a new node. The new node is returned.
    fn split(&mut self) -> Box<Self> {
        let split_point = self.count / 2;
        
        // Create a new node with the same branching factor
        let mut new_node = Box::new(Self::new(self.branching_factor));
        
        // Move items from split_point onwards to the new node
        for i in split_point..self.count {
            new_node.items[i - split_point] = self.items[i].take();
            new_node.count += 1;
        }
        
        // Update count in current node
        self.count = split_point;
        
        // Link new node into the chain (new_node's next = self.next, self.next = new_node)
        new_node.next = self.next.take();
        
        new_node
    }
    
    /// Count the number of leaf nodes in the linked list starting from this node
    fn count_leaves(&self) -> usize {
        let mut count = 1; // Start with this node
        let mut current = self;
        
        while let Some(ref next_node) = current.next {
            count += 1;
            current = next_node;
        }
        
        count
    }
    
    /// Get the sizes of all leaf nodes in the linked list starting from this node
    fn get_leaf_sizes(&self) -> Vec<usize> {
        let mut sizes = Vec::new();
        let mut current = self;
        
        // Add this node's size
        sizes.push(current.count);
        
        // Add sizes of all linked nodes
        while let Some(ref next_node) = current.next {
            sizes.push(next_node.count);
            current = next_node;
        }
        
        sizes
    }
    
    /// Returns all key-value pairs in the range [min_key, max_key] in sorted order.
    /// If min_key is None, starts from the smallest key.
    /// If max_key is None, goes up to the largest key.
    fn range(&self, min_key: Option<&K>, max_key: Option<&K>) -> Vec<(&K, &V)> {
        let mut result = Vec::new();
        let mut current_node = self;
        
        // Loop through all nodes in the linked list
        loop {
            // Process entries in the current node
            for i in 0..current_node.count {
                if let Some(ref entry) = current_node.items[i] {
                    // Check min bound
                    if let Some(min) = min_key {
                        if &entry.key < min {
                            continue;
                        }
                    }
                    
                    // Check max bound
                    if let Some(max) = max_key {
                        if &entry.key > max {
                            // We've gone past the max, so we can stop processing entirely
                            return result;
                        }
                    }
                    
                    result.push((&entry.key, &entry.value));
                }
            }
            
            // Move to the next node if available
            if let Some(ref next_node) = current_node.next {
                current_node = next_node;
            } else {
                break;
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
    
    /// Returns the number of leaf nodes in the tree (for testing)
    pub fn leaf_count(&self) -> usize {
        self.root.count_leaves()
    }
    
    /// Returns the size of each leaf node (for testing)
    pub fn leaf_sizes(&self) -> Vec<usize> {
        self.root.get_leaf_sizes()
    }

    /// Inserts a key-value pair into the tree.
    pub fn insert(&mut self, key: K, value: V) -> Option<V> {
        // Check if the root node is already full and needs splitting before insert
        if self.root.count >= self.branching_factor {
            // Need to split the root node first
            let new_node = self.root.split();
            
            // Set up the linked list from root to new node
            self.root.next = Some(new_node);
        }
        
        // Find the correct node to insert into - first check if it belongs in root
        let belongs_in_root = self.root.count == 0 || 
            (self.root.count > 0 && 
            match &self.root.items[self.root.count - 1] {
                Some(entry) => &key <= &entry.key,
                None => true, // If no items, insert in root
            });
            
        if belongs_in_root {
            // Insert into root
            return self.root.insert(key, value);
        } else if let Some(ref mut next_node) = self.root.next {
            // Insert into the next node
            return next_node.insert(key, value);
        }
        
        // If we get here, we should insert into root (shouldn't happen with proper logic)
        self.root.insert(key, value)
    }

    /// Returns a reference to the value corresponding to the key.
    pub fn get(&self, key: &K) -> Option<&V> {
        // Start by checking the root node
        let result = self.root.get(key);
        if result.is_some() {
            return result;
        }
        
        // If not found in root, check subsequent nodes
        let mut current = &self.root;
        while let Some(ref next_node) = current.next {
            let result = next_node.get(key);
            if result.is_some() {
                return result;
            }
            current = next_node;
        }
        
        None
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
        let mut total = 0;
        let mut current = &self.root;
        
        // Add count from the root
        total += current.len();
        
        // Add counts from all linked nodes
        while let Some(ref next_node) = current.next {
            total += next_node.len();
            current = next_node;
        }
        
        total
    }

    /// Returns `true` if the tree contains no elements.
    pub fn is_empty(&self) -> bool {
        self.root.is_empty()
    }
}

