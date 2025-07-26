const std = @import("std");
const testing = std.testing;
const bplustree = @import("bplustree");

// Fuzz test configuration
const FuzzConfig = struct {
    max_operations: usize = 10000,
    max_key: i32 = 1000,
    seed: u64 = 12345,
    verbose: bool = false,
};

// Operation for replay
const Operation = union(enum) {
    Insert: struct { key: i32, value: i32 },
    Remove: struct { key: i32 },
    Get: struct { key: i32 },
    Clear: void,
};

test "fuzz: basic operations against reference" {
    const allocator = testing.allocator;
    const config = FuzzConfig{};
    
    // Test with various capacities
    const capacities = [_]usize{ 2, 3, 4, 5, 8, 16, 32 };
    
    for (capacities) |capacity| {
        // Our B+ tree
        const Tree = bplustree.BPlusTree(i32, i32);
        var tree = Tree.init(allocator, capacity);
        defer tree.deinit();
        
        // Reference implementation (simple sorted array)
        var reference = std.ArrayList(struct { key: i32, value: i32 }).init(allocator);
        defer reference.deinit();
        
        var prng = std.Random.DefaultPrng.init(config.seed);
        const random = prng.random();
        
        var operations = std.ArrayList(Operation).init(allocator);
        defer operations.deinit();
        
        // Perform random operations
        for (0..config.max_operations) |_| {
            const op_type = random.intRangeAtMost(u8, 0, 3);
            
            switch (op_type) {
                0, 1 => { // Insert (weighted higher)
                    const key = random.intRangeAtMost(i32, 0, config.max_key);
                    const value = key * 10;
                    
                    try operations.append(.{ .Insert = .{ .key = key, .value = value } });
                    
                    // Insert into B+ tree
                    try tree.insert(key, value);
                    
                    // Update reference
                    var found = false;
                    for (reference.items) |*item| {
                        if (item.key == key) {
                            item.value = value;
                            found = true;
                            break;
                        }
                    }
                    if (!found) {
                        try reference.append(.{ .key = key, .value = value });
                        // Keep sorted
                        std.mem.sort(@TypeOf(reference.items[0]), reference.items, {}, struct {
                            fn lessThan(_: void, a: @TypeOf(reference.items[0]), b: @TypeOf(reference.items[0])) bool {
                                return a.key < b.key;
                            }
                        }.lessThan);
                    }
                },
                2 => { // Remove
                    if (reference.items.len > 0) {
                        const idx = random.intRangeLessThan(usize, 0, reference.items.len);
                        const key = reference.items[idx].key;
                        
                        try operations.append(.{ .Remove = .{ .key = key } });
                        
                        // Remove from B+ tree
                        _ = try tree.remove(key);
                        
                        // Remove from reference
                        _ = reference.orderedRemove(idx);
                    }
                },
                3 => { // Get
                    const key = random.intRangeAtMost(i32, 0, config.max_key);
                    try operations.append(.{ .Get = .{ .key = key } });
                    
                    // Get from B+ tree
                    const tree_result = tree.get(key);
                    
                    // Get from reference
                    var ref_result: ?i32 = null;
                    for (reference.items) |item| {
                        if (item.key == key) {
                            ref_result = item.value;
                            break;
                        }
                    }
                    
                    // Compare results
                    try testing.expectEqual(ref_result, tree_result);
                },
                else => unreachable,
            }
            
            // Periodically verify consistency
            if (operations.items.len % 100 == 0) {
                try verifyConsistency(&tree, &reference, &operations);
            }
        }
        
        // Final verification
        try verifyConsistency(&tree, &reference, &operations);
    }
}

fn verifyConsistency(
    tree: anytype,
    reference: anytype,
    operations: *std.ArrayList(Operation),
) !void {
    // Verify length
    try testing.expectEqual(reference.items.len, tree.len());
    
    // Verify all keys match
    for (reference.items) |ref_item| {
        const tree_value = tree.get(ref_item.key);
        if (tree_value == null or tree_value.? != ref_item.value) {
            std.debug.print("Mismatch for key {}: tree has {?}, reference has {}\n", .{
                ref_item.key,
                tree_value,
                ref_item.value,
            });
            dumpOperations(operations);
            return error.ConsistencyCheckFailed;
        }
    }
    
    // Verify iteration order
    var tree_keys = std.ArrayList(i32).init(testing.allocator);
    defer tree_keys.deinit();
    
    var iter = tree.iterator();
    while (iter.next()) |entry| {
        try tree_keys.append(entry.key);
    }
    
    try testing.expectEqual(reference.items.len, tree_keys.items.len);
    
    for (reference.items, tree_keys.items) |ref_item, tree_key| {
        try testing.expectEqual(ref_item.key, tree_key);
    }
}

fn dumpOperations(operations: *std.ArrayList(Operation)) void {
    std.debug.print("\nOperations leading to failure:\n", .{});
    for (operations.items, 0..) |op, i| {
        switch (op) {
            .Insert => |insert| {
                std.debug.print("  [{}] Insert({}, {})\n", .{ i, insert.key, insert.value });
            },
            .Remove => |remove| {
                std.debug.print("  [{}] Remove({})\n", .{ i, remove.key });
            },
            .Get => |get| {
                std.debug.print("  [{}] Get({})\n", .{ i, get.key });
            },
            .Clear => {
                std.debug.print("  [{}] Clear()\n", .{i});
            },
        }
    }
}

