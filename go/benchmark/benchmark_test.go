package benchmark

import (
	"fmt"
	"math/rand"
	"testing"

	"github.com/example/bplustree/internal/bplustree"
)

func BenchmarkInsertionWithDifferentCapacities(b *testing.B) {
	capacities := []int{8, 16, 32, 64, 128, 256}
	n := 100000
	
	for _, capacity := range capacities {
		b.Run(fmt.Sprintf("capacity-%d", capacity), func(b *testing.B) {
			b.ResetTimer()
			for i := 0; i < b.N; i++ {
				tree := bplustree.New[int, int](capacity)
				for j := 0; j < n; j++ {
					tree.Insert(j, j)
				}
			}
		})
	}
}

func BenchmarkSequentialInsert(b *testing.B) {
	tree := bplustree.New[int, int](128)
	b.ResetTimer()
	
	for i := 0; i < b.N; i++ {
		tree.Insert(i, i)
	}
}

func BenchmarkRandomInsert(b *testing.B) {
	tree := bplustree.New[int, int](128)
	rng := rand.New(rand.NewSource(12345))
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		key := rng.Int()
		tree.Insert(key, key)
	}
}

func BenchmarkSequentialLookup(b *testing.B) {
	tree := bplustree.New[int, int](128)
	n := 100000
	
	// Pre-populate
	for i := 0; i < n; i++ {
		tree.Insert(i, i)
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		tree.Get(i % n)
	}
}

func BenchmarkRandomLookup(b *testing.B) {
	tree := bplustree.New[int, int](128)
	n := 100000
	rng := rand.New(rand.NewSource(54321))
	
	// Pre-populate
	for i := 0; i < n; i++ {
		tree.Insert(i, i)
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		key := rng.Intn(n)
		tree.Get(key)
	}
}

func BenchmarkContains(b *testing.B) {
	tree := bplustree.New[int, int](128)
	n := 100000
	
	// Pre-populate
	for i := 0; i < n; i++ {
		tree.Insert(i, i*10)
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		tree.Contains(i % n)
	}
}

func BenchmarkRandomDelete(b *testing.B) {
	n := 100000
	rng := rand.New(rand.NewSource(99999))
	
	// Pre-populate tree for each iteration
	b.StopTimer()
	tree := bplustree.New[int, int](128)
	for i := 0; i < n; i++ {
		tree.Insert(i, i)
	}
	b.StartTimer()
	
	for i := 0; i < b.N && tree.Len() > 0; i++ {
		key := rng.Intn(n)
		tree.Delete(key)
	}
}

func BenchmarkRangeQuery(b *testing.B) {
	tree := bplustree.New[int, int](128)
	n := 100000
	
	// Pre-populate
	for i := 0; i < n; i++ {
		tree.Insert(i, i)
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		start := (i * 1000) % n
		end := start + 1000
		if end > n {
			end = n
		}
		_ = tree.Range(start, end)
	}
}

func BenchmarkFullIteration(b *testing.B) {
	tree := bplustree.New[int, int](128)
	n := 100000
	
	// Pre-populate
	for i := 0; i < n; i++ {
		tree.Insert(i, i)
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		iter := tree.Iterator()
		count := 0
		for iter.Next() {
			count++
		}
		if count != n {
			b.Fatalf("Expected %d items, got %d", n, count)
		}
	}
}

func BenchmarkMixedOperations(b *testing.B) {
	tree := bplustree.New[int, int](128)
	rng := rand.New(rand.NewSource(42))
	
	// Pre-populate
	for i := 0; i < 10000; i++ {
		tree.Insert(i, i)
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		op := rng.Intn(100)
		key := rng.Intn(20000)
		
		switch {
		case op < 30: // 30% insert
			tree.Insert(key, key)
		case op < 60: // 30% lookup
			tree.Get(key)
		case op < 80: // 20% delete
			tree.Delete(key)
		default: // 20% contains
			tree.Contains(key)
		}
	}
}