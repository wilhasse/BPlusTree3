const std = @import("std");
const testing = std.testing;
const bplustree = @import("bplustree");

test "should handle unbounded range queries - from start" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert test data
    for (1..11) |i| {
        try tree.insert(@intCast(i), @intCast(i * 10));
    }
    
    // Query from start to 5 (inclusive)
    var results = std.ArrayList(Tree.Entry).init(allocator);
    defer results.deinit();
    
    try tree.rangeTo(5, &results);
    
    // Should return keys 1, 2, 3, 4, 5
    try testing.expectEqual(@as(usize, 5), results.items.len);
    
    for (1..6) |i| {
        const idx = i - 1;
        try testing.expectEqual(@as(i32, @intCast(i)), results.items[idx].key);
        try testing.expectEqual(@as(i32, @intCast(i * 10)), results.items[idx].value);
    }
}

test "should handle unbounded range queries - to end" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert test data
    for (1..11) |i| {
        try tree.insert(@intCast(i), @intCast(i * 10));
    }
    
    // Query from 6 to end
    var results = std.ArrayList(Tree.Entry).init(allocator);
    defer results.deinit();
    
    try tree.rangeFrom(6, &results);
    
    // Should return keys 6, 7, 8, 9, 10
    try testing.expectEqual(@as(usize, 5), results.items.len);
    
    for (6..11) |i| {
        const idx = i - 6;
        try testing.expectEqual(@as(i32, @intCast(i)), results.items[idx].key);
        try testing.expectEqual(@as(i32, @intCast(i * 10)), results.items[idx].value);
    }
}

test "should handle exclusive range queries" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert test data
    for (1..11) |i| {
        try tree.insert(@intCast(i), @intCast(i * 10));
    }
    
    // Query range [3, 7) - 3 inclusive, 7 exclusive
    var results = std.ArrayList(Tree.Entry).init(allocator);
    defer results.deinit();
    
    try tree.rangeExclusive(3, 7, &results);
    
    // Should return keys 3, 4, 5, 6
    try testing.expectEqual(@as(usize, 4), results.items.len);
    
    const expected = [_]Tree.Entry{
        .{ .key = 3, .value = 30 },
        .{ .key = 4, .value = 40 },
        .{ .key = 5, .value = 50 },
        .{ .key = 6, .value = 60 },
    };
    
    for (expected, results.items) |exp, res| {
        try testing.expectEqual(exp.key, res.key);
        try testing.expectEqual(exp.value, res.value);
    }
}

test "should handle empty range queries" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert test data
    for (1..11) |i| {
        try tree.insert(@intCast(i), @intCast(i * 10));
    }
    
    // Query with start > end
    var results = std.ArrayList(Tree.Entry).init(allocator);
    defer results.deinit();
    
    try tree.range(7, 3, &results);
    
    // Should return empty
    try testing.expectEqual(@as(usize, 0), results.items.len);
    
    // Query range that doesn't overlap with any keys
    results.clearRetainingCapacity();
    try tree.range(20, 30, &results);
    
    // Should return empty
    try testing.expectEqual(@as(usize, 0), results.items.len);
}

test "should handle single element ranges" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert test data
    for (1..11) |i| {
        try tree.insert(@intCast(i), @intCast(i * 10));
    }
    
    // Query range [5, 5] - single element
    var results = std.ArrayList(Tree.Entry).init(allocator);
    defer results.deinit();
    
    try tree.range(5, 5, &results);
    
    // Should return only key 5
    try testing.expectEqual(@as(usize, 1), results.items.len);
    try testing.expectEqual(@as(i32, 5), results.items[0].key);
    try testing.expectEqual(@as(i32, 50), results.items[0].value);
}

test "should handle ranges with non-existent boundaries" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert test data - only even numbers
    for (1..6) |i| {
        const key: i32 = @intCast(i * 2);
        try tree.insert(key, key * 10);
    }
    
    // Query range [3, 7] - boundaries don't exist
    var results = std.ArrayList(Tree.Entry).init(allocator);
    defer results.deinit();
    
    try tree.range(3, 7, &results);
    
    // Should return keys 4, 6
    try testing.expectEqual(@as(usize, 2), results.items.len);
    try testing.expectEqual(@as(i32, 4), results.items[0].key);
    try testing.expectEqual(@as(i32, 40), results.items[0].value);
    try testing.expectEqual(@as(i32, 6), results.items[1].key);
    try testing.expectEqual(@as(i32, 60), results.items[1].value);
}

test "should handle range query on large dataset" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 128);
    defer tree.deinit();
    
    // Insert large dataset
    const n = 10000;
    for (0..n) |i| {
        try tree.insert(@intCast(i), @intCast(i));
    }
    
    // Query middle range
    var results = std.ArrayList(Tree.Entry).init(allocator);
    defer results.deinit();
    
    try tree.range(4000, 4100, &results);
    
    // Should return 101 elements
    try testing.expectEqual(@as(usize, 101), results.items.len);
    
    // Verify they're in order
    for (0..101) |i| {
        const expected_key: i32 = @intCast(4000 + i);
        try testing.expectEqual(expected_key, results.items[i].key);
        try testing.expectEqual(expected_key, results.items[i].value);
    }
}