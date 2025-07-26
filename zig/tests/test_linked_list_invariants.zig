const std = @import("std");
const testing = std.testing;
const bplustree = @import("bplustree");

test "leaf nodes should maintain bidirectional links" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert enough items to create multiple leaf nodes
    for (0..20) |i| {
        try tree.insert(@intCast(i), @intCast(i * 10));
    }
    
    // Verify forward traversal
    var forward_entries = std.ArrayList(Tree.Entry).init(allocator);
    defer forward_entries.deinit();
    
    var iter = tree.iterator();
    while (iter.next()) |entry| {
        try forward_entries.append(entry);
    }
    
    // Verify reverse traversal
    var reverse_entries = std.ArrayList(Tree.Entry).init(allocator);
    defer reverse_entries.deinit();
    
    var rev_iter = tree.reverseIterator();
    while (rev_iter.next()) |entry| {
        try reverse_entries.append(entry);
    }
    
    // Both should have same count
    try testing.expectEqual(forward_entries.items.len, reverse_entries.items.len);
    
    // Verify they are reverse of each other
    for (forward_entries.items, 0..) |fwd_entry, i| {
        const rev_idx = reverse_entries.items.len - 1 - i;
        const rev_entry = reverse_entries.items[rev_idx];
        try testing.expectEqual(fwd_entry.key, rev_entry.key);
        try testing.expectEqual(fwd_entry.value, rev_entry.value);
    }
}

test "leaf links should survive node splits" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert in a pattern that causes splits
    for (0..50) |i| {
        try tree.insert(@intCast(i), @intCast(i));
    }
    
    // Collect all entries via forward iteration
    var entries = std.ArrayList(i32).init(allocator);
    defer entries.deinit();
    
    var iter = tree.iterator();
    while (iter.next()) |entry| {
        try entries.append(entry.key);
    }
    
    // Verify all keys are present and in order
    try testing.expectEqual(@as(usize, 50), entries.items.len);
    for (entries.items, 0..) |key, i| {
        try testing.expectEqual(@as(i32, @intCast(i)), key);
    }
}

test "leaf links should survive node merges during deletion" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Build a tree with multiple leaf nodes
    for (0..40) |i| {
        try tree.insert(@intCast(i), @intCast(i));
    }
    
    // Delete elements that should cause merges
    for (0..20) |i| {
        _ = try tree.remove(@intCast(i * 2)); // Remove even numbers
    }
    
    // Verify forward iteration still works
    var forward_keys = std.ArrayList(i32).init(allocator);
    defer forward_keys.deinit();
    
    var iter = tree.iterator();
    while (iter.next()) |entry| {
        try forward_keys.append(entry.key);
    }
    
    // Verify reverse iteration still works
    var reverse_keys = std.ArrayList(i32).init(allocator);
    defer reverse_keys.deinit();
    
    var rev_iter = tree.reverseIterator();
    while (rev_iter.next()) |entry| {
        try reverse_keys.append(entry.key);
    }
    
    // Both should have 20 odd numbers
    try testing.expectEqual(@as(usize, 20), forward_keys.items.len);
    try testing.expectEqual(@as(usize, 20), reverse_keys.items.len);
    
    // Verify forward iteration has odd numbers in order
    for (forward_keys.items, 0..) |key, i| {
        try testing.expectEqual(@as(i32, @intCast(i * 2 + 1)), key);
    }
    
    // Verify reverse iteration is the reverse
    for (reverse_keys.items, 0..) |key, i| {
        const expected = @as(i32, @intCast((19 - i) * 2 + 1));
        try testing.expectEqual(expected, key);
    }
}

test "range queries should work correctly with linked leaves" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert data across multiple leaf nodes
    for (0..100) |i| {
        try tree.insert(@intCast(i), @intCast(i * 100));
    }
    
    // Test range query that spans multiple leaf nodes
    var results = std.ArrayList(Tree.Entry).init(allocator);
    defer results.deinit();
    
    try tree.range(25, 75, &results);
    
    // Should have 51 results (25 through 75 inclusive)
    try testing.expectEqual(@as(usize, 51), results.items.len);
    
    // Verify they're in order
    for (results.items, 0..) |entry, i| {
        const expected_key = @as(i32, @intCast(25 + i));
        try testing.expectEqual(expected_key, entry.key);
        try testing.expectEqual(expected_key * 100, entry.value);
    }
}

test "first and last leaf pointers should be maintained" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert enough to create multiple levels and leaves
    for (0..50) |i| {
        try tree.insert(@intCast(i), @intCast(i));
    }
    
    // Get first item via iterator
    var iter = tree.iterator();
    const first = iter.next().?;
    try testing.expectEqual(@as(i32, 0), first.key);
    
    // Get last item via reverse iterator
    var rev_iter = tree.reverseIterator();
    const last = rev_iter.next().?;
    try testing.expectEqual(@as(i32, 49), last.key);
    
    // Test after deletions
    _ = try tree.remove(0);
    _ = try tree.remove(49);
    
    // New first should be 1
    iter = tree.iterator();
    const new_first = iter.next().?;
    try testing.expectEqual(@as(i32, 1), new_first.key);
    
    // New last should be 48
    rev_iter = tree.reverseIterator();
    const new_last = rev_iter.next().?;
    try testing.expectEqual(@as(i32, 48), new_last.key);
}

test "linked list should handle single node tree" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Single element
    try tree.insert(42, 420);
    
    // Forward iteration
    var iter = tree.iterator();
    const entry = iter.next().?;
    try testing.expectEqual(@as(i32, 42), entry.key);
    try testing.expect(iter.next() == null);
    
    // Reverse iteration
    var rev_iter = tree.reverseIterator();
    const rev_entry = rev_iter.next().?;
    try testing.expectEqual(@as(i32, 42), rev_entry.key);
    try testing.expect(rev_iter.next() == null);
}

test "verify leaf chain integrity after complex operations" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Phase 1: Build initial tree
    for (0..30) |i| {
        try tree.insert(@intCast(i * 3), @intCast(i));
    }
    
    // Phase 2: Insert values that go between existing ones
    for (0..20) |i| {
        try tree.insert(@intCast(i * 3 + 1), @intCast(i + 100));
    }
    
    // Phase 3: Delete some values
    for (0..10) |i| {
        _ = try tree.remove(@intCast(i * 6));
    }
    
    // Collect all keys via forward iteration
    var forward_keys = std.ArrayList(i32).init(allocator);
    defer forward_keys.deinit();
    
    var iter = tree.iterator();
    while (iter.next()) |entry| {
        try forward_keys.append(entry.key);
    }
    
    // Verify keys are strictly increasing
    for (1..forward_keys.items.len) |i| {
        try testing.expect(forward_keys.items[i] > forward_keys.items[i - 1]);
    }
    
    // Verify count
    try testing.expectEqual(tree.len(), forward_keys.items.len);
}