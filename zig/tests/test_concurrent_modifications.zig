const std = @import("std");
const testing = std.testing;
const bplustree = @import("bplustree");

test "concurrent modifications: simulated reader-writer patterns" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Initial data
    for (0..100) |i| {
        try tree.insert(@intCast(i), @intCast(i * 10));
    }
    
    // Simulate concurrent read-write pattern
    // Writers modify every 5th element
    // Readers access all elements
    
    var write_count: usize = 0;
    var read_count: usize = 0;
    
    // Simulate 10 "time slices"
    for (0..10) |round| {
        // Writer operations
        for (0..20) |i| {
            const key = @as(i32, @intCast(i * 5));
            const new_value = @as(i32, @intCast(round * 1000 + i));
            try tree.insert(key, new_value);
            write_count += 1;
        }
        
        // Reader operations (interleaved)
        for (0..100) |i| {
            const key = @as(i32, @intCast(i));
            _ = tree.get(key);
            read_count += 1;
        }
        
        // Verify tree consistency
        var iter = tree.iterator();
        var last_key: ?i32 = null;
        while (iter.next()) |entry| {
            if (last_key) |lk| {
                try testing.expect(entry.key > lk);
            }
            last_key = entry.key;
        }
    }
    
    try testing.expect(write_count == 200);
    try testing.expect(read_count == 1000);
}

test "concurrent modifications: iterator invalidation patterns" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Fill tree
    for (0..50) |i| {
        try tree.insert(@intCast(i), @intCast(i));
    }
    
    // Pattern 1: Modification during iteration
    var iter1 = tree.iterator();
    var count1: usize = 0;
    
    while (iter1.next()) |_| {
        count1 += 1;
        
        // Simulate concurrent modification every 10 items
        if (count1 % 10 == 0) {
            // Add new items that would appear later in iteration
            try tree.insert(@intCast(100 + count1), @intCast(count1));
        }
    }
    
    // Pattern 2: Deletion during iteration
    var iter2 = tree.iterator();
    var keys_to_delete = std.ArrayList(i32).init(allocator);
    defer keys_to_delete.deinit();
    
    while (iter2.next()) |entry| {
        if (@mod(entry.key, 3) == 0) {
            try keys_to_delete.append(entry.key);
        }
    }
    
    // Simulate concurrent deletions
    for (keys_to_delete.items) |key| {
        _ = tree.remove(key) catch {};
    }
    
    // Verify final state
    var final_count: usize = 0;
    var final_iter = tree.iterator();
    while (final_iter.next()) |_| {
        final_count += 1;
    }
    
    try testing.expect(final_count > 0);
}

test "concurrent modifications: range query consistency" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 8);
    defer tree.deinit();
    
    // Setup initial data
    for (0..200) |i| {
        try tree.insert(@intCast(i), @intCast(i));
    }
    
    // Simulate concurrent range queries and modifications
    var results1 = std.ArrayList(Tree.Entry).init(allocator);
    defer results1.deinit();
    
    var results2 = std.ArrayList(Tree.Entry).init(allocator);
    defer results2.deinit();
    
    // Query 1: Range 50-100
    try tree.range(50, 100, &results1);
    const initial_range_size = results1.items.len;
    
    // Concurrent modifications within the range
    for (60..80) |i| {
        _ = try tree.remove(@intCast(i));
    }
    
    // Query 2: Same range after modifications
    try tree.range(50, 100, &results2);
    
    // Verify consistency
    try testing.expect(results2.items.len < initial_range_size);
    
    // Verify no duplicates in results
    var seen = std.AutoHashMap(i32, void).init(allocator);
    defer seen.deinit();
    
    for (results2.items) |entry| {
        const result = try seen.getOrPut(entry.key);
        try testing.expect(!result.found_existing);
    }
}

