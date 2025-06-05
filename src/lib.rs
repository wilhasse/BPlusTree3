//! B+ Tree implementation in Rust with dict-like API.
//!
//! This module provides a B+ tree data structure with a dictionary-like interface,
//! supporting efficient insertion, deletion, lookup, and range queries.

use std::marker::PhantomData;

// Constants
const MIN_CAPACITY: usize = 4;

/// Node ID type for arena-based allocation
pub type NodeId = u32;

/// Special node ID constants
pub const NULL_NODE: NodeId = u32::MAX;
pub const ROOT_NODE: NodeId = 0;

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

    // Arena-based allocation for leaf nodes
    /// Arena storage for leaf nodes.
    leaf_arena: Vec<Option<LeafNode<K, V>>>,
    /// Free leaf node IDs available for reuse.
    free_leaf_ids: Vec<NodeId>,

    // Arena-based allocation for branch nodes
    /// Arena storage for branch nodes.
    branch_arena: Vec<Option<BranchNode<K, V>>>,
    /// Free branch node IDs available for reuse.
    free_branch_ids: Vec<NodeId>,
}

/// Node reference that can be either a leaf or branch node
#[derive(Debug, Clone)]
pub enum NodeRef<K, V> {
    Leaf(NodeId, PhantomData<(K, V)>),
    Branch(NodeId, PhantomData<(K, V)>),
}

impl<K, V> NodeRef<K, V> {
    /// Return the raw node ID.
    pub fn id(&self) -> NodeId {
        match *self {
            NodeRef::Leaf(id, _) => id,
            NodeRef::Branch(id, _) => id,
        }
    }

    /// Returns true if this reference points to a leaf node.
    pub fn is_leaf(&self) -> bool {
        matches!(self, NodeRef::Leaf(_, _))
    }
}


/// Node data that can be allocated in the arena after a split.
pub enum SplitNodeData<K, V> {
    Leaf(LeafNode<K, V>),
    Branch(BranchNode<K, V>),
}

/// Result of an insertion operation on a node.
pub enum InsertResult<K, V> {
    /// Insertion completed without splitting. Contains the old value if key existed.
    Updated(Option<V>),
    /// Insertion caused a split with arena allocation needed.
    Split {
        old_value: Option<V>,
        new_node_data: SplitNodeData<K, V>,
        separator_key: K,
    },
}

impl<K: Ord + Clone, V: Clone> BPlusTreeMap<K, V> {
    // ============================================================================
    // CONSTRUCTION
    // ============================================================================

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

        // Initialize arena with the first leaf at id=0
        let mut leaf_arena = Vec::new();
        leaf_arena.push(Some(LeafNode::new(capacity))); // First leaf at id=0

        // Initialize branch arena (starts empty)
        let branch_arena = Vec::new();

