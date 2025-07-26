package bplustree

import (
	"cmp"
	"errors"
)

// ErrKeyNotFound is returned when trying to delete a non-existent key
var ErrKeyNotFound = errors.New("key not found")

// Entry represents a key-value pair
type Entry[K cmp.Ordered, V any] struct {
	Key   K
	Value V
}

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

// Delete removes a key-value pair from the tree
func (t *BPlusTree[K, V]) Delete(key K) (V, error) {
	var zero V
	if t.root == nil {
		return zero, ErrKeyNotFound
	}
	
	// Delete from the tree
	value, err := t.deleteFromNode(t.root, key)
	if err != nil {
		return zero, err
	}
	
	// Handle root becoming empty
	if t.root.nodeType == branchNode && len(t.root.keys) == 0 {
		if len(t.root.children) > 0 {
			t.root = t.root.children[0]
		}
	}
	
	// Handle empty tree
	if t.root.nodeType == leafNode && len(t.root.keys) == 0 {
		t.root = nil
	}
	
	t.size--
	return value, nil
}

// deleteFromNode deletes a key from the given node
func (t *BPlusTree[K, V]) deleteFromNode(n *node[K, V], key K) (V, error) {
	var zero V
	
	if n.nodeType == leafNode {
		// Find and delete from leaf
		for i, k := range n.keys {
			if k == key {
				value := n.values[i]
				
				// Remove key and value
				n.keys = append(n.keys[:i], n.keys[i+1:]...)
				n.values = append(n.values[:i], n.values[i+1:]...)
				
				return value, nil
			}
		}
		return zero, ErrKeyNotFound
	}
	
	// Find child containing the key
	childIdx := 0
	for childIdx < len(n.keys) && key >= n.keys[childIdx] {
		childIdx++
	}
	if childIdx >= len(n.children) {
		childIdx = len(n.children) - 1
	}
	
	child := n.children[childIdx]
	minKeys := (t.capacity + 1) / 2 - 1
	
	// Check if child will underflow
	if len(child.keys) <= minKeys {
		// Try to handle underflow
		t.handleUnderflow(n, childIdx)
		// Re-find child after potential merge
		if childIdx >= len(n.children) {
			childIdx = len(n.children) - 1
		}
		child = n.children[childIdx]
	}
	
	return t.deleteFromNode(child, key)
}

// handleUnderflow handles node underflow by redistribution or merging
func (t *BPlusTree[K, V]) handleUnderflow(parent *node[K, V], childIdx int) {
	child := parent.children[childIdx]
	minKeys := (t.capacity + 1) / 2 - 1
	
	// Try borrowing from left sibling
	if childIdx > 0 {
		leftSibling := parent.children[childIdx-1]
		if len(leftSibling.keys) > minKeys {
			if child.nodeType == leafNode {
				// Borrow from left sibling
				borrowedKey := leftSibling.keys[len(leftSibling.keys)-1]
				borrowedValue := leftSibling.values[len(leftSibling.values)-1]
				
				leftSibling.keys = leftSibling.keys[:len(leftSibling.keys)-1]
				leftSibling.values = leftSibling.values[:len(leftSibling.values)-1]
				
				child.keys = append([]K{borrowedKey}, child.keys...)
				child.values = append([]V{borrowedValue}, child.values...)
				
				parent.keys[childIdx-1] = child.keys[0]
			}
			return
		}
	}
	
	// Try borrowing from right sibling
	if childIdx < len(parent.children)-1 {
		rightSibling := parent.children[childIdx+1]
		if len(rightSibling.keys) > minKeys {
			if child.nodeType == leafNode {
				// Borrow from right sibling
				borrowedKey := rightSibling.keys[0]
				borrowedValue := rightSibling.values[0]
				
				rightSibling.keys = rightSibling.keys[1:]
				rightSibling.values = rightSibling.values[1:]
				
				child.keys = append(child.keys, borrowedKey)
				child.values = append(child.values, borrowedValue)
				
				parent.keys[childIdx] = rightSibling.keys[0]
			}
			return
		}
	}
	
	// Merge with sibling
	if childIdx > 0 {
		// Merge with left sibling
		t.mergeNodes(parent, childIdx-1, childIdx)
	} else {
		// Merge with right sibling
		t.mergeNodes(parent, childIdx, childIdx+1)
	}
}

// mergeNodes merges two sibling nodes
func (t *BPlusTree[K, V]) mergeNodes(parent *node[K, V], leftIdx, rightIdx int) {
	left := parent.children[leftIdx]
	right := parent.children[rightIdx]
	
	if left.nodeType == leafNode {
		// Merge leaf nodes
		left.keys = append(left.keys, right.keys...)
		left.values = append(left.values, right.values...)
		
		// Update leaf links
		left.next = right.next
		if right.next != nil {
			right.next.prev = left
		}
		
		// Remove from parent
		parent.keys = append(parent.keys[:leftIdx], parent.keys[leftIdx+1:]...)
		parent.children = append(parent.children[:rightIdx], parent.children[rightIdx+1:]...)
	}
}

