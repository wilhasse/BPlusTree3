const std = @import("std");
const testing = std.testing;
const bplustree = @import("bplustree");

test "deletion should trigger node merging when underflow occurs" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4); // Small capacity to trigger merging
    defer tree.deinit();
    
    // Insert enough to create multiple nodes
    for (1..17) |i| {
        try tree.insert(@intCast(i), @intCast(i * 10));
    }
    
    const initial_height = tree.getHeight();
    try testing.expect(initial_height > 1);
    
    // Delete keys to cause underflow and merging
    for (1..9) |i| {
        _ = try tree.remove(@intCast(i));
    }
    
    // Tree should still be valid
    try testing.expectEqual(@as(usize, 8), tree.len());
    
    // Verify remaining keys are accessible
    for (9..17) |i| {
        const key = @as(i32, @intCast(i));
        try testing.expectEqual(key * 10, tree.get(key).?);
    }
    
    // Height might have decreased due to merging
    try testing.expect(tree.getHeight() <= initial_height);
}

test "deletion from root when it becomes empty" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 3); // Minimum capacity
    defer tree.deinit();
    
    // Insert and remove all
    try tree.insert(1, 100);
    try tree.insert(2, 200);
    try tree.insert(3, 300);
    
    _ = try tree.remove(1);
    _ = try tree.remove(2);
    _ = try tree.remove(3);
    
    try testing.expectEqual(@as(usize, 0), tree.len());
    try testing.expectEqual(@as(usize, 0), tree.getHeight());
}

test "deletion should redistribute keys from siblings before merging" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 6); // Capacity where redistribution makes sense
    defer tree.deinit();
    
    // Build a specific tree structure
    for (1..31) |i| {
        try tree.insert(@intCast(i), @intCast(i));
    }
    
    // Delete keys that would cause underflow
    const keys_to_delete = [_]i32{ 10, 11, 12, 13, 14 };
    for (keys_to_delete) |key| {
        _ = try tree.remove(key);
    }
    
    // Verify tree is still balanced and all remaining keys are accessible
    try testing.expectEqual(@as(usize, 25), tree.len());
    
    for (1..31) |i| {
        const key = @as(i32, @intCast(i));
        const found = tree.contains(key);
        
        // Check if this key should exist
        var should_exist = true;
        for (keys_to_delete) |deleted| {
            if (key == deleted) {
                should_exist = false;
                break;
            }
        }
        
        try testing.expectEqual(should_exist, found);
    }
}

test "deletion causing cascading merges up the tree" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Create a tree with specific structure
    for (1..33) |i| {
        try tree.insert(@intCast(i), @intCast(i * 100));
    }
    
    const initial_height = tree.getHeight();
    
    // Strategic deletions to cause cascading merges
    const delete_sequence = [_]i32{ 16, 17, 15, 18, 14, 19, 13, 20 };
    for (delete_sequence) |key| {
        _ = try tree.remove(key);
    }
    
    // Verify tree integrity
    try testing.expectEqual(@as(usize, 32 - delete_sequence.len), tree.len());
    
    // Tree might have reduced height
    try testing.expect(tree.getHeight() <= initial_height);
    
    // Verify all non-deleted keys are still accessible
    var iter = tree.iterator();
    var count: usize = 0;
    while (iter.next()) |entry| {
        count += 1;
        try testing.expectEqual(entry.key * 100, entry.value);
    }
    try testing.expectEqual(tree.len(), count);
}

test "deletion stress test with underflow handling" {
    const allocator = testing.allocator;
    var prng = std.Random.DefaultPrng.init(42);
    const random = prng.random();
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 5); // Small capacity for more underflows
    defer tree.deinit();
    
    // Track what should be in the tree
    var expected = std.AutoHashMap(i32, i32).init(allocator);
    defer expected.deinit();
    
    // Insert initial data
    for (0..100) |i| {
        const key = @as(i32, @intCast(i));
        try tree.insert(key, key * 2);
        try expected.put(key, key * 2);
    }
    
    // Randomly delete half the keys
    var keys_to_delete = std.ArrayList(i32).init(allocator);
    defer keys_to_delete.deinit();
    
    var iter = expected.iterator();
    while (iter.next()) |entry| {
        if (random.int(u8) % 2 == 0) {
            try keys_to_delete.append(entry.key_ptr.*);
        }
    }
    
    // Perform deletions
    for (keys_to_delete.items) |key| {
        _ = try tree.remove(key);
        _ = expected.remove(key);
    }
    
    // Verify final state
    try testing.expectEqual(expected.count(), tree.len());
    
    // Verify all remaining entries
    iter = expected.iterator();
    while (iter.next()) |entry| {
        const tree_val = tree.get(entry.key_ptr.*);
        try testing.expectEqual(@as(?i32, entry.value_ptr.*), tree_val);
    }
    
    // Verify iteration order
    var tree_iter = tree.iterator();
    var last_key: ?i32 = null;
    while (tree_iter.next()) |tree_entry| {
        if (last_key) |lk| {
            try testing.expect(tree_entry.key > lk);
        }
        last_key = tree_entry.key;
    }
}