package bplustree

import (
	"testing"
)

func TestForwardIteratorOnEmptyTree(t *testing.T) {
	// Arrange
	tree := New[int, string](128)

	// Act
	iter := tree.Iterator()

	// Assert
	if iter.Next() {
		t.Error("Expected iterator on empty tree to return false")
	}
}

func TestForwardIteratorSingleElement(t *testing.T) {
	// Arrange
	tree := New[int, string](128)
	tree.Insert(42, "answer")

	// Act
	iter := tree.Iterator()

	// Assert
	if !iter.Next() {
		t.Fatal("Expected iterator to have next element")
	}
	
	key, value := iter.Key(), iter.Value()
	if key != 42 || value != "answer" {
		t.Errorf("Expected (42, 'answer'), got (%d, '%s')", key, value)
	}

	if iter.Next() {
		t.Error("Expected no more elements")
	}
}

func TestForwardIteratorMultipleElements(t *testing.T) {
	// Arrange
	tree := New[int, int](128)
	expected := []Entry[int, int]{}
	for i := 0; i < 10; i++ {
		tree.Insert(i, i*10)
		expected = append(expected, Entry[int, int]{Key: i, Value: i * 10})
	}

	// Act
	iter := tree.Iterator()
	var results []Entry[int, int]
	for iter.Next() {
		results = append(results, Entry[int, int]{
			Key:   iter.Key(),
			Value: iter.Value(),
		})
	}

	// Assert
	if len(results) != len(expected) {
		t.Fatalf("Expected %d elements, got %d", len(expected), len(results))
	}

	for i, entry := range results {
		if entry.Key != expected[i].Key || entry.Value != expected[i].Value {
			t.Errorf("Position %d: expected %+v, got %+v", i, expected[i], entry)
		}
	}
}

func TestForwardIteratorAcrossMultipleNodes(t *testing.T) {
	// Arrange - small capacity to ensure multiple nodes
	tree := New[int, string](4)
	for i := 0; i < 50; i++ {
		tree.Insert(i, "value")
	}

	// Act
	iter := tree.Iterator()
	lastKey := -1
	count := 0

	// Assert - verify order and count
	for iter.Next() {
		key := iter.Key()
		if key <= lastKey {
			t.Errorf("Keys not in order: %d <= %d", key, lastKey)
		}
		lastKey = key
		count++
	}

	if count != 50 {
		t.Errorf("Expected 50 elements, got %d", count)
	}
}

func TestReverseIteratorOnEmptyTree(t *testing.T) {
	// Arrange
	tree := New[int, string](128)

	// Act
	iter := tree.ReverseIterator()

	// Assert
	if iter.Next() {
		t.Error("Expected reverse iterator on empty tree to return false")
	}
}

func TestReverseIteratorSingleElement(t *testing.T) {
	// Arrange
	tree := New[int, string](128)
	tree.Insert(42, "answer")

	// Act
	iter := tree.ReverseIterator()

	// Assert
	if !iter.Next() {
		t.Fatal("Expected reverse iterator to have next element")
	}
	
	key, value := iter.Key(), iter.Value()
	if key != 42 || value != "answer" {
		t.Errorf("Expected (42, 'answer'), got (%d, '%s')", key, value)
	}

	if iter.Next() {
		t.Error("Expected no more elements")
	}
}

func TestReverseIteratorMultipleElements(t *testing.T) {
	// Arrange
	tree := New[int, int](128)
	for i := 0; i < 10; i++ {
		tree.Insert(i, i*10)
	}

	// Act
	iter := tree.ReverseIterator()
	var results []int
	for iter.Next() {
		results = append(results, iter.Key())
	}

	// Assert - should be in descending order
	expected := []int{9, 8, 7, 6, 5, 4, 3, 2, 1, 0}
	if len(results) != len(expected) {
		t.Fatalf("Expected %d elements, got %d", len(expected), len(results))
	}

	for i, key := range results {
		if key != expected[i] {
			t.Errorf("Position %d: expected %d, got %d", i, expected[i], key)
		}
	}
}

func TestIteratorWithNonSequentialInserts(t *testing.T) {
	// Arrange - insert in random order
	tree := New[int, string](128)
	keys := []int{50, 20, 80, 10, 30, 70, 90, 5, 15, 25}
	for _, k := range keys {
		tree.Insert(k, "value")
	}

	// Act - forward iteration
	iter := tree.Iterator()
	var forward []int
	for iter.Next() {
		forward = append(forward, iter.Key())
	}

	// Assert - should be sorted
	expected := []int{5, 10, 15, 20, 25, 30, 50, 70, 80, 90}
	if len(forward) != len(expected) {
		t.Fatalf("Expected %d elements, got %d", len(expected), len(forward))
	}

	for i, key := range forward {
		if key != expected[i] {
			t.Errorf("Position %d: expected %d, got %d", i, expected[i], key)
		}
	}

	// Act - reverse iteration
	revIter := tree.ReverseIterator()
	var reverse []int
	for revIter.Next() {
		reverse = append(reverse, revIter.Key())
	}

	// Assert - should be reverse sorted
	expectedReverse := []int{90, 80, 70, 50, 30, 25, 20, 15, 10, 5}
	for i, key := range reverse {
		if key != expectedReverse[i] {
			t.Errorf("Reverse position %d: expected %d, got %d", i, expectedReverse[i], key)
		}
	}
}

func TestContainsMethod(t *testing.T) {
	// Arrange
	tree := New[int, string](128)
	tree.Insert(10, "ten")
	tree.Insert(20, "twenty")
	tree.Insert(30, "thirty")

	// Act & Assert
	testCases := []struct {
		key      int
		expected bool
	}{
		{10, true},
		{20, true},
		{30, true},
		{15, false},
		{40, false},
		{0, false},
	}

	for _, tc := range testCases {
		if tree.Contains(tc.key) != tc.expected {
			t.Errorf("Contains(%d): expected %v", tc.key, tc.expected)
		}
	}
}

func TestClearMethod(t *testing.T) {
	// Arrange
	tree := New[int, int](128)
	for i := 0; i < 100; i++ {
		tree.Insert(i, i*10)
	}

	// Act
	tree.Clear()

	// Assert
	if tree.Len() != 0 {
		t.Errorf("Expected empty tree after clear, got %d items", tree.Len())
	}

	// Verify tree is usable after clear
	tree.Insert(42, 420)
	if tree.Len() != 1 {
		t.Errorf("Expected 1 item after insert, got %d", tree.Len())
	}

	value, found := tree.Get(42)
	if !found || value != 420 {
		t.Error("Failed to insert/retrieve after clear")
	}
}