        Ok(Self {
            capacity,
            root: NodeRef::Leaf(0, PhantomData), // Root points to the arena leaf at id=0
            // Initialize arena storage
            leaf_arena,
            free_leaf_ids: Vec::new(),
            branch_arena,
            free_branch_ids: Vec::new(),
        })
    }

    // ============================================================================
    // GET OPERATIONS
    // ============================================================================

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
        self.get_recursive(node, key)
    }

    /// Check if key exists in the tree.
    pub fn contains_key(&self, key: &K) -> bool {
        self.get(key).is_some()
    }

    /// Get value for a key with default.
    pub fn get_or_default<'a>(&'a self, key: &K, default: &'a V) -> &'a V {
        self.get(key).unwrap_or(default)
    }

    /// Get value for a key, returning an error if the key doesn't exist.
    /// This is equivalent to Python's `tree[key]`.
    pub fn get_item(&self, key: &K) -> Result<&V, BPlusTreeError> {
        self.get(key).ok_or(BPlusTreeError::KeyNotFound)
    }

    /// Get a mutable reference to the value for a key.
    pub fn get_mut(&mut self, key: &K) -> Option<&mut V> {
        match &self.root {
            NodeRef::Leaf(id, _) => {
                let id = *id;
                self.get_leaf_mut(id).and_then(|leaf| leaf.get_mut(key))
            }
            NodeRef::Branch(id, _) => {
                let id = *id;
                self.get_mut_in_branch(id, key)
            }
        }
    }

    /// Get mutable reference in an arena branch
    fn get_mut_in_branch(&mut self, branch_id: NodeId, key: &K) -> Option<&mut V> {
        // Get child info using helper
        let (_child_index, child_ref) = self.get_child_for_key(branch_id, key)?;

        // Traverse to child
        match child_ref {
            NodeRef::Leaf(leaf_id, _) => self
                .get_leaf_mut(leaf_id)
                .and_then(|leaf| leaf.get_mut(key)),
            NodeRef::Branch(child_branch_id, _) => self.get_mut_in_branch(child_branch_id, key),
        }
    }

    // ============================================================================
    // HELPERS FOR GET OPERATIONS
    // ============================================================================

    /// Helper to get child info for a key in a branch
    fn get_child_for_key(&self, branch_id: NodeId, key: &K) -> Option<(usize, NodeRef<K, V>)> {
        let branch = self.get_branch(branch_id)?;
        let child_index = branch.find_child_index(key);
        branch
            .children
            .get(child_index)
            .cloned()
            .map(|child| (child_index, child))
    }

    /// Helper to check if a node is underfull
    fn is_node_underfull(&self, node_ref: &NodeRef<K, V>) -> bool {
        match node_ref {
            NodeRef::Leaf(id, _) => self
                .get_leaf(*id)
                .map(|leaf| leaf.is_underfull())
                .unwrap_or(false),
            NodeRef::Branch(id, _) => self
                .get_branch(*id)
                .map(|branch| branch.is_underfull())
                .unwrap_or(false),
        }
    }

    /// Helper to check if a node can donate
    fn can_node_donate(&self, node_ref: &NodeRef<K, V>) -> bool {
        match node_ref {
            NodeRef::Leaf(id, _) => self
                .get_leaf(*id)
                .map(|leaf| leaf.can_donate())
                .unwrap_or(false),
            NodeRef::Branch(id, _) => self
                .get_branch(*id)
                .map(|branch| branch.can_donate())
                .unwrap_or(false),
        }
    }

    /// Get sibling node reference if it exists and types match
    fn get_branch_sibling(
        &self,
        branch_id: NodeId,
        child_index: usize,
        get_left: bool,
    ) -> Option<NodeRef<K, V>> {
        let branch = self.get_branch(branch_id)?;
        let sibling_index = if get_left {
            child_index.checked_sub(1)?
        } else {
            child_index + 1
        };

        branch.children.get(child_index).and_then(|current| {
            if let NodeRef::Branch(_, _) = current {
                branch.children.get(sibling_index).and_then(|sibling| {
                    if let NodeRef::Branch(_, _) = sibling {
                        Some(sibling.clone())
                    } else {
                        None
                    }
                })
            } else {
                None
            }
        })
    }

    /// Extract adjacent leaf node IDs if both children are leaves
    fn get_adjacent_leaf_ids(
        &self,
        branch_id: NodeId,
        child_index: usize,
    ) -> Option<(NodeId, NodeId)> {
        let branch = self.get_branch(branch_id)?;
        branch
            .children
            .get(child_index)
            .zip(branch.children.get(child_index + 1))
            .and_then(|(left, right)| {
                if let (NodeRef::Leaf(left_id, _), NodeRef::Leaf(right_id, _)) = (left, right) {
                    Some((*left_id, *right_id))
                } else {
                    None
                }
            })
    }

    fn get_recursive<'a>(&'a self, node: &'a NodeRef<K, V>, key: &K) -> Option<&'a V> {
        match node {
            NodeRef::Leaf(id, _) => self.get_leaf(*id).and_then(|leaf| leaf.get(key)),
            NodeRef::Branch(id, _) => self
                .get_branch(*id)
                .and_then(|branch| branch.get_child(key))
                .and_then(|child| self.get_recursive(child, key)),
        }
    }

    // ============================================================================
    // INSERT OPERATIONS
    // ============================================================================

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
        // Use insert_recursive to handle the insertion
        let result = self.insert_recursive(&self.root.clone(), key, value);

        match result {
            InsertResult::Updated(old_value) => old_value,
            InsertResult::Split {
                old_value,
                new_node_data,
                separator_key,
            } => {
                // Root split - need to create a new root
                let new_node_ref = match new_node_data {
                    SplitNodeData::Leaf(new_leaf_data) => {
                        let new_id = self.allocate_leaf(new_leaf_data);

                        // Update linked list pointers for root leaf split
                        if let NodeRef::Leaf(original_id, _) = &self.root {
                            self.get_leaf_mut(*original_id)
                                .map(|leaf| leaf.next = new_id);
                        }

                        NodeRef::Leaf(new_id, PhantomData)
                    }
                    SplitNodeData::Branch(new_branch_data) => {
                        let new_id = self.allocate_branch(new_branch_data);
                        NodeRef::Branch(new_id, PhantomData)
                    }
                };

                // Create new root with the split nodes
                let new_root = self.new_root(new_node_ref, separator_key);
                let root_id = self.allocate_branch(new_root);
                self.root = NodeRef::Branch(root_id, PhantomData);

                old_value
            }
        }
    }

    // ============================================================================
    // HELPERS FOR INSERT OPERATIONS
    // ============================================================================

    /// New roots are the only BranchNodes allowed to remain underfull
    fn new_root(&mut self, new_node: NodeRef<K, V>, separator_key: K) -> BranchNode<K, V> {
        let mut new_root = BranchNode::new(self.capacity);
        new_root.keys.push(separator_key);

        // Move the current root to be the left child
        // For arena-based implementation, create a placeholder arena leaf
        let placeholder_id = self.allocate_leaf(LeafNode::new(self.capacity));
        let placeholder = NodeRef::Leaf(placeholder_id, PhantomData);
        let old_root = std::mem::replace(&mut self.root, placeholder);

        new_root.children.push(old_root);
        new_root.children.push(new_node);
        new_root
    }

    /// Recursively insert a key with proper arena access.
    fn insert_recursive(&mut self, node: &NodeRef<K, V>, key: K, value: V) -> InsertResult<K, V> {
        match node {
            NodeRef::Leaf(id, _) => {
                if let Some(leaf) = self.get_leaf_mut(*id) {
                    leaf.insert(key, value)
                } else {
                    InsertResult::Updated(None)
                }
            }
            NodeRef::Branch(id, _) => {
                let id = *id;

                // First get child info without mutable borrow
                let (child_index, child_ref) = match self.get_child_for_key(id, &key) {
                    Some(info) => info,
                    None => return InsertResult::Updated(None),
                };

                // Recursively insert
                let child_result = self.insert_recursive(&child_ref, key, value);

                // Handle the result
                match child_result {
                    InsertResult::Updated(old_value) => InsertResult::Updated(old_value),
                    InsertResult::Split {
                        old_value,
                        new_node_data,
                        separator_key,
                    } => {
                        // Allocate the new node based on its type
                        let new_node = match new_node_data {
                            SplitNodeData::Leaf(new_leaf_data) => {
                                let new_id = self.allocate_leaf(new_leaf_data);

                                // Update linked list pointers for leaf splits
                                if let NodeRef::Leaf(original_id, _) = child_ref {
                                    // Update the original leaf's next pointer to point to the new leaf
                                    if let Some(original_leaf) = self.get_leaf_mut(original_id) {
                                        original_leaf.next = new_id;
                                    }
                                }

                                NodeRef::Leaf(new_id, PhantomData)
                            }
                            SplitNodeData::Branch(new_branch_data) => {
                                let new_id = self.allocate_branch(new_branch_data);
                                NodeRef::Branch(new_id, PhantomData)
                            }
                        };

                        // Insert into this branch
                        if let Some(branch) = self.get_branch_mut(id) {
                            if let Some((new_branch_data, promoted_key)) = branch
                                .insert_child_and_split_if_needed(
                                    child_index,
                                    separator_key,
                                    new_node,
                                )
                            {
                                // This branch split too - return raw branch data
                                InsertResult::Split {
                                    old_value,
                                    new_node_data: SplitNodeData::Branch(new_branch_data),
                                    separator_key: promoted_key,
                                }
                            } else {
                                // No split needed
                                InsertResult::Updated(old_value)
                            }
                        } else {
                            InsertResult::Updated(old_value)
                        }
                    }
                }
            }
        }
    }

    // ============================================================================
    // DELETE OPERATIONS
    // ============================================================================

    /// Remove a key from the tree.
    pub fn remove(&mut self, key: &K) -> Option<V> {
        // Special handling for Leaf root
        if let NodeRef::Leaf(id, _) = &self.root {
            let id = *id;
            if let Some(leaf) = self.get_leaf_mut(id) {
                let removed = leaf.remove(key);
                // No rebalancing needed for root leaf
                return removed;
            }
        }

        // Special handling for Branch root
        if let NodeRef::Branch(id, _) = &self.root {
            let removed = self.remove_from_branch(*id, key);

            // Check if root needs collapsing after removal
            if removed.is_some() {
                self.collapse_root_if_needed();
            }

            return removed;
        }

        None
    }

    /// Remove a key from a branch node with rebalancing
    fn remove_from_branch(&mut self, branch_id: NodeId, key: &K) -> Option<V> {
        // Find child index
        let child_index = self
            .get_branch(branch_id)
            .map(|branch| branch.find_child_index(key))?;

        // Get child reference
        let child_ref = self
            .get_branch(branch_id)
            .and_then(|branch| branch.children.get(child_index).cloned())?;

        // Remove from child
        let (removed_value, child_became_underfull) = match child_ref {
            NodeRef::Leaf(leaf_id, _) => {
                let removed = self.get_leaf_mut(leaf_id).and_then(|leaf| leaf.remove(key));

                // Check if leaf became underfull
                let is_underfull = self.is_node_underfull(&NodeRef::Leaf(leaf_id, PhantomData));

                (removed, is_underfull)
            }
            NodeRef::Branch(child_branch_id, _) => {
                let removed = self.remove_from_branch(child_branch_id, key);

                // Check if branch became underfull
                let is_underfull =
                    self.is_node_underfull(&NodeRef::Branch(child_branch_id, PhantomData));

                (removed, is_underfull)
            }
        };

        // If child became underfull, try to rebalance
        if removed_value.is_some() && child_became_underfull {
            let _child_still_exists = self.rebalance_child(branch_id, child_index);

            // After rebalancing (which might involve merging), check if the parent branch
            // itself became underfull. However, we don't propagate this up since the
            // caller will check this.
        }

        removed_value
    }

    /// Rebalance an underfull child in an arena branch
    fn rebalance_child(&mut self, branch_id: NodeId, child_index: usize) -> bool {
        // Get information about the child and its siblings
        let (has_left_sibling, has_right_sibling, child_is_leaf) = match self.get_branch(branch_id)
        {
            Some(branch) => {
                let has_left = child_index > 0;
                let has_right = child_index < branch.children.len() - 1;
                let is_leaf = matches!(branch.children[child_index], NodeRef::Leaf(_, _));
                (has_left, has_right, is_leaf)
            }
            None => return false,
        };

        if child_is_leaf {
            // Handle leaf rebalancing
            self.rebalance_leaf_child(branch_id, child_index, has_left_sibling, has_right_sibling)
        } else {
            // Handle branch rebalancing
            self.rebalance_branch_child(branch_id, child_index, has_left_sibling, has_right_sibling)
        }
    }

    /// Rebalance an underfull leaf child
    fn rebalance_leaf_child(
        &mut self,
        branch_id: NodeId,
        child_index: usize,
        has_left_sibling: bool,
        has_right_sibling: bool,
    ) -> bool {
        // Try borrowing from left sibling first
        if has_left_sibling {
            let can_borrow = self
                .get_branch(branch_id)
                .and_then(|branch| {
                    if child_index > 0 {
                        Some(&branch.children[child_index - 1])
                    } else {
                        None
                    }
                })
                .map(|left_sibling| self.can_node_donate(left_sibling))
                .unwrap_or(false);

            if can_borrow {
                return self.borrow_from_left_leaf(branch_id, child_index);
            }
        }

        // Try borrowing from right sibling
        if has_right_sibling {
            let can_borrow = self
                .get_branch(branch_id)
                .and_then(|branch| branch.children.get(child_index + 1))
                .map(|right_sibling| self.can_node_donate(right_sibling))
                .unwrap_or(false);

            if can_borrow {
                return self.borrow_from_right_leaf(branch_id, child_index);
            }
        }

        // Cannot borrow, must merge
        if has_left_sibling {
            return self.merge_with_left_leaf(branch_id, child_index);
        } else if has_right_sibling {
            return self.merge_with_right_leaf(branch_id, child_index);
        }

        // No siblings to merge with - this shouldn't happen
        false
    }

    /// Rebalance an underfull branch child
    fn rebalance_branch_child(
        &mut self,
        branch_id: NodeId,
        child_index: usize,
        has_left_sibling: bool,
        has_right_sibling: bool,
    ) -> bool {
        // Try borrowing from left sibling first
        if has_left_sibling {
            let can_borrow = self
                .get_branch_sibling(branch_id, child_index, true)
                .map(|sibling| self.can_node_donate(&sibling))
                .unwrap_or(false);

            if can_borrow {
                return self.borrow_from_left_branch(branch_id, child_index);
            }
        }

        // Try borrowing from right sibling
        if has_right_sibling {
            let can_borrow = self
                .get_branch_sibling(branch_id, child_index, false)
                .map(|sibling| self.can_node_donate(&sibling))
                .unwrap_or(false);

            if can_borrow {
                return self.borrow_from_right_branch(branch_id, child_index);
            }
        }

        // Check if we can merge with siblings
        if has_left_sibling {
            let can_merge = self
                .get_branch(branch_id)
                .and_then(|branch| {
                    if let (NodeRef::Branch(left_id, _), NodeRef::Branch(child_id, _)) = (
                        &branch.children[child_index - 1],
                        &branch.children[child_index],
                    ) {
                        Some((left_id, child_id))
                    } else {
                        None
                    }
                })
                .and_then(|(left_id, child_id)| {
                    self.get_branch(*left_id).zip(self.get_branch(*child_id))
                })
                .map(|(left, child)| left.keys.len() + 1 + child.keys.len() <= self.capacity)
                .unwrap_or(false);

            if can_merge {
                return self.merge_with_left_branch(branch_id, child_index);
            }
        }

        if has_right_sibling {
            let can_merge = self
                .get_branch(branch_id)
                .and_then(|branch| {
                    if let (NodeRef::Branch(child_id, _), NodeRef::Branch(right_id, _)) = (
                        &branch.children[child_index],
                        &branch.children[child_index + 1],
                    ) {
                        Some((child_id, right_id))
                    } else {
                        None
                    }
                })
                .and_then(|(child_id, right_id)| {
                    self.get_branch(*child_id).zip(self.get_branch(*right_id))
                })
                .map(|(child, right)| child.keys.len() + 1 + right.keys.len() <= self.capacity)
                .unwrap_or(false);

            if can_merge {
                return self.merge_with_right_branch(branch_id, child_index);
            }
        }

        // Cannot borrow or merge - leave the node underfull
        // This can happen when siblings are also near minimum capacity
        true
    }

    /// Merge branch with left sibling
    fn merge_with_left_branch(&mut self, parent_id: NodeId, child_index: usize) -> bool {
        // Get the branch IDs
        let parent = match self.get_branch(parent_id) {
            Some(p) => p,
            None => return false,
        };
        let (left_id, child_id, separator_key) = match (&parent.children[child_index - 1], &parent.children[child_index]) {
            (NodeRef::Branch(left, _), NodeRef::Branch(child, _)) => {
                (*left, *child, parent.keys[child_index - 1].clone())
            }
            _ => return false,
        };

        // Get the data from child branch
        let (mut child_keys, mut child_children) = match self.get_branch_mut(child_id) {
            Some(child_branch) => (
                std::mem::take(&mut child_branch.keys),
                std::mem::take(&mut child_branch.children),
            ),
            None => return false,
        };

        // Merge into left branch
        let merge_success = self
            .get_branch_mut(left_id)
            .map(|left_branch| {
                // Add separator key from parent
                left_branch.keys.push(separator_key);
                // Add all keys and children from child
                left_branch.keys.append(&mut child_keys);
                left_branch.children.append(&mut child_children);
                true
            })
            .unwrap_or(false);

        if !merge_success {
            return false;
        }

        // Remove child from parent
        self.get_branch_mut(parent_id).map(|parent| {
            parent.children.remove(child_index);
            parent.keys.remove(child_index - 1);
        });

        // Deallocate the merged child
        self.deallocate_branch(child_id);

        false // Child was merged away
    }

    /// Merge branch with right sibling
    fn merge_with_right_branch(&mut self, parent_id: NodeId, child_index: usize) -> bool {
        // Get the branch IDs
        let parent = match self.get_branch(parent_id) {
            Some(p) => p,
            None => return false,
        };
        let (child_id, right_id, separator_key) = match (&parent.children[child_index], &parent.children[child_index + 1]) {
            (NodeRef::Branch(child, _), NodeRef::Branch(right, _)) => {
                (*child, *right, parent.keys[child_index].clone())
            }
            _ => return false,
        };

        // Get the data from right branch
        let (mut right_keys, mut right_children) =
            match self.get_branch_mut(right_id).map(|right_branch| {
                (
                    std::mem::take(&mut right_branch.keys),
                    std::mem::take(&mut right_branch.children),
                )
            }) {
                Some(tuple) => tuple,
                None => return false,
            };

        // Merge into child branch
        if let Some(child_branch) = self.get_branch_mut(child_id) {
            // Add separator key from parent
            child_branch.keys.push(separator_key);
            // Add all keys and children from right
            child_branch.keys.append(&mut right_keys);
            child_branch.children.append(&mut right_children);
        } else {
            return false;
        }

        // Remove right from parent
        if let Some(parent) = self.get_branch_mut(parent_id) {
            parent.children.remove(child_index + 1);
            parent.keys.remove(child_index);
        }

        // Deallocate the merged right sibling
        self.deallocate_branch(right_id);

        true // Child still exists
    }

    /// Borrow from left sibling branch
    fn borrow_from_left_branch(&mut self, parent_id: NodeId, child_index: usize) -> bool {
        // Get the branch IDs and parent info
        let parent = match self.get_branch(parent_id) {
            Some(p) => p,
            None => return false,
        };
        let (left_id, child_id, separator_key) = match (&parent.children[child_index - 1], &parent.children[child_index]) {
            (NodeRef::Branch(left, _), NodeRef::Branch(child, _)) => {
                (*left, *child, parent.keys[child_index - 1].clone())
            }
            _ => return false,
        };

        // Take the last key and child from left sibling
        let (moved_key, moved_child) = match self.get_branch_mut(left_id).and_then(|left_branch| {
            match (left_branch.keys.pop(), left_branch.children.pop()) {
                (Some(k), Some(c)) => Some((k, c)),
                _ => None,
            }
        }) {
            Some(tuple) => tuple,
            None => return false,
        };

        // Insert into child branch at the beginning
        if let Some(child_branch) = self.get_branch_mut(child_id) {
            // The separator becomes the first key in child
            child_branch.keys.insert(0, separator_key);
            // The moved child becomes the first child
            child_branch.children.insert(0, moved_child);
        } else {
            return false;
        }

        // Update separator in parent (moved_key becomes new separator)
        if let Some(parent) = self.get_branch_mut(parent_id) {
            parent.keys[child_index - 1] = moved_key;
        }

        true
    }

    /// Borrow from right sibling branch
    fn borrow_from_right_branch(&mut self, parent_id: NodeId, child_index: usize) -> bool {
        // Get the branch IDs and parent info
        let parent = match self.get_branch(parent_id) {
            Some(p) => p,
            None => return false,
        };
        let (child_id, right_id, separator_key) = match (&parent.children[child_index], &parent.children[child_index + 1]) {
            (NodeRef::Branch(child, _), NodeRef::Branch(right, _)) => {
                (*child, *right, parent.keys[child_index].clone())
            }
            _ => return false,
        };

        // Take the first key and child from right sibling
        let (moved_key, moved_child) = match self.get_branch_mut(right_id) {
            Some(right_branch) if !right_branch.keys.is_empty() => {
                (right_branch.keys.remove(0), right_branch.children.remove(0))
            }
            _ => return false,
        };

        // Append to child branch
        if let Some(child_branch) = self.get_branch_mut(child_id) {
            // The separator becomes the last key in child
            child_branch.keys.push(separator_key);
            // The moved child becomes the last child
            child_branch.children.push(moved_child);
        } else {
            return false;
        }

        // Update separator in parent (moved_key becomes new separator)
        if let Some(parent) = self.get_branch_mut(parent_id) {
            parent.keys[child_index] = moved_key;
        }

        true
    }

    /// Borrow from left sibling leaf
    fn borrow_from_left_leaf(&mut self, branch_id: NodeId, child_index: usize) -> bool {
        // Extract the needed data to avoid borrow checker issues
        let branch = match self.get_branch(branch_id) {
            Some(b) => b,
            None => return false,
        };
        let (left_id, child_id, _separator_key) = match (
            &branch.children[child_index - 1],
            &branch.children[child_index],
        ) {
            (NodeRef::Leaf(left, _), NodeRef::Leaf(child, _)) => {
                (*left, *child, branch.keys[child_index - 1].clone())
            }
            _ => return false,
        };

        // Move last key-value from left to child
        let (key, value) = match self.get_leaf_mut(left_id) {
            Some(left_leaf) if !left_leaf.keys.is_empty() => {
                (left_leaf.keys.pop().unwrap(), left_leaf.values.pop().unwrap())
            }
            _ => return false,
        };

        // Insert into child at beginning
        if let Some(child_leaf) = self.get_leaf_mut(child_id) {
            child_leaf.keys.insert(0, key.clone());
            child_leaf.values.insert(0, value);
        } else {
            return false;
        }

        // Update separator in parent
        if let Some(branch) = self.get_branch_mut(branch_id) {
            branch.keys[child_index - 1] = key;
        }

        true
    }

    /// Borrow from right sibling leaf
    fn borrow_from_right_leaf(&mut self, branch_id: NodeId, child_index: usize) -> bool {
        // Extract the needed data
        let (child_id, right_id) = match self.get_adjacent_leaf_ids(branch_id, child_index) {
            Some(ids) => ids,
            None => return false,
        };

        // Move first key-value from right to child
        let (key, value) = match self.get_leaf_mut(right_id) {
            Some(right_leaf) if !right_leaf.keys.is_empty() => {
                (right_leaf.keys.remove(0), right_leaf.values.remove(0))
            }
            _ => return false,
        };

        // Append to child
        if let Some(child_leaf) = self.get_leaf_mut(child_id) {
            child_leaf.keys.push(key);
            child_leaf.values.push(value);
        } else {
            return false;
        }

        // Update separator in parent
        let new_separator = self
            .get_leaf(right_id)
            .and_then(|right_leaf| right_leaf.keys.first().cloned());

        if let Some(new_sep) = new_separator {
            if let Some(branch) = self.get_branch_mut(branch_id) {
                branch.keys[child_index] = new_sep;
            }
        }

        true
    }

    /// Merge with left sibling leaf
    fn merge_with_left_leaf(&mut self, branch_id: NodeId, child_index: usize) -> bool {
        // Extract the needed data
        let branch = match self.get_branch(branch_id) {
            Some(b) => b,
            None => return false,
        };
        let (left_id, child_id) = match (
            &branch.children[child_index - 1],
            &branch.children[child_index],
        ) {
            (NodeRef::Leaf(left, _), NodeRef::Leaf(child, _)) => (*left, *child),
            _ => return false,
        };

        // Move all keys and values from child to left, and get child's next pointer
        let (mut keys, mut values, child_next) = match self.get_leaf_mut(child_id) {
            Some(child_leaf) => (
                std::mem::take(&mut child_leaf.keys),
                std::mem::take(&mut child_leaf.values),
                child_leaf.next,
            ),
            None => return false,
        };

        // Merge the child into the left leaf and update linked list
        if let Some(left_leaf) = self.get_leaf_mut(left_id) {
            left_leaf.keys.append(&mut keys);
            left_leaf.values.append(&mut values);
            // Update linked list: left leaf's next should point to what child was pointing to
            left_leaf.next = child_next;
        } else {
            return false;
        }

        // Remove child from parent
        if let Some(branch) = self.get_branch_mut(branch_id) {
            branch.children.remove(child_index);
            branch.keys.remove(child_index - 1);
        }

        // Deallocate the merged child
        self.deallocate_leaf(child_id);

        false // Child was merged away
    }

    /// Merge with right sibling leaf
    fn merge_with_right_leaf(&mut self, branch_id: NodeId, child_index: usize) -> bool {
        // Extract the needed data
        let (child_id, right_id) = match self.get_adjacent_leaf_ids(branch_id, child_index) {
            Some(ids) => ids,
            None => return false,
        };

        // Move all keys and values from right to child, and get right's next pointer
        let (mut keys, mut values, right_next) = match self.get_leaf_mut(right_id) {
            Some(right_leaf) => (
                std::mem::take(&mut right_leaf.keys),
                std::mem::take(&mut right_leaf.values),
                right_leaf.next,
            ),
            None => return false,
        };

        // Merge the right leaf into the left leaf and update linked list
        if let Some(child_leaf) = self.get_leaf_mut(child_id) {
            child_leaf.keys.append(&mut keys);
            child_leaf.values.append(&mut values);
            // Update linked list: left leaf's next should point to what right was pointing to
            child_leaf.next = right_next;
        } else {
            return false;
        }

        // Remove right from parent
        if let Some(branch) = self.get_branch_mut(branch_id) {
            branch.children.remove(child_index + 1);
            branch.keys.remove(child_index);
        }

        // Deallocate the merged right sibling
        self.deallocate_leaf(right_id);

        true // Child still exists
    }

    /// Remove a key from the tree, returning an error if the key doesn't exist.
    /// This is equivalent to Python's `del tree[key]`.
    pub fn remove_item(&mut self, key: &K) -> Result<V, BPlusTreeError> {
        self.remove(key).ok_or(BPlusTreeError::KeyNotFound)
    }

    // ============================================================================
    // HELPERS FOR DELETE OPERATIONS
    // ============================================================================

    /// Collapse the root if it's a branch with only one child or no children.
    fn collapse_root_if_needed(&mut self) {
        loop {
            match &self.root {
                NodeRef::Branch(id, _) => {
                    if let Some(branch) = self.get_branch(*id) {
                        if branch.children.is_empty() {
                            // Root branch has no children, replace with empty arena leaf
                            let empty_id = self.allocate_leaf(LeafNode::new(self.capacity));
                            self.root = NodeRef::Leaf(empty_id, PhantomData);
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
                    } else {
                        // Missing arena branch, replace with empty arena leaf
                        let empty_id = self.allocate_leaf(LeafNode::new(self.capacity));
                        self.root = NodeRef::Leaf(empty_id, PhantomData);
                        break;
                    }
                }
                NodeRef::Leaf(_, _) => {
                    // Arena leaf root, no collapse needed
                    break;
                }
            }
        }
    }

    // ============================================================================
    // OTHER API OPERATIONS
    // ============================================================================

    /// Returns the number of elements in the tree.
    pub fn len(&self) -> usize {
        self.len_recursive(&self.root)
    }

    /// Recursively count elements with proper arena access.
    fn len_recursive(&self, node: &NodeRef<K, V>) -> usize {
        match node {
            NodeRef::Leaf(id, _) => self.get_leaf(*id).map(|leaf| leaf.len()).unwrap_or(0),
            NodeRef::Branch(id, _) => self
                .get_branch(*id)
                .map(|branch| {
                    branch
                        .children
                        .iter()
                        .map(|child| self.len_recursive(child))
                        .sum()
                })
                .unwrap_or(0),
        }
    }

    /// Returns true if the tree is empty.
    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    /// Returns true if the root is a leaf node.
    pub fn is_leaf_root(&self) -> bool {
        matches!(self.root, NodeRef::Leaf(_, _))
    }

    /// Returns the number of leaf nodes in the tree.
    pub fn leaf_count(&self) -> usize {
        self.leaf_count_recursive(&self.root)
    }

    /// Get the number of free leaf IDs in the arena (for testing/debugging).
    pub fn free_leaf_count(&self) -> usize {
        self.free_leaf_ids.len()
    }

    /// Get the number of free branch IDs in the arena (for testing/debugging).
    pub fn free_branch_count(&self) -> usize {
        self.free_branch_ids.len()
    }

    /// Recursively count leaf nodes with proper arena access.
    fn leaf_count_recursive(&self, node: &NodeRef<K, V>) -> usize {
        match node {
            NodeRef::Leaf(_, _) => 1, // An arena leaf is one leaf node
            NodeRef::Branch(id, _) => self
                .get_branch(*id)
                .map(|branch| {
                    branch
                        .children
                        .iter()
                        .map(|child| self.leaf_count_recursive(child))
                        .sum()
                })
                .unwrap_or(0),
        }
    }

    /// Clear all items from the tree.
    pub fn clear(&mut self) {
        // Clear the existing arena leaf at id=0
        if let Some(leaf) = self.get_leaf_mut(0) {
            leaf.keys.clear();
            leaf.values.clear();
            leaf.next = NULL_NODE;
        }
        // Reset root to point to the cleared arena leaf
        self.root = NodeRef::Leaf(0, PhantomData);
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

    /// Returns the first key-value pair in the tree.
    pub fn first(&self) -> Option<(&K, &V)> {
        self.items().next()
    }

    /// Returns the last key-value pair in the tree.
    pub fn last(&self) -> Option<(&K, &V)> {
        self.items().last()
    }

    // ============================================================================
    // ARENA-BASED ALLOCATION FOR LEAF NODES
    // ============================================================================

    /// Get the next available leaf ID (either from free list or arena length).
    fn next_leaf_id(&mut self) -> NodeId {
        self.free_leaf_ids
            .pop()
            .unwrap_or(self.leaf_arena.len() as NodeId)
    }

    /// Allocate a new leaf node in the arena and return its ID.
    pub fn allocate_leaf(&mut self, leaf: LeafNode<K, V>) -> NodeId {
        let id = self.next_leaf_id();

        // Extend arena if needed
        if id as usize >= self.leaf_arena.len() {
            self.leaf_arena.resize(id as usize + 1, None);
        }

        self.leaf_arena[id as usize] = Some(leaf);
        id
    }

    /// Deallocate a leaf node from the arena.
    pub fn deallocate_leaf(&mut self, id: NodeId) -> Option<LeafNode<K, V>> {
        self.leaf_arena.get_mut(id as usize)?.take().map(|leaf| {
            self.free_leaf_ids.push(id);
            leaf
        })
    }

    /// Get a reference to a leaf node in the arena.
    pub fn get_leaf(&self, id: NodeId) -> Option<&LeafNode<K, V>> {
        self.leaf_arena.get(id as usize)?.as_ref()
    }

    /// Get a mutable reference to a leaf node in the arena.
    pub fn get_leaf_mut(&mut self, id: NodeId) -> Option<&mut LeafNode<K, V>> {
        self.leaf_arena.get_mut(id as usize)?.as_mut()
    }

    /// Set the next pointer of a leaf node in the arena.
    pub fn set_leaf_next(&mut self, id: NodeId, next_id: NodeId) -> bool {
        self.get_leaf_mut(id)
            .map(|leaf| {
                leaf.next = next_id;
                true
            })
            .unwrap_or(false)
    }

    /// Get the next pointer of a leaf node in the arena.
    pub fn get_leaf_next(&self, id: NodeId) -> Option<NodeId> {
        self.get_leaf(id).and_then(|leaf| {
            if leaf.next == NULL_NODE {
                None
            } else {
                Some(leaf.next)
            }
        })
    }

    // ============================================================================
    // CHILD LOOKUP HELPERS (Phase 2)
    // ============================================================================

    /// Find the child index and `NodeRef` for `key` in the specified branch,
    /// returning `None` if the branch does not exist or index is out of range.
    pub fn find_child(&self, branch_id: NodeId, key: &K) -> Option<(usize, NodeRef<K, V>)> {
        self.get_branch(branch_id).and_then(|branch| {
            let idx = branch.find_child_index(key);
            branch.children.get(idx).cloned().map(|child| (idx, child))
        })
    }

    /// Mutable version of `find_child`.
    pub fn find_child_mut(&mut self, branch_id: NodeId, key: &K) -> Option<(usize, NodeRef<K, V>)> {
        self.get_branch_mut(branch_id).and_then(|branch| {
            let idx = branch.find_child_index(key);
            branch.children.get(idx).cloned().map(|child| (idx, child))
        })
    }

    // ============================================================================
    // ARENA-BASED ALLOCATION FOR BRANCH NODES
    // ============================================================================

    /// Get the next available branch ID (either from free list or arena length).
    fn next_branch_id(&mut self) -> NodeId {
        self.free_branch_ids
            .pop()
            .unwrap_or(self.branch_arena.len() as NodeId)
    }

    /// Allocate a new branch node in the arena and return its ID.
    pub fn allocate_branch(&mut self, branch: BranchNode<K, V>) -> NodeId {
        let id = self.next_branch_id();

        // Extend arena if needed
        if id as usize >= self.branch_arena.len() {
            self.branch_arena.resize(id as usize + 1, None);
        }

        self.branch_arena[id as usize] = Some(branch);
        id
    }

    /// Deallocate a branch node from the arena.
    pub fn deallocate_branch(&mut self, id: NodeId) -> Option<BranchNode<K, V>> {
        self.branch_arena
            .get_mut(id as usize)?
            .take()
            .map(|branch| {
                self.free_branch_ids.push(id);
                branch
            })
    }

    /// Get a reference to a branch node in the arena.
    pub fn get_branch(&self, id: NodeId) -> Option<&BranchNode<K, V>> {
        self.branch_arena.get(id as usize)?.as_ref()
    }

    /// Get a mutable reference to a branch node in the arena.
    pub fn get_branch_mut(&mut self, id: NodeId) -> Option<&mut BranchNode<K, V>> {
        self.branch_arena.get_mut(id as usize)?.as_mut()
    }

    // ============================================================================
    // OTHER HELPERS (TEST HELPERS)
    // ============================================================================

    /// Check if the tree maintains B+ tree invariants.
    /// Returns true if all invariants are satisfied.
    pub fn check_invariants(&self) -> bool {
        self.check_node_invariants(&self.root, None, None, true)
    }

    /// Check invariants with detailed error reporting.
    pub fn check_invariants_detailed(&self) -> Result<(), String> {
        // First check the tree structure invariants
        if !self.check_node_invariants(&self.root, None, None, true) {
            return Err("Tree invariants violated".to_string());
        }

        // Then check the linked list invariants
        self.check_linked_list_invariants()?;

        Ok(())
    }

    /// Check that the leaf linked list is properly ordered and complete.
    fn check_linked_list_invariants(&self) -> Result<(), String> {
        // Use the iterator to get all keys
        let keys: Vec<&K> = self.keys().collect();

        // Check that keys are sorted
        for i in 1..keys.len() {
            if keys[i - 1] >= keys[i] {
                return Err(format!("Iterator returned unsorted keys at index {}", i));
            }
        }

        // Verify we got the right number of keys
        if keys.len() != self.len() {
            return Err(format!(
                "Iterator returned {} keys but tree has {} items",
                keys.len(),
                self.len()
            ));
        }

        Ok(())
    }

    /// Alias for check_invariants_detailed (for test compatibility).
    pub fn validate(&self) -> Result<(), String> {
        self.check_invariants_detailed()
    }

    /// Returns all key-value pairs as a vector (for testing/debugging).
    pub fn slice(&self) -> Vec<(&K, &V)> {
        self.items().collect()
    }

    /// Returns the sizes of all leaf nodes (for testing/debugging).
    pub fn leaf_sizes(&self) -> Vec<usize> {
        let mut sizes = Vec::new();
        self.collect_leaf_sizes(&self.root, &mut sizes);
        sizes
    }

    /// Prints the node chain for debugging.
    pub fn print_node_chain(&self) {
        println!("Tree structure:");
        self.print_node(&self.root, 0);
    }

    fn collect_leaf_sizes(&self, node: &NodeRef<K, V>, sizes: &mut Vec<usize>) {
        match node {
            NodeRef::Leaf(id, _) => {
                let size = self.get_leaf(*id).map(|leaf| leaf.keys.len()).unwrap_or(0);
                sizes.push(size);
            }
            NodeRef::Branch(id, _) => {
                if let Some(branch) = self.get_branch(*id) {
                    for child in &branch.children {
                        self.collect_leaf_sizes(child, sizes);
                    }
                }
                // Missing arena branch contributes no leaf sizes (do nothing)
            }
        }
    }

    fn print_node(&self, node: &NodeRef<K, V>, depth: usize) {
        let indent = "  ".repeat(depth);
        match node {
            NodeRef::Leaf(id, _) => {
                if let Some(leaf) = self.get_leaf(*id) {
                    println!(
                        "{}Leaf[id={}, cap={}]: {} keys",
                        indent,
                        id,
                        leaf.capacity,
                        leaf.keys.len()
                    );
                } else {
                    println!("{}Leaf[id={}]: <missing>", indent, id);
                }
            }
            NodeRef::Branch(id, _) => {
                if let Some(branch) = self.get_branch(*id) {
                    println!(
                        "{}Branch[id={}, cap={}]: {} keys, {} children",
                        indent,
                        id,
                        branch.capacity,
                        branch.keys.len(),
                        branch.children.len()
                    );
                    for child in &branch.children {
                        self.print_node(child, depth + 1);
                    }
                } else {
                    println!("{}Branch[id={}]: <missing>", indent, id);
                }
            }
        }
    }

    /// Recursively check invariants for a node and its children.
    fn check_node_invariants(
        &self,
        node: &NodeRef<K, V>,
        min_key: Option<&K>,
        max_key: Option<&K>,
        _is_root: bool,
    ) -> bool {
        match node {
            NodeRef::Leaf(id, _) => {
                if let Some(leaf) = self.get_leaf(*id) {
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

                    // Check minimum occupancy
                    if !leaf.keys.is_empty() && leaf.is_underfull() {
                        // For root nodes, allow fewer keys only if it's the only node
                        if _is_root {
                            // Root leaf can have any number of keys >= 1
                            // (This is fine for leaf roots)
                        } else {
                            return false; // Non-root leaf is underfull
                        }
                    }

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
                } else {
                    false // Missing arena leaf is invalid
                }
            }
            NodeRef::Branch(id, _) => {
                if let Some(branch) = self.get_branch(*id) {
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

                    // Check minimum occupancy
                    if !branch.keys.is_empty() && branch.is_underfull() {
                        if _is_root {
                            // Root branch can have any number of keys >= 1 (as long as it has children)
                            // The only requirement is that keys.len() + 1 == children.len()
                            // This is already checked above, so root branches are always valid
                        } else {
                            return false; // Non-root branch is underfull
                        }
                    }

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
                } else {
                    false // Missing arena branch is invalid
                }
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
    /// Next leaf node in the linked list (for range queries).
    next: NodeId,
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
    // ============================================================================
    // CONSTRUCTION
    // ============================================================================

    /// Creates a new leaf node with the specified capacity.
    pub fn new(capacity: usize) -> Self {
        Self {
            capacity,
            keys: Vec::new(),
            values: Vec::new(),
            next: NULL_NODE,
        }
    }

    /// Get a reference to the keys in this leaf node.
    pub fn keys(&self) -> &Vec<K> {
        &self.keys
    }

    /// Get a reference to the values in this leaf node.
    pub fn values(&self) -> &Vec<V> {
        &self.values
    }

    /// Get a mutable reference to the values in this leaf node.
    pub fn values_mut(&mut self) -> &mut Vec<V> {
        &mut self.values
    }

    // ============================================================================
    // GET OPERATIONS
    // ============================================================================

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

    // ============================================================================
    // HELPERS FOR GET OPERATIONS
    // ============================================================================
    // (No additional helpers needed for LeafNode get operations)

    // ============================================================================
    // INSERT OPERATIONS
    // ============================================================================

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
                // Check if split is needed BEFORE inserting
                if !self.is_full() {
                    // Room to insert without splitting
                    self.insert_at_index(index, key, value);
                    // Simple insertion - no split needed
                    return InsertResult::Updated(None);
                }
                // Leaf is at capacity, split first then insert
                let mut new_leaf_data = self.split();
                let separator_key = new_leaf_data.keys[0].clone();

                // Determine which leaf should receive the new key
                if key < separator_key {
                    // Insert into the current (left) leaf
                    self.insert_at_index(index, key, value);
                } else {
                    // Insert into the new (right) leaf
                    match new_leaf_data.keys.binary_search(&key) {
                        Ok(_) => panic!("Key should not exist in new leaf"),
                        Err(new_index) => {
                            new_leaf_data.insert_at_index(new_index, key, value);
                        }
                    }
                }

                // Return the leaf data for arena allocation
                InsertResult::Split {
                    old_value: None,
                    new_node_data: SplitNodeData::Leaf(new_leaf_data),
                    separator_key,
                }
            }
        }
    }

    // ============================================================================
    // HELPERS FOR INSERT OPERATIONS
    // ============================================================================

    /// Insert a key-value pair at the specified index.
    fn insert_at_index(&mut self, index: usize, key: K, value: V) {
        self.keys.insert(index, key);
        self.values.insert(index, value);
    }

    /// Split this leaf node, returning the new right node.
    pub fn split(&mut self) -> LeafNode<K, V> {
        // For B+ trees, we need to ensure both resulting nodes have at least min_keys
        // When splitting a full node (capacity keys), we want to distribute them
        // so that both nodes have at least min_keys
        let min_keys = self.min_keys();
        let total_keys = self.keys.len();

        // Calculate split point to ensure both sides have at least min_keys
        // Left side gets min_keys, right side gets the rest
        let mid = min_keys;

        // Verify this split is valid
        debug_assert!(mid >= min_keys, "Left side would be underfull");
        debug_assert!(
            total_keys - mid >= min_keys,
            "Right side would be underfull"
        );

        // Create new leaf for right half (no Box allocation)
        let mut new_leaf = LeafNode::new(self.capacity);

        // Move right half of keys/values to new leaf
        new_leaf.keys = self.keys.split_off(mid);
        new_leaf.values = self.values.split_off(mid);

        // Maintain the linked list: new leaf inherits our next pointer
        new_leaf.next = self.next;
        // Note: The caller must update self.next to point to the new leaf's ID
        // This can't be done here as we don't know the new leaf's arena ID yet

        new_leaf
    }

    // ============================================================================
    // DELETE OPERATIONS
    // ============================================================================

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

    // ============================================================================
    // OTHER API OPERATIONS
    // ============================================================================

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

    /// Returns true if this leaf node needs to be split.
    /// We allow one extra key beyond capacity to ensure proper splitting.
    pub fn needs_split(&self) -> bool {
        self.keys.len() > self.capacity
    }

    /// Returns true if this leaf node is underfull (below minimum occupancy).
    pub fn is_underfull(&self) -> bool {
        self.keys.len() < self.min_keys()
    }

    /// Returns true if this leaf can donate a key to a sibling.
    pub fn can_donate(&self) -> bool {
        self.keys.len() > self.min_keys()
    }

    // ============================================================================
    // OTHER HELPERS
    // ============================================================================

    /// Returns the minimum number of keys this leaf should have.
    pub fn min_keys(&self) -> usize {
        // For leaf nodes, minimum is floor(capacity / 2)
        // Exception: root can have fewer keys
        self.capacity / 2
    }
}

impl<K: Ord + Clone, V: Clone> BranchNode<K, V> {
    // ============================================================================
    // CONSTRUCTION
    // ============================================================================

    /// Creates a new branch node with the specified capacity.
    pub fn new(capacity: usize) -> Self {
        Self {
            capacity,
            keys: Vec::new(),
            children: Vec::new(),
        }
    }

    // ============================================================================
    // GET OPERATIONS
    // ============================================================================

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

    // ============================================================================
    // HELPERS FOR GET OPERATIONS
    // ============================================================================

    /// Find the child index where the given key should be located.
    pub fn find_child_index(&self, key: &K) -> usize {
        // Binary search to find the appropriate child
        match self.keys.binary_search(key) {
            Ok(index) => index + 1, // Key found, go to right child
            Err(index) => index,    // Key not found, insert position is the child index
        }
    }

    // ============================================================================
    // INSERT OPERATIONS
    // ============================================================================

    /// Insert a separator key and new child into this branch node.
    /// Returns None if no split needed, or Some((new_branch_data, promoted_key)) if split occurred.
    /// The caller should handle arena allocation for the split data.
    pub fn insert_child_and_split_if_needed(
        &mut self,
        child_index: usize,
        separator_key: K,
        new_child: NodeRef<K, V>,
    ) -> Option<(BranchNode<K, V>, K)> {
        // Check if split is needed BEFORE inserting
        if self.is_full() {
            // Branch is at capacity, need to handle split
            // For branches, we MUST insert first because split promotes a key
            // With capacity=4: 4 keys → split needs 5 keys (2 left + 1 promoted + 2 right)
            self.keys.insert(child_index, separator_key);
            self.children.insert(child_index + 1, new_child);
            // Return raw data - caller should allocate through arena
            Some(self.split_data())
        } else {
            // Room to insert without splitting
            self.keys.insert(child_index, separator_key);
            self.children.insert(child_index + 1, new_child);
            None
        }
    }

    // ============================================================================
    // HELPERS FOR INSERT OPERATIONS
    // ============================================================================

    /// Split this branch node, returning the new right node and promoted key.
    /// Split this branch node, returning the new right node data and promoted key.
    /// The arena-allocating code should handle creating the actual NodeRef.
    pub fn split_data(&mut self) -> (BranchNode<K, V>, K) {
        // For branch nodes, we need to ensure both resulting nodes have at least min_keys
        // The middle key gets promoted, so we need at least min_keys on each side
        let min_keys = self.min_keys();
        let total_keys = self.keys.len();

        // For branch splits, we promote the middle key, so we need:
        // - Left side: min_keys keys
        // - Middle: 1 key (promoted)
        // - Right side: min_keys keys
        // Total needed: min_keys + 1 + min_keys
        let mid = min_keys;

        // Verify this split is valid
        debug_assert!(mid < total_keys, "Not enough keys to promote one");
        debug_assert!(mid >= min_keys, "Left side would be underfull");
        debug_assert!(
            total_keys - mid - 1 >= min_keys,
            "Right side would be underfull"
        );

        // The middle key gets promoted to the parent
        let promoted_key = self.keys[mid].clone();

        // Create new branch for right half (no Box allocation)
        let mut new_branch = BranchNode::new(self.capacity);

        // Move right half of keys to new branch (excluding the promoted key)
        new_branch.keys = self.keys.split_off(mid + 1);
        self.keys.truncate(mid); // Remove the promoted key from left side

        // Move right half of children to new branch
        new_branch.children = self.children.split_off(mid + 1);

        (new_branch, promoted_key)
    }

    // ============================================================================
    // HELPERS FOR DELETE OPERATIONS
    // ============================================================================

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

    // ============================================================================
    // OTHER API OPERATIONS
    // ============================================================================

    /// Returns true if this branch node is at capacity.
    pub fn is_full(&self) -> bool {
        self.keys.len() >= self.capacity
    }

    /// Returns true if this branch node needs to be split.
    /// We allow one extra key beyond capacity to ensure proper splitting.
    pub fn needs_split(&self) -> bool {
        self.keys.len() > self.capacity
    }

    /// Returns true if this branch node is underfull (below minimum occupancy).
    pub fn is_underfull(&self) -> bool {
        self.keys.len() < self.min_keys()
    }

    /// Returns true if this branch can donate a key to a sibling.
    pub fn can_donate(&self) -> bool {
        self.keys.len() > self.min_keys()
    }

    // ============================================================================
    // OTHER HELPERS
    // ============================================================================

    /// Returns the minimum number of keys this branch should have.
    pub fn min_keys(&self) -> usize {
        // For branch nodes, minimum is floor(capacity / 2)
        // Exception: root can have fewer keys
        self.capacity / 2
    }
}

/// Iterator over key-value pairs in the B+ tree using the leaf linked list.
pub struct ItemIterator<'a, K, V> {
    tree: &'a BPlusTreeMap<K, V>,
    current_leaf_id: Option<NodeId>,
    current_leaf_index: usize,
}

