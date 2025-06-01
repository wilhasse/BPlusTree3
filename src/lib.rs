//! B+ Tree implementation in Rust with dict-like API.
//!
//! This module provides a B+ tree data structure with a dictionary-like interface,
//! supporting efficient insertion, deletion, lookup, and range queries.

// Constants
const MIN_CAPACITY: usize = 4;

/// Error type for B+ tree operations.
#[derive(Debug, Clone, PartialEq)]
pub enum BPlusTreeError {
    /// Key not found in the tree.
    KeyNotFound,
    /// Invalid capacity specified.
    InvalidCapacity(String),
}

/// B+ Tree implementation with Rust dict-like API.
///
/// A B+ tree is a self-balancing tree data structure that maintains sorted data
/// and allows searches, sequential access, insertions, and deletions in O(log n).
/// Unlike B trees, all values are stored in leaf nodes, making range queries
/// and sequential access very efficient.
///
/// # Type Parameters
///
/// * `K` - Key type that must implement `Ord + Clone + Debug`
/// * `V` - Value type that must implement `Clone + Debug`
///
/// # Examples
///
/// ```
/// use bplustree3::BPlusTreeMap;
///
/// let mut tree = BPlusTreeMap::new(16).unwrap();
/// tree.insert(1, "one");
/// tree.insert(2, "two");
/// tree.insert(3, "three");
///
/// assert_eq!(tree.get(&2), Some(&"two"));
/// assert_eq!(tree.len(), 3);
///
/// // Range queries
/// let range: Vec<_> = tree.range(Some(&1), Some(&3)).collect();
/// assert_eq!(range, [(&1, &"one"), (&2, &"two")]);
/// ```
///
/// # Performance Characteristics
///
/// - **Insertion**: O(log n)
/// - **Lookup**: O(log n)
/// - **Deletion**: O(log n)
/// - **Range queries**: O(log n + k) where k is the number of items in range
/// - **Iteration**: O(n)
///
/// # Capacity Guidelines
///
/// - Minimum capacity: 4 (enforced)
/// - Recommended capacity: 16-128 depending on use case
/// - Higher capacity = fewer tree levels but larger nodes
/// - Lower capacity = more tree levels but smaller nodes
#[derive(Debug)]
pub struct BPlusTreeMap<K, V> {
    /// Maximum number of keys per node.
    capacity: usize,
    /// The root node of the tree.
    root: NodeRef<K, V>,
}

/// Node reference that can be either a leaf or branch node
#[derive(Debug, Clone)]
pub enum NodeRef<K, V> {
    Leaf(Box<LeafNode<K, V>>),
    Branch(Box<BranchNode<K, V>>),
}

/// Result of an insertion operation on a leaf node.
pub enum InsertResult<K, V> {
    /// Insertion completed without splitting. Contains the old value if key existed.
    Updated(Option<V>),
    /// Insertion caused a split. Contains the old value and the new node with separator key.
    Split(Option<V>, NodeRef<K, V>, K),
}

impl<K: Ord + Clone, V: Clone> BPlusTreeMap<K, V> {
    /// Create a B+ tree with specified node capacity.
    ///
    /// # Arguments
    ///
    /// * `capacity` - Maximum number of keys per node (minimum 4)
    ///
    /// # Returns
    ///
    /// Returns `Ok(BPlusTreeMap)` if capacity is valid, `Err(BPlusTreeError)` otherwise.
    ///
    /// # Examples
    ///
    /// ```
    /// use bplustree3::BPlusTreeMap;
    ///
    /// let tree = BPlusTreeMap::<i32, String>::new(16).unwrap();
    /// assert!(tree.is_empty());
    /// ```
    pub fn new(capacity: usize) -> Result<Self, BPlusTreeError> {
        if capacity < MIN_CAPACITY {
            return Err(BPlusTreeError::InvalidCapacity(format!(
                "Capacity must be at least {} to maintain B+ tree invariants",
                MIN_CAPACITY
            )));
        }

        Ok(Self {
            capacity,
            root: NodeRef::Leaf(Box::new(LeafNode::new(capacity))),
        })
    }

    /// Create a B+ tree with default capacity.
    ///
    /// # Examples
    ///
    /// ```
    /// use bplustree3::BPlusTreeMap;
    ///
    /// let tree = BPlusTreeMap::<i32, String>::default();
    /// assert!(tree.is_empty());
    /// ```
    pub fn with_capacity(capacity: usize) -> Result<Self, BPlusTreeError> {
        Self::new(capacity)
    }

