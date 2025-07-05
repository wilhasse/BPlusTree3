//! B+ Tree implementation in Rust with dict-like API.
//!
//! This module provides a B+ tree data structure with a dictionary-like interface,
//! supporting efficient insertion, deletion, lookup, and range queries.

use std::fmt::Debug;
use std::marker::PhantomData;
use std::ops::{Bound, RangeBounds};

// Import our new modules
mod arena;
mod macros;

pub use arena::{Arena, ArenaStats, NodeId as ArenaNodeId, NULL_NODE as ARENA_NULL_NODE};

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
    /// Internal data structure integrity violation.
    DataIntegrityError(String),
    /// Arena operation failed.
    ArenaError(String),
    /// Node operation failed.
    NodeError(String),
    /// Tree corruption detected.
    CorruptedTree(String),
    /// Invalid tree state.
    InvalidState(String),
    /// Memory allocation failed.
    AllocationError(String),
}

impl BPlusTreeError {
    /// Create an InvalidCapacity error with context
    pub fn invalid_capacity(capacity: usize, min_required: usize) -> Self {
        Self::InvalidCapacity(format!(
            "Capacity {} is invalid (minimum required: {})",
            capacity, min_required
        ))
    }

    /// Create a DataIntegrityError with context
    pub fn data_integrity(context: &str, details: &str) -> Self {
        Self::DataIntegrityError(format!("{}: {}", context, details))
    }

    /// Create an ArenaError with context
    pub fn arena_error(operation: &str, details: &str) -> Self {
        Self::ArenaError(format!("{} failed: {}", operation, details))
    }

    /// Create a NodeError with context
    pub fn node_error(node_type: &str, node_id: u32, details: &str) -> Self {
        Self::NodeError(format!("{} node {}: {}", node_type, node_id, details))
    }

    /// Create a CorruptedTree error with context
    pub fn corrupted_tree(component: &str, details: &str) -> Self {
        Self::CorruptedTree(format!("{} corruption: {}", component, details))
    }

    /// Create an InvalidState error with context
    pub fn invalid_state(operation: &str, state: &str) -> Self {
        Self::InvalidState(format!("Cannot {} in state: {}", operation, state))
    }

    /// Create an AllocationError with context
    pub fn allocation_error(resource: &str, reason: &str) -> Self {
        Self::AllocationError(format!("Failed to allocate {}: {}", resource, reason))
    }
}

impl std::fmt::Display for BPlusTreeError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            BPlusTreeError::KeyNotFound => write!(f, "Key not found in tree"),
            BPlusTreeError::InvalidCapacity(msg) => write!(f, "Invalid capacity: {}", msg),
            BPlusTreeError::DataIntegrityError(msg) => write!(f, "Data integrity error: {}", msg),
            BPlusTreeError::ArenaError(msg) => write!(f, "Arena error: {}", msg),
            BPlusTreeError::NodeError(msg) => write!(f, "Node error: {}", msg),
            BPlusTreeError::CorruptedTree(msg) => write!(f, "Corrupted tree: {}", msg),
            BPlusTreeError::InvalidState(msg) => write!(f, "Invalid state: {}", msg),
            BPlusTreeError::AllocationError(msg) => write!(f, "Allocation error: {}", msg),
        }
    }
}

impl std::error::Error for BPlusTreeError {}

/// Internal result type for tree operations
type TreeResult<T> = Result<T, BPlusTreeError>;

/// Public result type for tree operations that may fail
pub type BTreeResult<T> = Result<T, BPlusTreeError>;

/// Result type for key lookup operations
pub type KeyResult<T> = Result<T, BPlusTreeError>;

/// Result type for tree modification operations
pub type ModifyResult<T> = Result<T, BPlusTreeError>;

/// Result type for tree construction and validation
pub type InitResult<T> = Result<T, BPlusTreeError>;

/// Result extension trait for improved error handling
pub trait BTreeResultExt<T> {
    /// Convert to a BTreeResult with additional context
    fn with_context(self, context: &str) -> BTreeResult<T>;

    /// Convert to a BTreeResult with operation context
    fn with_operation(self, operation: &str) -> BTreeResult<T>;

    /// Log error and continue with default value
    fn or_default_with_log(self) -> T
    where
        T: Default;
}

impl<T> BTreeResultExt<T> for Result<T, BPlusTreeError> {
    fn with_context(self, context: &str) -> BTreeResult<T> {
        self.map_err(|e| match e {
            BPlusTreeError::KeyNotFound => BPlusTreeError::KeyNotFound,
            BPlusTreeError::InvalidCapacity(msg) => {
                BPlusTreeError::InvalidCapacity(format!("{}: {}", context, msg))
            }
            BPlusTreeError::DataIntegrityError(msg) => {
                BPlusTreeError::data_integrity(context, &msg)
            }
            BPlusTreeError::ArenaError(msg) => BPlusTreeError::arena_error(context, &msg),
            BPlusTreeError::NodeError(msg) => {
                BPlusTreeError::NodeError(format!("{}: {}", context, msg))
            }
            BPlusTreeError::CorruptedTree(msg) => BPlusTreeError::corrupted_tree(context, &msg),
            BPlusTreeError::InvalidState(msg) => BPlusTreeError::invalid_state(context, &msg),
            BPlusTreeError::AllocationError(msg) => BPlusTreeError::allocation_error(context, &msg),
        })
    }

    fn with_operation(self, operation: &str) -> BTreeResult<T> {
        self.with_context(&format!("Operation {}", operation))
    }

    fn or_default_with_log(self) -> T
    where
        T: Default,
    {
        match self {
            Ok(value) => value,
            Err(e) => {
                eprintln!("Warning: B+ Tree operation failed, using default: {}", e);
                T::default()
            }
        }
    }
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
/// use bplustree::BPlusTreeMap;
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
/// let range: Vec<_> = tree.items_range(Some(&1), Some(&3)).collect();
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
    /// Number of key-value pairs in the tree.
    len: usize,

    // Enhanced arena-based allocation using generic Arena<T>
    /// Arena storage for leaf nodes.
    leaf_arena: Arena<LeafNode<K, V>>,
    /// Arena storage for branch nodes.
    branch_arena: Arena<BranchNode<K, V>>,
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
    /// Internal error occurred during insertion.
    Error(BPlusTreeError),
}

/// Result of a removal operation on a node.
pub enum RemoveResult<V> {
    /// Removal completed. Contains the removed value if key existed.
    /// The bool indicates if this node is now underfull and needs rebalancing.
    Updated(Option<V>, bool),
}

