use bplustree3::BPlusTreeMap;
use std::collections::BTreeMap;
use std::time::Instant;

fn bench_insertions() {
    let sizes = [1000, 10000];
    
    println!("=== INSERTION BENCHMARKS ===");
    for &size in &sizes {
        // BTreeMap
        let start = Instant::now();
        let mut btree = BTreeMap::new();
        for i in 0..size {
            btree.insert(i, i * 2);
        }
        let btree_time = start.elapsed();
        
        // BPlusTreeMap
        let start = Instant::now();
        let mut bplus = BPlusTreeMap::new(16).unwrap();
        for i in 0..size {
            bplus.insert(i, i * 2);
        }
        let bplus_time = start.elapsed();
        
        let ratio = bplus_time.as_nanos() as f64 / btree_time.as_nanos() as f64;
        println!("Size {}: BTreeMap={:?}, BPlusTree={:?}, Ratio={:.2}x", 
                 size, btree_time, bplus_time, ratio);
    }
}

fn bench_lookups() {
    let size = 10000;
    
    // Pre-populate
    let mut btree = BTreeMap::new();
    let mut bplus = BPlusTreeMap::new(16).unwrap();
    for i in 0..size {
        btree.insert(i, i * 2);
        bplus.insert(i, i * 2);
    }
    
    println!("\n=== LOOKUP BENCHMARKS ===");
    let iterations = 10000;
    
    // BTreeMap lookups
    let start = Instant::now();
    for i in 0..iterations {
        let key = i % size;
        let _ = btree.get(&key);
    }
    let btree_time = start.elapsed();
    
    // BPlusTreeMap lookups  
    let start = Instant::now();
    for i in 0..iterations {
        let key = i % size;
        let _ = bplus.get(&key);
    }
    let bplus_time = start.elapsed();
    
    let ratio = bplus_time.as_nanos() as f64 / btree_time.as_nanos() as f64;
    println!("Lookups ({}): BTreeMap={:?}, BPlusTree={:?}, Ratio={:.2}x", 
             iterations, btree_time, bplus_time, ratio);
}

fn bench_iteration() {
    let size = 10000;
    
    // Pre-populate
    let mut btree = BTreeMap::new();
    let mut bplus = BPlusTreeMap::new(16).unwrap();
    for i in 0..size {
        btree.insert(i, i * 2);
        bplus.insert(i, i * 2);
    }
    
    println!("\n=== ITERATION BENCHMARKS ===");
    
    // BTreeMap iteration
    let start = Instant::now();
    for _ in 0..100 {
        for (k, v) in btree.iter() {
            let _ = (k, v); // Consume values
        }
    }
    let btree_time = start.elapsed();
    
    // BPlusTreeMap iteration
    let start = Instant::now();
    for _ in 0..100 {
        for (k, v) in bplus.items() {
            let _ = (k, v); // Consume values
        }
    }
    let bplus_time = start.elapsed();
    
    let ratio = bplus_time.as_nanos() as f64 / btree_time.as_nanos() as f64;
    println!("Iteration (100x): BTreeMap={:?}, BPlusTree={:?}, Ratio={:.2}x", 
             btree_time, bplus_time, ratio);
}

fn main() {
    println!("Quick Performance Comparison: BPlusTreeMap vs BTreeMap");
    println!("========================================================");
    
    bench_insertions();
    bench_lookups();
    bench_iteration();
    
    println!("\nNote: Ratio shows BPlusTree time / BTreeMap time");
    println!("      < 1.0 = BPlusTree faster, > 1.0 = BTreeMap faster");
}