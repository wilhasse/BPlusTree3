package bplustree

import (
	"testing"
)

func TestShouldDeleteSingleKey(t *testing.T) {
	// Arrange
	tree := New[int, string](128)
	tree.Insert(1, "one")
	tree.Insert(2, "two")
	tree.Insert(3, "three")

	// Act
	value, err := tree.Delete(2)

	// Assert
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
	if value != "two" {
		t.Errorf("Expected deleted value 'two', got '%s'", value)
	}
	if tree.Len() != 2 {
		t.Errorf("Expected tree to have 2 items after deletion, got %d", tree.Len())
	}

	// Verify key is deleted
	_, found := tree.Get(2)
	if found {
		t.Error("Expected key 2 to be deleted")
	}

	// Verify other keys still exist
	v1, found1 := tree.Get(1)
	v3, found3 := tree.Get(3)
	if !found1 || v1 != "one" {
		t.Error("Key 1 should still exist with value 'one'")
	}
	if !found3 || v3 != "three" {
		t.Error("Key 3 should still exist with value 'three'")
	}
}

func TestShouldReturnErrorWhenDeletingNonExistentKey(t *testing.T) {
	// Arrange
	tree := New[int, string](128)
	tree.Insert(1, "one")

	// Act
	_, err := tree.Delete(2)

	// Assert
	if err == nil {
		t.Error("Expected error when deleting non-existent key")
	}
	if err != ErrKeyNotFound {
		t.Errorf("Expected ErrKeyNotFound, got %v", err)
	}
}

func TestShouldDeleteFromEmptyTree(t *testing.T) {
	// Arrange
	tree := New[int, string](128)

	// Act
	_, err := tree.Delete(1)

	// Assert
	if err != ErrKeyNotFound {
		t.Errorf("Expected ErrKeyNotFound for empty tree, got %v", err)
	}
}

func TestShouldDeleteAllKeys(t *testing.T) {
	// Arrange
	tree := New[int, int](128)
	for i := 0; i < 10; i++ {
		tree.Insert(i, i*10)
	}

	// Act - delete all keys
	for i := 0; i < 10; i++ {
		value, err := tree.Delete(i)
		if err != nil {
			t.Errorf("Failed to delete key %d: %v", i, err)
		}
		if value != i*10 {
			t.Errorf("Expected value %d, got %d", i*10, value)
		}
	}

	// Assert
	if tree.Len() != 0 {
		t.Errorf("Expected empty tree after deleting all keys, got %d items", tree.Len())
	}
}