package test

import (
	"math/rand"
	"testing"

	"github.com/example/bplustree/internal/bplustree"
)

func TestStressRandomOperations(t *testing.T) {
	// Use fixed seed for reproducibility
	rng := rand.New(rand.NewSource(42))
	
	tree := bplustree.New[int, int](32)
	expected := make(map[int]int)
	
	numOps := 10000
	
	for i := 0; i < numOps; i++ {
		op := rng.Intn(100)
		key := rng.Intn(1000)
		
		switch {
		case op < 60: // 60% inserts
			value := rng.Intn(10000)
			tree.Insert(key, value)
			expected[key] = value
			
		case op < 80: // 20% deletes
			if _, err := tree.Delete(key); err == nil {
				delete(expected, key)
			}
			
		default: // 20% lookups
			treeVal, treeFound := tree.Get(key)
			expVal, expFound := expected[key]
			
			if treeFound != expFound {
				t.Errorf("Key %d: found mismatch - tree: %v, expected: %v", 
					key, treeFound, expFound)
			}
			if treeFound && treeVal != expVal {
				t.Errorf("Key %d: value mismatch - tree: %d, expected: %d", 
					key, treeVal, expVal)
			}
		}
	}
	
	// Verify final state
	if tree.Len() != len(expected) {
		t.Errorf("Size mismatch: tree has %d items, expected %d", 
			tree.Len(), len(expected))
	}
	
	// Verify all entries match
	for key, expVal := range expected {
		treeVal, found := tree.Get(key)
		if !found {
			t.Errorf("Key %d missing from tree", key)
		}
		if treeVal != expVal {
			t.Errorf("Key %d: value mismatch - tree: %d, expected: %d", 
				key, treeVal, expVal)
		}
	}
	
	// Verify iterator returns all entries in order
	iter := tree.Iterator()
	count := 0
	var lastKey *int
	for iter.Next() {
		key := iter.Key()
		if lastKey != nil && key <= *lastKey {
			t.Errorf("Iterator keys not in order: %d <= %d", key, *lastKey)
		}
		lastKey = &key
		count++
		
		if _, ok := expected[key]; !ok {
			t.Errorf("Iterator returned unexpected key %d", key)
		}
	}
	
	if count != len(expected) {
		t.Errorf("Iterator returned %d items, expected %d", count, len(expected))
	}
}

func TestStressSequentialOperations(t *testing.T) {
	tree := bplustree.New[int, int](64)
	n := 5000
	
	// Insert in ascending order
	for i := 0; i < n; i++ {
		tree.Insert(i, i*10)
	}
	if tree.Len() != n {
		t.Errorf("Expected %d items after insertion, got %d", n, tree.Len())
	}
	
	// Delete every third element
	deletedCount := 0
	notFoundCount := 0
	for i := 0; i < n; i += 3 {
		if _, err := tree.Delete(i); err != nil {
			notFoundCount++
			// Debug: check if key actually exists before delete attempt
			if _, found := tree.Get(i); found {
				t.Errorf("Delete failed but key %d exists: %v", i, err)
			}
		} else {
			deletedCount++
		}
	}
	
	// Debug output
	t.Logf("Deleted %d keys, %d not found", deletedCount, notFoundCount)
	
	expectedCount := n - deletedCount
	if tree.Len() != expectedCount {
		t.Errorf("Expected %d items after deletion, got %d", expectedCount, tree.Len())
	}
	
	// Insert in descending order (re-insert deleted keys)
	for i := n - 1; i >= 0; i-- {
		if i%3 == 0 {
			tree.Insert(i, i*20)
		}
	}
	
	// Verify all elements
	for i := 0; i < n; i++ {
		val, found := tree.Get(i)
		if i%3 == 0 {
			if !found {
				t.Errorf("Key %d should exist", i)
			}
			if val != i*20 {
				t.Errorf("Key %d: expected value %d, got %d", i, i*20, val)
			}
		} else {
			if !found {
				t.Errorf("Key %d should exist", i)
			}
			if val != i*10 {
				t.Errorf("Key %d: expected value %d, got %d", i, i*10, val)
			}
		}
	}
}

