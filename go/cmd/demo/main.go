package main

import (
	"fmt"

	"github.com/example/bplustree/internal/bplustree"
)

func main() {
	fmt.Println("=== B+ Tree Demo ===")
	
	// Create a B+ tree with string keys and values
	tree := bplustree.New[string, string](4)
	
	// Insert some data
	fmt.Println("\nInserting data...")
	data := map[string]string{
		"apple":  "A sweet fruit",
		"banana": "A yellow fruit",
		"cherry": "A small red fruit",
		"date":   "A brown sweet fruit",
		"elderberry": "A dark purple berry",
		"fig":    "A soft sweet fruit",
		"grape":  "A small round fruit",
	}
	
	for key, value := range data {
		tree.Insert(key, value)
		fmt.Printf("  Inserted: %s -> %s\n", key, value)
	}
	
	fmt.Printf("\nTree now contains %d items\n", tree.Len())
	fmt.Printf("Tree height: %d\n", tree.Height())
	
	// Lookup some values
	fmt.Println("\nLooking up values:")
	lookupKeys := []string{"apple", "cherry", "kiwi", "grape"}
	for _, key := range lookupKeys {
		if value, found := tree.Get(key); found {
			fmt.Printf("  %s: %s\n", key, value)
		} else {
			fmt.Printf("  %s: (not found)\n", key)
		}
	}
	
	// Test Contains
	fmt.Println("\nTesting contains:")
	if tree.Contains("banana") {
		fmt.Println("  Tree contains 'banana'")
	}
	if !tree.Contains("kiwi") {
		fmt.Println("  Tree does not contain 'kiwi'")
	}
	
	// Range query
	fmt.Println("\nRange query ['b' to 'd']:")
	results := tree.Range("b", "d")
	for _, entry := range results {
		fmt.Printf("  %s: %s\n", entry.Key, entry.Value)
	}
	
	// Forward iteration
	fmt.Println("\nForward iteration (first 5):")
	iter := tree.Iterator()
	count := 0
	for iter.Next() && count < 5 {
		fmt.Printf("  %s: %s\n", iter.Key(), iter.Value())
		count++
	}
	
	// Reverse iteration
	fmt.Println("\nReverse iteration (first 5):")
	revIter := tree.ReverseIterator()
	count = 0
	for revIter.Next() && count < 5 {
		fmt.Printf("  %s: %s\n", revIter.Key(), revIter.Value())
		count++
	}
	
	// Delete some items
	fmt.Println("\nDeleting 'cherry' and 'date'...")
	if val, err := tree.Delete("cherry"); err == nil {
		fmt.Printf("  Deleted cherry: %s\n", val)
	}
	if val, err := tree.Delete("date"); err == nil {
		fmt.Printf("  Deleted date: %s\n", val)
	}
	
	fmt.Printf("\nTree now contains %d items\n", tree.Len())
	
	// Show remaining items
	fmt.Println("\nRemaining items:")
	iter = tree.Iterator()
	for iter.Next() {
		fmt.Printf("  %s: %s\n", iter.Key(), iter.Value())
	}
	
	// Clear the tree
	fmt.Println("\nClearing the tree...")
	tree.Clear()
	fmt.Printf("Tree now contains %d items\n", tree.Len())
	
	// Performance demo with integers
	fmt.Println("\n=== Performance Demo ===")
	intTree := bplustree.New[int, int](128)
	
	n := 10000
	fmt.Printf("\nInserting %d sequential integers...\n", n)
	for i := 0; i < n; i++ {
		intTree.Insert(i, i*10)
	}
	
	fmt.Printf("Tree contains %d items\n", intTree.Len())
	fmt.Printf("Tree height: %d\n", intTree.Height())
	
	// Random lookups
	fmt.Println("\nPerforming some random lookups...")
	testKeys := []int{42, 1337, 9999, 5000, 12345}
	for _, key := range testKeys {
		if val, found := intTree.Get(key); found {
			fmt.Printf("  Key %d: value %d\n", key, val)
		} else {
			fmt.Printf("  Key %d: not found\n", key)
		}
	}
	
	// Range query on integers
	fmt.Println("\nRange query [1000 to 1010]:")
	intResults := intTree.Range(1000, 1010)
	for _, entry := range intResults {
		fmt.Printf("  %d: %d\n", entry.Key, entry.Value)
	}
	
	fmt.Println("\nDemo complete!")
}