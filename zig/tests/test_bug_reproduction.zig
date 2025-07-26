const std = @import("std");
const testing = std.testing;
const bplustree = @import("bplustree");

test "bug reproduction: linked list corruption during merge" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Create a scenario that will cause leaf merging
    // Insert keys to create multiple leaves
    for (0..20) |i| {
        try tree.insert(@intCast(i * 10), @intCast(i));
    }
    
    // Capture the linked list structure before deletion
    var items_before = std.ArrayList(Tree.Entry).init(allocator);
    defer items_before.deinit();
    
    var iter = tree.iterator();
    while (iter.next()) |entry| {
        try items_before.append(entry);
    }
    
    // Delete items to trigger merging
    for (5..15) |i| {
        _ = try tree.remove(@intCast(i * 10));
    }
    
    // Verify linked list is still consistent
    var items_after = std.ArrayList(Tree.Entry).init(allocator);
    defer items_after.deinit();
    
    iter = tree.iterator();
    while (iter.next()) |entry| {
        try items_after.append(entry);
    }
    
    // Check that iteration gives us all remaining keys in order
    var expected_keys = std.ArrayList(i32).init(allocator);
    defer expected_keys.deinit();
    
    for (0..5) |i| {
        try expected_keys.append(@intCast(i * 10));
    }
    for (15..20) |i| {
        try expected_keys.append(@intCast(i * 10));
    }
    
    try testing.expectEqual(expected_keys.items.len, items_after.items.len);
    
    for (expected_keys.items, items_after.items) |expected, actual| {
        try testing.expectEqual(expected, actual.key);
    }
}

test "bug reproduction: incorrect split logic odd capacity" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 5); // Odd capacity
    defer tree.deinit();
    
    // Insert enough data to cause splits
    for (0..20) |i| {
        try tree.insert(@intCast(i), @intCast(i));
    }
    
    // Verify tree structure is still valid
    // Min keys would be 5 / 2 = 2 for odd capacity
    
    // Since we can't directly inspect node sizes in Zig implementation,
    // we verify by checking that operations still work correctly
    
    // Remove some items
    for (5..10) |i| {
        _ = try tree.remove(@intCast(i));
    }
    
    // Tree should still be functional
    try testing.expect(tree.len() == 15);
    
    // Verify iteration still works
    var count: usize = 0;
    var iter = tree.iterator();
    while (iter.next()) |_| {
        count += 1;
    }
    try testing.expectEqual(@as(usize, 15), count);
}

test "bug reproduction: root split linked list race" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert enough to cause root split
    for (0..10) |i| {
        try tree.insert(@intCast(i), @intCast(i * 10));
    }
    
    // At this point we should have a branch root with leaf children
    // The leaf linked list should be properly maintained
    
    // Verify by checking that iteration gives us all keys in order
    var items = std.ArrayList(i32).init(allocator);
    defer items.deinit();
    
    var iter = tree.iterator();
    while (iter.next()) |entry| {
        try items.append(entry.key);
    }
    
    try testing.expectEqual(@as(usize, 10), items.items.len);
    
    // Check ordering
    for (1..items.items.len) |i| {
        try testing.expect(items.items[i] > items.items[i - 1]);
    }
}

test "bug reproduction: range iterator bound handling" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert test data
    for (0..10) |i| {
        try tree.insert(@intCast(i), @intCast(i * 10));
    }
    
    // Test exclusive range
    var results = std.ArrayList(Tree.Entry).init(allocator);
    defer results.deinit();
    
    try tree.rangeExclusive(3, 7, &results);
    
    // Should include 3, 4, 5, 6 but not 7 (half-open interval [3, 7))
    try testing.expectEqual(@as(usize, 4), results.items.len);
    
    const expected = [_]i32{ 3, 4, 5, 6 };
    for (expected, results.items) |exp, actual| {
        try testing.expectEqual(exp, actual.key);
    }
    
    // Test rangeFrom
    results.clearRetainingCapacity();
    try tree.rangeFrom(7, &results);
    
    // Should include 7, 8, 9
    try testing.expectEqual(@as(usize, 3), results.items.len);
    try testing.expectEqual(@as(i32, 7), results.items[0].key);
    
    // Test rangeTo
    results.clearRetainingCapacity();
    try tree.rangeTo(3, &results);
    
    // Should include 0, 1, 2, 3
    try testing.expectEqual(@as(usize, 4), results.items.len);
    try testing.expectEqual(@as(i32, 0), results.items[0].key);
    try testing.expectEqual(@as(i32, 3), results.items[3].key);
}