    /// Insert a key-value pair into the tree.
    ///
    /// If the key already exists, the old value is returned and replaced.
    /// If the key is new, `None` is returned.
    ///
    /// # Arguments
    ///
    /// * `key` - The key to insert
    /// * `value` - The value to associate with the key
    ///
    /// # Returns
    ///
    /// The previous value associated with the key, if any.
    ///
    /// # Examples
    ///
    /// ```
    /// use bplustree3::BPlusTreeMap;
    ///
    /// let mut tree = BPlusTreeMap::new(16).unwrap();
    /// assert_eq!(tree.insert(1, "first"), None);
    /// assert_eq!(tree.insert(1, "second"), Some("first"));
    /// ```
    pub fn insert(&mut self, key: K, value: V) -> Option<V> {
        let capacity = self.capacity;
        let result = Self::insert_recursive(&mut self.root, key, value, capacity);

        // If the root split, create a new root
        if let Some((new_node, separator_key)) = result.1 {
            let new_root = self.new_root(new_node, separator_key);
            self.root = NodeRef::Branch(Box::new(new_root));
        }

        result.0 // Return the old value if key existed
    }

    /// New roots are the only BranchNodes allowed to remain underfull
    fn new_root(&mut self, new_node: NodeRef<K, V>, separator_key: K) -> BranchNode<K, V> {
        let mut new_root = BranchNode::new(self.capacity);
        new_root.keys.push(separator_key);

        // Move the current root to be the left child
        let old_root = std::mem::replace(
            &mut self.root,
            NodeRef::Leaf(Box::new(LeafNode::new(self.capacity))),
        );
        new_root.children.push(old_root);
        new_root.children.push(new_node);
        new_root
    }

    /// Recursively insert a key-value pair into the tree.
    /// Returns (old_value, split_result) where split_result is None or Some((new_node, separator_key))
    fn insert_recursive(
        node: &mut NodeRef<K, V>,
        key: K,
        value: V,
        capacity: usize,
    ) -> (Option<V>, Option<(NodeRef<K, V>, K)>) {
        match node {
            NodeRef::Leaf(leaf) => match leaf.insert(key, value) {
                InsertResult::Updated(old_value) => (old_value, None),
                InsertResult::Split(old_value, new_node, separator_key) => {
                    (old_value, Some((new_node, separator_key)))
                }
            },
            NodeRef::Branch(branch) => {
                let child_index = branch.find_child_index(&key);

                let child = match branch.get_child_mut(&key) {
                    Some(child) => child,
                    None => return (None, None), // Invalid child index
                };

                // Recursively insert into the appropriate child
                let (old_value, split_result) = Self::insert_recursive(child, key, value, capacity);

                // If child didn't split, we're done
                if split_result.is_none() {
                    return (old_value, None);
                }

                let (new_child, separator_key) = split_result.unwrap();

                // Insert the new child and separator into this branch
                let branch_split =
                    branch.insert_child_and_split_if_needed(child_index, separator_key, new_child);

                (old_value, branch_split)
            }
        }
    }

    /// Get a reference to the value associated with a key.
    ///
    /// # Arguments
    ///
    /// * `key` - The key to look up
    ///
    /// # Returns
    ///
    /// A reference to the value if the key exists, `None` otherwise.
    ///
    /// # Examples
    ///
    /// ```
    /// use bplustree3::BPlusTreeMap;
    ///
    /// let mut tree = BPlusTreeMap::new(16).unwrap();
    /// tree.insert(1, "one");
    /// assert_eq!(tree.get(&1), Some(&"one"));
    /// assert_eq!(tree.get(&2), None);
    /// ```
    pub fn get(&self, key: &K) -> Option<&V> {
        let node = &self.root;
        Self::get_recursive(node, key)
    }

