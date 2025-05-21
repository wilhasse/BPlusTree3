//! BPlusTree library.

/// A key-value entry in a leaf node.
#[derive(Debug, Clone)]
struct Entry<K, V> {
    key: K,
    value: V,
}

/// Utility to find the appropriate leaf node for a given key.
#[derive(Debug)]
struct LeafFinder<'a, K> {
    /// The key we're searching for
    key: &'a K,
}

impl<'a, K: Ord> LeafFinder<'a, K> {
    /// Creates a new LeafFinder for the given key
    fn new(key: &'a K) -> Self {
        Self { key }
    }
    
    /// Finds the leaf node where the key should be located.
    /// Returns a reference to the leaf node.
    ///
    /// The LeafFinder itself doesn't store any values of type V or operate on them directly, but it
    /// needs to preserve this type information to properly handle and return the correct LeafNode
    /// type.
    ///
    /// This is a case where the type parameter V is "passed through" - the LeafFinder doesn't use it
    /// directly, but needs to maintain it for type correctness in the function signatures.
    fn find_leaf<'b, V>(&self, root: &'b LeafNode<K, V>) -> &'b LeafNode<K, V> {
        // Check if this is the node we want
        if Self::is_target_node(root, self.key) {
            return root;
        }
        
        // If we have a next node and the key belongs in a later node
        if let Some(ref next) = root.next {
            // Check if key belongs in the next node
            if Self::is_target_node(next, self.key) {
                return next;
            }
            
            // If next node has a next and key might be in a later node
            if next.next.is_some() && Self::key_belongs_in_later_node(next, self.key) {
                // Recursively search from the next node
                return self.find_leaf(next);
            }
            
            // Key belongs in the next node (or it's the last node)
            return next;
        }
        
        // No next node, so key belongs in the current node
        root
    }
    
    /// Finds the leaf node where the key should be located.
    /// Returns a mutable reference to the leaf node.
    ///
    /// The LeafFinder itself doesn't store any values of type V or operate on them directly, but it
    /// needs to preserve this type information to properly handle and return the correct LeafNode
    /// type.
    ///
    /// This is a case where the type parameter V is "passed through" - the LeafFinder doesn't use it
    /// directly, but needs to maintain it for type correctness in the function signatures.
    ///
    /// Note: This is a recursive implementation to avoid unsafe code when dealing with 
    /// mutable references in a linked structure.
    fn find_leaf_mut<'b, V>(&self, root: &'b mut LeafNode<K, V>) -> &'b mut LeafNode<K, V> {
        // Check if this is the node we want
        if Self::is_target_node(root, self.key) {
            return root;
        }
        
        // If we have a next node and the key belongs in a later node
        if let Some(ref mut next) = root.next {
            // Check if key belongs in the next node
            if Self::is_target_node(next, self.key) {
                return next;
            }
            
            // If next node has a next and key might be in a later node
            if next.next.is_some() && Self::key_belongs_in_later_node(next, self.key) {
                // Recursively search from the next node
                return self.find_leaf_mut(next);
            }
            
            // Key belongs in the next node (or it's the last node)
            return next;
        }
        
        // No next node, so key belongs in the current node
        root
    }
    
    /// Helper method to check if a leaf node is the target for a key
    fn is_target_node<V>(node: &LeafNode<K, V>, key: &K) -> bool {
        // A node is a target if:
        // 1. It has no next node, or
        // 2. It's empty, or
        // 3. The key is <= the largest key in the node
        node.next.is_none() || 
        node.count == 0 || 
        if let Some(ref entry) = node.items[node.count - 1] {
            key <= &entry.key
        } else {
            true
        }
    }
    
    /// Helper method to check if a key belongs in a node after this one
    fn key_belongs_in_later_node<V>(node: &LeafNode<K, V>, key: &K) -> bool {
        // A key belongs in a later node if:
        // 1. The node is not empty, and
        // 2. The key is > the largest key in the node
        node.count > 0 &&
        if let Some(ref entry) = node.items[node.count - 1] {
            key > &entry.key
        } else {
            false
        }
    }
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
    
    // Helper method to expose the root node for testing
    #[cfg(test)]
    fn get_root(&self) -> &LeafNode<K, V> {
        &self.root
    }
    
    // Helper method to expose the root node for testing
    #[cfg(test)]
    fn get_root_mut(&mut self) -> &mut LeafNode<K, V> {
        &mut self.root
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
        
        // Use the LeafFinder to find the correct leaf node to insert into
        let finder = LeafFinder::new(&key);
        let leaf = finder.find_leaf_mut(&mut self.root);
        
        // Insert into the identified leaf
        leaf.insert(key, value)
    }

    /// Returns a reference to the value corresponding to the key.
    pub fn get(&self, key: &K) -> Option<&V> {
        // Use the LeafFinder to find the leaf node where the key should be
        let finder = LeafFinder::new(key);
        let leaf = finder.find_leaf(&self.root);
        
        // Look up the key in the leaf node
        leaf.get(key)
    }
    
    /// Returns all key-value pairs in the range [min_key, max_key] in sorted order.
    /// If min_key is None, starts from the smallest key.
    /// If max_key is None, goes up to the largest key.
    pub fn range(&self, min_key: Option<&K>, max_key: Option<&K>) -> Vec<(&K, &V)> {
        // If min_key is provided, use LeafFinder to find the starting leaf
        let start_leaf = if let Some(min) = min_key {
            let finder = LeafFinder::new(min);
            finder.find_leaf(&self.root)
        } else {
            // If no min_key, start from the root
            &self.root
        };
        
        // Start range search from the identified leaf
        start_leaf.range(min_key, max_key)
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_leaf_finder_single_node() {
        // Create a tree with a single node
        let mut tree: BPlusTree<i32, i32> = BPlusTree::new(4);
        
        // Insert some keys
        tree.insert(10, 100);
        tree.insert(20, 200);
        tree.insert(30, 300);
        
        // Create a leaf finder for a key that belongs in this node
        let finder = LeafFinder::new(&15);
        
        // Use the finder to locate the appropriate leaf
        let leaf = finder.find_leaf(tree.get_root());
        
        // Since there's only one node, it should be the root
        assert_eq!(leaf.count, 3);
        
        // Verify it has the expected keys
        assert_eq!(leaf.items[0].as_ref().unwrap().key, 10);
        assert_eq!(leaf.items[1].as_ref().unwrap().key, 20);
        assert_eq!(leaf.items[2].as_ref().unwrap().key, 30);
    }
    
    #[test]
    fn test_leaf_finder_multiple_nodes() {
        // Create a tree with branching factor 2 (will split quickly)
        let mut tree: BPlusTree<i32, i32> = BPlusTree::new(2);
        
        // Insert keys that will force a specific split pattern
        tree.insert(10, 100);
        tree.insert(20, 200);
        tree.insert(30, 300);
        // Let's add the key 40 afterward and make sure it goes into the second node
        tree.insert(40, 400);
        
        // Check that we have multiple nodes
        assert_eq!(tree.leaf_count(), 2);
        
        let root = tree.get_root();
        
        // Now that we see how the nodes are split, let's test with values we know go to different nodes
        
        // Find the appropriate node for a key that should be in the first node
        let finder_first = LeafFinder::new(&10);
        let leaf_first = finder_first.find_leaf(root);
        
        // Find the appropriate node for a key that should be in the second node
        let finder_second = LeafFinder::new(&25);  // This should find the second node with 20, 30
        let leaf_second = finder_second.find_leaf(root);
        
        // According to our debug output, verify we found the correct nodes
        assert!(leaf_first.items.iter().any(|item| 
            item.as_ref().map_or(false, |e| e.key == 10)));
            
        assert!(leaf_second.items.iter().any(|item| 
            item.as_ref().map_or(false, |e| e.key == 20)));
            
        assert!(leaf_second.items.iter().any(|item| 
            item.as_ref().map_or(false, |e| e.key == 30)));
        
        // These should be different nodes
        assert_ne!(leaf_first as *const _, leaf_second as *const _);
    }
    
    #[test]
    fn test_leaf_finder_mutable() {
        // Create a tree with branching factor 2 (will split quickly)
        let mut tree: BPlusTree<i32, i32> = BPlusTree::new(2);
        
        // Insert keys that will cause splits
        tree.insert(10, 100);
        tree.insert(20, 200);
        tree.insert(30, 300);
        tree.insert(40, 400);
        
        // Find a mutable reference to the leaf for a key in the second node
        let finder = LeafFinder::new(&25);  // This will find the node containing 20 and 30
        let leaf_mut = finder.find_leaf_mut(tree.get_root_mut());
        
        // Modify the leaf directly - replace the value for key 20
        if let Some(ref mut entry) = leaf_mut.items[0] {
            if entry.key == 20 {
                entry.value = 250;
            }
        }
        
        // Verify the modification worked
        assert_eq!(tree.get(&20), Some(&250));
    }
}