test "bug reproduction: root collapse edge cases" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Create a tree with multiple levels
    for (0..100) |i| {
        try tree.insert(@intCast(i), @intCast(i));
    }
    
    // Remove most items to force multiple levels of collapse
    for (0..95) |i| {
        _ = try tree.remove(@intCast(i));
    }
    
    // Tree should still be valid with remaining items
    try testing.expectEqual(@as(usize, 5), tree.len());
    
    // Check that the remaining items are still accessible
    for (95..100) |i| {
        const value = tree.get(@intCast(i));
        try testing.expectEqual(@as(i32, @intCast(i)), value.?);
    }
    
    // Verify iteration still works
    var count: usize = 0;
    var iter = tree.iterator();
    while (iter.next()) |entry| {
        count += 1;
        try testing.expect(entry.key >= 95 and entry.key < 100);
    }
    try testing.expectEqual(@as(usize, 5), count);
}

test "bug reproduction: iterator lifetime safety" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert test data
    for (0..10) |i| {
        try tree.insert(@intCast(i), @intCast(i));
    }
    
    // Create a range iterator
    var results = std.ArrayList(Tree.Entry).init(allocator);
    defer results.deinit();
    
    try tree.range(3, 6, &results);
    
    // This should not panic due to lifetime issues
    try testing.expectEqual(@as(usize, 4), results.items.len);
    
    // Verify the results are correct
    for (results.items, 0..) |entry, i| {
        try testing.expectEqual(@as(i32, @intCast(3 + i)), entry.key);
    }
}

test "bug reproduction: deletion pattern stress" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert a larger dataset
    for (0..50) |i| {
        try tree.insert(@intCast(i), @intCast(i * 100));
    }
    
    // Delete in a pattern that stresses rebalancing
    // Delete every third element
    for (0..17) |i| {
        _ = try tree.remove(@intCast(i * 3));
    }
    
    // Verify tree is still consistent
    var remaining_count: usize = 0;
    var iter = tree.iterator();
    var last_key: ?i32 = null;
    
    while (iter.next()) |entry| {
        remaining_count += 1;
        
        // Verify ordering is maintained
        if (last_key) |lk| {
            try testing.expect(entry.key > lk);
        }
        last_key = entry.key;
        
        // Verify we didn't delete this key
        try testing.expect(@mod(entry.key, 3) != 0 or entry.key >= 51);
    }
    
    try testing.expectEqual(tree.len(), remaining_count);
}

test "bug reproduction: rapid insert remove cycles" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Rapidly insert and remove the same keys
    for (0..10) |cycle| {
        // Insert batch
        for (0..20) |i| {
            try tree.insert(@intCast(i), @intCast(i + cycle * 100));
        }
        
        // Remove half
        for (0..10) |i| {
            _ = try tree.remove(@intCast(i * 2));
        }
        
        // Verify consistency
        var count: usize = 0;
        var iter = tree.iterator();
        while (iter.next()) |_| {
            count += 1;
        }
        try testing.expectEqual(@as(usize, 10), count);
        
        // Remove the rest
        for (0..10) |i| {
            _ = try tree.remove(@intCast(i * 2 + 1));
        }
        
        // Tree should be empty
        try testing.expectEqual(@as(usize, 0), tree.len());
    }
}

test "bug reproduction: large key value stress" {
    const allocator = testing.allocator;
    
    // Use maximum integer values to stress arithmetic
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    const test_values = [_]i32{
        std.math.minInt(i32),
        std.math.minInt(i32) + 1,
        -1000,
        -1,
        0,
        1,
        1000,
        std.math.maxInt(i32) - 1,
        std.math.maxInt(i32),
    };
    
    // Insert in random order
    const insert_order = [_]usize{ 4, 8, 0, 3, 7, 1, 5, 2, 6 };
    
    for (insert_order) |idx| {
        const key = test_values[idx];
        try tree.insert(key, key);
    }
    
    // Verify all values are present and in order
    var iter = tree.iterator();
    var collected = std.ArrayList(i32).init(allocator);
    defer collected.deinit();
    
    while (iter.next()) |entry| {
        try collected.append(entry.key);
    }
    
    // Should be in sorted order
    try testing.expectEqual(@as(usize, 9), collected.items.len);
    for (1..collected.items.len) |i| {
        try testing.expect(collected.items[i] > collected.items[i - 1]);
    }
}

test "bug reproduction: empty tree edge cases" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Test operations on empty tree
    try testing.expectEqual(@as(usize, 0), tree.len());
    try testing.expect(tree.get(0) == null);
    try testing.expectError(Tree.Error.KeyNotFound, tree.remove(0));
    try testing.expect(!tree.contains(0));
    
    // Test range operations on empty tree
    var results = std.ArrayList(Tree.Entry).init(allocator);
    defer results.deinit();
    
    try tree.range(0, 100, &results);
    try testing.expectEqual(@as(usize, 0), results.items.len);
    
    // Test single element tree
    try tree.insert(42, 420);
    try testing.expectEqual(@as(usize, 1), tree.len());
    
    // Remove the single element
    const removed = try tree.remove(42);
    try testing.expectEqual(@as(i32, 420), removed);
    try testing.expectEqual(@as(usize, 0), tree.len());
    
    // Tree should behave like empty again
    try testing.expectError(Tree.Error.KeyNotFound, tree.remove(42));
}