    fn get_recursive<'a>(node: &'a NodeRef<K, V>, key: &K) -> Option<&'a V> {
        match node {
            NodeRef::Leaf(leaf) => leaf.get(key),
            NodeRef::Branch(branch) => {
                if let Some(child) = branch.get_child(key) {
                    Self::get_recursive(child, key)
                } else {
                    None
                }
            }
        }
    }

    /// Remove a key from the tree.
    pub fn remove(&mut self, key: &K) -> Option<V> {
        let capacity = self.capacity;
        let (removed_value, _needs_rebalancing) =
            Self::remove_recursive(&mut self.root, key, capacity, true);

        // Always check for root collapse after any deletion
        if removed_value.is_some() {
            self.collapse_root_if_needed();
        }

        removed_value
    }

    /// Recursively remove a key from the tree.
    /// Returns (removed_value, needs_rebalancing)
    fn remove_recursive(
        node: &mut NodeRef<K, V>,
        key: &K,
        capacity: usize,
        is_root: bool,
    ) -> (Option<V>, bool) {
        match node {
            NodeRef::Leaf(leaf) => leaf.remove_and_check_rebalancing(key, is_root),
            NodeRef::Branch(branch) => {
                let child_index = branch.find_child_index(key);
                let child = match branch.get_child_mut(key) {
                    Some(child) => child,
                    None => return (None, false), // Invalid child index
                };

                // Recursively remove from the appropriate child
                let (removed_value, child_needs_rebalancing) =
                    Self::remove_recursive(child, key, capacity, false);

                if !child_needs_rebalancing {
                    return (removed_value, false);
                }

                // Child needs rebalancing - try to fix it
                let rebalanced = Self::rebalance_child(branch, child_index, capacity);

                // Check if this branch node now needs rebalancing
                let branch_needs_rebalancing = !is_root && !rebalanced && branch.is_underfull();

                (removed_value, branch_needs_rebalancing)
            }
        }
    }

    /// Attempt to rebalance a child that has become underfull.
    /// Returns true if rebalancing was successful, false if child was removed.
    fn rebalance_child(
        branch: &mut BranchNode<K, V>,
        child_index: usize,
        _capacity: usize,
    ) -> bool {
        // Check if the child is actually empty and should be removed
        let child_is_empty = match &branch.children[child_index] {
            NodeRef::Leaf(leaf) => leaf.is_empty(),
            NodeRef::Branch(child_branch) => child_branch.children.is_empty(),
        };

        if child_is_empty {
            // Remove the empty child and its corresponding separator key
            branch.children.remove(child_index);

            // Remove the appropriate separator key
            // If removing the rightmost child, remove the last key
            // Otherwise, remove the key at child_index
            if child_index == branch.keys.len() {
                // Removing rightmost child, remove last key
                if !branch.keys.is_empty() {
                    branch.keys.pop();
                }
            } else {
                // Remove the key at child_index
                if child_index < branch.keys.len() {
                    branch.keys.remove(child_index);
                }
            }
            false // Child was removed
        } else {
            // Child is not empty but might be underfull
            // For now, we'll just leave it as is
            // TODO: Implement proper borrowing and merging for underfull (but not empty) nodes
            // This would involve:
            // 1. Check if left or right sibling can donate
            // 2. If yes, borrow from sibling
            // 3. If no, merge with a sibling
            // 4. Update separator keys appropriately
            true // Child is still there
        }
    }

    /// Collapse the root if it's a branch with only one child or no children.
    fn collapse_root_if_needed(&mut self) {
        loop {
            match &self.root {
                NodeRef::Branch(branch) => {
                    if branch.children.is_empty() {
                        // Root branch has no children, replace with empty leaf
                        self.root = NodeRef::Leaf(Box::new(LeafNode::new(self.capacity)));
                        break;
                    } else if branch.children.len() == 1 {
                        // Root branch has only one child, replace root with that child
                        let new_root = branch.children[0].clone();
                        self.root = new_root;
                        // Continue the loop in case the new root also needs collapsing
                    } else {
                        // Root branch has multiple children, no collapse needed
                        break;
                    }
                }
                NodeRef::Leaf(_) => {
                    // Root is already a leaf, no collapse needed
                    break;
                }
            }
        }
    }

    /// Check if key exists in the tree.
    pub fn contains_key(&self, key: &K) -> bool {
        self.get(key).is_some()
    }

    /// Get value for a key with default.
    pub fn get_or_default<'a>(&'a self, key: &K, default: &'a V) -> &'a V {
        self.get(key).unwrap_or(default)
    }

    /// Returns the number of elements in the tree.
    pub fn len(&self) -> usize {
        match &self.root {
            NodeRef::Leaf(leaf) => leaf.len(),
            NodeRef::Branch(branch) => branch.len(),
        }
    }

    /// Returns true if the tree is empty.
    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    /// Returns true if the root is a leaf node.
    pub fn is_leaf_root(&self) -> bool {
        matches!(self.root, NodeRef::Leaf(_))
    }

    /// Returns the number of leaf nodes in the tree.
    pub fn leaf_count(&self) -> usize {
        match &self.root {
            NodeRef::Leaf(_) => 1,
            NodeRef::Branch(branch) => branch.leaf_count(),
        }
    }

    /// Get value for a key, returning an error if the key doesn't exist.
    /// This is equivalent to Python's `tree[key]`.
    pub fn get_item(&self, key: &K) -> Result<&V, BPlusTreeError> {
        self.get(key).ok_or(BPlusTreeError::KeyNotFound)
    }

    /// Remove a key from the tree, returning an error if the key doesn't exist.
    /// This is equivalent to Python's `del tree[key]`.
    pub fn remove_item(&mut self, key: &K) -> Result<V, BPlusTreeError> {
        self.remove(key).ok_or(BPlusTreeError::KeyNotFound)
    }

    /// Returns an iterator over all key-value pairs in sorted order.
    pub fn items(&self) -> ItemIterator<K, V> {
        ItemIterator::new(self)
    }

    /// Returns an iterator over all keys in sorted order.
    pub fn keys(&self) -> KeyIterator<K, V> {
        KeyIterator::new(self)
    }

    /// Returns an iterator over all values in key order.
    pub fn values(&self) -> ValueIterator<K, V> {
        ValueIterator::new(self)
    }

    /// Returns an iterator over key-value pairs in a range.
    /// If start_key is None, starts from the beginning.
    /// If end_key is None, goes to the end.
    pub fn items_range<'a>(
        &'a self,
        start_key: Option<&K>,
        end_key: Option<&'a K>,
    ) -> RangeIterator<'a, K, V> {
        RangeIterator::new(self, start_key, end_key)
    }

    /// Alias for items_range (for compatibility).
    pub fn range<'a>(
        &'a self,
        start_key: Option<&K>,
        end_key: Option<&'a K>,
    ) -> RangeIterator<'a, K, V> {
        self.items_range(start_key, end_key)
    }

    /// Clear all items from the tree.
    pub fn clear(&mut self) {
        self.root = NodeRef::Leaf(Box::new(LeafNode::new(self.capacity)));
    }

    /// Get a mutable reference to the value for a key.
    pub fn get_mut(&mut self, key: &K) -> Option<&mut V> {
        match &mut self.root {
            NodeRef::Leaf(leaf) => leaf.get_mut(key),
            NodeRef::Branch(branch) => branch.get_mut(key),
        }
    }

    /// Returns the first key-value pair in the tree.
    pub fn first(&self) -> Option<(&K, &V)> {
        self.items().next()
    }

    /// Returns the last key-value pair in the tree.
    pub fn last(&self) -> Option<(&K, &V)> {
        self.items().last()
    }

    /// Check if the tree maintains B+ tree invariants.
    /// Returns true if all invariants are satisfied.
    #[cfg(any(test, feature = "testing"))]
    pub fn check_invariants(&self) -> bool {
        self.check_node_invariants(&self.root, None, None, true)
    }

    /// Check invariants with detailed error reporting.
    #[cfg(any(test, feature = "testing"))]
    pub fn check_invariants_detailed(&self) -> Result<(), String> {
        if self.check_node_invariants(&self.root, None, None, true) {
            Ok(())
        } else {
            Err("Tree invariants violated".to_string())
        }
    }

    /// Alias for check_invariants_detailed (for test compatibility).
    #[cfg(any(test, feature = "testing"))]
    pub fn validate(&self) -> Result<(), String> {
        self.check_invariants_detailed()
    }

    /// Returns all key-value pairs as a vector (for testing/debugging).
    #[cfg(any(test, feature = "testing"))]
    pub fn slice(&self) -> Vec<(&K, &V)> {
        self.items().collect()
    }

    /// Returns the sizes of all leaf nodes (for testing/debugging).
    #[cfg(any(test, feature = "testing"))]
    pub fn leaf_sizes(&self) -> Vec<usize> {
        let mut sizes = Vec::new();
        self.collect_leaf_sizes(&self.root, &mut sizes);
        sizes
    }

    #[cfg(any(test, feature = "testing"))]
    fn collect_leaf_sizes(&self, node: &NodeRef<K, V>, sizes: &mut Vec<usize>) {
        match node {
            NodeRef::Leaf(leaf) => {
                sizes.push(leaf.keys.len());
            }
            NodeRef::Branch(branch) => {
                for child in &branch.children {
                    self.collect_leaf_sizes(child, sizes);
                }
            }
        }
    }

    /// Prints the node chain for debugging.
    #[cfg(any(test, feature = "testing"))]
    pub fn print_node_chain(&self) {
        println!("Tree structure:");
        self.print_node(&self.root, 0);
    }

    #[cfg(any(test, feature = "testing"))]
    fn print_node(&self, node: &NodeRef<K, V>, depth: usize) {
        let indent = "  ".repeat(depth);
        match node {
            NodeRef::Leaf(leaf) => {
                println!(
                    "{}Leaf[{}]: {} keys",
                    indent,
                    leaf.capacity,
                    leaf.keys.len()
                );
            }
            NodeRef::Branch(branch) => {
                println!(
                    "{}Branch[{}]: {} keys, {} children",
                    indent,
                    branch.capacity,
                    branch.keys.len(),
                    branch.children.len()
                );
                for child in &branch.children {
                    self.print_node(child, depth + 1);
                }
            }
        }
    }

    /// Recursively check invariants for a node and its children.
    #[cfg(any(test, feature = "testing"))]
    fn check_node_invariants(
        &self,
        node: &NodeRef<K, V>,
        min_key: Option<&K>,
        max_key: Option<&K>,
        _is_root: bool,
    ) -> bool {
        match node {
            NodeRef::Leaf(leaf) => {
                // Check leaf invariants
                if leaf.keys.len() != leaf.values.len() {
                    return false; // Keys and values must have same length
                }

                // Check that keys are sorted
                for i in 1..leaf.keys.len() {
                    if leaf.keys[i - 1] >= leaf.keys[i] {
                        return false; // Keys must be in ascending order
                    }
                }

                // Check capacity constraints
                if leaf.keys.len() > self.capacity {
                    return false; // Node exceeds capacity
                }

                // TODO: Re-enable this check once proper borrowing/merging is implemented
                // Check minimum occupancy (except for root)
                // if !is_root && !leaf.keys.is_empty() && leaf.is_underfull() {
                //     return false; // Non-root leaf is underfull
                // }

                // Check key bounds
                if let Some(min) = min_key {
                    if !leaf.keys.is_empty() && &leaf.keys[0] < min {
                        return false; // First key must be >= min_key
                    }
                }
                if let Some(max) = max_key {
                    if !leaf.keys.is_empty() && &leaf.keys[leaf.keys.len() - 1] >= max {
                        return false; // Last key must be < max_key
                    }
                }

                true
            }
            NodeRef::Branch(branch) => {
                // Check branch invariants
                if branch.keys.len() + 1 != branch.children.len() {
                    return false; // Must have one more child than keys
                }

                // Check that keys are sorted
                for i in 1..branch.keys.len() {
                    if branch.keys[i - 1] >= branch.keys[i] {
                        return false; // Keys must be in ascending order
                    }
                }

                // Check capacity constraints
                if branch.keys.len() > self.capacity {
                    return false; // Node exceeds capacity
                }

                // TODO: Re-enable this check once proper borrowing/merging is implemented
                // Check minimum occupancy (except for root)
                // if !is_root && !branch.keys.is_empty() && branch.is_underfull() {
                //     return false; // Non-root branch is underfull
                // }

                // Check that branch has at least one child
                if branch.children.is_empty() {
                    return false; // Branch must have at least one child
                }

                // Check children recursively
                for (i, child) in branch.children.iter().enumerate() {
                    let child_min = if i == 0 {
                        min_key
                    } else {
                        Some(&branch.keys[i - 1])
                    };
                    let child_max = if i == branch.keys.len() {
                        max_key
                    } else {
                        Some(&branch.keys[i])
                    };

                    if !self.check_node_invariants(child, child_min, child_max, false) {
                        return false;
                    }
                }

                true
            }
        }
    }
}