func TestStressLargeDataset(t *testing.T) {
	tree := bplustree.New[uint32, uint32](128)
	n := uint32(100000)
	
	// Insert large dataset
	for i := uint32(0); i < n; i++ {
		tree.Insert(i, i*2)
	}
	
	if tree.Len() != int(n) {
		t.Errorf("Expected %d items, got %d", n, tree.Len())
	}
	
	// Random lookups
	rng := rand.New(rand.NewSource(12345))
	for i := 0; i < 10000; i++ {
		key := uint32(rng.Intn(int(n)))
		val, found := tree.Get(key)
		if !found {
			t.Errorf("Key %d not found", key)
		}
		if val != key*2 {
			t.Errorf("Key %d: expected value %d, got %d", key, key*2, val)
		}
	}
	
	// Range query performance
	rangeStart := n / 4
	rangeEnd := n / 2
	results := tree.Range(rangeStart, rangeEnd)
	
	expectedLen := int(rangeEnd - rangeStart + 1)
	if len(results) != expectedLen {
		t.Errorf("Range query returned %d results, expected %d", 
			len(results), expectedLen)
	}
}

func TestStressMinimumCapacity(t *testing.T) {
	// Test with minimum capacity of 3
	tree := bplustree.New[int, int](3)
	
	// Insert enough to force multiple splits
	for i := 1; i <= 20; i++ {
		tree.Insert(i, i*100)
	}
	
	// Verify all insertions worked
	if tree.Len() != 20 {
		t.Errorf("Expected 20 items, got %d", tree.Len())
	}
	
	if tree.Height() < 2 {
		t.Error("Expected tree height >= 2 with minimum capacity")
	}
	
	// Verify all values are retrievable
	for i := 1; i <= 20; i++ {
		val, found := tree.Get(i)
		if !found {
			t.Errorf("Key %d not found", i)
		}
		if val != i*100 {
			t.Errorf("Key %d: expected value %d, got %d", i, i*100, val)
		}
	}
}

func TestStressMaximumCapacity(t *testing.T) {
	// Test with very large capacity
	tree := bplustree.New[int, int](1024)
	
	// Insert many items
	for i := 1; i <= 2000; i++ {
		tree.Insert(i, i)
	}
	
	// With large capacity, tree should be shallow
	if tree.Len() != 2000 {
		t.Errorf("Expected 2000 items, got %d", tree.Len())
	}
	
	if tree.Height() > 3 {
		t.Errorf("Expected tree height <= 3 with large capacity, got %d", tree.Height())
	}
	
	// Test range query on large node
	results := tree.Range(500, 600)
	if len(results) != 101 {
		t.Errorf("Expected 101 results, got %d", len(results))
	}
}

func TestStressDuplicateInsertions(t *testing.T) {
	tree := bplustree.New[int, int](16)
	
	// Insert same key many times
	for i := 0; i < 100; i++ {
		tree.Insert(42, i)
	}
	
	// Should only have one entry
	if tree.Len() != 1 {
		t.Errorf("Expected 1 item, got %d", tree.Len())
	}
	
	// Should have the last value
	val, found := tree.Get(42)
	if !found {
		t.Error("Key 42 not found")
	}
	if val != 99 {
		t.Errorf("Expected value 99, got %d", val)
	}
}

func TestStressAlternatingInsertDelete(t *testing.T) {
	tree := bplustree.New[int, int](8)
	
	// Alternating pattern
	for i := 0; i < 1000; i++ {
		tree.Insert(i, i)
		
		// Delete previous key
		if i > 0 {
			if _, err := tree.Delete(i - 1); err != nil {
				t.Errorf("Failed to delete key %d: %v", i-1, err)
			}
		}
	}
	
	// Should only have the last key
	if tree.Len() != 1 {
		t.Errorf("Expected 1 item, got %d", tree.Len())
	}
	
	val, found := tree.Get(999)
	if !found {
		t.Error("Key 999 not found")
	}
	if val != 999 {
		t.Errorf("Expected value 999, got %d", val)
	}
	
	// Re-insert all deleted keys
	for i := 0; i < 999; i++ {
		tree.Insert(i, i*2)
	}
	
	// Should have all keys now
	if tree.Len() != 1000 {
		t.Errorf("Expected 1000 items, got %d", tree.Len())
	}
}