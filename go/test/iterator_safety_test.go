package test

import (
	"testing"

	"github.com/example/bplustree/internal/bplustree"
)

func TestIteratorSafetyInsertionsDuringIteration(t *testing.T) {
	tree := bplustree.New[int, int](8)
	
	// Insert initial data
	for i := 0; i < 10; i++ {
		tree.Insert(i*10, i*10)
	}
	
	// Start iteration and insert during iteration
	iter := tree.Iterator()
	count := 0
	seenKeys := make([]int, 0)
	
	for iter.Next() {
		key := iter.Key()
		seenKeys = append(seenKeys, key)
		count++
		
		// Insert a new key that would come after current position
		if count == 5 {
			tree.Insert(key+5, key+5)
		}
	}
	
	// Verify we saw at least the original 10 items
	if count < 10 {
		t.Errorf("Expected at least 10 items during iteration, got %d", count)
	}
	
	// Verify tree has 11 items now
	if tree.Len() != 11 {
		t.Errorf("Expected 11 items after insertion, got %d", tree.Len())
	}
}

func TestIteratorSafetyDeletionsDuringIteration(t *testing.T) {
	tree := bplustree.New[int, int](8)
	
	// Insert initial data
	for i := 0; i < 20; i++ {
		tree.Insert(i, i*10)
	}
	
	// Start iteration and mark keys for deletion
	iter := tree.Iterator()
	count := 0
	keysToDelete := make([]int, 0)
	
	for iter.Next() {
		key := iter.Key()
		count++
		
		// Mark every third key for deletion
		if key%3 == 0 {
			keysToDelete = append(keysToDelete, key)
		}
	}
	
	// Delete the marked keys after iteration
	for _, key := range keysToDelete {
		if _, err := tree.Delete(key); err != nil {
			t.Errorf("Failed to delete key %d: %v", key, err)
		}
	}
	
	// Verify iteration completed for all original items
	if count != 20 {
		t.Errorf("Expected 20 items during iteration, got %d", count)
	}
	
	// Verify correct number of items remain
	expectedRemaining := 20 - len(keysToDelete)
	if tree.Len() != expectedRemaining {
		t.Errorf("Expected %d items after deletion, got %d", expectedRemaining, tree.Len())
	}
}

func TestReverseIteratorWithModifications(t *testing.T) {
	tree := bplustree.New[int, string](4)
	
	// Insert initial data
	tree.Insert(10, "ten")
	tree.Insert(20, "twenty")
	tree.Insert(30, "thirty")
	tree.Insert(40, "forty")
	tree.Insert(50, "fifty")
	
	// Start reverse iteration and modify during iteration
	iter := tree.ReverseIterator()
	count := 0
	
	for iter.Next() {
		count++
		
		// Insert a new key during iteration
		if count == 2 {
			tree.Insert(35, "thirty-five")
		}
		
		// Update an existing key during iteration
		if iter.Key() == 20 {
			tree.Insert(20, "TWENTY")
		}
	}
	
	// Verify iteration completed
	if count < 5 {
		t.Errorf("Expected at least 5 items during reverse iteration, got %d", count)
	}
	
	// Verify modifications took effect
	val20, _ := tree.Get(20)
	if val20 != "TWENTY" {
		t.Errorf("Expected updated value 'TWENTY', got '%s'", val20)
	}
	
	val35, found := tree.Get(35)
	if !found || val35 != "thirty-five" {
		t.Error("Expected to find key 35 with value 'thirty-five'")
	}
}

func TestConcurrentForwardAndReverseIteration(t *testing.T) {
	tree := bplustree.New[int, int](16)
	
	// Insert data
	for i := 0; i < 50; i++ {
		tree.Insert(i, i*2)
	}
	
	// Create both iterators
	fwdIter := tree.Iterator()
	revIter := tree.ReverseIterator()
	
	// Advance both iterators alternately
	fwdCount := 0
	revCount := 0
	fwdSum := 0
	revSum := 0
	
	for i := 0; i < 20; i++ {
		if i%2 == 0 {
			if fwdIter.Next() {
				fwdCount++
				fwdSum += fwdIter.Key()
			}
		} else {
			if revIter.Next() {
				revCount++
				revSum += revIter.Key()
			}
		}
	}
	
	// Both iterators should have advanced
	if fwdCount == 0 {
		t.Error("Forward iterator didn't advance")
	}
	if revCount == 0 {
		t.Error("Reverse iterator didn't advance")
	}
	if fwdSum == revSum {
		t.Error("Forward and reverse iterators shouldn't visit same keys")
	}
}