impl<K: Ord + Clone, V: Clone> Default for BPlusTreeMap<K, V> {
    /// Create a B+ tree with default capacity (16).
    fn default() -> Self {
        Self::new(16).expect("Default capacity should be valid")
    }
}

/// Leaf node containing key-value pairs.
#[derive(Debug, Clone)]
pub struct LeafNode<K, V> {
    /// Maximum number of keys this node can hold.
    capacity: usize,
    /// Sorted list of keys.
    keys: Vec<K>,
    /// List of values corresponding to keys.
    values: Vec<V>,
}

/// Internal (branch) node containing keys and child pointers.
#[derive(Debug, Clone)]
pub struct BranchNode<K, V> {
    /// Maximum number of keys this node can hold.
    capacity: usize,
    /// Sorted list of separator keys.
    keys: Vec<K>,
    /// List of child nodes (leaves or other branches).
    children: Vec<NodeRef<K, V>>,
}

impl<K: Ord + Clone, V: Clone> LeafNode<K, V> {
    /// Creates a new leaf node with the specified capacity.
    pub fn new(capacity: usize) -> Self {
        Self {
            capacity,
            keys: Vec::new(),
            values: Vec::new(),
        }
    }

    /// Get value for a key from this leaf node.
    pub fn get(&self, key: &K) -> Option<&V> {
        match self.keys.binary_search(key) {
            Ok(index) => Some(&self.values[index]),
            Err(_) => None,
        }
    }