test "concurrent modifications: high contention simulation" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Simulate high contention on specific keys
    const hot_keys = [_]i32{ 10, 20, 30, 40, 50 };
    const cold_keys = [_]i32{ 100, 200, 300, 400, 500 };
    
    // Insert initial data
    for (hot_keys) |key| {
        try tree.insert(key, key);
    }
    for (cold_keys) |key| {
        try tree.insert(key, key);
    }
    
    // Simulate high contention access pattern
    for (0..1000) |i| {
        const op = i % 4;
        const is_hot = i % 5 < 4; // 80% hot keys
        const keys = if (is_hot) hot_keys else cold_keys;
        const key = keys[i % keys.len];
        
        switch (op) {
            0 => _ = tree.get(key), // Read
            1 => try tree.insert(key, @intCast(i)), // Update
            2 => { // Conditional update
                if (tree.get(key)) |current| {
                    if (current < 1000) {
                        try tree.insert(key, current + 1);
                    }
                }
            },
            3 => { // Range query around key
                var results = std.ArrayList(Tree.Entry).init(allocator);
                defer results.deinit();
                try tree.range(key - 5, key + 5, &results);
            },
            else => unreachable,
        }
    }
    
    // Verify all keys still exist
    for (hot_keys) |key| {
        try testing.expect(tree.contains(key));
    }
    for (cold_keys) |key| {
        try testing.expect(tree.contains(key));
    }
}

test "concurrent modifications: bulk operations interleaving" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 16);
    defer tree.deinit();
    
    // Simulate interleaved bulk operations
    const batch_size = 50;
    
    // Thread 1: Bulk inserts in ascending order
    // Thread 2: Bulk inserts in descending order
    // Thread 3: Bulk deletes
    
    for (0..10) |round| {
        // Thread 1 operations
        const base1 = @as(i32, @intCast(round * 1000));
        for (0..batch_size) |i| {
            try tree.insert(base1 + @as(i32, @intCast(i)), @intCast(i));
        }
        
        // Thread 2 operations
        const base2 = @as(i32, @intCast(round * 1000 + 500));
        var j: i32 = @intCast(batch_size - 1);
        while (j >= 0) : (j -= 1) {
            try tree.insert(base2 + j, j);
        }
        
        // Thread 3 operations (delete from previous rounds)
        if (round > 0) {
            const delete_base = @as(i32, @intCast((round - 1) * 1000));
            for (0..batch_size / 2) |i| {
                _ = tree.remove(delete_base + @as(i32, @intCast(i * 2))) catch {};
            }
        }
        
        // Verify tree consistency
        var iter = tree.iterator();
        var prev_key: ?i32 = null;
        while (iter.next()) |entry| {
            if (prev_key) |pk| {
                try testing.expect(entry.key > pk);
            }
            prev_key = entry.key;
        }
    }
}

test "concurrent modifications: mixed size operations" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, []const u8);
    var tree = Tree.init(allocator, 8);
    defer tree.deinit();
    
    // Different value sizes to simulate varied memory patterns
    const small_value = "small";
    const medium_value = "medium_value_with_more_data";
    const large_value = "large_value_with_significantly_more_data_to_test_memory_handling";
    
    // Mixed operations with different value sizes
    for (0..100) |i| {
        const key = @as(i32, @intCast(i));
        const value = switch (i % 3) {
            0 => small_value,
            1 => medium_value,
            2 => large_value,
            else => unreachable,
        };
        try tree.insert(key, value);
    }
    
    // Simulate concurrent access with mixed operations
    var prng = std.Random.DefaultPrng.init(12345);
    const random = prng.random();
    
    for (0..500) |_| {
        const key = random.intRangeAtMost(i32, 0, 150);
        const op = random.intRangeAtMost(u8, 0, 3);
        
        switch (op) {
            0 => { // Read
                _ = tree.get(key);
            },
            1 => { // Update with different size
                const new_value = switch (random.intRangeAtMost(u8, 0, 2)) {
                    0 => small_value,
                    1 => medium_value,
                    2 => large_value,
                    else => unreachable,
                };
                try tree.insert(key, new_value);
            },
            2 => { // Delete
                _ = tree.remove(key) catch {};
            },
            3 => { // Range query
                var results = std.ArrayList(Tree.Entry).init(allocator);
                defer results.deinit();
                try tree.range(key, key + 10, &results);
            },
            else => unreachable,
        }
    }
    
    // Final consistency check
    var count: usize = 0;
    var iter = tree.iterator();
    while (iter.next()) |_| {
        count += 1;
    }
    try testing.expectEqual(tree.len(), count);
}

