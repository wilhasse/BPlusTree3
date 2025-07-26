package bplustree

import (
	"testing"
)

func TestShouldCreateEmptyBPlusTree(t *testing.T) {
	// Arrange & Act
	tree := New[int, string](128)

	// Assert
	if tree == nil {
		t.Error("Expected tree to be created, got nil")
	}
	if tree.Len() != 0 {
		t.Errorf("Expected empty tree to have 0 items, got %d", tree.Len())
	}
}

func TestShouldInsertSingleKeyValuePair(t *testing.T) {
	// Arrange
	tree := New[int, string](128)

	// Act
	tree.Insert(42, "answer")

	// Assert
	if tree.Len() != 1 {
		t.Errorf("Expected tree to have 1 item, got %d", tree.Len())
	}
	
	value, found := tree.Get(42)
	if !found {
		t.Error("Expected to find key 42")
	}
	if value != "answer" {
		t.Errorf("Expected value 'answer', got '%s'", value)
	}
}

func TestShouldRetrieveInsertedValue(t *testing.T) {
	// Arrange
	tree := New[int, string](128)
	tree.Insert(10, "ten")
	tree.Insert(20, "twenty")
	tree.Insert(30, "thirty")

	// Act & Assert
	testCases := []struct {
		key      int
		expected string
		found    bool
	}{
		{10, "ten", true},
		{20, "twenty", true},
		{30, "thirty", true},
		{40, "", false},
	}

	for _, tc := range testCases {
		value, found := tree.Get(tc.key)
		if found != tc.found {
			t.Errorf("Key %d: expected found=%v, got %v", tc.key, tc.found, found)
		}
		if found && value != tc.expected {
			t.Errorf("Key %d: expected value '%s', got '%s'", tc.key, tc.expected, value)
		}
	}
}

func TestShouldHandleMultipleInsertions(t *testing.T) {
	// Arrange
	tree := New[int, int](128)

	// Act
	for i := 0; i < 100; i++ {
		tree.Insert(i, i*10)
	}

	// Assert
	if tree.Len() != 100 {
		t.Errorf("Expected tree to have 100 items, got %d", tree.Len())
	}

	// Verify some values
	for i := 0; i < 100; i += 10 {
		value, found := tree.Get(i)
		if !found {
			t.Errorf("Expected to find key %d", i)
		}
		if value != i*10 {
			t.Errorf("Key %d: expected value %d, got %d", i, i*10, value)
		}
	}
}

func TestShouldUpdateExistingKey(t *testing.T) {
	// Arrange
	tree := New[string, int](128)
	tree.Insert("key", 100)

	// Act
	tree.Insert("key", 200)

	// Assert
	if tree.Len() != 1 {
		t.Errorf("Expected tree to have 1 item after update, got %d", tree.Len())
	}

	value, found := tree.Get("key")
	if !found {
		t.Error("Expected to find 'key'")
	}
	if value != 200 {
		t.Errorf("Expected updated value 200, got %d", value)
	}
}

func TestShouldReturnNotFoundForNonExistentKey(t *testing.T) {
	// Arrange
	tree := New[int, string](128)
	tree.Insert(1, "one")
	tree.Insert(2, "two")

	// Act
	value, found := tree.Get(3)

	// Assert
	if found {
		t.Error("Expected not to find key 3")
	}
	if value != "" {
		t.Errorf("Expected empty value for non-existent key, got '%s'", value)
	}
}

func TestShouldHandleNodeSplitting(t *testing.T) {
	// Arrange - use small capacity to force splitting
	tree := New[int, string](4)

	// Act - insert enough to force splits
	for i := 0; i < 20; i++ {
		tree.Insert(i, "value")
	}

	// Assert
	if tree.Len() != 20 {
		t.Errorf("Expected tree to have 20 items, got %d", tree.Len())
	}

	// Tree should have height > 1 due to splits
	if tree.Height() <= 1 {
		t.Error("Expected tree height > 1 after splits")
	}

	// All values should still be retrievable
	for i := 0; i < 20; i++ {
		_, found := tree.Get(i)
		if !found {
			t.Errorf("Expected to find key %d after splits", i)
		}
	}
}