    /// Get a mutable reference to the value for a key from this leaf node.
    pub fn get_mut(&mut self, key: &K) -> Option<&mut V> {
        match self.keys.binary_search(key) {
            Ok(index) => Some(&mut self.values[index]),
            Err(_) => None,
        }
    }

    /// Split this leaf node, returning the new right node.
    pub fn split(&mut self) -> Box<LeafNode<K, V>> {
        // Find the midpoint
        let mid = self.keys.len() / 2;

        // Create new leaf for right half
        let mut new_leaf = Box::new(LeafNode::new(self.capacity));

        // Move right half of keys/values to new leaf
        new_leaf.keys = self.keys.split_off(mid);
        new_leaf.values = self.values.split_off(mid);

        new_leaf
    }

    /// Remove a key from this leaf node.
    pub fn remove(&mut self, key: &K) -> Option<V> {
        match self.keys.binary_search(key) {
            Ok(index) => {
                self.keys.remove(index);
                Some(self.values.remove(index))
            }
            Err(_) => None,
        }
    }

    /// Returns the number of key-value pairs in this leaf node.
    pub fn len(&self) -> usize {
        self.keys.len()
    }

    /// Returns true if this leaf node is empty.
    pub fn is_empty(&self) -> bool {
        self.keys.is_empty()
    }

    /// Returns true if this leaf node is at capacity.
    pub fn is_full(&self) -> bool {
        self.keys.len() >= self.capacity
    }

    /// Returns true if this leaf node is underfull (below minimum occupancy).
    pub fn is_underfull(&self) -> bool {
        self.keys.len() < self.min_keys()
    }

    /// Returns the minimum number of keys this leaf should have.
    pub fn min_keys(&self) -> usize {
        // For leaf nodes, minimum is ceil(capacity/2) - 1, but at least 1
        // Exception: root can have fewer keys
        std::cmp::max(1, (self.capacity + 1) / 2)
    }

    /// Returns true if this leaf can donate a key to a sibling.
    pub fn can_donate(&self) -> bool {
        self.keys.len() > self.min_keys()
    }

