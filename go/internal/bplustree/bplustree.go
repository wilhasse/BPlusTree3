package bplustree

import (
	"cmp"
)

// nodeType represents the type of a B+ tree node
type nodeType int

const (
	leafNode nodeType = iota
	branchNode
)

// node represents a B+ tree node
type node[K cmp.Ordered, V any] struct {
	nodeType nodeType
	keys     []K
	
	// For leaf nodes
	values []V
	next   *node[K, V]
	prev   *node[K, V]
	
	// For branch nodes
	children []*node[K, V]
}

// BPlusTree represents a B+ tree data structure
type BPlusTree[K cmp.Ordered, V any] struct {
	root     *node[K, V]
	capacity int
	size     int
}

// New creates a new B+ tree with the given capacity
func New[K cmp.Ordered, V any](capacity int) *BPlusTree[K, V] {
	if capacity < 3 {
		capacity = 3
	}
	return &BPlusTree[K, V]{
		capacity: capacity,
		size:     0,
		root:     nil,
	}
}

// Len returns the number of key-value pairs in the tree
func (t *BPlusTree[K, V]) Len() int {
	return t.size
}

// Height returns the height of the tree
func (t *BPlusTree[K, V]) Height() int {
	if t.root == nil {
		return 0
	}
	
	height := 1
	current := t.root
	for current.nodeType == branchNode && len(current.children) > 0 {
		height++
		current = current.children[0]
	}
	return height
}

// Insert inserts or updates a key-value pair in the tree
func (t *BPlusTree[K, V]) Insert(key K, value V) {
	if t.root == nil {
		t.root = &node[K, V]{
			nodeType: leafNode,
			keys:     []K{key},
			values:   []V{value},
		}
		t.size++
		return
	}
	
	// Check if root needs splitting
	if t.root.nodeType == leafNode && len(t.root.keys) >= t.capacity {
		// Split root
		newNode := t.splitLeaf(t.root)
		
		// Create new root
		newRoot := &node[K, V]{
			nodeType: branchNode,
			keys:     []K{newNode.keys[0]},
			children: []*node[K, V]{t.root, newNode},
		}
		t.root = newRoot
	}
	
	// Insert into the tree
	t.insertIntoNode(t.root, key, value)
}

// insertIntoNode inserts a key-value pair into the given node
func (t *BPlusTree[K, V]) insertIntoNode(n *node[K, V], key K, value V) {
	if n.nodeType == leafNode {
		// Find position to insert
		pos := 0
		for pos < len(n.keys) && n.keys[pos] < key {
			pos++
		}
		
		// Check if key already exists
		if pos < len(n.keys) && n.keys[pos] == key {
			n.values[pos] = value
			return
		}
		
		// Insert at position
		n.keys = append(n.keys[:pos], append([]K{key}, n.keys[pos:]...)...)
		n.values = append(n.values[:pos], append([]V{value}, n.values[pos:]...)...)
		t.size++
	} else {
		// Find child to insert into
		childIdx := 0
		for childIdx < len(n.keys) && key >= n.keys[childIdx] {
			childIdx++
		}
		if childIdx >= len(n.children) {
			childIdx = len(n.children) - 1
		}
		
		child := n.children[childIdx]
		
		// Check if child needs splitting
		if len(child.keys) >= t.capacity {
			var newNode *node[K, V]
			if child.nodeType == leafNode {
				newNode = t.splitLeaf(child)
			} else {
				newNode = t.splitBranch(child)
			}
			
			// Insert new key into parent
			splitKey := newNode.keys[0]
			
			// Insert key and child pointer
			n.keys = append(n.keys[:childIdx], append([]K{splitKey}, n.keys[childIdx:]...)...)
			n.children = append(n.children[:childIdx+1], append([]*node[K, V]{newNode}, n.children[childIdx+1:]...)...)
			
			// Decide which child to insert into
			if key >= splitKey {
				t.insertIntoNode(newNode, key, value)
			} else {
				t.insertIntoNode(child, key, value)
			}
		} else {
			t.insertIntoNode(child, key, value)
		}
	}
}

// splitLeaf splits a leaf node and returns the new node
func (t *BPlusTree[K, V]) splitLeaf(leaf *node[K, V]) *node[K, V] {
	mid := len(leaf.keys) / 2
	
	// Create new leaf with right half
	newLeaf := &node[K, V]{
		nodeType: leafNode,
		keys:     append([]K(nil), leaf.keys[mid:]...),
		values:   append([]V(nil), leaf.values[mid:]...),
		next:     leaf.next,
		prev:     leaf,
	}
	
	// Update leaf links
	if leaf.next != nil {
		leaf.next.prev = newLeaf
	}
	leaf.next = newLeaf
	
	// Keep only left half in original leaf
	leaf.keys = leaf.keys[:mid]
	leaf.values = leaf.values[:mid]
	
	return newLeaf
}

// splitBranch splits a branch node and returns the new node
func (t *BPlusTree[K, V]) splitBranch(branch *node[K, V]) *node[K, V] {
	mid := len(branch.keys) / 2
	
	// Create new branch with right half
	newBranch := &node[K, V]{
		nodeType: branchNode,
		keys:     append([]K(nil), branch.keys[mid+1:]...),
		children: append([]*node[K, V](nil), branch.children[mid+1:]...),
	}
	
	// Keep only left half in original branch
	branch.keys = branch.keys[:mid]
	branch.children = branch.children[:mid+1]
	
	return newBranch
}

// Get retrieves the value associated with a key
func (t *BPlusTree[K, V]) Get(key K) (V, bool) {
	var zero V
	if t.root == nil {
		return zero, false
	}
	
	current := t.root
	
	// Navigate to leaf
	for current.nodeType == branchNode {
		childIdx := 0
		for childIdx < len(current.keys) && key >= current.keys[childIdx] {
			childIdx++
		}
		if childIdx >= len(current.children) {
			childIdx = len(current.children) - 1
		}
		current = current.children[childIdx]
	}
	
	// Search in leaf
	for i, k := range current.keys {
		if k == key {
			return current.values[i], true
		}
	}
	
	return zero, false
}