const std = @import("std");
const testing = std.testing;
const bplustree = @import("bplustree");

test "critical bug: linked list corruption causes data loss" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, []const u8);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Create a specific pattern to test merge operations
    // This scenario triggers merge operations
    
    // Insert keys that will create multiple leaves
    const keys = [_]i32{ 10, 20, 30, 40, 50, 60, 70, 80, 90, 100 };
    for (keys) |key| {
        const value = try std.fmt.allocPrint(allocator, "value_{}", .{key});
        defer allocator.free(value);
        try tree.insert(key, value);
    }
    
    // Count initial items
    var initial_count: usize = 0;
    var iter = tree.iterator();
    while (iter.next()) |_| {
        initial_count += 1;
    }
    try testing.expectEqual(@as(usize, 10), initial_count);
    
    // Now delete items in a pattern that will trigger merging
    _ = try tree.remove(40);
    _ = try tree.remove(50);
    _ = try tree.remove(60);
    
    // Verify linked list integrity during merge operations
    
    // Check if all remaining items are still accessible
    const expected_remaining = [_]i32{ 10, 20, 30, 70, 80, 90, 100 };
    
    // Check each item individually via get()
    for (expected_remaining) |key| {
        if (!tree.contains(key)) {
            std.debug.panic("Key {} became unreachable", .{key});
        }
    }
    
    // Check iteration consistency
    var actual_keys = std.ArrayList(i32).init(allocator);
    defer actual_keys.deinit();
    
    iter = tree.iterator();
    while (iter.next()) |entry| {
        try actual_keys.append(entry.key);
    }
    
    try testing.expectEqual(expected_remaining.len, actual_keys.items.len);
    
    for (expected_remaining, actual_keys.items) |expected, actual| {
        try testing.expectEqual(expected, actual);
    }
}

test "critical bug: root collapse infinite loop potential" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Build a multi-level tree
    for (0..64) |i| {
        try tree.insert(@intCast(i), @intCast(i * 10));
    }
    
    // Track progress to detect infinite loops
    var deletions_completed: usize = 0;
    const max_iterations = 1000; // Safety limit
    
    // Delete in a pattern that forces repeated root collapses
    var i: i32 = 63;
    var iterations: usize = 0;
    
    while (i >= 0) : (i -= 1) {
        iterations += 1;
        if (iterations > max_iterations) {
            std.debug.panic("Infinite loop detected in root collapse!", .{});
        }
        
        if (@mod(i, 8) != 0) {
            _ = try tree.remove(i);
            deletions_completed += 1;
        }
    }
    
    // If we get here, no infinite loop occurred
    try testing.expect(deletions_completed > 0);
    try testing.expect(tree.len() < 64);
}

test "critical bug: iterator invalidation during modification" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Fill tree
    for (0..20) |i| {
        try tree.insert(@intCast(i), @intCast(i * 10));
    }
    
    // Start iteration
    var iter = tree.iterator();
    var count: usize = 0;
    var modifications: usize = 0;
    
    // Collect first 5 items
    while (count < 5) {
        if (iter.next()) |_| {
            count += 1;
        } else {
            break;
        }
    }
    
    // Modify tree while iterator is active
    try tree.insert(100, 1000);
    modifications += 1;
    _ = tree.remove(15) catch {};
    modifications += 1;
    
    // Continue iteration - should not crash or corrupt
    while (iter.next()) |_| {
        count += 1;
        if (count > 100) {
            std.debug.panic("Iterator seems to be in infinite loop!", .{});
        }
    }
    
    // Verify tree is still consistent
    var verification_count: usize = 0;
    var verify_iter = tree.iterator();
    while (verify_iter.next()) |_| {
        verification_count += 1;
    }
    
    try testing.expectEqual(tree.len(), verification_count);
}

test "critical bug: range query boundary corruption" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Create specific structure
    for (0..50) |i| {
        try tree.insert(@intCast(i * 2), @intCast(i));
    }
    
    // Perform deletions that might corrupt leaf boundaries
    for (10..20) |i| {
        _ = try tree.remove(@intCast(i * 2));
    }
    
    // Test range queries at critical boundaries
    var results = std.ArrayList(Tree.Entry).init(allocator);
    defer results.deinit();
    
    // Query range that spans deleted region
    try tree.range(15, 45, &results);
    
    // Verify no duplicates or missing entries
    var seen = std.AutoHashMap(i32, void).init(allocator);
    defer seen.deinit();
    
    for (results.items) |entry| {
        const result = try seen.getOrPut(entry.key);
        if (result.found_existing) {
            std.debug.panic("Duplicate key {} in range results!", .{entry.key});
        }
        
        // Verify key is actually in range
        try testing.expect(entry.key >= 15);
        try testing.expect(entry.key <= 45);
    }
    
    // Verify all expected keys are present
    for (0..50) |i| {
        const key = @as(i32, @intCast(i * 2));
        if (key >= 15 and key <= 45 and (i < 10 or i >= 20)) {
            if (!seen.contains(key)) {
                std.debug.panic("Missing key {} in range results!", .{key});
            }
        }
    }
}