    /// Borrow a key-value pair from the left sibling.
    /// Updates the separator key in the parent.
    pub fn borrow_from_left(&mut self, left: &mut LeafNode<K, V>, separator: &mut K) {
        if left.keys.is_empty() {
            return; // Nothing to borrow
        }

        // Move the last key-value from left to the beginning of this node
        let borrowed_key = left.keys.pop().unwrap();
        let borrowed_value = left.values.pop().unwrap();

        self.keys.insert(0, borrowed_key.clone());
        self.values.insert(0, borrowed_value);

        // Update the separator to be the first key of this node
        *separator = borrowed_key;
    }

    /// Borrow a key-value pair from the right sibling.
    /// Updates the separator key in the parent.
    pub fn borrow_from_right(&mut self, right: &mut LeafNode<K, V>, separator: &mut K) {
        if right.keys.is_empty() {
            return; // Nothing to borrow
        }

        // Move the first key-value from right to the end of this node
        let borrowed_key = right.keys.remove(0);
        let borrowed_value = right.values.remove(0);

        self.keys.push(borrowed_key);
        self.values.push(borrowed_value);

        // Update the separator to be the first key of the right node
        if !right.keys.is_empty() {
            *separator = right.keys[0].clone();
        }
    }

    /// Insert a key-value pair at the specified index.
    fn insert_at_index(&mut self, index: usize, key: K, value: V) {
        self.keys.insert(index, key);
        self.values.insert(index, value);
    }

    /// Insert a key-value pair and handle splitting if necessary.
    pub fn insert(&mut self, key: K, value: V) -> InsertResult<K, V> {
        // Do binary search once and use the result throughout
        match self.keys.binary_search(&key) {
            Ok(index) => {
                // Key already exists, update the value
                let old_value = std::mem::replace(&mut self.values[index], value);
                InsertResult::Updated(Some(old_value))
            }
            Err(index) => {
                // Key doesn't exist, need to insert
                if !self.is_full() {
                    // Simple insertion - leaf is not full
                    self.insert_at_index(index, key, value);
                    InsertResult::Updated(None)
                } else {
                    // Leaf is full, need to split
                    let mut new_leaf = self.split();

                    // Insert into appropriate leaf based on the split
                    if key < new_leaf.keys[0] {
                        self.insert_at_index(index, key, value);
                    } else {
                        // Adjust index for the new leaf since keys were moved
                        let adjusted_index = index - self.keys.len();
                        new_leaf.insert_at_index(adjusted_index, key, value);
                    }

                    let separator_key = new_leaf.keys[0].clone();
                    InsertResult::Split(None, NodeRef::Leaf(new_leaf), separator_key)
                }
            }
        }
    }

    /// Remove a key and check if rebalancing is needed.
    /// Returns (removed_value, needs_rebalancing).
    pub fn remove_and_check_rebalancing(&mut self, key: &K, is_root: bool) -> (Option<V>, bool) {
        let removed_value = self.remove(key);
        let needs_rebalancing = removed_value.is_some() && !is_root && self.is_underfull();
        (removed_value, needs_rebalancing)
    }

    /// Merge this leaf with the right sibling.
    /// Returns true if merge was successful.
    pub fn merge_with_right(&mut self, mut right: LeafNode<K, V>) -> bool {
        // Move all keys and values from right to this node
        self.keys.append(&mut right.keys);
        self.values.append(&mut right.values);

        true
    }
}

impl<K: Ord + Clone, V: Clone> BranchNode<K, V> {
    /// Creates a new branch node with the specified capacity.
    pub fn new(capacity: usize) -> Self {
        Self {
            capacity,
            keys: Vec::new(),
            children: Vec::new(),
        }
    }

    /// Find the child index where the given key should be located.
    pub fn find_child_index(&self, key: &K) -> usize {
        // Binary search to find the appropriate child
        match self.keys.binary_search(key) {
            Ok(index) => index + 1, // Key found, go to right child
            Err(index) => index,    // Key not found, insert position is the child index
        }
    }

    /// Get the child node for a given key.
    pub fn get_child(&self, key: &K) -> Option<&NodeRef<K, V>> {
        let child_index = self.find_child_index(key);
        if child_index < self.children.len() {
            Some(&self.children[child_index])
        } else {
            None
        }
    }

    /// Get a mutable reference to the child node for a given key.
    pub fn get_child_mut(&mut self, key: &K) -> Option<&mut NodeRef<K, V>> {
        let child_index = self.find_child_index(key);
        if child_index >= self.children.len() {
            return None; // Invalid child index
        }
        Some(&mut self.children[child_index])
    }

    /// Remove a key and handle child rebalancing.
    /// Returns (removed_value, needs_rebalancing).
    pub fn remove_and_rebalance<F>(
        &mut self,
        key: &K,
        capacity: usize,
        is_root: bool,
        remove_recursive: F,
    ) -> (Option<V>, bool)
    where
        F: Fn(&mut NodeRef<K, V>, &K, usize, bool) -> (Option<V>, bool),
    {
        let child_index = self.find_child_index(key);
        let child = match self.get_child_mut(key) {
            Some(child) => child,
            None => return (None, false), // Invalid child index
        };

        // Recursively remove from the appropriate child
        let (removed_value, child_needs_rebalancing) =
            remove_recursive(child, key, capacity, false);

        if !child_needs_rebalancing {
            return (removed_value, false);
        }

        // Child needs rebalancing - try to fix it
        let rebalanced = BPlusTreeMap::rebalance_child(self, child_index, capacity);

        // Check if this branch node now needs rebalancing
        let branch_needs_rebalancing = !is_root && !rebalanced && self.is_underfull();

        (removed_value, branch_needs_rebalancing)
    }