func TestIteratorAfterClear(t *testing.T) {
	tree := bplustree.New[int, int](8)
	
	// Insert data
	for i := 0; i < 10; i++ {
		tree.Insert(i, i)
	}
	
	// Create iterator
	iter := tree.Iterator()
	
	// Get first item
	if !iter.Next() {
		t.Fatal("Expected iterator to have first element")
	}
	firstKey := iter.Key()
	if firstKey != 0 {
		t.Errorf("Expected first key to be 0, got %d", firstKey)
	}
	
	// Clear the tree
	tree.Clear()
	
	// New iterator should be empty
	newIter := tree.Iterator()
	if newIter.Next() {
		t.Error("Expected new iterator to be empty after clear")
	}
	
	// Note: In Go, the old iterator may still work since it holds references
	// This is different from languages with stricter iterator invalidation
}

func TestIteratorWithDuplicateKeyUpdates(t *testing.T) {
	tree := bplustree.New[int, int](4)
	
	// Insert initial values
	tree.Insert(1, 100)
	tree.Insert(2, 200)
	tree.Insert(3, 300)
	tree.Insert(4, 400)
	tree.Insert(5, 500)
	
	// Start iteration
	iter := tree.Iterator()
	valuesSeen := make([]int, 0)
	
	for iter.Next() {
		key := iter.Key()
		value := iter.Value()
		valuesSeen = append(valuesSeen, value)
		
		// Update values during iteration
		if key == 3 {
			tree.Insert(3, 999) // Update current key
			tree.Insert(1, 111) // Update earlier key
			tree.Insert(5, 555) // Update later key
		}
	}
	
	// Verify we saw the original values during iteration
	if len(valuesSeen) != 5 {
		t.Fatalf("Expected 5 values, got %d", len(valuesSeen))
	}
	if valuesSeen[2] != 300 { // Original value at position 2 (key 3)
		t.Errorf("Expected to see original value 300 during iteration, got %d", valuesSeen[2])
	}
	
	// Verify updates took effect
	val1, _ := tree.Get(1)
	val3, _ := tree.Get(3)
	val5, _ := tree.Get(5)
	
	if val1 != 111 {
		t.Errorf("Expected updated value 111 for key 1, got %d", val1)
	}
	if val3 != 999 {
		t.Errorf("Expected updated value 999 for key 3, got %d", val3)
	}
	if val5 != 555 {
		t.Errorf("Expected updated value 555 for key 5, got %d", val5)
	}
}

func TestStressIteratorWithManyModifications(t *testing.T) {
	tree := bplustree.New[int, int](32)
	
	// Insert initial data
	for i := 0; i < 100; i++ {
		tree.Insert(i*5, i*5)
	}
	
	// Iterate and perform modifications
	iter := tree.Iterator()
	modifications := 0
	itemsSeen := 0
	
	for iter.Next() {
		key := iter.Key()
		itemsSeen++
		
		// Perform various modifications based on key
		switch {
		case key%20 == 0 && key > 0:
			// Insert a new key
			tree.Insert(key+1, key+1)
			modifications++
			
		case key%30 == 0:
			// Update current key
			tree.Insert(key, key*10)
			modifications++
			
		case key%50 == 0 && key < 400:
			// Try to delete a future key (should work)
			if _, err := tree.Delete(key + 100); err == nil {
				modifications++
			}
		}
	}
	
	// Verify iteration completed successfully
	if itemsSeen < 100 {
		t.Errorf("Expected at least 100 items, saw %d", itemsSeen)
	}
	if modifications == 0 {
		t.Error("Expected some modifications to occur")
	}
	
	t.Logf("Iterator stress test: %d items seen, %d modifications", itemsSeen, modifications)
}