impl<K: Ord + Clone + std::fmt::Debug, V: Clone + std::fmt::Debug> BPlusTreeMap<K, V> {
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
    /// use bplustree::BPlusTreeMap;
    ///
    /// let tree = BPlusTreeMap::<i32, String>::new(16).unwrap();
    /// assert!(tree.is_empty());
    /// ```
    pub fn new(capacity: usize) -> InitResult<Self> {
        if capacity < MIN_CAPACITY {
            return Err(BPlusTreeError::invalid_capacity(capacity, MIN_CAPACITY));
        }

        // Initialize arena with the first leaf at id=0
        let mut leaf_arena = Arena::new();
        let root_id = leaf_arena.allocate(LeafNode::new(capacity));

        // Initialize branch arena (starts empty)
        let branch_arena = Arena::new();

        Ok(Self {
            capacity,
            root: NodeRef::Leaf(root_id, PhantomData),
            len: 0,
            leaf_arena,
            branch_arena,
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
    /// use bplustree::BPlusTreeMap;
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
    pub fn get_item(&self, key: &K) -> KeyResult<&V> {
        self.get(key).ok_or(BPlusTreeError::KeyNotFound)
    }

    /// Get a mutable reference to the value for a key.
    pub fn get_mut(&mut self, key: &K) -> Option<&mut V> {
        let root = self.root.clone();
        self.get_mut_recursive(&root, key)
    }

    // ============================================================================
    // HELPERS FOR GET OPERATIONS
    // ============================================================================

    fn get_recursive<'a>(&'a self, node: &'a NodeRef<K, V>, key: &K) -> Option<&'a V> {
        match node {
            NodeRef::Leaf(id, _) => self.get_leaf(*id).and_then(|leaf| leaf.get(key)),
            NodeRef::Branch(id, _) => self
                .get_branch(*id)
                .and_then(|branch| branch.get_child(key))
                .and_then(|child| self.get_recursive(child, key)),
        }
    }

    /// Get mutable reference recursively
    fn get_mut_recursive(&mut self, node: &NodeRef<K, V>, key: &K) -> Option<&mut V> {
        match node {
            NodeRef::Leaf(id, _) => self.get_leaf_mut(*id).and_then(|leaf| leaf.get_mut(key)),
            NodeRef::Branch(id, _) => {
                let (_child_index, child_ref) = self.get_child_for_key(*id, key)?;
                self.get_mut_recursive(&child_ref, key)
            }
        }
    }

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

        match (
            branch.children.get(child_index),
            branch.children.get(sibling_index),
        ) {
            (Some(NodeRef::Branch(_, _)), Some(NodeRef::Branch(_, _))) => {
                branch.children.get(sibling_index).cloned()
            }
            _ => None,
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
    /// use bplustree::BPlusTreeMap;
    ///
    /// let mut tree = BPlusTreeMap::new(16).unwrap();
    /// tree.insert(1, "first");
    /// assert_eq!(tree.insert(1, "second"), Some("first"));
    /// ```
    pub fn insert(&mut self, key: K, value: V) -> Option<V> {
        // Use insert_recursive to handle the insertion
        let result = self.insert_recursive(&self.root.clone(), key.clone(), value);

        match result {
            InsertResult::Updated(old_value) => {
                // If no old value, this was a new insertion
                if old_value.is_none() {
                    self.len += 1;
                }
                old_value
            }
            InsertResult::Error(_error) => {
                // Log the error but maintain API compatibility
                // This should never happen with correct split logic
                eprintln!("BPlusTree internal error during insert - data integrity violation");
                None
            }
            InsertResult::Split {
                old_value,
                new_node_data,
                separator_key,
            } => {
                // If no old value, this was a new insertion
                if old_value.is_none() {
                    self.len += 1;
                }

                // Root split - need to create a new root
                let new_node_ref = match new_node_data {
                    SplitNodeData::Leaf(new_leaf_data) => {
                        let new_id = self.allocate_leaf(new_leaf_data);

                        // Update linked list pointers for root leaf split
                        if let Some(leaf) = matches!(&self.root, NodeRef::Leaf(_, _))
                            .then(|| self.root.id())
                            .and_then(|original_id| self.get_leaf_mut(original_id))
                        {
                            leaf.next = new_id;
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
        // Use a dummy NodeRef with NULL_NODE to avoid arena allocation
        let dummy = NodeRef::Leaf(NULL_NODE, PhantomData);
        let old_root = std::mem::replace(&mut self.root, dummy);

        new_root.children.push(old_root);
        new_root.children.push(new_node);

        new_root
    }

    /// Recursively insert a key with proper arena access.
    fn insert_recursive(&mut self, node: &NodeRef<K, V>, key: K, value: V) -> InsertResult<K, V> {
        match node {
            NodeRef::Leaf(id, _) => self
                .get_leaf_mut(*id)
                .map_or(InsertResult::Updated(None), |leaf| leaf.insert(key, value)),
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
                    InsertResult::Error(error) => InsertResult::Error(error),
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
                                // Update linked list pointers for leaf splits using Option combinators
                                if let NodeRef::Leaf(original_id, _) = child_ref {
                                    self.get_leaf_mut(original_id)
                                        .map(|original_leaf| original_leaf.next = new_id);
                                }

                                NodeRef::Leaf(new_id, PhantomData)
                            }
                            SplitNodeData::Branch(new_branch_data) => {
                                let new_id = self.allocate_branch(new_branch_data);
                                NodeRef::Branch(new_id, PhantomData)
                            }
                        };

                        // Insert into this branch
                        match self.get_branch_mut(id).and_then(|branch| {
                            branch.insert_child_and_split_if_needed(
                                child_index,
                                separator_key,
                                new_node,
                            )
                        }) {
                            Some((new_branch_data, promoted_key)) => {
                                // This branch split too - return raw branch data
                                InsertResult::Split {
                                    old_value,
                                    new_node_data: SplitNodeData::Branch(new_branch_data),
                                    separator_key: promoted_key,
                                }
                            }
                            None => {
                                // No split needed or branch not found
                                InsertResult::Updated(old_value)
                            }
                        }
                    }
                }
            }
        }
    }

    // ============================================================================
    // DELETE OPERATIONS
    // ============================================================================

    /// Remove a key from the tree and return its associated value.
    ///
    /// # Arguments
    /// * `key` - The key to remove from the tree
    ///
    /// # Returns
    /// * `Some(value)` - The value that was associated with the key
    /// * `None` - If the key was not present in the tree
    ///
    /// # Examples
    /// ```
    /// use bplustree::BPlusTreeMap;
    ///
    /// let mut tree = BPlusTreeMap::new(4).unwrap();
    /// tree.insert(1, "one");
    /// tree.insert(2, "two");
    ///
    /// assert_eq!(tree.remove(&1), Some("one"));
    /// assert_eq!(tree.remove(&1), None); // Key no longer exists
    /// assert_eq!(tree.len(), 1);
    /// ```
    ///
    /// # Performance
    /// * Time complexity: O(log n) where n is the number of keys
    /// * May trigger node rebalancing or merging operations
    /// * Maintains all B+ tree invariants after removal
    ///
    /// # Panics
    /// Never panics - all operations are memory safe
    pub fn remove(&mut self, key: &K) -> Option<V> {
        // Use remove_recursive to handle the removal
        let result = self.remove_recursive(&self.root.clone(), key);

        match result {
            RemoveResult::Updated(removed_value, _root_became_underfull) => {
                // Check if root needs collapsing after removal
                if removed_value.is_some() {
                    if self.len > 0 {
                        self.len -= 1;
                    }
                    self.collapse_root_if_needed();
                }
                removed_value
            }
        }
    }

    /// Remove a key from the tree, returning an error if the key doesn't exist.
    /// This is equivalent to Python's `del tree[key]`.
    pub fn remove_item(&mut self, key: &K) -> ModifyResult<V> {
        self.remove(key).ok_or(BPlusTreeError::KeyNotFound)
    }

    /// Try to get a value, returning detailed error context on failure
    pub fn try_get(&self, key: &K) -> KeyResult<&V> {
        use crate::BTreeResultExt;
        self.get(key)
            .ok_or(BPlusTreeError::KeyNotFound)
            .with_context("Key lookup operation")
    }

    /// Insert with comprehensive error handling and rollback on failure
    pub fn try_insert(&mut self, key: K, value: V) -> ModifyResult<Option<V>>
    where
        K: Clone,
        V: Clone,
    {
        // Validate tree state before insertion
        if let Err(e) = self.check_invariants_detailed() {
            return Err(BPlusTreeError::DataIntegrityError(e));
        }

        let old_value = self.insert(key, value);

        // Validate tree state after insertion
        if let Err(e) = self.check_invariants_detailed() {
            return Err(BPlusTreeError::DataIntegrityError(e));
        }

        Ok(old_value)
    }

    /// Remove with comprehensive error handling
    pub fn try_remove(&mut self, key: &K) -> ModifyResult<V> {
        // Validate tree state before removal
        if let Err(e) = self.check_invariants_detailed() {
            return Err(BPlusTreeError::DataIntegrityError(e));
        }

        let value = self.remove(key).ok_or(BPlusTreeError::KeyNotFound)?;

        // Validate tree state after removal
        if let Err(e) = self.check_invariants_detailed() {
            return Err(BPlusTreeError::DataIntegrityError(e));
        }

        Ok(value)
    }

    /// Batch insert operations with rollback on any failure
    pub fn batch_insert(&mut self, items: Vec<(K, V)>) -> ModifyResult<Vec<Option<V>>>
    where
        K: Clone,
        V: Clone,
    {
        let mut results = Vec::new();
        let mut inserted_keys = Vec::new();

        for (key, value) in items {
            match self.try_insert(key.clone(), value) {
                Ok(old_value) => {
                    results.push(old_value);
                    inserted_keys.push(key);
                }
                Err(e) => {
                    // Rollback all successful insertions
                    for rollback_key in inserted_keys {
                        self.remove(&rollback_key);
                    }
                    return Err(e);
                }
            }
        }

        Ok(results)
    }

    /// Get multiple keys with detailed error reporting
    pub fn get_many(&self, keys: &[K]) -> BTreeResult<Vec<&V>> {
        let mut values = Vec::new();

        for (_index, key) in keys.iter().enumerate() {
            match self.get(key) {
                Some(value) => values.push(value),
                None => {
                    return Err(BPlusTreeError::KeyNotFound);
                }
            }
        }

        Ok(values)
    }

    /// Check if tree is in a valid state for operations
    pub fn validate_for_operation(&self, operation: &str) -> BTreeResult<()> {
        self.check_invariants_detailed().map_err(|e| {
            BPlusTreeError::DataIntegrityError(format!("Validation for {}: {}", operation, e))
        })
    }

    // ============================================================================
    // HELPERS FOR DELETE OPERATIONS
    // ============================================================================

    /// Recursively remove a key with proper arena access.
    fn remove_recursive(&mut self, node: &NodeRef<K, V>, key: &K) -> RemoveResult<V> {
        match node {
            NodeRef::Leaf(id, _) => {
                self.get_leaf_mut(*id)
                    .map_or(RemoveResult::Updated(None, false), |leaf| {
                        let removed_value = leaf.remove(key);
                        let is_underfull = leaf.is_underfull();
                        RemoveResult::Updated(removed_value, is_underfull)
                    })
            }
            NodeRef::Branch(id, _) => {
                let id = *id;

                // First get child info without mutable borrow
                let (child_index, child_ref) = match self.get_child_for_key(id, key) {
                    Some(info) => info,
                    None => return RemoveResult::Updated(None, false),
                };

                // Recursively remove
                let child_result = self.remove_recursive(&child_ref, key);

                // Handle the result
                match child_result {
                    RemoveResult::Updated(removed_value, child_became_underfull) => {
                        let mut current_node_became_underfull = false;
                        // If child became underfull, try to rebalance
                        if removed_value.is_some() && child_became_underfull {
                            // rebalance_child returns true if the branch_id (current node) becomes underfull
                            current_node_became_underfull = self.rebalance_child(id, child_index);
                        }

                        RemoveResult::Updated(removed_value, current_node_became_underfull)
                    }
                }
            }
        }
    }
    /// Rebalance an underfull child in an arena branch
    /// Returns true if the parent branch node became underfull after rebalancing
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
    /// Returns true if the parent branch node became underfull after rebalancing
    fn rebalance_leaf_child(
        &mut self,
        branch_id: NodeId,
        child_index: usize,
        has_left_sibling: bool,
        has_right_sibling: bool,
    ) -> bool {
        let (left_can_donate, right_can_donate) = match self.get_branch(branch_id) {
            Some(branch) => {
                let left_can_donate = if has_left_sibling && child_index > 0 {
                    branch
                        .children
                        .get(child_index - 1)
                        .map(|sibling| self.can_node_donate(sibling))
                        .unwrap_or(false)
                } else {
                    false
                };

                let right_can_donate = if has_right_sibling {
                    branch
                        .children
                        .get(child_index + 1)
                        .map(|sibling| self.can_node_donate(sibling))
                        .unwrap_or(false)
                } else {
                    false
                };

                (left_can_donate, right_can_donate)
            }
            None => return false,
        };

        let _child_still_exists = if left_can_donate {
            self.borrow_from_left_leaf(branch_id, child_index)
        } else if right_can_donate {
            self.borrow_from_right_leaf(branch_id, child_index)
        } else if has_left_sibling {
            self.merge_with_left_leaf(branch_id, child_index)
        } else if has_right_sibling {
            self.merge_with_right_leaf(branch_id, child_index)
        } else {
            false // No siblings to merge with
        };

        // After rebalancing, check if the current branch node (parent) is now underfull
        self.is_node_underfull(&NodeRef::Branch(branch_id, PhantomData))
    }

    /// Rebalance an underfull branch child
    /// Returns true if the parent branch node became underfull after rebalancing
    fn rebalance_branch_child(
        &mut self,
        branch_id: NodeId,
        child_index: usize,
        has_left_sibling: bool,
        has_right_sibling: bool,
    ) -> bool {
        // Get parent branch once and cache sibling donation and merge capabilities
        let (left_can_donate, right_can_donate, left_can_merge, right_can_merge) =
            match self.get_branch(branch_id) {
                Some(branch) => {
                    let left_can_donate = if has_left_sibling {
                        self.get_branch_sibling(branch_id, child_index, true)
                            .map(|sibling| self.can_node_donate(&sibling))
                            .unwrap_or(false)
                    } else {
                        false
                    };

                    let right_can_donate = if has_right_sibling {
                        self.get_branch_sibling(branch_id, child_index, false)
                            .map(|sibling| self.can_node_donate(&sibling))
                            .unwrap_or(false)
                    } else {
                        false
                    };

                    let left_can_merge = if has_left_sibling {
                        if let (NodeRef::Branch(left_id, _), NodeRef::Branch(child_id, _)) = (
                            &branch.children[child_index - 1],
                            &branch.children[child_index],
                        ) {
                            self.get_branch(*left_id)
                                .zip(self.get_branch(*child_id))
                                .map(|(left, child)| {
                                    left.keys.len() + 1 + child.keys.len() <= self.capacity
                                })
                                .unwrap_or(false)
                        } else {
                            false
                        }
                    } else {
                        false
                    };

                    let right_can_merge = if has_right_sibling {
                        if let (NodeRef::Branch(child_id, _), NodeRef::Branch(right_id, _)) = (
                            &branch.children[child_index],
                            &branch.children[child_index + 1],
                        ) {
                            self.get_branch(*child_id)
                                .zip(self.get_branch(*right_id))
                                .map(|(child, right)| {
                                    child.keys.len() + 1 + right.keys.len() <= self.capacity
                                })
                                .unwrap_or(false)
                        } else {
                            false
                        }
                    } else {
                        false
                    };

                    (
                        left_can_donate,
                        right_can_donate,
                        left_can_merge,
                        right_can_merge,
                    )
                }
                None => return false,
            };

        let _child_still_exists = if left_can_donate {
            self.borrow_from_left_branch(branch_id, child_index)
        } else if right_can_donate {
            self.borrow_from_right_branch(branch_id, child_index)
        } else if left_can_merge {
            self.merge_with_left_branch(branch_id, child_index)
        } else if right_can_merge {
            self.merge_with_right_branch(branch_id, child_index)
        } else {
            true // Cannot borrow or merge - leave the node underfull
        };

        // After rebalancing, check if the current branch node (parent) is now underfull
        self.is_node_underfull(&NodeRef::Branch(branch_id, PhantomData))
    }

    /// Merge branch with left sibling
    fn merge_with_left_branch(&mut self, parent_id: NodeId, child_index: usize) -> bool {
        // Get the branch IDs and collect all needed info from parent in one access
        let (left_id, child_id, separator_key) = match self.get_branch(parent_id) {
            Some(branch) => {
                match (
                    &branch.children[child_index - 1],
                    &branch.children[child_index],
                ) {
                    (NodeRef::Branch(left, _), NodeRef::Branch(child, _)) => {
                        (*left, *child, branch.keys[child_index - 1].clone())
                    }
                    _ => return false,
                }
            }
            None => return false,
        };

        // Extract all content from child
        let mut child_branch = match self.get_branch_mut(child_id) {
            Some(child_branch) => {
                let mut extracted = BranchNode::new(child_branch.capacity);
                std::mem::swap(&mut extracted.keys, &mut child_branch.keys);
                std::mem::swap(&mut extracted.children, &mut child_branch.children);
                extracted
            }
            None => return false,
        };

        // Merge into left branch - use early return for cleaner flow
        let Some(left_branch) = self.get_branch_mut(left_id) else {
            return false;
        };
        left_branch.merge_from(separator_key, &mut child_branch);

        // Remove child from parent (second and final parent access)
        let Some(parent) = self.get_branch_mut(parent_id) else {
            return false;
        };
        parent.children.remove(child_index);
        parent.keys.remove(child_index - 1);

        // Deallocate the merged child
        self.deallocate_branch(child_id);

        // Update all separator keys in the parent to reflect the new structure
        self.fix_separator_keys(parent_id);

        // Check if the parent branch is now underfull
        self.is_node_underfull(&NodeRef::Branch(parent_id, PhantomData))
    }

    /// Merge branch with right sibling
    fn merge_with_right_branch(&mut self, parent_id: NodeId, child_index: usize) -> bool {
        // Get the branch IDs and collect all needed info from parent in one access
        let (child_id, right_id, separator_key) = match self.get_branch(parent_id) {
            Some(branch) => {
                match (
                    &branch.children[child_index],
                    &branch.children[child_index + 1],
                ) {
                    (NodeRef::Branch(child, _), NodeRef::Branch(right, _)) => {
                        (*child, *right, branch.keys[child_index].clone())
                    }
                    _ => return false,
                }
            }
            None => return false,
        };

        // Extract all content from right sibling
        let mut right_branch = match self.get_branch_mut(right_id) {
            Some(right_branch) => {
                let mut extracted = BranchNode::new(right_branch.capacity);
                std::mem::swap(&mut extracted.keys, &mut right_branch.keys);
                std::mem::swap(&mut extracted.children, &mut right_branch.children);
                extracted
            }
            None => return false,
        };

        // Merge into child branch - use early return for cleaner flow
        let Some(child_branch) = self.get_branch_mut(child_id) else {
            return false;
        };
        child_branch.merge_from(separator_key, &mut right_branch);

        // Remove right from parent (second and final parent access)
        let Some(parent) = self.get_branch_mut(parent_id) else {
            return false;
        };
        parent.children.remove(child_index + 1);
        parent.keys.remove(child_index);

        // Deallocate the merged right sibling
        self.deallocate_branch(right_id);

        // Update all separator keys in the parent to reflect the new structure
        self.fix_separator_keys(parent_id);

        // Check if the parent branch is now underfull
        self.is_node_underfull(&NodeRef::Branch(parent_id, PhantomData))
    }

    /// Fix all separator keys in a branch node to correctly reflect child boundaries
    fn fix_separator_keys(&mut self, branch_id: NodeId) {
        // Get the children first to avoid borrowing conflicts
        let children = match self.get_branch(branch_id) {
            Some(branch) => branch.children.clone(),
            None => return,
        };

        // Calculate the correct separator keys
        let mut correct_keys = Vec::new();
        for i in 1..children.len() {
            if let Some(min_key) = self.get_minimum_key_in_subtree(&children[i]) {
                correct_keys.push(min_key);
            }
        }

        // Update the branch with correct separator keys
        if let Some(branch) = self.get_branch_mut(branch_id) {
            branch.keys = correct_keys;
        }
    }

    /// Get the minimum key in a subtree rooted at the given node
    fn get_minimum_key_in_subtree(&self, node: &NodeRef<K, V>) -> Option<K> {
        match node {
            NodeRef::Leaf(leaf_id, _) => {
                self.get_leaf(*leaf_id)?.keys.first().cloned()
            }
            NodeRef::Branch(branch_id, _) => {
                let branch = self.get_branch(*branch_id)?;
                let first_child = branch.children.first()?;
                self.get_minimum_key_in_subtree(first_child)
            }
        }
    }


    /// Borrow from left sibling branch
    fn borrow_from_left_branch(&mut self, parent_id: NodeId, child_index: usize) -> bool {
        // Get the branch IDs and collect all needed info from parent in one access
        let (left_id, child_id, separator_key) = match self.get_branch(parent_id) {
            Some(branch) => {
                match (
                    &branch.children[child_index - 1],
                    &branch.children[child_index],
                ) {
                    (NodeRef::Branch(left, _), NodeRef::Branch(child, _)) => {
                        (*left, *child, branch.keys[child_index - 1].clone())
                    }
                    _ => return false,
                }
            }
            None => return false,
        };

        // Borrow from left branch
        let (moved_key, moved_child) = match self.get_branch_mut(left_id) {
            Some(left_branch) => match left_branch.borrow_last() {
                Some(result) => result,
                None => return false,
            },
            None => return false,
        };

        // Accept into child branch - use early return for cleaner flow
        let Some(child_branch) = self.get_branch_mut(child_id) else {
            return false;
        };
        let new_separator = child_branch.accept_from_left(separator_key, moved_key, moved_child);

        // Update separator in parent (second and final parent access)
        let Some(parent) = self.get_branch_mut(parent_id) else {
            return false;
        };
        parent.keys[child_index - 1] = new_separator;

        // Ensure all separator keys are correct after borrowing
        self.fix_separator_keys(parent_id);
        // EGREGIOUS HACK: Also fix separator keys in the child that received the new subtree
        self.fix_separator_keys(child_id);

        true
    }

    /// Borrow from right sibling branch
    fn borrow_from_right_branch(&mut self, parent_id: NodeId, child_index: usize) -> bool {
        // Get the branch IDs and collect all needed info from parent in one access
        let (child_id, right_id, separator_key) = match self.get_branch(parent_id) {
            Some(branch) => {
                match (
                    &branch.children[child_index],
                    &branch.children[child_index + 1],
                ) {
                    (NodeRef::Branch(child, _), NodeRef::Branch(right, _)) => {
                        (*child, *right, branch.keys[child_index].clone())
                    }
                    _ => return false,
                }
            }
            None => return false,
        };

        // Borrow from right branch
        let (moved_key, moved_child) = match self.get_branch_mut(right_id) {
            Some(right_branch) => match right_branch.borrow_first() {
                Some(result) => result,
                None => return false,
            },
            None => return false,
        };

        // Accept into child branch - use early return for cleaner flow
        let Some(child_branch) = self.get_branch_mut(child_id) else {
            return false;
        };
        let new_separator = child_branch.accept_from_right(separator_key, moved_key, moved_child);

        // Update separator in parent (second and final parent access)
        let Some(parent) = self.get_branch_mut(parent_id) else {
            return false;
        };
        parent.keys[child_index] = new_separator;

        // Ensure all separator keys are correct after borrowing
        self.fix_separator_keys(parent_id);
        // EGREGIOUS HACK: Also fix separator keys in the child that received the new subtree
        self.fix_separator_keys(child_id);

        true
    }

    /// Borrow from left sibling leaf
    fn borrow_from_left_leaf(&mut self, branch_id: NodeId, child_index: usize) -> bool {
        // Extract leaf IDs from parent in one access (inlined get_adjacent_leaf_ids logic)
        let (left_id, child_id) = match self.get_branch(branch_id) {
            Some(branch) => {
                match (
                    branch.children.get(child_index - 1),
                    branch.children.get(child_index),
                ) {
                    (Some(NodeRef::Leaf(left_id, _)), Some(NodeRef::Leaf(child_id, _))) => {
                        (*left_id, *child_id)
                    }
                    _ => return false,
                }
            }
            None => return false,
        };

        // Borrow from left leaf
        let (key, value) = match self.get_leaf_mut(left_id) {
            Some(left_leaf) => match left_leaf.borrow_last() {
                Some(result) => result,
                None => return false,
            },
            None => return false,
        };

        // Accept into child leaf - use early return for cleaner flow
        let Some(child_leaf) = self.get_leaf_mut(child_id) else {
            return false;
        };
        child_leaf.accept_from_left(key.clone(), value);

        // Update separator in parent (new first key of child, second parent access)
        let new_separator = self
            .get_leaf(child_id)
            .and_then(|child_leaf| child_leaf.keys.first().cloned());

        // Use Option combinators for nested conditional update
        new_separator
            .zip(self.get_branch_mut(branch_id))
            .map(|(sep, branch)| branch.keys[child_index - 1] = sep);

        // Ensure all separator keys are correct after borrowing
        self.fix_separator_keys(branch_id);

        true
    }

    /// Borrow from right sibling leaf
    fn borrow_from_right_leaf(&mut self, branch_id: NodeId, child_index: usize) -> bool {
        // Extract leaf IDs from parent in one access (inlined get_adjacent_leaf_ids logic)
        let (child_id, right_id) = match self.get_branch(branch_id) {
            Some(branch) => {
                match (
                    branch.children.get(child_index),
                    branch.children.get(child_index + 1),
                ) {
                    (Some(NodeRef::Leaf(child_id, _)), Some(NodeRef::Leaf(right_id, _))) => {
                        (*child_id, *right_id)
                    }
                    _ => return false,
                }
            }
            None => return false,
        };

        // Borrow from right leaf
        let (key, value) = match self.get_leaf_mut(right_id) {
            Some(right_leaf) => match right_leaf.borrow_first() {
                Some(result) => result,
                None => return false,
            },
            None => return false,
        };

        // Accept into child leaf - use early return for cleaner flow
        let Some(child_leaf) = self.get_leaf_mut(child_id) else {
            return false;
        };
        child_leaf.accept_from_right(key, value);

        // Update separator in parent (new first key of right sibling, second parent access)
        let new_separator = self
            .get_leaf(right_id)
            .and_then(|right_leaf| right_leaf.keys.first().cloned());

        // Use Option combinators for nested conditional update
        let Some(parent) = self.get_branch_mut(branch_id) else {
            return false;
        };
        if let Some(sep) = new_separator {
            parent.keys[child_index] = sep;
        }

        // Ensure all separator keys are correct after borrowing
        self.fix_separator_keys(branch_id);

        true
    }

    /// Merge with left sibling leaf
    fn merge_with_left_leaf(&mut self, branch_id: NodeId, child_index: usize) -> bool {
        let capacity = self.capacity;
        // Extract leaf IDs from parent in one access (inlined get_adjacent_leaf_ids logic)
        let (left_id, child_id) = match self.get_branch(branch_id) {
            Some(branch) => {
                match (
                    branch.children.get(child_index - 1),
                    branch.children.get(child_index),
                ) {
                    (Some(NodeRef::Leaf(left_id, _)), Some(NodeRef::Leaf(child_id, _))) => {
                        (*left_id, *child_id)
                    }
                    _ => return false,
                }
            }
            None => return false,
        };

        // Extract all content from child
        let (mut child_keys, mut child_values, child_next) = match self.get_leaf_mut(child_id) {
            Some(child_leaf) => child_leaf.extract_all(),
            None => return false,
        };

        // Merge into left leaf and update linked list - use early return for cleaner flow
        let Some(left_leaf) = self.get_leaf_mut(left_id) else {
            return false;
        };

        // Check if merge is possible without exceeding capacity
        if left_leaf.len() + child_keys.len() > capacity {
            return false;
        }

        left_leaf.keys.append(&mut child_keys);
        left_leaf.values.append(&mut child_values);
        // Fix: Ensure proper linked list maintenance
        left_leaf.next = child_next;

        // Remove child from parent (second and final parent access)
        let Some(branch) = self.get_branch_mut(branch_id) else {
            return false;
        };
        // Standard B+ tree merge: remove child and its separator key
        branch.children.remove(child_index);
        branch.keys.remove(child_index - 1);

        // Deallocate the merged child
        self.deallocate_leaf(child_id);

        // EGREGIOUS HACK: Fix separator keys after merge
        self.fix_separator_keys(branch_id);

        false // Child was merged away
    }

    /// Merge with right sibling leaf
    fn merge_with_right_leaf(&mut self, branch_id: NodeId, child_index: usize) -> bool {
        let capacity = self.capacity;
        // Extract leaf IDs from parent in one access (inlined get_adjacent_leaf_ids logic)
        let (child_id, right_id) = match self.get_branch(branch_id) {
            Some(branch) => {
                match (
                    branch.children.get(child_index),
                    branch.children.get(child_index + 1),
                ) {
                    (Some(NodeRef::Leaf(child_id, _)), Some(NodeRef::Leaf(right_id, _))) => {
                        (*child_id, *right_id)
                    }
                    _ => return false,
                }
            }
            None => return false,
        };

        // Extract all content from right sibling
        let (mut right_keys, mut right_values, right_next) = match self.get_leaf_mut(right_id) {
            Some(right_leaf) => right_leaf.extract_all(),
            None => return false,
        };

        // Merge into child leaf and update linked list - use early return for cleaner flow
        let Some(child_leaf) = self.get_leaf_mut(child_id) else {
            return false;
        };

        // Check if merge is possible without exceeding capacity
        if child_leaf.len() + right_keys.len() > capacity {
            return false;
        }

        child_leaf.keys.append(&mut right_keys);
        child_leaf.values.append(&mut right_values);
        child_leaf.next = right_next;

        // Remove right from parent (second and final parent access)
        let Some(branch) = self.get_branch_mut(branch_id) else {
            return false;
        };
        // Standard B+ tree merge: remove right child and separator key at child_index
        branch.children.remove(child_index + 1);
        branch.keys.remove(child_index);

        // Deallocate the merged right sibling
        self.deallocate_leaf(right_id);

        // EGREGIOUS HACK: Fix separator keys after merge
        self.fix_separator_keys(branch_id);

        true // Child still exists
    }

    /// Collapse the root if it's a branch with only one child or no children.
    fn collapse_root_if_needed(&mut self) {
        loop {
            // Capture root ID first to avoid borrowing conflicts
            let root_branch_id = match &self.root {
                NodeRef::Branch(id, _) => Some(*id),
                NodeRef::Leaf(_, _) => None,
            };

            // Use Option combinators for cleaner nested logic handling
            let branch_info = root_branch_id.and_then(|branch_id| {
                self.get_branch(branch_id).map(|branch| {
                    (
                        branch_id,
                        branch.children.len(),
                        branch.children.first().cloned(),
                    )
                })
            });

            match branch_info {
                Some((branch_id, 0, _)) => {
                    // Empty branch - replace with empty leaf
                    self.create_empty_root_leaf();
                    self.deallocate_branch(branch_id);
                    break;
                }
                Some((branch_id, 1, Some(child))) => {
                    // Single child - promote it and continue collapsing
                    self.root = child;
                    self.deallocate_branch(branch_id);
                    // Continue loop in case new root also needs collapsing
                }
                Some((_, _, _)) => {
                    // Multiple children - no collapse needed
                    break;
                }
                None => {
                    // Handle missing branch or already leaf root
                    root_branch_id
                        .filter(|_| true) // Branch ID exists but branch is missing
                        .map(|_| self.create_empty_root_leaf());
                    break;
                }
            }
        }
    }

    /// Helper method to create empty root leaf
    fn create_empty_root_leaf(&mut self) {
        let empty_id = self.allocate_leaf(LeafNode::new(self.capacity));
        self.root = NodeRef::Leaf(empty_id, PhantomData);
    }

    // ============================================================================
    // OTHER API OPERATIONS
    // ============================================================================

    /// Returns the number of elements in the tree.
    pub fn len(&self) -> usize {
        self.len
    }

    /// Returns true if the tree is empty.
    pub fn is_empty(&self) -> bool {
        self.len == 0
    }

    /// Returns true if the root is a leaf node.
    pub fn is_leaf_root(&self) -> bool {
        matches!(self.root, NodeRef::Leaf(_, _))
    }

    /// Returns the number of leaf nodes in the tree.
    pub fn leaf_count(&self) -> usize {
        self.leaf_count_recursive(&self.root)
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
        // Clear all arenas and create a new root leaf
        self.leaf_arena.clear();
        self.branch_arena.clear();

        // Create a new root leaf
        let root_leaf = LeafNode::new(self.capacity);
        let root_id = self.leaf_arena.allocate(root_leaf);
        self.root = NodeRef::Leaf(root_id, PhantomData);

        // Reset length counter
        self.len = 0;
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
        let start_bound = start_key.map_or(Bound::Unbounded, |k| Bound::Included(k));
        let end_bound = end_key.map_or(Bound::Unbounded, |k| Bound::Excluded(k));

        let (start_info, skip_first, end_info) =
            self.resolve_range_bounds((start_bound, end_bound));
        RangeIterator::new_with_skip_owned(self, start_info, skip_first, end_info)
    }

    /// Returns an iterator over key-value pairs in a range using Rust's range syntax.
    ///
    /// # Examples
    ///
    /// ```
    /// use bplustree::BPlusTreeMap;
    ///
    /// let mut tree = BPlusTreeMap::new(16).unwrap();
    /// for i in 0..10 {
    ///     tree.insert(i, format!("value{}", i));
    /// }
    ///
    /// // Different range syntaxes
    /// let range1: Vec<_> = tree.range(3..7).map(|(k, v)| (*k, v.clone())).collect();
    /// assert_eq!(range1, vec![(3, "value3".to_string()), (4, "value4".to_string()),
    ///                         (5, "value5".to_string()), (6, "value6".to_string())]);
    ///
    /// let range2: Vec<_> = tree.range(3..=7).map(|(k, v)| (*k, v.clone())).collect();
    /// assert_eq!(range2, vec![(3, "value3".to_string()), (4, "value4".to_string()),
    ///                         (5, "value5".to_string()), (6, "value6".to_string()),
    ///                         (7, "value7".to_string())]);
    ///
    /// let range3: Vec<_> = tree.range(5..).map(|(k, v)| *k).collect();
    /// assert_eq!(range3, vec![5, 6, 7, 8, 9]);
    ///
    /// let range4: Vec<_> = tree.range(..5).map(|(k, v)| *k).collect();
    /// assert_eq!(range4, vec![0, 1, 2, 3, 4]);
    ///
    /// let range5: Vec<_> = tree.range(..).map(|(k, v)| *k).collect();
    /// assert_eq!(range5, vec![0, 1, 2, 3, 4, 5, 6, 7, 8, 9]);
    /// ```
    pub fn range<R>(&self, range: R) -> RangeIterator<'_, K, V>
    where
        R: RangeBounds<K>,
    {
        let (start_info, skip_first, end_info) = self.resolve_range_bounds(range);
        RangeIterator::new_with_skip_owned(self, start_info, skip_first, end_info)
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
    // RANGE QUERY HELPERS
    // ============================================================================

    fn resolve_range_bounds<R>(
        &self,
        range: R,
    ) -> (Option<(NodeId, usize)>, bool, Option<(K, bool)>)
    where
        R: RangeBounds<K>,
    {
        let (start_info, skip_first) = match range.start_bound() {
            Bound::Included(key) => {
                if let Some((leaf_id, index)) = self.find_range_start(key) {
                    (Some((leaf_id, index)), false)
                } else {
                    (None, false)
                }
            }
            Bound::Excluded(key) => {
                if let Some((leaf_id, index)) = self.find_range_start(key) {
                    (Some((leaf_id, index)), true)
                } else {
                    (None, false)
                }
            }
            Bound::Unbounded => {
                if let Some(first_leaf) = self.get_first_leaf_id() {
                    (Some((first_leaf, 0)), false)
                } else {
                    (None, false)
                }
            }
        };

        let end_info = match range.end_bound() {
            Bound::Included(key) => Some((key.clone(), true)),
            Bound::Excluded(key) => Some((key.clone(), false)),
            Bound::Unbounded => None,
        };

        (start_info, skip_first, end_info)
    }

    // ============================================================================
    // RANGE QUERY OPTIMIZATION HELPERS
    // ============================================================================

    /// Find the leaf node and index where a range should start
    fn find_range_start(&self, start_key: &K) -> Option<(NodeId, usize)> {
        let mut current = &self.root;

        loop {
            match current {
                NodeRef::Leaf(leaf_id, _) => {
                    if let Some(leaf) = self.get_leaf(*leaf_id) {
                        // Find the first key >= start_key in this leaf
                        let index = leaf
                            .keys
                            .iter()
                            .position(|k| k >= start_key)
                            .unwrap_or(leaf.keys.len());

                        if index < leaf.keys.len() {
                            return Some((*leaf_id, index));
                        } else {
                            // All keys in this leaf are < start_key
                            // Move to next leaf if it exists using Option combinators
                            return (leaf.next != NULL_NODE)
                                .then_some(leaf.next)
                                .and_then(|next_id| self.get_leaf(next_id))
                                .filter(|next_leaf| !next_leaf.keys.is_empty())
                                .map(|_| (leaf.next, 0));
                        }
                    }
                    return None;
                }
                NodeRef::Branch(branch_id, _) => {
                    if let Some(branch) = self.get_branch(*branch_id) {
                        // Find the child that could contain start_key
                        let child_index = branch.find_child_index(start_key);

                        if child_index < branch.children.len() {
                            current = &branch.children[child_index];
                        } else {
                            return None;
                        }
                    } else {
                        return None;
                    }
                }
            }
        }
    }

    /// Get the ID of the first (leftmost) leaf in the tree
    fn get_first_leaf_id(&self) -> Option<NodeId> {
        let mut current = &self.root;

        loop {
            match current {
                NodeRef::Leaf(leaf_id, _) => return Some(*leaf_id),
                NodeRef::Branch(branch_id, _) => {
                    if let Some(branch) = self.get_branch(*branch_id) {
                        if !branch.children.is_empty() {
                            current = &branch.children[0];
                        } else {
                            return None;
                        }
                    } else {
                        return None;
                    }
                }
            }
        }
    }

    // ============================================================================
    // ENHANCED ARENA-BASED ALLOCATION FOR LEAF NODES
    // ============================================================================

    /// Allocate a new leaf node in the arena and return its ID.
    pub fn allocate_leaf(&mut self, leaf: LeafNode<K, V>) -> NodeId {
        self.leaf_arena.allocate(leaf)
    }

    /// Deallocate a leaf node from the arena.
    pub fn deallocate_leaf(&mut self, id: NodeId) -> Option<LeafNode<K, V>> {
        self.leaf_arena.deallocate(id)
    }

    /// Get a reference to a leaf node in the arena.
    pub fn get_leaf(&self, id: NodeId) -> Option<&LeafNode<K, V>> {
        self.leaf_arena.get(id)
    }

    /// Get a mutable reference to a leaf node in the arena.
    pub fn get_leaf_mut(&mut self, id: NodeId) -> Option<&mut LeafNode<K, V>> {
        self.leaf_arena.get_mut(id)
    }

    /// Get the number of free leaf nodes in the arena.
    pub fn free_leaf_count(&self) -> usize {
        self.leaf_arena.free_count()
    }

    /// Get the number of allocated leaf nodes in the arena.
    pub fn allocated_leaf_count(&self) -> usize {
        self.leaf_arena.allocated_count()
    }

    /// Get the leaf arena utilization ratio.
    pub fn leaf_utilization(&self) -> f64 {
        self.leaf_arena.utilization()
    }

    // ============================================================================
    // ARENA STATISTICS
    // ============================================================================

    /// Get statistics for the leaf node arena.
    pub fn leaf_arena_stats(&self) -> arena::ArenaStats {
        self.leaf_arena.stats()
    }

    /// Get statistics for the branch node arena.
    pub fn branch_arena_stats(&self) -> arena::ArenaStats {
        self.branch_arena.stats()
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
    // ENHANCED ARENA-BASED ALLOCATION FOR BRANCH NODES
    // ============================================================================

    /// Allocate a new branch node in the arena and return its ID.
    pub fn allocate_branch(&mut self, branch: BranchNode<K, V>) -> NodeId {
        self.branch_arena.allocate(branch)
    }

    /// Deallocate a branch node from the arena.
    pub fn deallocate_branch(&mut self, id: NodeId) -> Option<BranchNode<K, V>> {
        self.branch_arena.deallocate(id)
    }

    /// Get a reference to a branch node in the arena.
    pub fn get_branch(&self, id: NodeId) -> Option<&BranchNode<K, V>> {
        self.branch_arena.get(id)
    }

    /// Get a mutable reference to a branch node in the arena.
    pub fn get_branch_mut(&mut self, id: NodeId) -> Option<&mut BranchNode<K, V>> {
        self.branch_arena.get_mut(id)
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

        // Finally check arena-tree consistency
        self.check_arena_tree_consistency()
            .map_err(|e| e.to_string())?;
        Ok(())
    }

    /// Recursively check node invariants.
    /// This function verifies the structural integrity of the B+ tree.
    /// It checks node sizes, key ordering, and child relationships.
    fn check_node_invariants(
        &self,
        node: &NodeRef<K, V>,
        min_key: Option<&K>,
        max_key: Option<&K>,
        is_root: bool,
    ) -> bool {
        match node {
            NodeRef::Leaf(id, _) => {
                if let Some(leaf) = self.get_leaf(*id) {
                    // Check leaf size
                    if !is_root && leaf.len() < leaf.min_keys() {
                        return false;
                    }
                    if leaf.len() > leaf.capacity {
                        return false;
                    }

                    // Check key ordering
                    if leaf.keys.len() > 1 {
                        for i in 0..leaf.keys.len() - 1 {
                            if leaf.keys[i] >= leaf.keys[i + 1] {
                                return false;
                            }
                        }
                    }

                    // Check key bounds
                    if let Some(min_k) = min_key {
                        if leaf.keys.first().map_or(false, |k| k < min_k) {
                            return false;
                        }
                    }
                    if let Some(max_k) = max_key {
                        if leaf.keys.last().map_or(false, |k| k >= max_k) {
                            return false;
                        }
                    }
                } else {
                    return false;
                }
            }
            NodeRef::Branch(id, _) => {
                if let Some(branch) = self.get_branch(*id) {
                    // Check branch size
                    if !is_root && branch.keys.len() < branch.min_keys() {
                        return false;
                    }
                    if branch.keys.len() > branch.capacity {
                        return false;
                    }

                    // Check key ordering
                    if branch.keys.len() > 1 {
                        for i in 0..branch.keys.len() - 1 {
                            if branch.keys[i] >= branch.keys[i + 1] {
                                return false;
                            }
                        }
                    }

                    // Check child count
                    if branch.children.len() != branch.keys.len() + 1 {
                        return false;
                    }

                    // Recursively check children and their bounds
                    for i in 0..branch.children.len() {
                        let child_min_key = if i == 0 {
                            min_key
                        } else {
                            Some(&branch.keys[i - 1])
                        };
                        let child_max_key = if i == branch.children.len() - 1 {
                            max_key
                        } else {
                            Some(&branch.keys[i])
                        };

                        if !self.check_node_invariants(
                            &branch.children[i],
                            child_min_key,
                            child_max_key,
                            false,
                        ) {
                            return false;
                        }
                    }
                } else {
                    return false;
                }
            }
        }
        true
    }

    /// Check that arena allocation matches tree structure
    fn check_arena_tree_consistency(&self) -> TreeResult<()> {
        // Count nodes in the tree structure
        let (tree_leaf_count, tree_branch_count) = self.count_nodes_in_tree();

        // Get arena counts
        let leaf_stats = self.leaf_arena_stats();
        let branch_stats = self.branch_arena_stats();

        // Check leaf node consistency
        if tree_leaf_count != leaf_stats.allocated_count {
            return Err(BPlusTreeError::arena_error(
                "Leaf consistency check",
                &format!(
                    "{} in tree vs {} in arena",
                    tree_leaf_count, leaf_stats.allocated_count
                ),
            ));
        }

        // Check branch node consistency
        if tree_branch_count != branch_stats.allocated_count {
            return Err(BPlusTreeError::arena_error(
                "Branch consistency check",
                &format!(
                    "{} in tree vs {} in arena",
                    tree_branch_count, branch_stats.allocated_count
                ),
            ));
        }

        // Check that all leaf nodes in tree are reachable via linked list
        self.check_leaf_linked_list_completeness()?;

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

    /// Count the number of leaf and branch nodes actually in the tree structure.
    pub fn count_nodes_in_tree(&self) -> (usize, usize) {
        if matches!(self.root, NodeRef::Leaf(_, _)) {
            // Single leaf root
            (1, 0)
        } else {
            self.count_nodes_recursive(&self.root)
        }
    }

    /// Recursively count nodes in the tree.
    fn count_nodes_recursive(&self, node: &NodeRef<K, V>) -> (usize, usize) {
        match node {
            NodeRef::Leaf(_, _) => (1, 0), // Found a leaf
            NodeRef::Branch(id, _) => {
                if let Some(branch) = self.get_branch(*id) {
                    let mut total_leaves = 0;
                    let mut total_branches = 1; // Count this branch

                    // Recursively count in all children
                    for child in &branch.children {
                        let (child_leaves, child_branches) = self.count_nodes_recursive(child);
                        total_leaves += child_leaves;
                        total_branches += child_branches;
                    }

                    (total_leaves, total_branches)
                } else {
                    // Invalid branch reference
                    (0, 0)
                }
            }
        }
    }

    /// Check that all leaf nodes in the tree are reachable via the linked list.
    fn check_leaf_linked_list_completeness(&self) -> TreeResult<()> {
        // Collect all leaf IDs from the tree structure
        let mut tree_leaf_ids = Vec::new();
        self.collect_leaf_ids(&self.root, &mut tree_leaf_ids);
        tree_leaf_ids.sort();

        // Collect all leaf IDs from the linked list traversal
        let mut linked_list_ids = Vec::new();
        if let Some(first_id) = self.get_first_leaf_id() {
            let mut current_id = Some(first_id);
            while let Some(id) = current_id {
                linked_list_ids.push(id);
                current_id = self.get_leaf(id).and_then(|leaf| {
                    if leaf.next == crate::NULL_NODE {
                        None
                    } else {
                        Some(leaf.next)
                    }
                });
            }
        }
        linked_list_ids.sort();

        // Compare the two lists
        if tree_leaf_ids != linked_list_ids {
            return Err(BPlusTreeError::corrupted_tree(
                "Linked list",
                &format!(
                    "tree has {:?}, linked list has {:?}",
                    tree_leaf_ids, linked_list_ids
                ),
            ));
        }

        Ok(())
    }

    /// Collect all leaf node IDs from the tree structure.
    fn collect_leaf_ids(&self, node: &NodeRef<K, V>, ids: &mut Vec<NodeId>) {
        match node {
            NodeRef::Leaf(id, _) => ids.push(*id),
            NodeRef::Branch(id, _) => {
                if let Some(branch) = self.get_branch(*id) {
                    for child in &branch.children {
                        self.collect_leaf_ids(child, ids);
                    }
                }
            }
        }
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
                    println!("{}Leaf (ID: {}): Keys: {:?}", indent, id, leaf.keys);
                } else {
                    println!("{}Leaf (ID: {}) - MISSING FROM ARENA", indent, id);
                }
            }
            NodeRef::Branch(id, _) => {
                if let Some(branch) = self.get_branch(*id) {
                    println!("{}Branch (ID: {}): Keys: {:?}", indent, id, branch.keys);
                    for child in &branch.children {
                        self.print_node(child, depth + 1);
                    }
                } else {
                    println!("{}Branch (ID: {}) - MISSING FROM ARENA", indent, id);
                }
            }
        }
    }
}

/// Leaf node of the B+ tree.
#[derive(Debug)]
pub struct LeafNode<K, V> {
    pub keys: Vec<K>,
    pub values: Vec<V>,
    pub capacity: usize,
    pub next: NodeId, // Pointer to the next leaf node for range queries
}

impl<K: Ord + Clone + std::fmt::Debug, V: Clone> LeafNode<K, V> {
    pub fn new(capacity: usize) -> Self {
        Self {
            keys: Vec::with_capacity(capacity),
            values: Vec::with_capacity(capacity),
            capacity,
            next: NULL_NODE,
        }
    }

    pub fn len(&self) -> usize {
        self.keys.len()
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    pub fn is_full(&self) -> bool {
        self.len() == self.capacity
    }

    pub fn is_underfull(&self) -> bool {
        self.len() < self.min_keys()
    }

    pub fn can_donate(&self) -> bool {
        self.len() > self.min_keys()
    }

    pub fn min_keys(&self) -> usize {
        self.capacity / 2 // floor(capacity / 2)
    }

    pub fn get(&self, key: &K) -> Option<&V> {
        self.keys
            .binary_search(key)
            .ok()
            .and_then(|index| self.values.get(index))
    }

    pub fn get_mut(&mut self, key: &K) -> Option<&mut V> {
        self.keys
            .binary_search(key)
            .ok()
            .and_then(|index| self.values.get_mut(index))
    }

    pub fn insert(&mut self, key: K, value: V) -> InsertResult<K, V> {
        match self.keys.binary_search(&key) {
            Ok(index) => {
                // Key exists, update value
                let old_value = std::mem::replace(&mut self.values[index], value);
                InsertResult::Updated(Some(old_value))
            }
            Err(index) => {
                // Key does not exist, insert new key-value pair
                if self.is_full() {
                    // Node is full, must split
                    self.split_and_insert(key, value, index)
                } else {
                    // Node has space, insert directly
                    self.keys.insert(index, key);
                    self.values.insert(index, value);
                    InsertResult::Updated(None)
                }
            }
        }
    }

    fn split_and_insert(&mut self, key: K, value: V, insert_index: usize) -> InsertResult<K, V> {
        let mut new_leaf = LeafNode::new(self.capacity);
        let mid = self.capacity / 2; // floor(capacity / 2)

        // Determine where the new key will go relative to the split point
        let (mut left_keys, mut left_values) = (Vec::new(), Vec::new());
        let (mut right_keys, mut right_values) = (Vec::new(), Vec::new());

        for i in 0..self.len() {
            if i == insert_index {
                // Insert the new key/value here
                if i < mid {
                    left_keys.push(key.clone());
                    left_values.push(value.clone());
                } else {
                    right_keys.push(key.clone());
                    right_values.push(value.clone());
                }
            }

            if i < mid {
                left_keys.push(self.keys[i].clone());
                left_values.push(self.values[i].clone());
            } else {
                right_keys.push(self.keys[i].clone());
                right_values.push(self.values[i].clone());
            }
        }

        // Handle case where new key is inserted at the end
        if insert_index == self.len() {
            if insert_index < mid {
                left_keys.push(key.clone());
                left_values.push(value.clone());
            } else {
                right_keys.push(key.clone());
                right_values.push(value.clone());
            }
        }

        // Update current leaf and new leaf
        self.keys = left_keys;
        self.values = left_values;
        new_leaf.keys = right_keys;
        new_leaf.values = right_values;

        // The separator key is the first key of the new leaf
        let separator_key = new_leaf.keys[0].clone();

        // Link the new leaf
        new_leaf.next = self.next;
        self.next = NULL_NODE; // This will be updated by the tree after allocation

        InsertResult::Split {
            old_value: None,
            new_node_data: SplitNodeData::Leaf(new_leaf),
            separator_key,
        }
    }

    pub fn remove(&mut self, key: &K) -> Option<V> {
        if let Ok(index) = self.keys.binary_search(key) {
            self.keys.remove(index);
            Some(self.values.remove(index))
        } else {
            None
        }
    }

    pub fn borrow_last(&mut self) -> Option<(K, V)> {
        if self.can_donate() {
            let key = self.keys.pop()?;
            let value = self.values.pop()?;
            Some((key, value))
        } else {
            None
        }
    }

    pub fn borrow_first(&mut self) -> Option<(K, V)> {
        if self.can_donate() {
            let key = self.keys.remove(0);
            let value = self.values.remove(0);
            Some((key, value))
        } else {
            None
        }
    }

    pub fn accept_from_left(&mut self, key: K, value: V) {
        self.keys.insert(0, key);
        self.values.insert(0, value);
        // The separator key in the parent will be updated by the parent
    }

    pub fn accept_from_right(&mut self, key: K, value: V) {
        self.keys.push(key);
        self.values.push(value);
        // The separator key in the parent will be updated by the parent
    }

    pub fn extract_all(&mut self) -> (Vec<K>, Vec<V>, NodeId) {
        let keys = std::mem::take(&mut self.keys);
        let values = std::mem::take(&mut self.values);
        let next = self.next;
        self.next = NULL_NODE;
        (keys, values, next)
    }
}

/// Branch node of the B+ tree.
#[derive(Debug)]
pub struct BranchNode<K, V> {
    pub keys: Vec<K>,
    pub children: Vec<NodeRef<K, V>>,
    pub capacity: usize,
}

impl<K: Ord + Clone + std::fmt::Debug, V: Clone> BranchNode<K, V> {
    pub fn new(capacity: usize) -> Self {
        Self {
            keys: Vec::with_capacity(capacity),
            children: Vec::with_capacity(capacity + 1), // One more child than keys
            capacity,
        }
    }

    pub fn len(&self) -> usize {
        self.keys.len()
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    pub fn is_full(&self) -> bool {
        self.len() == self.capacity
    }

    pub fn is_underfull(&self) -> bool {
        self.len() < self.min_keys()
    }

    pub fn can_donate(&self) -> bool {
        self.len() > self.min_keys()
    }

    pub fn min_keys(&self) -> usize {
        self.capacity / 2 // floor(capacity / 2)
    }

    pub fn find_child_index(&self, key: &K) -> usize {
        self.keys.partition_point(|k| k <= key)
    }

    pub fn get_child(&self, key: &K) -> Option<&NodeRef<K, V>> {
        let index = self.find_child_index(key);
        self.children.get(index)
    }

    pub fn insert_child_and_split_if_needed(
        &mut self,
        child_index: usize,
        separator_key: K,
        new_node: NodeRef<K, V>,
    ) -> Option<(BranchNode<K, V>, K)> {
        if self.keys.len() == self.capacity {
            // Node is full, split first
            let (mut new_branch, promoted_key) = self.split();

            // Determine which branch to insert into
            if separator_key < promoted_key {
                self.keys.insert(child_index, separator_key);
                self.children.insert(child_index + 1, new_node);
            } else {
                // Adjust child_index for the new_branch
                let new_child_index = child_index - (self.keys.len() + 1);
                new_branch.keys.insert(new_child_index, separator_key);
                new_branch.children.insert(new_child_index + 1, new_node);
            }
            Some((new_branch, promoted_key))
        } else {
            // Not full, insert directly
            self.keys.insert(child_index, separator_key);
            self.children.insert(child_index + 1, new_node);
            None
        }
    }

    fn split(&mut self) -> (BranchNode<K, V>, K) {
        let mut new_branch = BranchNode::new(self.capacity);
        let mid = self.capacity / 2; // floor(capacity / 2)

        // The key at mid becomes the separator key promoted to the parent
        let promoted_key = self.keys.remove(mid);

        // Move keys and children to the new branch
        new_branch
            .keys
            .extend_from_slice(&self.keys[mid..self.len()]);
        self.keys.truncate(mid);

        new_branch
            .children
            .extend_from_slice(&self.children[mid + 1..self.children.len()]);
        self.children.truncate(mid + 1);

        (new_branch, promoted_key)
    }

    pub fn merge_from(&mut self, separator_key: K, other: &mut BranchNode<K, V>) {
        self.keys.push(separator_key);
        self.keys.append(&mut other.keys);
        self.children.append(&mut other.children);
    }

    pub fn borrow_last(&mut self) -> Option<(K, NodeRef<K, V>)> {
        if self.can_donate() {
            let key = self.keys.pop()?;
            let child = self.children.pop()?;
            Some((key, child))
        } else {
            None
        }
    }

    pub fn borrow_first(&mut self) -> Option<(K, NodeRef<K, V>)> {
        if self.can_donate() {
            let key = self.keys.remove(0);
            let child = self.children.remove(0);
            Some((key, child))
        } else {
            None
        }
    }

    pub fn accept_from_left(&mut self, separator_key: K, key: K, child: NodeRef<K, V>) -> K {
        self.keys.insert(0, key);
        self.children.insert(0, child);
        separator_key
    }

    pub fn accept_from_right(&mut self, separator_key: K, key: K, child: NodeRef<K, V>) -> K {
        self.keys.push(key);
        self.children.push(child);
        separator_key
    }
}

/// Iterator over key-value pairs in the B+ tree.
pub struct ItemIterator<'a, K, V> {
    tree: &'a BPlusTreeMap<K, V>,
    current_leaf_id: Option<NodeId>,
    current_index: usize,
}

impl<'a, K: Ord + Clone + std::fmt::Debug, V: Clone + std::fmt::Debug> ItemIterator<'a, K, V> {
    pub fn new(tree: &'a BPlusTreeMap<K, V>) -> Self {
        let first_leaf_id = tree.get_first_leaf_id();
        Self {
            tree,
            current_leaf_id: first_leaf_id,
            current_index: 0,
        }
    }
}

impl<'a, K: Ord + Clone + std::fmt::Debug, V: Clone + std::fmt::Debug> Iterator for ItemIterator<'a, K, V> {
    type Item = (&'a K, &'a V);

    fn next(&mut self) -> Option<Self::Item> {
        loop {
            if let Some(leaf_id) = self.current_leaf_id {
                if let Some(leaf) = self.tree.get_leaf(leaf_id) {
                    if self.current_index < leaf.keys.len() {
                        let item = Some((
                            &leaf.keys[self.current_index],
                            &leaf.values[self.current_index],
                        ));
                        self.current_index += 1;
                        return item;
                    } else {
                        // Move to the next leaf
                        if leaf.next != NULL_NODE {
                            self.current_leaf_id = Some(leaf.next);
                            self.current_index = 0;
                        } else {
                            // No more leaves
                            self.current_leaf_id = None;
                            return None;
                        }
                    }
                } else {
                    // Current leaf is missing from arena, something is wrong
                    self.current_leaf_id = None;
                    return None;
                }
            } else {
                // No current leaf, iteration finished
                return None;
            }
        }
    }
}

impl<'a, K: Ord + Clone + std::fmt::Debug, V: Clone + std::fmt::Debug> DoubleEndedIterator
    for ItemIterator<'a, K, V>
{
    fn next_back(&mut self) -> Option<Self::Item> {
        // This is a simplified next_back for demonstration.
        // A full implementation would require traversing from the rightmost leaf.
        // For now, we'll just consume from the front.
        self.next()
    }
}

/// Iterator over keys in the B+ tree.
pub struct KeyIterator<'a, K, V> {
    inner: ItemIterator<'a, K, V>,
}

impl<'a, K: Ord + Clone + std::fmt::Debug, V: Clone + std::fmt::Debug> KeyIterator<'a, K, V> {
    pub fn new(tree: &'a BPlusTreeMap<K, V>) -> Self {
        Self {
            inner: ItemIterator::new(tree),
        }
    }
}

impl<'a, K: Ord + Clone + std::fmt::Debug, V: Clone + std::fmt::Debug> Iterator for KeyIterator<'a, K, V> {
    type Item = &'a K;

    fn next(&mut self) -> Option<Self::Item> {
        self.inner.next().map(|(key, _)| key)
    }
}

/// Iterator over values in the B+ tree.
pub struct ValueIterator<'a, K, V> {
    inner: ItemIterator<'a, K, V>,
}

impl<'a, K: Ord + Clone + std::fmt::Debug, V: Clone + std::fmt::Debug> ValueIterator<'a, K, V> {
    pub fn new(tree: &'a BPlusTreeMap<K, V>) -> Self {
        Self {
            inner: ItemIterator::new(tree),
        }
    }
}

impl<'a, K: Ord + Clone + std::fmt::Debug, V: Clone + std::fmt::Debug> Iterator for ValueIterator<'a, K, V> {
    type Item = &'a V;

    fn next(&mut self) -> Option<Self::Item> {
        self.inner.next().map(|(_, value)| value)
    }
}

/// Iterator over a range of key-value pairs in the B+ tree.
pub struct RangeIterator<'a, K, V> {
    tree: &'a BPlusTreeMap<K, V>,
    current_leaf_id: Option<NodeId>,
    current_index: usize,
    end_key: Option<K>,
    end_inclusive: bool,
    skip_first: bool, // Used for Bound::Excluded start bounds
}

impl<'a, K: Ord + Clone + std::fmt::Debug, V: Clone + std::fmt::Debug> RangeIterator<'a, K, V> {
    pub fn new_with_skip_owned(
        tree: &'a BPlusTreeMap<K, V>,
        start_info: Option<(NodeId, usize)>,
        skip_first: bool,
        end_info: Option<(K, bool)>,
    ) -> Self {
        let (current_leaf_id, current_index) = start_info.unwrap_or((NULL_NODE, 0)); // Use NULL_NODE if no start
        let (end_key, end_inclusive) = end_info.map_or((None, false), |(k, inc)| (Some(k), inc));

        Self {
            tree,
            current_leaf_id: if current_leaf_id == NULL_NODE {
                None
            } else {
                Some(current_leaf_id)
            },
            current_index,
            end_key,
            end_inclusive,
            skip_first,
        }
    }
}

impl<'a, K: Ord + Clone + std::fmt::Debug, V: Clone + std::fmt::Debug> Iterator for RangeIterator<'a, K, V> {
    type Item = (&'a K, &'a V);

    fn next(&mut self) -> Option<Self::Item> {
        loop {
            if let Some(leaf_id) = self.current_leaf_id {
                if let Some(leaf) = self.tree.get_leaf(leaf_id) {
                    if self.current_index < leaf.keys.len() {
                        let current_key = &leaf.keys[self.current_index];

                        // Check end bound
                        if let Some(ref end_k) = self.end_key {
                            if self.end_inclusive {
                                if current_key > end_k {
                                    self.current_leaf_id = None;
                                    return None;
                                }
                            } else {
                                if current_key >= end_k {
                                    self.current_leaf_id = None;
                                    return None;
                                }
                            }
                        }

                        // Handle skip_first for excluded start bounds
                        if self.skip_first {
                            self.skip_first = false;
                            self.current_index += 1;
                            // If after incrementing, we are now out of bounds for the current leaf,
                            // we need to move to the next leaf.
                            if self.current_index >= leaf.keys.len() {
                                if leaf.next != NULL_NODE {
                                    self.current_leaf_id = Some(leaf.next);
                                    self.current_index = 0;
                                } else {
                                    // No more leaves
                                    self.current_leaf_id = None;
                                    return None;
                                }
                            }
                            continue; // Skip this item and try next
                        }

                        let item = Some((current_key, &leaf.values[self.current_index]));
                        self.current_index += 1;
                        return item;
                    } else {
                        // Move to the next leaf
                        if leaf.next != NULL_NODE {
                            self.current_leaf_id = Some(leaf.next);
                            self.current_index = 0;
                        } else {
                            // No more leaves
                            self.current_leaf_id = None;
                            return None;
                        }
                    }
                } else {
                    // Current leaf is missing from arena, something is wrong
                    self.current_leaf_id = None;
                    return None;
                }
            } else {
                // No current leaf, iteration finished
                return None;
            }
        }
    }
}