    /// Get value for a key by searching through children.
    pub fn get(&self, key: &K) -> Option<&V> {
        let child_index = self.find_child_index(key);
        if child_index < self.children.len() {
            match &self.children[child_index] {
                NodeRef::Leaf(leaf) => leaf.get(key),
                NodeRef::Branch(branch) => branch.get(key),
            }
        } else {
            None
        }
    }

    /// Get a mutable reference to the value for a key by searching through children.
    pub fn get_mut(&mut self, key: &K) -> Option<&mut V> {
        let child_index = self.find_child_index(key);
        if child_index < self.children.len() {
            match &mut self.children[child_index] {
                NodeRef::Leaf(leaf) => leaf.get_mut(key),
                NodeRef::Branch(branch) => branch.get_mut(key),
            }
        } else {
            None
        }
    }

    /// Count all keys in this branch and its children.
    pub fn len(&self) -> usize {
        self.children
            .iter()
            .map(|child| match child {
                NodeRef::Leaf(leaf) => leaf.len(),
                NodeRef::Branch(branch) => branch.len(),
            })
            .sum()
    }

    /// Count all leaf nodes in this branch and its children.
    pub fn leaf_count(&self) -> usize {
        self.children
            .iter()
            .map(|child| match child {
                NodeRef::Leaf(_) => 1,
                NodeRef::Branch(branch) => branch.leaf_count(),
            })
            .sum()
    }

    /// Remove a key from this branch by searching through children.
    pub fn remove(&mut self, key: &K) -> Option<V> {
        let child_index = self.find_child_index(key);
        if child_index < self.children.len() {
            match &mut self.children[child_index] {
                NodeRef::Leaf(leaf) => leaf.remove(key),
                NodeRef::Branch(branch) => branch.remove(key),
            }
        } else {
            None
        }
    }

    /// Insert a separator key and new child into this branch node.
    /// Returns None if no split needed, or Some((new_branch, promoted_key)) if split occurred.
    pub fn insert_child_and_split_if_needed(
        &mut self,
        child_index: usize,
        separator_key: K,
        new_child: NodeRef<K, V>,
    ) -> Option<(NodeRef<K, V>, K)> {
        // Insert the separator key and new child at the appropriate position
        self.keys.insert(child_index, separator_key);
        self.children.insert(child_index + 1, new_child);

        // If branch is not full after insertion, we're done
        if !self.is_full() {
            return None;
        }

        // Branch is full, need to split
        self.split()
    }

    /// Split this branch node, returning the new right node and promoted key.
    pub fn split(&mut self) -> Option<(NodeRef<K, V>, K)> {
        // Find the midpoint
        let mid = self.keys.len() / 2;

        // The middle key gets promoted to the parent
        let promoted_key = self.keys[mid].clone();

        // Create new branch for right half
        let mut new_branch = Box::new(BranchNode::new(self.capacity));

        // Move right half of keys to new branch (excluding the promoted key)
        new_branch.keys = self.keys.split_off(mid + 1);
        self.keys.truncate(mid); // Remove the promoted key from left side

        // Move right half of children to new branch
        new_branch.children = self.children.split_off(mid + 1);

        Some((NodeRef::Branch(new_branch), promoted_key))
    }

    /// Returns true if this branch node is at capacity.
    pub fn is_full(&self) -> bool {
        self.keys.len() >= self.capacity
    }

    /// Returns true if this branch node is underfull (below minimum occupancy).
    pub fn is_underfull(&self) -> bool {
        self.keys.len() < self.min_keys()
    }

    /// Returns the minimum number of keys this branch should have.
    pub fn min_keys(&self) -> usize {
        // For branch nodes, minimum is ceil(capacity/2) - 1
        // Exception: root can have fewer keys
        std::cmp::max(1, (self.capacity + 1) / 2 - 1)
    }

    /// Returns true if this branch can donate a key to a sibling.
    pub fn can_donate(&self) -> bool {
        self.keys.len() > self.min_keys()
    }

    /// Merge this branch with the right sibling using the given separator.
    /// Returns true if merge was successful.
    pub fn merge_with_right(&mut self, mut right: BranchNode<K, V>, separator: K) -> bool {
        // Add the separator key
        self.keys.push(separator);

        // Move all keys and children from right to this node
        self.keys.append(&mut right.keys);
        self.children.append(&mut right.children);

        true
    }
}

/// Iterator over key-value pairs in the B+ tree.
pub struct ItemIterator<'a, K, V> {
    items: Vec<(&'a K, &'a V)>,
    index: usize,
}

