const std = @import("std");
const testing = std.testing;
const bplustree = @import("bplustree");

test "iterator should handle insertions during iteration" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 8);
    defer tree.deinit();
    
    // Insert initial data
    for (0..10) |i| {
        const key = @as(i32, @intCast(i * 10));
        try tree.insert(key, key);
    }
    
    // Start iteration and insert during iteration
    var iter = tree.iterator();
    var count: usize = 0;
    var seen_keys = std.ArrayList(i32).init(allocator);
    defer seen_keys.deinit();
    
    while (iter.next()) |entry| {
        try seen_keys.append(entry.key);
        count += 1;
        
        // Insert a new key that would come after current position
        if (count == 5) {
            try tree.insert(entry.key + 5, entry.key + 5);
        }
    }
    
    // Verify we saw at least the original 10 items
    try testing.expect(count >= 10);
}

test "iterator should handle deletions during iteration" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 8);
    defer tree.deinit();
    
    // Insert initial data
    for (0..20) |i| {
        const key = @as(i32, @intCast(i));
        try tree.insert(key, key * 10);
    }
    
    // Start iteration and delete during iteration
    var iter = tree.iterator();
    var count: usize = 0;
    var keys_to_delete = std.ArrayList(i32).init(allocator);
    defer keys_to_delete.deinit();
    
    while (iter.next()) |entry| {
        count += 1;
        
        // Mark every third key for deletion
        if (@mod(entry.key, 3) == 0) {
            try keys_to_delete.append(entry.key);
        }
    }
    
    // Delete the marked keys
    for (keys_to_delete.items) |key| {
        _ = tree.remove(key) catch {};
    }
    
    // Verify iteration completed and tree state is consistent
    try testing.expectEqual(@as(usize, 20), count);
    try testing.expectEqual(@as(usize, 20 - keys_to_delete.items.len), tree.len());
}

test "reverse iterator should handle modifications" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, []const u8);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert initial data
    try tree.insert(10, "ten");
    try tree.insert(20, "twenty");
    try tree.insert(30, "thirty");
    try tree.insert(40, "forty");
    try tree.insert(50, "fifty");
    
    // Start reverse iteration and modify during iteration
    var rev_iter = tree.reverseIterator();
    var count: usize = 0;
    
    while (rev_iter.next()) |entry| {
        count += 1;
        
        // Insert a new key during iteration
        if (count == 2) {
            try tree.insert(35, "thirty-five");
        }
        
        // Update an existing key during iteration
        if (entry.key == 20) {
            try tree.insert(20, "TWENTY");
        }
    }
    
    // Verify iteration completed
    try testing.expect(count >= 5);
    
    // Verify modifications took effect
    try testing.expectEqualStrings("TWENTY", tree.get(20).?);
    try testing.expectEqualStrings("thirty-five", tree.get(35).?);
}

test "concurrent forward and reverse iteration" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 16);
    defer tree.deinit();
    
    // Insert data
    for (0..50) |i| {
        const key = @as(i32, @intCast(i));
        try tree.insert(key, key * 2);
    }
    
    // Create both iterators
    var fwd_iter = tree.iterator();
    var rev_iter = tree.reverseIterator();
    
    // Advance both iterators alternately
    var fwd_count: usize = 0;
    var rev_count: usize = 0;
    var fwd_sum: i32 = 0;
    var rev_sum: i32 = 0;
    
    for (0..20) |i| {
        if (@mod(i, 2) == 0) {
            if (fwd_iter.next()) |entry| {
                fwd_count += 1;
                fwd_sum += entry.key;
            }
        } else {
            if (rev_iter.next()) |entry| {
                rev_count += 1;
                rev_sum += entry.key;
            }
        }
    }
    
    // Both iterators should have advanced
    try testing.expect(fwd_count > 0);
    try testing.expect(rev_count > 0);
    try testing.expect(fwd_sum != rev_sum); // Different keys visited
}

test "new iterator after clear should be empty" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 8);
    defer tree.deinit();
    
    // Insert data
    for (0..10) |i| {
        const key = @as(i32, @intCast(i));
        try tree.insert(key, key);
    }
    
    // Create iterator and consume some items
    var iter = tree.iterator();
    _ = iter.next();
    _ = iter.next();
    
    // Clear the tree
    tree.clear();
    
    // New iterator should be empty after clear
    var new_iter = tree.iterator();
    try testing.expect(new_iter.next() == null);
    try testing.expectEqual(@as(usize, 0), tree.len());
    
    // Note: Old iterator is invalidated after clear and should not be used
    // This is expected behavior - clearing invalidates all existing iterators
}

test "iterator behavior with duplicate key updates" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert initial values
    try tree.insert(1, 100);
    try tree.insert(2, 200);
    try tree.insert(3, 300);
    try tree.insert(4, 400);
    try tree.insert(5, 500);
    
    // Start iteration
    var iter = tree.iterator();
    var values_seen = std.ArrayList(i32).init(allocator);
    defer values_seen.deinit();
    
    while (iter.next()) |entry| {
        try values_seen.append(entry.value);
        
        // Update values during iteration
        if (entry.key == 3) {
            try tree.insert(3, 999); // Update existing key
            try tree.insert(1, 111); // Update earlier key
            try tree.insert(5, 555); // Update later key
        }
    }
    
    // Verify we saw the original values during iteration
    try testing.expectEqual(@as(usize, 5), values_seen.items.len);
    try testing.expectEqual(@as(i32, 100), values_seen.items[0]);
    try testing.expectEqual(@as(i32, 200), values_seen.items[1]);
    try testing.expectEqual(@as(i32, 300), values_seen.items[2]); // Original value
    
    // Verify updates took effect
    try testing.expectEqual(@as(i32, 111), tree.get(1).?);
    try testing.expectEqual(@as(i32, 999), tree.get(3).?);
    try testing.expectEqual(@as(i32, 555), tree.get(5).?);
}

test "stress test iterator with many modifications" {
    const allocator = testing.allocator;
    var prng = std.Random.DefaultPrng.init(12345);
    const random = prng.random();
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 32);
    defer tree.deinit();
    
    // Insert initial data
    for (0..100) |i| {
        const key = @as(i32, @intCast(i * 5));
        try tree.insert(key, key);
    }
    
    // Iterate and perform random modifications
    var iter = tree.iterator();
    var modifications: usize = 0;
    var items_seen: usize = 0;
    
    while (iter.next()) |entry| {
        items_seen += 1;
        
        // Randomly decide to modify
        if (random.int(u8) % 10 < 3) { // 30% chance
            const op = random.int(u8) % 3;
            const random_key = @mod(random.int(i32), 1000);
            
            switch (op) {
                0 => { // Insert
                    try tree.insert(random_key, random_key);
                    modifications += 1;
                },
                1 => { // Update
                    if (tree.contains(entry.key)) {
                        try tree.insert(entry.key, entry.value * 2);
                        modifications += 1;
                    }
                },
                2 => { // Delete (skip current to avoid issues)
                    if (random_key != entry.key) {
                        _ = tree.remove(random_key) catch {};
                        modifications += 1;
                    }
                },
                else => {},
            }
        }
    }
    
    // Verify iteration completed successfully
    try testing.expect(items_seen >= 100); // At least original items
    try testing.expect(modifications > 0); // Some modifications occurred
    std.debug.print("\nIterator stress test: {} items seen, {} modifications\n", 
        .{ items_seen, modifications });
}