impl<'a, K: Ord + Clone, V: Clone> ItemIterator<'a, K, V> {
    fn new(tree: &'a BPlusTreeMap<K, V>) -> Self {
        // Start with the first leaf in the arena (leftmost leaf)
        let leftmost_id = if tree.leaf_arena.is_empty() || tree.leaf_arena[0].is_none() {
            None
        } else {
            Some(0)
        };

        Self {
            tree,
            current_leaf_id: leftmost_id,
            current_leaf_index: 0,
        }
    }
}

impl<'a, K: Ord + Clone, V: Clone> Iterator for ItemIterator<'a, K, V> {
    type Item = (&'a K, &'a V);

    fn next(&mut self) -> Option<Self::Item> {
        loop {
            if let Some(leaf_id) = self.current_leaf_id {
                if let Some(leaf) = self.tree.get_leaf(leaf_id) {
                    // Check if we have more items in the current leaf
                    if self.current_leaf_index < leaf.keys.len() {
                        let key = &leaf.keys[self.current_leaf_index];
                        let value = &leaf.values[self.current_leaf_index];
                        self.current_leaf_index += 1;
                        return Some((key, value));
                    } else {
                        // Move to next leaf
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
            } else {
                // No more leaves
                return None;
            }
        }
    }
}

/// Iterator over keys in the B+ tree.
pub struct KeyIterator<'a, K, V> {
    items: ItemIterator<'a, K, V>,
}

impl<'a, K: Ord + Clone, V: Clone> KeyIterator<'a, K, V> {
    fn new(tree: &'a BPlusTreeMap<K, V>) -> Self {
        Self {
            items: ItemIterator::new(tree),
        }
    }
}

impl<'a, K: Ord + Clone, V: Clone> Iterator for KeyIterator<'a, K, V> {
    type Item = &'a K;