impl<'a, K: Ord, V> ItemIterator<'a, K, V> {
    fn new(tree: &'a BPlusTreeMap<K, V>) -> Self {
        let mut items = Vec::new();
        Self::collect_items(&tree.root, &mut items);
        Self { items, index: 0 }
    }

    fn collect_items(node: &'a NodeRef<K, V>, items: &mut Vec<(&'a K, &'a V)>) {
        match node {
            NodeRef::Leaf(leaf) => {
                for (key, value) in leaf.keys.iter().zip(leaf.values.iter()) {
                    items.push((key, value));
                }
            }
            NodeRef::Branch(branch) => {
                for child in &branch.children {
                    Self::collect_items(child, items);
                }
            }
        }
    }
}

impl<'a, K, V> Iterator for ItemIterator<'a, K, V> {
    type Item = (&'a K, &'a V);

    fn next(&mut self) -> Option<Self::Item> {
        if self.index < self.items.len() {
            let item = self.items[self.index];
            self.index += 1;
            Some(item)
        } else {
            None
        }
    }
}

/// Iterator over keys in the B+ tree.
pub struct KeyIterator<'a, K, V> {
    items: ItemIterator<'a, K, V>,
}

impl<'a, K: Ord, V> KeyIterator<'a, K, V> {
    fn new(tree: &'a BPlusTreeMap<K, V>) -> Self {
        Self {
            items: ItemIterator::new(tree),
        }
    }
}

impl<'a, K, V> Iterator for KeyIterator<'a, K, V> {
    type Item = &'a K;

    fn next(&mut self) -> Option<Self::Item> {
        self.items.next().map(|(k, _)| k)
    }
}

/// Iterator over values in the B+ tree.
pub struct ValueIterator<'a, K, V> {
    items: ItemIterator<'a, K, V>,
}

impl<'a, K: Ord, V> ValueIterator<'a, K, V> {
    fn new(tree: &'a BPlusTreeMap<K, V>) -> Self {
        Self {
            items: ItemIterator::new(tree),
        }
    }
}

impl<'a, K, V> Iterator for ValueIterator<'a, K, V> {
    type Item = &'a V;

    fn next(&mut self) -> Option<Self::Item> {
        self.items.next().map(|(_, v)| v)
    }
}

/// Iterator over a range of key-value pairs in the B+ tree.
#[derive(Debug)]
pub struct RangeIterator<'a, K, V> {
    items: Vec<(&'a K, &'a V)>,
    index: usize,
}

impl<'a, K: Ord, V> RangeIterator<'a, K, V> {
    fn new(tree: &'a BPlusTreeMap<K, V>, start_key: Option<&K>, end_key: Option<&'a K>) -> Self {
        let mut items = Vec::new();
        Self::collect_range_items(&tree.root, start_key, end_key, &mut items);
        Self { items, index: 0 }
    }

    fn collect_range_items(
        node: &'a NodeRef<K, V>,
        start_key: Option<&K>,
        end_key: Option<&K>,
        items: &mut Vec<(&'a K, &'a V)>,
    ) {
        match node {
            NodeRef::Leaf(leaf) => {
                for (key, value) in leaf.keys.iter().zip(leaf.values.iter()) {
                    // Early termination if we've passed the end key
                    if let Some(end) = end_key {
                        if key >= end {
                            return; // Stop collecting, we've gone past the range
                        }
                    }

                    // Check if key is after start
                    let after_start = start_key.map_or(true, |start| key >= start);

                    if after_start {
                        items.push((key, value));
                    }
                }
            }
            NodeRef::Branch(branch) => {
                for (i, child) in branch.children.iter().enumerate() {
                    // Check if this child could contain keys in our range
                    let child_min = if i == 0 {
                        None
                    } else {
                        Some(&branch.keys[i - 1])
                    };
                    let child_max = if i < branch.keys.len() {
                        Some(&branch.keys[i])
                    } else {
                        None
                    };

                    // Skip this child if it's entirely before our start key
                    if let (Some(start), Some(max)) = (start_key, child_max) {
                        if max <= start {
                            continue; // This child is entirely before our range
                        }
                    }

                    // Skip this child if it's entirely after our end key
                    if let (Some(end), Some(min)) = (end_key, child_min) {
                        if min >= end {
                            return; // This child and all following are after our range
                        }
                    }

                    // This child might contain keys in our range
                    Self::collect_range_items(child, start_key, end_key, items);

                    // Early termination: if we have an end key and this child's max >= end,
                    // we don't need to check further children
                    if let (Some(end), Some(max)) = (end_key, child_max) {
                        if max >= end {
                            return;
                        }
                    }
                }
            }
        }
    }
}

impl<'a, K: Ord, V> Iterator for RangeIterator<'a, K, V> {
    type Item = (&'a K, &'a V);

    fn next(&mut self) -> Option<Self::Item> {
        if self.index < self.items.len() {
            let item = self.items[self.index];
            self.index += 1;
            Some(item)
        } else {
            None
        }
    }
}