test "concurrent modifications: version counter pattern" {
    const allocator = testing.allocator;
    
    // Value type with version counter
    const VersionedValue = struct {
        data: i32,
        version: u32,
    };
    
    const Tree = bplustree.BPlusTree(i32, VersionedValue);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Initialize with versioned values
    for (0..50) |i| {
        try tree.insert(@intCast(i), .{ .data = @intCast(i), .version = 0 });
    }
    
    // Simulate concurrent updates with version checking
    for (0..200) |op_num| {
        const key = @as(i32, @intCast(op_num % 50));
        
        // Read-modify-write pattern
        if (tree.get(key)) |current| {
            const new_value = VersionedValue{
                .data = current.data + 1,
                .version = current.version + 1,
            };
            try tree.insert(key, new_value);
        }
    }
    
    // Verify all values have been updated
    for (0..50) |i| {
        const value = tree.get(@intCast(i));
        try testing.expect(value != null);
        try testing.expect(value.?.version > 0);
    }
}

test "concurrent modifications: insertion and iteration race" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Initial small dataset
    for (0..10) |i| {
        try tree.insert(@intCast(i * 10), @intCast(i));
    }
    
    // Start iteration
    var iter = tree.iterator();
    var seen_keys = std.ArrayList(i32).init(allocator);
    defer seen_keys.deinit();
    
    // Consume some items
    for (0..5) |_| {
        if (iter.next()) |entry| {
            try seen_keys.append(entry.key);
        }
    }
    
    // Insert items that would affect iteration
    for (0..5) |i| {
        // Insert keys that are:
        // 1. Before current position (shouldn't see)
        try tree.insert(@intCast(i), @intCast(i));
        // 2. After current position (might see)
        try tree.insert(@intCast(100 + i), @intCast(i));
    }
    
    // Continue iteration
    while (iter.next()) |entry| {
        try seen_keys.append(entry.key);
    }
    
    // Verify we saw a consistent view
    for (1..seen_keys.items.len) |i| {
        try testing.expect(seen_keys.items[i] > seen_keys.items[i - 1]);
    }
}

test "concurrent modifications: clear during operations" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Pattern: Build, partially iterate, clear, rebuild
    for (0..5) |round| {
        // Build tree
        for (0..30) |i| {
            try tree.insert(@intCast(i), @intCast(i + round * 100));
        }
        
        // Start iteration
        var iter = tree.iterator();
        var count: usize = 0;
        
        // Partially iterate
        while (count < 10) {
            if (iter.next()) |_| {
                count += 1;
            } else {
                break;
            }
        }
        
        // Clear tree (simulating concurrent clear)
        tree.clear();
        
        // Verify tree is empty
        try testing.expectEqual(@as(usize, 0), tree.len());
        
        // Note: In a real concurrent scenario, continuing iteration after clear
        // would be undefined behavior. For this test, we skip checking the iterator
        // after clear to avoid accessing deallocated memory.
    }
}

test "concurrent modifications: ABA problem simulation" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, []const u8);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // ABA pattern: A -> B -> A
    const key = 42;
    const value_a = "value_A";
    const value_b = "value_B";
    
    // Insert A
    try tree.insert(key, value_a);
    
    // Verify A
    try testing.expectEqualStrings(value_a, tree.get(key).?);
    
    // Change to B
    try tree.insert(key, value_b);
    
    // Verify B
    try testing.expectEqualStrings(value_b, tree.get(key).?);
    
    // Change back to A
    try tree.insert(key, value_a);
    
    // Verify A again
    try testing.expectEqualStrings(value_a, tree.get(key).?);
    
    // More complex ABA with deletion
    _ = try tree.remove(key);
    try testing.expect(tree.get(key) == null);
    
    // Re-insert with same key but different value
    try tree.insert(key, value_b);
    try testing.expectEqualStrings(value_b, tree.get(key).?);
}