    fn next(&mut self) -> Option<Self::Item> {
        self.items.next().map(|(k, _)| k)
    }
}

/// Iterator over values in the B+ tree.
pub struct ValueIterator<'a, K, V> {
    items: ItemIterator<'a, K, V>,
}

impl<'a, K: Ord + Clone, V: Clone> ValueIterator<'a, K, V> {
    fn new(tree: &'a BPlusTreeMap<K, V>) -> Self {
        Self {
            items: ItemIterator::new(tree),
        }
    }
}

impl<'a, K: Ord + Clone, V: Clone> Iterator for ValueIterator<'a, K, V> {
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

impl<'a, K: Ord + Clone, V: Clone> RangeIterator<'a, K, V> {
    fn new(tree: &'a BPlusTreeMap<K, V>, start_key: Option<&K>, end_key: Option<&'a K>) -> Self {
        let mut items = Vec::new();
        Self::collect_range_items(tree, &tree.root, start_key, end_key, &mut items);
        Self { items, index: 0 }
    }

    fn collect_range_items(
        tree: &'a BPlusTreeMap<K, V>,
        node: &'a NodeRef<K, V>,
        start_key: Option<&K>,
        end_key: Option<&K>,
        items: &mut Vec<(&'a K, &'a V)>,
    ) {
        match node {
            NodeRef::Leaf(id, _) => {
                if let Some(leaf) = tree.get_leaf(*id) {
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
            }
            NodeRef::Branch(id, _) => {
                if let Some(branch) = tree.get_branch(*id) {
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
                        Self::collect_range_items(tree, child, start_key, end_key, items);

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