// Range returns all entries with keys in the range [start, end]
func (t *BPlusTree[K, V]) Range(start, end K) []Entry[K, V] {
	var results []Entry[K, V]
	
	if t.root == nil || start > end {
		return results
	}
	
	// Find the first leaf that could contain start
	current := t.root
	for current.nodeType == branchNode {
		childIdx := 0
		for childIdx < len(current.keys) && start >= current.keys[childIdx] {
			childIdx++
		}
		if childIdx >= len(current.children) {
			childIdx = len(current.children) - 1
		}
		current = current.children[childIdx]
	}
	
	// Traverse leaves collecting entries in range
	for current != nil {
		for i, key := range current.keys {
			if key > end {
				return results
			}
			if key >= start {
				results = append(results, Entry[K, V]{
					Key:   key,
					Value: current.values[i],
				})
			}
		}
		current = current.next
	}
	
	return results
}

// Iterator represents a forward iterator over the B+ tree
type Iterator[K cmp.Ordered, V any] struct {
	currentNode  *node[K, V]
	currentIndex int
	key          K
	value        V
}

// Iterator returns a new forward iterator
func (t *BPlusTree[K, V]) Iterator() *Iterator[K, V] {
	if t.root == nil {
		return &Iterator[K, V]{
			currentNode:  nil,
			currentIndex: 0,
		}
	}
	
	// Find leftmost leaf
	current := t.root
	for current.nodeType == branchNode {
		current = current.children[0]
	}
	
	return &Iterator[K, V]{
		currentNode:  current,
		currentIndex: -1,
	}
}

// Next advances the iterator and returns true if there are more elements
func (it *Iterator[K, V]) Next() bool {
	if it.currentNode == nil {
		return false
	}
	
	it.currentIndex++
	
	// Check if we have more items in current node
	if it.currentIndex < len(it.currentNode.keys) {
		it.key = it.currentNode.keys[it.currentIndex]
		it.value = it.currentNode.values[it.currentIndex]
		return true
	}
	
	// Move to next leaf node
	it.currentNode = it.currentNode.next
	it.currentIndex = 0
	
	// Try again with next node
	if it.currentNode != nil && len(it.currentNode.keys) > 0 {
		it.key = it.currentNode.keys[0]
		it.value = it.currentNode.values[0]
		return true
	}
	
	return false
}

// Key returns the current key
func (it *Iterator[K, V]) Key() K {
	return it.key
}

// Value returns the current value
func (it *Iterator[K, V]) Value() V {
	return it.value
}

// ReverseIterator represents a reverse iterator over the B+ tree
type ReverseIterator[K cmp.Ordered, V any] struct {
	currentNode  *node[K, V]
	currentIndex int
	key          K
	value        V
}

// ReverseIterator returns a new reverse iterator
func (t *BPlusTree[K, V]) ReverseIterator() *ReverseIterator[K, V] {
	if t.root == nil {
		return &ReverseIterator[K, V]{
			currentNode:  nil,
			currentIndex: 0,
		}
	}
	
	// Find rightmost leaf
	current := t.root
	for current.nodeType == branchNode {
		current = current.children[len(current.children)-1]
	}
	
	return &ReverseIterator[K, V]{
		currentNode:  current,
		currentIndex: len(current.keys),
	}
}

// Next advances the reverse iterator and returns true if there are more elements
func (it *ReverseIterator[K, V]) Next() bool {
	if it.currentNode == nil {
		return false
	}
	
	it.currentIndex--
	
	// Check if we have more items in current node
	if it.currentIndex >= 0 {
		it.key = it.currentNode.keys[it.currentIndex]
		it.value = it.currentNode.values[it.currentIndex]
		return true
	}
	
	// Move to previous leaf node
	it.currentNode = it.currentNode.prev
	if it.currentNode != nil {
		it.currentIndex = len(it.currentNode.keys) - 1
		if it.currentIndex >= 0 {
			it.key = it.currentNode.keys[it.currentIndex]
			it.value = it.currentNode.values[it.currentIndex]
			return true
		}
	}
	
	return false
}

// Key returns the current key
func (it *ReverseIterator[K, V]) Key() K {
	return it.key
}

// Value returns the current value
func (it *ReverseIterator[K, V]) Value() V {
	return it.value
}

// Contains checks if a key exists in the tree
func (t *BPlusTree[K, V]) Contains(key K) bool {
	_, found := t.Get(key)
	return found
}

// Clear removes all elements from the tree
func (t *BPlusTree[K, V]) Clear() {
	t.root = nil
	t.size = 0
}