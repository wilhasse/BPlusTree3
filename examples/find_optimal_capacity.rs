use bplustree3::BPlusTreeMap;
use std::collections::BTreeMap;
use std::time::{Duration, Instant};

const ITERATIONS: usize = 10;
const INSERT_COUNT: usize = 10_000;
const LOOKUP_COUNT: usize = 100_000;
const ITER_COUNT: usize = 100;

fn benchmark_capacity(capacity: usize) -> (Duration, Duration, Duration) {
    let mut insert_times = Vec::new();
    let mut lookup_times = Vec::new();
    let mut iter_times = Vec::new();

    for _ in 0..ITERATIONS {
        let mut tree = BPlusTreeMap::new(capacity).unwrap();
        
        // Benchmark insertion
        let start = Instant::now();
        for i in 0..INSERT_COUNT {
            tree.insert(i, i.to_string());
        }
        insert_times.push(start.elapsed());
        
        // Benchmark lookup
        let start = Instant::now();
        for _ in 0..LOOKUP_COUNT / INSERT_COUNT {
            for i in 0..INSERT_COUNT {
                let _ = tree.get(&i);
            }
        }
        lookup_times.push(start.elapsed());
        
        // Benchmark iteration
        let start = Instant::now();
        for _ in 0..ITER_COUNT {
            let _: Vec<_> = tree.items().collect();
        }
        iter_times.push(start.elapsed());
    }
    
    // Return median times
    insert_times.sort();
    lookup_times.sort();
    iter_times.sort();
    
    (
        insert_times[ITERATIONS / 2],
        lookup_times[ITERATIONS / 2],
        iter_times[ITERATIONS / 2],
    )
}

fn benchmark_btreemap() -> (Duration, Duration, Duration) {
    let mut insert_times = Vec::new();
    let mut lookup_times = Vec::new();
    let mut iter_times = Vec::new();

    for _ in 0..ITERATIONS {
        let mut tree = BTreeMap::new();
        
        // Benchmark insertion
        let start = Instant::now();
        for i in 0..INSERT_COUNT {
            tree.insert(i, i.to_string());
        }
        insert_times.push(start.elapsed());
        
        // Benchmark lookup
        let start = Instant::now();
        for _ in 0..LOOKUP_COUNT / INSERT_COUNT {
            for i in 0..INSERT_COUNT {
                let _ = tree.get(&i);
            }
        }
        lookup_times.push(start.elapsed());
        
        // Benchmark iteration
        let start = Instant::now();
        for _ in 0..ITER_COUNT {
            let _: Vec<_> = tree.iter().collect();
        }
        iter_times.push(start.elapsed());
    }
    
    // Return median times
    insert_times.sort();
    lookup_times.sort();
    iter_times.sort();
    
    (
        insert_times[ITERATIONS / 2],
        lookup_times[ITERATIONS / 2],
        iter_times[ITERATIONS / 2],
    )
}

fn main() {
    println!("Finding Optimal B+ Tree Capacity");
    println!("================================");
    println!("Testing capacities from 4 to 256...\n");
    
    // First get BTreeMap baseline
    println!("Benchmarking BTreeMap baseline...");
    let (btree_insert, btree_lookup, btree_iter) = benchmark_btreemap();
    println!("BTreeMap results:");
    println!("  Insert: {:?}", btree_insert);
    println!("  Lookup: {:?}", btree_lookup);
    println!("  Iter:   {:?}\n", btree_iter);
    
    // Test different capacities
    let capacities = vec![4, 8, 16, 24, 32, 48, 64, 96, 128, 192, 256];
    
    println!("Capacity | Insert Ratio | Lookup Ratio | Iter Ratio | Combined Score");
    println!("---------|--------------|--------------|------------|---------------");
    
    let mut best_capacity = 4;
    let mut best_score = f64::MAX;
    
    for capacity in capacities {
        let (insert, lookup, iter) = benchmark_capacity(capacity);
        
        let insert_ratio = insert.as_secs_f64() / btree_insert.as_secs_f64();
        let lookup_ratio = lookup.as_secs_f64() / btree_lookup.as_secs_f64();
        let iter_ratio = iter.as_secs_f64() / btree_iter.as_secs_f64();
        
        // Combined score (lower is better) - weighted average
        // Weight lookups more heavily as they're most common
        let score = insert_ratio * 0.3 + lookup_ratio * 0.5 + iter_ratio * 0.2;
        
        println!(
            "{:>8} | {:>12.2} | {:>12.2} | {:>10.2} | {:>13.3}",
            capacity, insert_ratio, lookup_ratio, iter_ratio, score
        );
        
        if score < best_score {
            best_score = score;
            best_capacity = capacity;
        }
    }
    
    println!("\n🏆 Optimal capacity: {} (score: {:.3})", best_capacity, best_score);
    println!("\nNote: Score is weighted average (30% insert, 50% lookup, 20% iter)");
    println!("Lower scores are better (ratio < 1.0 means faster than BTreeMap)");
}