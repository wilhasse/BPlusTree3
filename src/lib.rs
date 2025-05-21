//! BPlusTree library.

use std::collections::BTreeMap;

/// A node in the B+ tree containing the actual key-value data.
#[derive(Debug)]
struct LeafNode<K, V> {
    /// Maximum number of entries this node can hold before splitting
    branching_factor: usize,
    /// Data stored in this leaf node
    entries: BTreeMap<K, V>,
}

impl<K: Ord, V> LeafNode<K, V> {
    fn new(branching_factor: usize) -> Self {
        Self {
            branching_factor,
            entries: BTreeMap::new(),
        }
    }
}

#[derive(Debug)]
pub struct BPlusTree<K, V> {
    /// Maximum number of entries in each node
    branching_factor: usize,
    /// Root node of the tree (temporarily using BTreeMap until we implement proper tree structure)
    root: LeafNode<K, V>,
}

impl<K: Ord, V> BPlusTree<K, V> {
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
        self.root.entries.insert(key, value)
    }

    /// Returns a reference to the value corresponding to the key.
    pub fn get(&self, key: &K) -> Option<&V> {
        self.root.entries.get(key)
    }

    /// Removes a key from the tree, returning the value if it existed.
    pub fn remove(&mut self, _key: &K) -> Option<V> {
        unimplemented!("not yet implemented")
    }

    /// Returns the number of elements in the tree.
    pub fn len(&self) -> usize {
        self.root.entries.len()
    }

    /// Returns `true` if the tree contains no elements.
    pub fn is_empty(&self) -> bool {
        self.root.entries.is_empty()
    }
}