test "critical bug: split operation key distribution" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 5); // Odd capacity to test split logic
    defer tree.deinit();
    
    // Insert sequential data to force splits
    for (0..50) |i| {
        try tree.insert(@intCast(i), @intCast(i));
    }
    
    // Verify tree properties after splits
    // Min keys would be 5 / 2 = 2 for odd capacity
    
    // Delete items to expose potential split issues
    for (10..40) |i| {
        if (@mod(i, 3) == 0) {
            _ = try tree.remove(@intCast(i));
        }
    }
    
    // Tree should still maintain invariants
    var iter = tree.iterator();
    var last_key: ?i32 = null;
    var item_count: usize = 0;
    
    while (iter.next()) |entry| {
        item_count += 1;
        
        // Verify ordering
        if (last_key) |lk| {
            if (entry.key <= lk) {
                std.debug.panic("Key ordering violation: {} <= {}", .{ entry.key, lk });
            }
        }
        last_key = entry.key;
    }
    
    // Verify count matches
    try testing.expectEqual(tree.len(), item_count);
}

test "critical bug: concurrent-like operation ordering" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Simulate operations that might arrive in problematic order
    const operations = [_]struct { op: enum { Insert, Remove }, key: i32, value: i32 }{
        .{ .op = .Insert, .key = 50, .value = 500 },
        .{ .op = .Insert, .key = 30, .value = 300 },
        .{ .op = .Insert, .key = 70, .value = 700 },
        .{ .op = .Insert, .key = 20, .value = 200 },
        .{ .op = .Insert, .key = 60, .value = 600 },
        .{ .op = .Insert, .key = 40, .value = 400 },
        .{ .op = .Remove, .key = 30, .value = 0 },
        .{ .op = .Insert, .key = 35, .value = 350 },
        .{ .op = .Remove, .key = 50, .value = 0 },
        .{ .op = .Insert, .key = 55, .value = 550 },
        .{ .op = .Remove, .key = 20, .value = 0 },
        .{ .op = .Insert, .key = 25, .value = 250 },
    };
    
    for (operations) |op| {
        switch (op.op) {
            .Insert => try tree.insert(op.key, op.value),
            .Remove => _ = tree.remove(op.key) catch {},
        }
        
        // Verify tree consistency after each operation
        var count: usize = 0;
        var iter = tree.iterator();
        while (iter.next()) |_| {
            count += 1;
            if (count > 100) {
                std.debug.panic("Iterator corruption detected!", .{});
            }
        }
    }
    
    // Final verification
    const expected_keys = [_]i32{ 25, 35, 40, 55, 60, 70 };
    var actual_keys = std.ArrayList(i32).init(allocator);
    defer actual_keys.deinit();
    
    var final_iter = tree.iterator();
    while (final_iter.next()) |entry| {
        try actual_keys.append(entry.key);
    }
    
    try testing.expectEqualSlices(i32, &expected_keys, actual_keys.items);
}

test "critical bug: extreme capacity edge cases" {
    const allocator = testing.allocator;
    
    // Test with minimum capacity
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 2);
    defer tree.deinit();
    
    // This should work without issues
    for (0..100) |i| {
        try tree.insert(@intCast(i), @intCast(i));
    }
    
    // Delete most items
    for (0..90) |i| {
        _ = try tree.remove(@intCast(i));
    }
    
    // Tree should still be functional
    try testing.expectEqual(@as(usize, 10), tree.len());
    
    // Verify remaining items
    for (90..100) |i| {
        const value = tree.get(@intCast(i));
        try testing.expectEqual(@as(i32, @intCast(i)), value.?);
    }
}

test "critical bug: value type memory safety" {
    const allocator = testing.allocator;
    
    // Test with heap-allocated values
    const ValueType = struct {
        data: []u8,
        allocator: std.mem.Allocator,
        
        fn init(alloc: std.mem.Allocator, value: []const u8) !@This() {
            const data = try alloc.dupe(u8, value);
            return .{ .data = data, .allocator = alloc };
        }
        
        fn deinit(self: @This()) void {
            self.allocator.free(self.data);
        }
    };
    
    const Tree = bplustree.BPlusTree(i32, ValueType);
    var tree = Tree.init(allocator, 4);
    defer {
        // Clean up remaining values
        var iter = tree.iterator();
        while (iter.next()) |entry| {
            entry.value.deinit();
        }
        tree.deinit();
    }
    
    // Insert values
    for (0..20) |i| {
        const value_str = try std.fmt.allocPrint(allocator, "value_{}", .{i});
        defer allocator.free(value_str);
        
        const value = try ValueType.init(allocator, value_str);
        try tree.insert(@intCast(i), value);
    }
    
    // Remove some values (must clean up)
    for (5..15) |i| {
        if (tree.remove(@intCast(i))) |removed| {
            removed.deinit();
        } else |_| {}
    }
    
    // Verify remaining values are intact
    var remaining_count: usize = 0;
    var iter = tree.iterator();
    while (iter.next()) |entry| {
        remaining_count += 1;
        // Verify data is still valid
        try testing.expect(entry.value.data.len > 0);
    }
    
    try testing.expectEqual(@as(usize, 10), remaining_count);
}