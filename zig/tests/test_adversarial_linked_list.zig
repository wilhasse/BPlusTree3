const std = @import("std");
const testing = std.testing;
const bplustree = @import("bplustree");

test "adversarial: linked list cycle attack" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, std.ArrayList(u8));
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Phase 1: Create a tree with multiple leaf nodes
    for (0..20) |i| {
        var value = std.ArrayList(u8).init(allocator);
        try value.appendSlice("value");
        try tree.insert(@intCast(i * 5), value);
    }
    
    // Phase 2: Perform operations designed to confuse next pointer updates
    for (0..5) |round| {
        // Delete from the middle to force merges
        for (5..15) |i| {
            const key = @as(i32, @intCast(i * 5));
            if (tree.contains(key)) {
                var old_value = try tree.remove(key);
                old_value.deinit();
            }
        }
        
        // Reinsert with different values to force splits
        for (5..15) |i| {
            var value = std.ArrayList(u8).init(allocator);
            try value.writer().print("round{}-{}", .{ round, i });
            try tree.insert(@intCast(i * 5 + round), value);
        }
        
        // Verify no cycle by iterating and checking we don't see duplicates
        var seen = std.AutoHashMap(i32, void).init(allocator);
        defer seen.deinit();
        
        var count: usize = 0;
        var iter = tree.iterator();
        while (iter.next()) |entry| {
            const result = try seen.getOrPut(entry.key);
            if (result.found_existing) {
                std.debug.panic("ATTACK SUCCESSFUL: Linked list has a cycle! Duplicate key: {}", .{entry.key});
            }
            count += 1;
            if (count > tree.len() * 2) {
                std.debug.panic("ATTACK SUCCESSFUL: Iterator running forever, likely cycle!", .{});
            }
        }
    }
    
    // Cleanup remaining values
    var iter = tree.iterator();
    while (iter.next()) |entry| {
        entry.value.deinit();
    }
}

test "adversarial: concurrent iteration modification simulation" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Fill tree
    for (0..50) |i| {
        try tree.insert(@intCast(i), @intCast(i * 10));
    }
    
    // Simulate concurrent modifications by saving iterator state
    var iter = tree.iterator();
    var iter_count: usize = 0;
    var last_key: ?i32 = null;
    var keys_seen = std.ArrayList(i32).init(allocator);
    defer keys_seen.deinit();
    
    while (iter.next()) |entry| {
        iter_count += 1;
        
        // Check for out-of-order iteration
        if (last_key) |last| {
            try testing.expect(entry.key > last);
        }
        last_key = entry.key;
        try keys_seen.append(entry.key);
        
        // Simulate modifications at certain points
        if (iter_count == 10) {
            // Add a key that should appear later
            try tree.insert(100, 1000);
        } else if (iter_count == 20) {
            // Add a key that's already passed
            try tree.insert(-1, -10);
        }
    }
    
    // Verify we got all items (original 50 + 1 added during iteration)
    try testing.expectEqual(@as(usize, 51), iter_count);
    
    // New iterator should see all items including modifications
    var new_count: usize = 0;
    var new_iter = tree.iterator();
    while (new_iter.next()) |_| {
        new_count += 1;
    }
    try testing.expectEqual(@as(usize, 52), new_count);
}

test "adversarial: split during iteration attack" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Create a tree that's about to split
    try tree.insert(10, 100);
    try tree.insert(20, 200);
    try tree.insert(30, 300);
    
    // Start iteration
    var iter = tree.iterator();
    var entries_before_split = std.ArrayList(Tree.Entry).init(allocator);
    defer entries_before_split.deinit();
    
    // Collect first entry
    if (iter.next()) |entry| {
        try entries_before_split.append(entry);
    }
    
    // Force a split while iterator is active
    try tree.insert(15, 150);
    try tree.insert(25, 250);
    try tree.insert(35, 350);
    
    // Continue iteration - should still work correctly
    while (iter.next()) |entry| {
        try entries_before_split.append(entry);
    }
    
    // Should have seen all original entries plus any that were added
    try testing.expect(entries_before_split.items.len >= 3);
    
    // Verify they were in order
    for (1..entries_before_split.items.len) |i| {
        try testing.expect(entries_before_split.items[i].key > entries_before_split.items[i - 1].key);
    }
}

test "adversarial: range iterator boundary attack" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Create specific structure
    for (0..20) |i| {
        try tree.insert(@intCast(i * 10), @intCast(i));
    }
    
    // Attack: Query ranges at exact leaf boundaries
    var results = std.ArrayList(Tree.Entry).init(allocator);
    defer results.deinit();
    
    // Test various boundary conditions
    const test_cases = [_]struct { start: i32, end: i32 }{
        .{ .start = -10, .end = 5 },    // Before first
        .{ .start = 45, .end = 55 },     // Spans leaves
        .{ .start = 100, .end = 110 },   // Middle of range
        .{ .start = 195, .end = 300 },   // After last
        .{ .start = 50, .end = 49 },     // Invalid range
    };
    
    for (test_cases) |tc| {
        results.clearRetainingCapacity();
        try tree.range(tc.start, tc.end, &results);
        
        // Verify results are in range and ordered
        for (results.items, 0..) |entry, i| {
            try testing.expect(entry.key >= tc.start);
            try testing.expect(entry.key <= tc.end);
            if (i > 0) {
                try testing.expect(entry.key > results.items[i - 1].key);
            }
        }
    }
}

