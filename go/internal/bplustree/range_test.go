package bplustree

import (
	"testing"
)

func TestShouldReturnEmptyRangeForEmptyTree(t *testing.T) {
	// Arrange
	tree := New[int, string](128)

	// Act
	results := tree.Range(1, 10)

	// Assert
	if len(results) != 0 {
		t.Errorf("Expected empty range for empty tree, got %d results", len(results))
	}
}

func TestShouldReturnKeysWithinRange(t *testing.T) {
	// Arrange
	tree := New[int, string](128)
	tree.Insert(1, "one")
	tree.Insert(5, "five")
	tree.Insert(10, "ten")
	tree.Insert(15, "fifteen")
	tree.Insert(20, "twenty")

	// Act
	results := tree.Range(5, 15)

	// Assert
	if len(results) != 3 {
		t.Errorf("Expected 3 results in range [5, 15], got %d", len(results))
	}

	// Verify results
	expected := []Entry[int, string]{
		{Key: 5, Value: "five"},
		{Key: 10, Value: "ten"},
		{Key: 15, Value: "fifteen"},
	}

	for i, entry := range results {
		if entry.Key != expected[i].Key || entry.Value != expected[i].Value {
			t.Errorf("Result %d: expected %+v, got %+v", i, expected[i], entry)
		}
	}
}

func TestShouldReturnEmptyRangeWhenNoKeysMatch(t *testing.T) {
	// Arrange
	tree := New[int, string](128)
	tree.Insert(1, "one")
	tree.Insert(2, "two")
	tree.Insert(10, "ten")

	// Act
	results := tree.Range(5, 8)

	// Assert
	if len(results) != 0 {
		t.Errorf("Expected empty range for [5, 8], got %d results", len(results))
	}
}

func TestShouldHandleRangeAcrossMultipleNodes(t *testing.T) {
	// Arrange - small capacity to ensure multiple nodes
	tree := New[int, int](4)
	for i := 0; i < 50; i++ {
		tree.Insert(i, i*10)
	}

	// Act
	results := tree.Range(20, 30)

	// Assert
	if len(results) != 11 {
		t.Errorf("Expected 11 results in range [20, 30], got %d", len(results))
	}

	// Verify results are in order and correct
	for i, entry := range results {
		expectedKey := 20 + i
		if entry.Key != expectedKey {
			t.Errorf("Result %d: expected key %d, got %d", i, expectedKey, entry.Key)
		}
		if entry.Value != expectedKey*10 {
			t.Errorf("Result %d: expected value %d, got %d", i, expectedKey*10, entry.Value)
		}
	}
}

func TestShouldHandleSingleKeyRange(t *testing.T) {
	// Arrange
	tree := New[int, string](128)
	tree.Insert(5, "five")
	tree.Insert(10, "ten")
	tree.Insert(15, "fifteen")

	// Act
	results := tree.Range(10, 10)

	// Assert
	if len(results) != 1 {
		t.Errorf("Expected 1 result for single key range, got %d", len(results))
	}
	if results[0].Key != 10 || results[0].Value != "ten" {
		t.Errorf("Expected {10, 'ten'}, got %+v", results[0])
	}
}

func TestShouldHandleRangeBoundaries(t *testing.T) {
	// Arrange
	tree := New[int, int](128)
	for i := 0; i < 20; i++ {
		tree.Insert(i, i)
	}

	// Test cases for different boundary conditions
	testCases := []struct {
		start    int
		end      int
		expected int
	}{
		{0, 19, 20},   // Full range
		{-5, 5, 6},    // Start before min
		{15, 25, 5},   // End after max
		{-10, -5, 0},  // Both before min
		{25, 30, 0},   // Both after max
		{10, 5, 0},    // Invalid range (start > end)
	}

	for _, tc := range testCases {
		results := tree.Range(tc.start, tc.end)
		if len(results) != tc.expected {
			t.Errorf("Range [%d, %d]: expected %d results, got %d", 
				tc.start, tc.end, tc.expected, len(results))
		}
	}
}