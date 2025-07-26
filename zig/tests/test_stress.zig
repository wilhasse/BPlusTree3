const std = @import("std");
const testing = std.testing;
const bplustree = @import("bplustree");

test "stress test with random operations" {
    const allocator = testing.allocator;
    var prng = std.Random.DefaultPrng.init(42); // Fixed seed for reproducibility
    const random = prng.random();
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 32);
    defer tree.deinit();
    
    const num_operations = 10000;
    var expected_map = std.AutoHashMap(i32, i32).init(allocator);
    defer expected_map.deinit();
    
    // Perform random operations
    for (0..num_operations) |_| {
        const op = random.int(u8) % 100;
        const key = @mod(random.int(i32), 1000); // Keys in range [0, 999]
        
        if (op < 60) { // 60% inserts
            const value = random.int(i32);
            try tree.insert(key, value);
            try expected_map.put(key, value);
        } else if (op < 80) { // 20% deletes
            if (tree.remove(key)) |_| {
                _ = expected_map.remove(key);
            } else |_| {}
        } else { // 20% lookups
            const tree_val = tree.get(key);
            const map_val = expected_map.get(key);
            try testing.expectEqual(map_val, tree_val);
        }
    }
    
    // Verify final state
    try testing.expectEqual(expected_map.count(), tree.len());
    
    // Verify all entries match
    var map_iter = expected_map.iterator();
    while (map_iter.next()) |entry| {
        const tree_val = tree.get(entry.key_ptr.*);
        try testing.expectEqual(@as(?i32, entry.value_ptr.*), tree_val);
    }
    
    // Verify iterator returns all entries
    var tree_iter = tree.iterator();
    var count: usize = 0;
    var last_key: ?i32 = null;
    while (tree_iter.next()) |entry| {
        // Verify sorted order
        if (last_key) |lk| {
            try testing.expect(entry.key > lk);
        }
        last_key = entry.key;
        count += 1;
        
        // Verify value matches
        try testing.expectEqual(expected_map.get(entry.key).?, entry.value);
    }
    try testing.expectEqual(tree.len(), count);
}

test "stress test with sequential operations" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 64);
    defer tree.deinit();
    
    const n = 5000;
    
    // Insert in ascending order
    for (0..n) |i| {
        const key = @as(i32, @intCast(i));
        try tree.insert(key, key * 10);
    }
    try testing.expectEqual(@as(usize, n), tree.len());
    
    // Delete every third element
    var i: i32 = 0;
    while (i < n) : (i += 3) {
        _ = try tree.remove(i);
    }
    
    // Verify remaining elements
    const expected_count = n - (n + 2) / 3;
    try testing.expectEqual(expected_count, tree.len());
    
    // Insert in descending order
    i = @intCast(n - 1);
    while (i >= 0) : (i -= 1) {
        if (@mod(i, 3) == 0) {
            try tree.insert(i, i * 20);
        }
    }
    
    // Verify all elements
    for (0..n) |j| {
        const key = @as(i32, @intCast(j));
        if (tree.get(key)) |val| {
            if (@mod(key, 3) == 0) {
                try testing.expectEqual(key * 20, val); // Re-inserted
            } else {
                try testing.expectEqual(key * 10, val); // Original
            }
        }
    }
}

test "stress test with large dataset" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(u32, u32);
    var tree = Tree.init(allocator, 128);
    defer tree.deinit();
    
    const n = 100000;
    
    // Insert large dataset
    var timer = try std.time.Timer.start();
    for (0..n) |i| {
        try tree.insert(@intCast(i), @intCast(i * 2));
    }
    const insert_time = timer.read();
    
    try testing.expectEqual(@as(usize, n), tree.len());
    std.debug.print("\nInserted {} items in {}ms\n", .{ n, insert_time / 1_000_000 });
    
    // Random lookups
    timer.reset();
    var prng = std.Random.DefaultPrng.init(12345);
    const random = prng.random();
    
    for (0..10000) |_| {
        const key = random.int(u32) % n;
        const val = tree.get(key);
        try testing.expectEqual(@as(u32, key * 2), val.?);
    }
    const lookup_time = timer.read();
    std.debug.print("10000 random lookups in {}ms\n", .{lookup_time / 1_000_000});
    
    // Range query performance
    timer.reset();
    var results = std.ArrayList(Tree.Entry).init(allocator);
    defer results.deinit();
    
    const range_start = n / 4;
    const range_end = n / 2;
    try tree.range(@intCast(range_start), @intCast(range_end), &results);
    const range_time = timer.read();
    
    try testing.expectEqual(range_end - range_start + 1, results.items.len);
    std.debug.print("Range query [{}, {}] in {}ms\n", .{ range_start, range_end, range_time / 1_000_000 });
}

test "edge case: minimum capacity" {
    const allocator = testing.allocator;
    
    // Test with minimum capacity of 3
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 3);
    defer tree.deinit();
    
    // Insert enough to force multiple splits
    for (1..21) |i| {
        try tree.insert(@intCast(i), @intCast(i * 100));
    }
    
    // Verify all insertions worked
    try testing.expectEqual(@as(usize, 20), tree.len());
    try testing.expect(tree.getHeight() >= 2);
    
    // Verify all values are retrievable
    for (1..21) |i| {
        try testing.expectEqual(@as(i32, @intCast(i * 100)), tree.get(@intCast(i)).?);
    }
}

test "edge case: maximum capacity" {
    const allocator = testing.allocator;
    
    // Test with very large capacity
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 1024);
    defer tree.deinit();
    
    // Insert many items
    for (1..2001) |i| {
        try tree.insert(@intCast(i), @intCast(i));
    }
    
    // With large capacity, tree should be shallow
    try testing.expectEqual(@as(usize, 2000), tree.len());
    try testing.expect(tree.getHeight() <= 3);
    
    // Test range query on large node
    var results = std.ArrayList(Tree.Entry).init(allocator);
    defer results.deinit();
    
    try tree.range(500, 600, &results);
    try testing.expectEqual(@as(usize, 101), results.items.len);
}

test "edge case: duplicate insertions" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 16);
    defer tree.deinit();
    
    // Insert same key many times
    for (0..100) |i| {
        try tree.insert(42, @intCast(i));
    }
    
    // Should only have one entry
    try testing.expectEqual(@as(usize, 1), tree.len());
    
    // Should have the last value
    try testing.expectEqual(@as(i32, 99), tree.get(42).?);
}

test "edge case: alternating insert and delete" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 8);
    defer tree.deinit();
    
    // Alternating pattern
    for (0..1000) |i| {
        const key = @as(i32, @intCast(i));
        try tree.insert(key, key);
        
        // Delete previous key
        if (i > 0) {
            _ = try tree.remove(key - 1);
        }
    }
    
    // Should only have the last key
    try testing.expectEqual(@as(usize, 1), tree.len());
    try testing.expectEqual(@as(i32, 999), tree.get(999).?);
    
    // Re-insert all deleted keys
    for (0..999) |i| {
        const key = @as(i32, @intCast(i));
        try tree.insert(key, key * 2);
    }
    
    // Should have all keys now
    try testing.expectEqual(@as(usize, 1000), tree.len());
}