use bplustree::BPlusTreeMap;

fn main() {
    println!("B+ Tree Range Syntax Demo");
    println!("=========================");

    let mut tree = BPlusTreeMap::new(16).unwrap();

    // Insert some data
    for i in 0..20 {
        tree.insert(i, format!("value_{}", i));
    }

    println!(
        "Tree contains {} items: {:?}",
        tree.len(),
        tree.keys().cloned().collect::<Vec<_>>()
    );

    // Demonstrate different range syntaxes
    println!("\n1. Inclusive range 5..=10:");
    let range1: Vec<_> = tree.range(5..=10).map(|(k, v)| (*k, v.clone())).collect();
    println!("   {:?}", range1);

    println!("\n2. Exclusive range 5..10:");
    let range2: Vec<_> = tree.range(5..10).map(|(k, v)| (*k, v.clone())).collect();
    println!("   {:?}", range2);

    println!("\n3. Open-ended range 15..:");
    let range3: Vec<_> = tree.range(15..).map(|(k, v)| (*k, v.clone())).collect();
    println!("   {:?}", range3);

    println!("\n4. Range to 7:");
    let range4: Vec<_> = tree.range(..7).map(|(k, v)| (*k, v.clone())).collect();
    println!("   {:?}", range4);

    println!("\n5. Range to (inclusive) 7:");
    let range5: Vec<_> = tree.range(..=7).map(|(k, v)| (*k, v.clone())).collect();
    println!("   {:?}", range5);

    println!("\n6. Full range ..:");
    let range6: Vec<_> = tree.range(..).map(|(k, _v)| *k).collect();
    println!("   First 10: {:?}", &range6[0..10]);

    // Show that we can use any range type
    println!("\n7. Using custom excluded start bound:");
    use std::ops::{Bound, RangeBounds};

    struct CustomRange {
        start: i32,
        end: i32,
    }

    impl RangeBounds<i32> for CustomRange {
        fn start_bound(&self) -> Bound<&i32> {
            Bound::Excluded(&self.start) // Exclude start
        }

        fn end_bound(&self) -> Bound<&i32> {
            Bound::Included(&self.end) // Include end
        }
    }

    let custom_range = CustomRange { start: 5, end: 10 };
    let range7: Vec<_> = tree
        .range(custom_range)
        .map(|(k, v)| (*k, v.clone()))
        .collect();
    println!("   (5, 10] = {:?}", range7);

    // Demonstrate with strings
    println!("\n8. String range example:");
    let mut string_tree = BPlusTreeMap::new(16).unwrap();
    let fruits = [
        "apple",
        "banana",
        "cherry",
        "date",
        "elderberry",
        "fig",
        "grape",
    ];
    for fruit in &fruits {
        string_tree.insert(fruit.to_string(), format!("{}_info", fruit));
    }

    let fruit_range: Vec<_> = string_tree
        .range("cherry".to_string()..="fig".to_string())
        .map(|(k, v)| (k.clone(), v.clone()))
        .collect();
    println!("   \"cherry\"..=\"fig\": {:?}", fruit_range);

    println!("\nRange syntax makes B+ tree queries much more natural and Rust-idiomatic!");
}