test "fuzz: stress test with extreme patterns" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    var prng = std.Random.DefaultPrng.init(42);
    const random = prng.random();
    
    // Pattern 1: Ascending insertions with random deletions
    for (0..1000) |i| {
        try tree.insert(@intCast(i), @intCast(i));
        
        if (random.boolean() and tree.len() > 10) {
            const key_to_remove = random.intRangeLessThan(i32, 0, @intCast(i));
            _ = tree.remove(key_to_remove) catch {};
        }
    }
    
    // Pattern 2: Random operations with verification
    var expected_keys = std.AutoHashMap(i32, i32).init(allocator);
    defer expected_keys.deinit();
    
    // Collect current state
    var iter = tree.iterator();
    while (iter.next()) |entry| {
        try expected_keys.put(entry.key, entry.value);
    }
    
    // Random modifications
    for (0..1000) |_| {
        const key = random.intRangeAtMost(i32, 0, 2000);
        
        switch (random.intRangeAtMost(u8, 0, 2)) {
            0 => { // Insert
                const value = key * 2;
                try tree.insert(key, value);
                try expected_keys.put(key, value);
            },
            1 => { // Remove
                if (expected_keys.remove(key)) {
                    _ = try tree.remove(key);
                }
            },
            2 => { // Get
                const tree_val = tree.get(key);
                const exp_val = expected_keys.get(key);
                try testing.expectEqual(exp_val, tree_val);
            },
            else => unreachable,
        }
    }
    
    // Final verification
    try testing.expectEqual(expected_keys.count(), tree.len());
}

test "fuzz: concurrent-like operations" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 8);
    defer tree.deinit();
    
    // Simulate concurrent operations by interleaving different operation streams
    const streams = 3;
    var prng = std.Random.DefaultPrng.init(999);
    const random = prng.random();
    
    // Each stream works on different key ranges
    const ranges = [_]struct { start: i32, end: i32 }{
        .{ .start = 0, .end = 333 },
        .{ .start = 334, .end = 666 },
        .{ .start = 667, .end = 999 },
    };
    
    // Interleave operations from different streams
    for (0..3000) |i| {
        const stream = i % streams;
        const range = ranges[stream];
        const key = random.intRangeAtMost(i32, range.start, range.end);
        
        switch (random.intRangeAtMost(u8, 0, 2)) {
            0 => try tree.insert(key, key),
            1 => _ = tree.remove(key) catch {},
            2 => _ = tree.get(key),
            else => unreachable,
        }
        
        // Periodic consistency check
        if (i % 500 == 0) {
            var count: usize = 0;
            var last_key: ?i32 = null;
            var check_iter = tree.iterator();
            
            while (check_iter.next()) |entry| {
                if (last_key) |lk| {
                    try testing.expect(entry.key > lk);
                }
                last_key = entry.key;
                count += 1;
            }
            
            try testing.expectEqual(tree.len(), count);
        }
    }
}

test "fuzz: property-based testing" {
    const allocator = testing.allocator;
    
    // Properties to verify:
    // 1. Inserting a key always allows retrieving it
    // 2. Removing a key means it can't be retrieved
    // 3. Tree maintains sorted order
    // 4. Tree size is accurate
    // 5. All operations maintain tree invariants
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    var prng = std.Random.DefaultPrng.init(777);
    const random = prng.random();
    
    for (0..1000) |_| {
        const key = random.intRangeAtMost(i32, 0, 100);
        const value = random.int(i32);
        
        // Property 1: Insert then get
        try tree.insert(key, value);
        try testing.expectEqual(value, tree.get(key).?);
        
        // Property 2: Remove then get
        if (random.boolean()) {
            const removed = try tree.remove(key);
            try testing.expectEqual(value, removed);
            try testing.expect(tree.get(key) == null);
            
            // Re-insert for next iteration
            try tree.insert(key, value);
        }
        
        // Property 3: Sorted order
        if (tree.len() > 1) {
            var order_iter = tree.iterator();
            var prev = order_iter.next().?;
            
            while (order_iter.next()) |entry| {
                try testing.expect(entry.key > prev.key);
                prev = entry;
            }
        }
        
        // Property 4: Size accuracy
        var size_check: usize = 0;
        var size_iter = tree.iterator();
        while (size_iter.next()) |_| {
            size_check += 1;
        }
        try testing.expectEqual(tree.len(), size_check);
    }
}

test "fuzz: edge case fuzzing" {
    const allocator = testing.allocator;
    
    // Fuzz with edge case values
    const edge_values = [_]i32{
        0,
        -1,
        1,
        std.math.minInt(i32),
        std.math.maxInt(i32),
        std.math.minInt(i32) + 1,
        std.math.maxInt(i32) - 1,
    };
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 3);
    defer tree.deinit();
    
    var prng = std.Random.DefaultPrng.init(555);
    const random = prng.random();
    
    // Insert edge values in random order
    for (0..100) |_| {
        const key = edge_values[random.intRangeLessThan(usize, 0, edge_values.len)];
        const value = random.int(i32);
        
        try tree.insert(key, value);
        try testing.expectEqual(value, tree.get(key).?);
    }
    
    // Verify all operations work with edge values
    for (edge_values) |key| {
        if (tree.contains(key)) {
            _ = try tree.remove(key);
            try tree.insert(key, key);
        }
    }
}