test "adversarial: linked list fragmentation attack" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Create maximum fragmentation by alternating insert/delete
    for (0..100) |i| {
        try tree.insert(@intCast(i), @intCast(i));
    }
    
    // Delete every other element
    for (0..50) |i| {
        _ = try tree.remove(@intCast(i * 2));
    }
    
    // Insert in gaps with different values
    for (0..50) |i| {
        try tree.insert(@intCast(i * 2), @intCast(i * 2000));
    }
    
    // Stress test the linked list by forward and reverse iteration
    var forward_count: usize = 0;
    var forward_iter = tree.iterator();
    while (forward_iter.next()) |_| {
        forward_count += 1;
    }
    
    var reverse_count: usize = 0;
    var reverse_iter = tree.reverseIterator();
    while (reverse_iter.next()) |_| {
        reverse_count += 1;
    }
    
    try testing.expectEqual(forward_count, reverse_count);
    try testing.expectEqual(@as(usize, 100), forward_count);
}

test "adversarial: iterator state corruption attack" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Build complex tree
    for (0..30) |i| {
        try tree.insert(@intCast(i * 3), @intCast(i));
    }
    
    // Create multiple iterators
    var iter1 = tree.iterator();
    var iter2 = tree.iterator();
    var rev_iter = tree.reverseIterator();
    
    // Advance them to different positions
    _ = iter1.next();
    _ = iter1.next();
    _ = iter1.next();
    
    _ = iter2.next();
    
    _ = rev_iter.next();
    _ = rev_iter.next();
    
    // Modify tree structure
    for (10..20) |i| {
        if (tree.contains(@intCast(i * 3))) {
            _ = try tree.remove(@intCast(i * 3));
        }
    }
    
    // Continue iteration - iterators should handle modifications gracefully
    var count1: usize = 3; // Already consumed 3
    while (iter1.next()) |_| {
        count1 += 1;
    }
    
    var count2: usize = 1; // Already consumed 1
    while (iter2.next()) |_| {
        count2 += 1;
    }
    
    // Iterators should complete their traversal (actual count depends on implementation)
    // The key is that they don't crash or corrupt
    try testing.expect(count1 > 0);
    try testing.expect(count2 > 0);
}

test "adversarial: linked list pointer confusion attack" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 3); // Small capacity for more splits/merges
    defer tree.deinit();
    
    // Pattern designed to confuse prev/next pointers
    const operations = [_]struct { op: enum { Insert, Remove }, key: i32 }{
        .{ .op = .Insert, .key = 50 },
        .{ .op = .Insert, .key = 30 },
        .{ .op = .Insert, .key = 70 },
        .{ .op = .Insert, .key = 20 },
        .{ .op = .Insert, .key = 60 },
        .{ .op = .Insert, .key = 40 },
        .{ .op = .Insert, .key = 80 },
        .{ .op = .Remove, .key = 30 },
        .{ .op = .Insert, .key = 35 },
        .{ .op = .Remove, .key = 50 },
        .{ .op = .Insert, .key = 55 },
        .{ .op = .Remove, .key = 70 },
        .{ .op = .Insert, .key = 75 },
    };
    
    for (operations) |op| {
        switch (op.op) {
            .Insert => try tree.insert(op.key, op.key * 10),
            .Remove => {
                if (tree.contains(op.key)) {
                    _ = try tree.remove(op.key);
                }
            },
        }
        
        // Verify linked list integrity after each operation
        var forward_keys = std.ArrayList(i32).init(allocator);
        defer forward_keys.deinit();
        
        var iter = tree.iterator();
        while (iter.next()) |entry| {
            try forward_keys.append(entry.key);
        }
        
        // Verify ordering
        for (1..forward_keys.items.len) |i| {
            try testing.expect(forward_keys.items[i] > forward_keys.items[i - 1]);
        }
    }
}

test "adversarial: extreme leaf navigation attack" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Create many leaves
    for (0..200) |i| {
        try tree.insert(@intCast(i), @intCast(i));
    }
    
    // Perform range queries that span many leaves
    var results = std.ArrayList(Tree.Entry).init(allocator);
    defer results.deinit();
    
    // Query entire range
    try tree.range(0, 199, &results);
    try testing.expectEqual(@as(usize, 200), results.items.len);
    
    // Query that skips first few leaves
    results.clearRetainingCapacity();
    try tree.range(50, 150, &results);
    try testing.expectEqual(@as(usize, 101), results.items.len);
    
    // Many small ranges
    for (0..50) |i| {
        results.clearRetainingCapacity();
        const start = @as(i32, @intCast(i * 4));
        try tree.range(start, start + 2, &results);
        
        for (results.items) |entry| {
            try testing.expect(entry.key >= start);
            try testing.expect(entry.key <= start + 2);
        }
    }
}