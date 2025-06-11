use bplustree::BPlusTreeMap;

fn main() {
    println!("Running README examples...");

    // Quick Start example
    quick_start_example();

    // API examples
    api_examples();

    // Range query examples
    range_query_examples();

    // Time series example
    time_series_example();

    println!("All examples completed successfully!");
}

fn quick_start_example() {
    println!("\n=== Quick Start Example ===");

    let mut tree = BPlusTreeMap::new(4).unwrap();

    // Insert some data
    tree.insert(1, "one");
    tree.insert(3, "three");
    tree.insert(2, "two");

    // Range query
    let range: Vec<_> = tree.items_range(Some(&1), Some(&2)).collect();
    println!("Range [1,2]: {:?}", range); // [(&1, &"one"), (&2, &"two")]

    // Sequential access
    println!("All entries in order:");
    for (key, value) in tree.slice() {
        println!("  {}: {}", key, value);
    }
}

fn api_examples() {
    println!("\n=== API Examples ===");

    let mut tree = BPlusTreeMap::new(4).unwrap();

    // Insert key-value pairs
    tree.insert(10, "ten");
    tree.insert(20, "twenty");
    tree.insert(5, "five");

    // Get values by key
    assert_eq!(tree.get(&10), Some(&"ten"));
    assert_eq!(tree.get(&99), None);
    println!("Get 10: {:?}", tree.get(&10));
    println!("Get 99: {:?}", tree.get(&99));

    // Update existing keys (returns old value)
    let old_value = tree.insert(10, "TEN");
    assert_eq!(old_value, Some("ten"));
    println!("Updated 10, old value: {:?}", old_value);

    // Check tree properties
    assert_eq!(tree.len(), 3);
    assert!(!tree.is_empty());
    println!("Tree length: {}", tree.len());
    println!("Tree empty: {}", tree.is_empty());
}

fn range_query_examples() {
    println!("\n=== Range Query Examples ===");

    let mut tree = BPlusTreeMap::new(4).unwrap();
    tree.insert(5, "five");
    tree.insert(10, "ten");
    tree.insert(15, "fifteen");
    tree.insert(20, "twenty");
    tree.insert(25, "twenty-five");

    // Get all entries in a range
    let entries: Vec<_> = tree.items_range(Some(&5), Some(&15)).collect();
    println!("Range [5,15]: {:?}", entries);

    // Get all entries from a minimum key
    let entries: Vec<_> = tree.items_range(Some(&15), None).collect();
    println!("Range [15,∞): {:?}", entries);

    // Get all entries up to a maximum key
    let entries: Vec<_> = tree.items_range(None, Some(&15)).collect();
    println!("Range (-∞,15]: {:?}", entries);

    // Get all entries in sorted order
    let all_entries = tree.slice();
    println!("All entries: {:?}", all_entries);
}

fn time_series_example() {
    println!("\n=== Time Series Example ===");

    let mut time_series = BPlusTreeMap::new(16).unwrap();

    // Insert timestamped data
    time_series.insert(1640995200, "2022-01-01 data");
    time_series.insert(1641081600, "2022-01-02 data");
    time_series.insert(1641168000, "2022-01-03 data");
    time_series.insert(1641254400, "2022-01-04 data");

    // Efficient range query for a time period
    let start_time = 1640995200;
    let end_time = 1641168000;
    let period_data: Vec<_> = time_series
        .items_range(Some(&start_time), Some(&end_time))
        .collect();

    println!("Time series data from {} to {}:", start_time, end_time);
    for (timestamp, data) in period_data {
        println!("  {}: {}", timestamp, data);
    }

    // Sequential scan
    println!("All time series data:");
    for (timestamp, data) in time_series.slice() {
        println!("  {}: {}", timestamp, data);
    }
}
