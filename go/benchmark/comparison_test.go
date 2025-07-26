package benchmark

import (
	"fmt"
	"math/rand"
	"sync"
	"testing"

	"github.com/example/bplustree/internal/bplustree"
)

// Compare B+ Tree with Go's built-in map and sync.Map

func BenchmarkComparison(b *testing.B) {
	sizes := []int{100, 1000, 10000, 100000}
	
	for _, size := range sizes {
		b.Run(fmt.Sprintf("Size-%d", size), func(b *testing.B) {
			// Prepare data
			keys := make([]int, size)
			for i := range keys {
				keys[i] = i
			}
			
			// Shuffle for random access
			shuffled := make([]int, size)
			copy(shuffled, keys)
			rand.Shuffle(len(shuffled), func(i, j int) {
				shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
			})
			
			// Sequential Insertion
			b.Run("SequentialInsert/BPlusTree", func(b *testing.B) {
				b.ResetTimer()
				for i := 0; i < b.N; i++ {
					tree := bplustree.New[int, int](128)
					for j := 0; j < size; j++ {
						tree.Insert(j, j*2)
					}
				}
			})
			
			b.Run("SequentialInsert/Map", func(b *testing.B) {
				b.ResetTimer()
				for i := 0; i < b.N; i++ {
					m := make(map[int]int, size)
					for j := 0; j < size; j++ {
						m[j] = j * 2
					}
				}
			})
			
			b.Run("SequentialInsert/SyncMap", func(b *testing.B) {
				b.ResetTimer()
				for i := 0; i < b.N; i++ {
					var m sync.Map
					for j := 0; j < size; j++ {
						m.Store(j, j*2)
					}
				}
			})
			
			// Random Insertion
			b.Run("RandomInsert/BPlusTree", func(b *testing.B) {
				b.ResetTimer()
				for i := 0; i < b.N; i++ {
					tree := bplustree.New[int, int](128)
					for _, k := range shuffled {
						tree.Insert(k, k*2)
					}
				}
			})
			
			b.Run("RandomInsert/Map", func(b *testing.B) {
				b.ResetTimer()
				for i := 0; i < b.N; i++ {
					m := make(map[int]int, size)
					for _, k := range shuffled {
						m[k] = k * 2
					}
				}
			})
			
			// Prepare populated structures for lookup
			tree := bplustree.New[int, int](128)
			m := make(map[int]int, size)
			var sm sync.Map
			
			for i := 0; i < size; i++ {
				tree.Insert(i, i*2)
				m[i] = i * 2
				sm.Store(i, i*2)
			}
			
			// Lookup
			b.Run("Lookup/BPlusTree", func(b *testing.B) {
				b.ResetTimer()
				for i := 0; i < b.N; i++ {
					for _, k := range shuffled[:min(1000, size)] {
						tree.Get(k)
					}
				}
			})
			
			b.Run("Lookup/Map", func(b *testing.B) {
				b.ResetTimer()
				for i := 0; i < b.N; i++ {
					for _, k := range shuffled[:min(1000, size)] {
						_ = m[k]
					}
				}
			})
			
			b.Run("Lookup/SyncMap", func(b *testing.B) {
				b.ResetTimer()
				for i := 0; i < b.N; i++ {
					for _, k := range shuffled[:min(1000, size)] {
						sm.Load(k)
					}
				}
			})
			
			// Iteration (only meaningful for B+ Tree and range over map)
			if size <= 10000 { // Limit iteration tests to smaller sizes
				b.Run("Iteration/BPlusTree", func(b *testing.B) {
					b.ResetTimer()
					for i := 0; i < b.N; i++ {
						iter := tree.Iterator()
						count := 0
						for iter.Next() {
							count++
						}
						if count != size {
							b.Fatalf("Expected %d items, got %d", size, count)
						}
					}
				})
				
				b.Run("Iteration/Map", func(b *testing.B) {
					b.ResetTimer()
					for i := 0; i < b.N; i++ {
						count := 0
						for range m {
							count++
						}
						if count != size {
							b.Fatalf("Expected %d items, got %d", size, count)
						}
					}
				})
				
				// Range Query (B+ Tree only)
				b.Run("RangeQuery/BPlusTree", func(b *testing.B) {
					start := size / 4
					end := start + size/10
					b.ResetTimer()
					for i := 0; i < b.N; i++ {
						results := tree.Range(start, end)
						if len(results) == 0 && size > 10 {
							b.Fatal("Range query returned no results")
						}
					}
				})
			}
		})
	}
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// Detailed comparison output
func TestComparisonSummary(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping comparison summary in short mode")
	}
	
	fmt.Println("\n=== B+ Tree vs Map/SyncMap Comparison Summary ===\n")
	
	fmt.Println("B+ Tree advantages:")
	fmt.Println("  ✓ Ordered keys - iteration in sorted order")
	fmt.Println("  ✓ Efficient range queries O(log n + k)")
	fmt.Println("  ✓ Better memory locality for sequential access")
	fmt.Println("  ✓ Predictable worst-case performance")
	fmt.Println("  ✓ Support for custom key types with ordering")
	
	fmt.Println("\nMap advantages:")
	fmt.Println("  ✓ O(1) average case for all operations")
	fmt.Println("  ✓ Simpler implementation")
	fmt.Println("  ✓ Lower memory overhead for small datasets")
	fmt.Println("  ✓ Faster for purely random access patterns")
	
	fmt.Println("\nSyncMap advantages:")
	fmt.Println("  ✓ Thread-safe without external locking")
	fmt.Println("  ✓ Optimized for concurrent access")
	fmt.Println("  ✓ Good for read-heavy workloads")
	
	fmt.Println("\nUse B+ Tree when:")
	fmt.Println("  - You need ordered iteration")
	fmt.Println("  - You need range queries")
	fmt.Println("  - You have sequential access patterns")
	fmt.Println("  - You need predictable performance")
	
	fmt.Println("\nUse Map when:")
	fmt.Println("  - You only need key-value lookups")
	fmt.Println("  - Access patterns are random")
	fmt.Println("  - Dataset is relatively small")
	fmt.Println("  - Simplicity is important")
}