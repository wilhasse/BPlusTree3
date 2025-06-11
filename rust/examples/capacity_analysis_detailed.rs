use bplustree::BPlusTreeMap;
use std::time::{Duration, Instant};

const ITERATIONS: usize = 5;
const INSERT_COUNT: usize = 10_000;
const LOOKUP_COUNT: usize = 100_000;
const ITER_COUNT: usize = 100;

fn benchmark_capacity(capacity: usize) -> (Duration, Duration, Duration, usize, usize) {
    let mut insert_times = Vec::new();
    let mut lookup_times = Vec::new();
    let mut iter_times = Vec::new();
    let mut leaf_counts = Vec::new();
    let mut free_counts = Vec::new();

    for _ in 0..ITERATIONS {
        let mut tree = BPlusTreeMap::new(capacity).unwrap();

        // Benchmark insertion
        let start = Instant::now();
        for i in 0..INSERT_COUNT {
            tree.insert(i, i.to_string());
        }
        insert_times.push(start.elapsed());

        // Record tree statistics
        leaf_counts.push(tree.leaf_count());
        free_counts.push(tree.free_leaf_count());

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

    // Return median times and average stats
    insert_times.sort();
    lookup_times.sort();
    iter_times.sort();

    (
        insert_times[ITERATIONS / 2],
        lookup_times[ITERATIONS / 2],
        iter_times[ITERATIONS / 2],
        leaf_counts.iter().sum::<usize>() / leaf_counts.len(),
        free_counts.iter().sum::<usize>() / free_counts.len(),
    )
}

fn main() {
    println!("Detailed B+ Tree Capacity Analysis");
    println!("==================================");
    println!("Dataset: {} items\n", INSERT_COUNT);

    // Test capacities
    let capacities = vec![4, 8, 16, 32, 64, 128, 256, 512];

    println!("Cap | Leaves | Free | Avg Fill | Insert(µs) | Lookup(µs) | Iter(µs) | Efficiency");
    println!("----|--------|------|----------|------------|------------|----------|------------");

    for capacity in capacities {
        let (insert, lookup, iter, leaves, free) = benchmark_capacity(capacity);

        let avg_fill = (INSERT_COUNT as f64) / (leaves as f64 * capacity as f64) * 100.0;
        let efficiency = (INSERT_COUNT as f64) / ((leaves + free) as f64 * capacity as f64) * 100.0;

        println!(
            "{:>3} | {:>6} | {:>4} | {:>7.1}% | {:>10.0} | {:>10.0} | {:>8.0} | {:>9.1}%",
            capacity,
            leaves,
            free,
            avg_fill,
            insert.as_micros(),
            lookup.as_micros() / (LOOKUP_COUNT as u128 / INSERT_COUNT as u128),
            iter.as_micros() / ITER_COUNT as u128,
            efficiency
        );
    }

    println!("\nLegend:");
    println!("- Cap: Node capacity");
    println!("- Leaves: Number of leaf nodes");
    println!("- Free: Number of deallocated leaves in free list");
    println!("- Avg Fill: Average leaf utilization");
    println!("- Efficiency: Space efficiency (including free list)");

    // Memory analysis
    println!("\nMemory Analysis (approximate):");
    println!("Cap | Leaf Size | Total Leaves | Memory Used | Overhead");
    println!("----|-----------|--------------|-------------|----------");

    for capacity in vec![4, 8, 16, 32, 64, 128, 256] {
        let (_, _, _, leaves, free) = benchmark_capacity(capacity);

        // Approximate memory per leaf (keys + values + overhead)
        let key_size = std::mem::size_of::<i32>();
        let value_size = std::mem::size_of::<String>() + 10; // String overhead + avg content
        let leaf_overhead = 32; // Vec overhead, next pointer, etc.
        let leaf_size = capacity * (key_size + value_size) + leaf_overhead;

        let total_memory = (leaves + free) * leaf_size;
        let overhead =
            ((total_memory as f64 / (INSERT_COUNT * (key_size + value_size)) as f64) - 1.0) * 100.0;

        println!(
            "{:>3} | {:>9} | {:>12} | {:>11} | {:>7.1}%",
            capacity,
            format!("{} B", leaf_size),
            leaves + free,
            format!("{:.1} KB", total_memory as f64 / 1024.0),
            overhead
        );
    }
}
