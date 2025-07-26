use criterion::{black_box, criterion_group, criterion_main, Criterion, BenchmarkId};
use bplustree::BPlusTreeMap;
use std::collections::BTreeMap;
use rand::prelude::*;

/// Simple comparison benchmark aligned with Go and Zig implementations
/// Compares B+ Tree vs BTreeMap for basic operations

fn benchmark_sequential_insert(c: &mut Criterion) {
    let mut group = c.benchmark_group("SequentialInsert");
    let sizes = [100, 1000, 10000, 100000];
    
    for size in sizes {
        // B+ Tree
        group.bench_with_input(BenchmarkId::new("BPlusTree", size), &size, |b, &size| {
            b.iter(|| {
                let mut tree = BPlusTreeMap::new(128).unwrap();
                for i in 0..size {
                    tree.insert(black_box(i), black_box(i * 2));
                }
                tree
            });
        });
        
        // BTreeMap
        group.bench_with_input(BenchmarkId::new("BTreeMap", size), &size, |b, &size| {
            b.iter(|| {
                let mut btree = BTreeMap::new();
                for i in 0..size {
                    btree.insert(black_box(i), black_box(i * 2));
                }
                btree
            });
        });
    }
    
    group.finish();
}

fn benchmark_random_insert(c: &mut Criterion) {
    let mut group = c.benchmark_group("RandomInsert");
    let sizes = [100, 1000, 10000, 100000];
    
    for size in sizes {
        // Pre-generate random keys
        let mut rng = StdRng::seed_from_u64(42);
        let keys: Vec<i32> = (0..size).map(|_| rng.gen_range(0..size*10)).collect();
        
        // B+ Tree
        group.bench_with_input(BenchmarkId::new("BPlusTree", size), &size, |b, &size| {
            b.iter(|| {
                let mut tree = BPlusTreeMap::new(128).unwrap();
                for &key in &keys {
                    tree.insert(black_box(key), black_box(key * 2));
                }
                tree
            });
        });
        
        // BTreeMap
        group.bench_with_input(BenchmarkId::new("BTreeMap", size), &size, |b, &size| {
            b.iter(|| {
                let mut btree = BTreeMap::new();
                for &key in &keys {
                    btree.insert(black_box(key), black_box(key * 2));
                }
                btree
            });
        });
    }
    
    group.finish();
}

fn benchmark_lookup(c: &mut Criterion) {
    let mut group = c.benchmark_group("Lookup");
    let sizes = [100, 1000, 10000, 100000];
    
    for size in sizes {
        // Pre-populate structures
        let mut tree = BPlusTreeMap::new(128).unwrap();
        let mut btree = BTreeMap::new();
        for i in 0..size {
            tree.insert(i, i * 2);
            btree.insert(i, i * 2);
        }
        
        // Generate random lookup keys
        let mut rng = StdRng::seed_from_u64(42);
        let lookup_keys: Vec<i32> = (0..1000).map(|_| rng.gen_range(0..size)).collect();
        
        // B+ Tree
        group.bench_with_input(BenchmarkId::new("BPlusTree", size), &size, |b, _| {
            b.iter(|| {
                for &key in &lookup_keys {
                    black_box(tree.get(&black_box(key)));
                }
            });
        });
        
        // BTreeMap
        group.bench_with_input(BenchmarkId::new("BTreeMap", size), &size, |b, _| {
            b.iter(|| {
                for &key in &lookup_keys {
                    black_box(btree.get(&black_box(key)));
                }
            });
        });
    }
    
    group.finish();
}

fn benchmark_iteration(c: &mut Criterion) {
    let mut group = c.benchmark_group("Iteration");
    let sizes = [100, 1000, 10000]; // Skip 100k for iteration to keep it fast
    
    for size in sizes {
        // Pre-populate structures
        let mut tree = BPlusTreeMap::new(128).unwrap();
        let mut btree = BTreeMap::new();
        for i in 0..size {
            tree.insert(i, i * 2);
            btree.insert(i, i * 2);
        }
        
        // B+ Tree
        group.bench_with_input(BenchmarkId::new("BPlusTree", size), &size, |b, _| {
            b.iter(|| {
                let mut count = 0;
                for (k, v) in tree.range(..) {
                    black_box((k, v));
                    count += 1;
                }
                count
            });
        });
        
        // BTreeMap
        group.bench_with_input(BenchmarkId::new("BTreeMap", size), &size, |b, _| {
            b.iter(|| {
                let mut count = 0;
                for (k, v) in btree.iter() {
                    black_box((k, v));
                    count += 1;
                }
                count
            });
        });
    }
    
    group.finish();
}

fn benchmark_range_query(c: &mut Criterion) {
    let mut group = c.benchmark_group("RangeQuery");
    let sizes = [100, 1000, 10000];
    
    for size in sizes {
        // Pre-populate structures
        let mut tree = BPlusTreeMap::new(128).unwrap();
        let mut btree = BTreeMap::new();
        for i in 0..size {
            tree.insert(i, i * 2);
            btree.insert(i, i * 2);
        }
        
        let range_start = size / 4;
        let range_end = range_start + size / 10;
        
        // B+ Tree
        group.bench_with_input(BenchmarkId::new("BPlusTree", size), &size, |b, _| {
            b.iter(|| {
                let mut count = 0;
                for (k, v) in tree.range(black_box(range_start)..black_box(range_end)) {
                    black_box((k, v));
                    count += 1;
                }
                count
            });
        });
        
        // BTreeMap  
        group.bench_with_input(BenchmarkId::new("BTreeMap", size), &size, |b, _| {
            b.iter(|| {
                let mut count = 0;
                for (k, v) in btree.range(black_box(range_start)..black_box(range_end)) {
                    black_box((k, v));
                    count += 1;
                }
                count
            });
        });
    }
    
    group.finish();
}

criterion_group!(
    benches,
    benchmark_sequential_insert,
    benchmark_random_insert,
    benchmark_lookup,
    benchmark_iteration,
    benchmark_range_query
);
criterion_main!(benches);