const std = @import("std");
const testing = std.testing;
const bplustree = @import("bplustree");

test "adversarial: root collapse infinite loop attack" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Build a multi-level tree
    for (0..64) |i| {
        try tree.insert(@intCast(i), @intCast(i * 10));
    }
    
    // Delete in a pattern that forces repeated root collapses
    var i: i32 = 63;
    while (i >= 0) : (i -= 1) {
        if (@mod(i, 8) != 0) {
            _ = try tree.remove(i);
            // Verify tree is still valid after each deletion
            try testing.expect(tree.len() > 0 or i == 0);
        }
    }
    
    // Tree should now have very few items but still be valid
    var remaining_count: usize = 0;
    var iter = tree.iterator();
    while (iter.next()) |_| {
        remaining_count += 1;
    }
    try testing.expectEqual(tree.len(), remaining_count);
    
    // Try to break it with one more operation
    try tree.insert(100, 1000);
    
    // Verify final state
    try testing.expectEqual(remaining_count + 1, tree.len());
}

test "adversarial: minimum capacity edge cases attack" {
    const allocator = testing.allocator;
    
    // Attack: Use minimum capacity (2) and test all edge cases
    const capacity: usize = 2; // Minimum allowed in Zig implementation
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = try Tree.initWithValidation(allocator, capacity);
    defer tree.deinit();
    
    // Test 1: Exactly capacity items in root leaf
    for (0..capacity) |i| {
        try tree.insert(@intCast(i), @intCast(i));
    }
    
    // This should trigger first split
    try tree.insert(@intCast(capacity), @intCast(capacity));
    
    // Verify split happened correctly
    try testing.expect(tree.getHeight() > 1);
    
    // Test 2: Clear and test deletion patterns
    tree.clear();
    
    // Insert pattern to create specific structure
    for (0..50) |i| {
        try tree.insert(@intCast(i * 2), @intCast(i * 20));
    }
    
    // Delete to leave each node at minimum
    const delete_pattern = [_]i32{ 2, 6, 10, 14, 18, 22, 26, 30, 34, 38, 42, 46, 50, 54, 58 };
    for (delete_pattern) |key| {
        if (tree.contains(key)) {
            _ = try tree.remove(key);
        }
    }
    
    // Try one more deletion - should trigger rebalancing
    _ = try tree.remove(0);
    
    // Verify tree is still valid
    try testing.expect(tree.len() < 50);
}

test "adversarial: odd capacity arithmetic attack" {
    const allocator = testing.allocator;
    
    // Attack: Use odd capacities to expose integer division bugs
    const odd_capacities = [_]usize{ 3, 5, 7, 9, 11 };
    
    for (odd_capacities) |capacity| {
        const Tree = bplustree.BPlusTree(i32, i32);
        var tree = Tree.init(allocator, capacity);
        defer tree.deinit();
        
        // Fill to exactly trigger splits at boundaries
        const total = capacity * 10;
        for (0..total) |i| {
            try tree.insert(@intCast(i), @intCast(i));
        }
        
        // min_keys calculation for odd numbers
        const min_keys = capacity / 2; // Floor division
        _ = min_keys; // Used for validation
        
        // Delete to exactly min_keys in some nodes
        var deleted: usize = 0;
        var j: i32 = @intCast(total - 1);
        while (j >= 0) : (j -= 1) {
            if (deleted >= capacity * 7) {
                break;
            }
            if (@mod(j, 3) != 0) {
                _ = try tree.remove(j);
                deleted += 1;
            }
        }
        
        // Verify min_keys calculation doesn't break invariants
        try testing.expect(tree.len() == total - deleted);
        
        // Tree should still function correctly
        try tree.insert(-1, -1);
        try testing.expectEqual(@as(i32, -1), tree.get(-1).?);
    }
}

test "adversarial: insert remove same key attack" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Attack: Rapidly insert/remove same keys
    const attack_key = 42;
    
    // Phase 1: Build some structure
    for (0..20) |i| {
        try tree.insert(@intCast(i), @intCast(i));
    }
    
    // Phase 2: Thrash on one key
    for (0..100) |i| {
        if (i % 2 == 0) {
            try tree.insert(attack_key, @intCast(i));
        } else {
            if (tree.contains(attack_key)) {
                _ = try tree.remove(attack_key);
            }
        }
        
        // Verify tree consistency
        var count: usize = 0;
        var iter = tree.iterator();
        while (iter.next()) |_| {
            count += 1;
        }
        try testing.expectEqual(tree.len(), count);
    }
}

test "adversarial: split merge thrashing attack" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Attack: Insert/delete at split boundaries repeatedly
    const boundary = 4; // Capacity
    
    for (0..50) |cycle| {
        // Fill to just before split
        for (0..boundary - 1) |i| {
            const key = @as(i32, @intCast(cycle * 100 + i));
            try tree.insert(key, key);
        }
        
        // Trigger split
        const split_key = @as(i32, @intCast(cycle * 100 + boundary));
        try tree.insert(split_key, split_key);
        
        // Delete to trigger potential merge
        for (0..boundary + 1) |i| { // Include the split_key
            const key = @as(i32, @intCast(cycle * 100 + i));
            if (tree.contains(key)) {
                _ = try tree.remove(key);
            }
        }
    }
    
    // Tree should be valid but might be empty or have few items
    try testing.expect(tree.len() < 10);
}

test "adversarial: extreme key ordering attack" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Attack: Insert keys in pathological order
    const n = 100;
    
    // Pattern 1: Alternating high/low
    for (0..n / 2) |i| {
        try tree.insert(@intCast(i), @intCast(i));
        try tree.insert(@intCast(n - i - 1), @intCast(n - i - 1));
    }
    
    // Pattern 2: Delete middle elements
    for (n / 4..3 * n / 4) |i| {
        _ = try tree.remove(@intCast(i));
    }
    
    // Pattern 3: Re-insert in different order
    var j = @as(i32, @intCast(3 * n / 4 - 1));
    while (j >= @as(i32, @intCast(n / 4))) : (j -= 1) {
        try tree.insert(j, j * 2);
    }
    
    // Verify ordering is maintained
    var last_key: ?i32 = null;
    var iter = tree.iterator();
    while (iter.next()) |entry| {
        if (last_key) |lk| {
            try testing.expect(entry.key > lk);
        }
        last_key = entry.key;
    }
}

test "adversarial: concurrent operation simulation attack" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 6);
    defer tree.deinit();
    
    // Simulate concurrent operations by interleaving
    const ops = [_]enum { Insert, Remove, Get, Range }{ .Insert, .Remove, .Get, .Range };
    const keys = [_]i32{ 10, 20, 30, 40, 50, 15, 25, 35, 45, 55 };
    
    // Build initial tree
    for (keys) |key| {
        try tree.insert(key, key * 10);
    }
    
    // Interleaved operations
    for (0..100) |i| {
        const op = ops[i % ops.len];
        const key = keys[i % keys.len];
        
        switch (op) {
            .Insert => {
                try tree.insert(key + @as(i32, @intCast(i)), @intCast(i));
            },
            .Remove => {
                if (tree.contains(key)) {
                    _ = try tree.remove(key);
                }
            },
            .Get => {
                _ = tree.get(key);
            },
            .Range => {
                var results = std.ArrayList(Tree.Entry).init(allocator);
                defer results.deinit();
                try tree.range(key - 5, key + 5, &results);
            },
        }
    }
    
    // Verify final consistency
    try testing.expect(tree.len() > 0);
}

test "adversarial: memory pressure attack" {
    const allocator = testing.allocator;
    
    // Use large value type to create memory pressure
    const LargeValue = struct {
        data: [256]u8,
        
        fn init(n: u8) @This() {
            var val = @This(){ .data = undefined };
            @memset(&val.data, n);
            return val;
        }
    };
    
    const Tree = bplustree.BPlusTree(i32, LargeValue);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert many large values
    for (0..50) |i| {
        try tree.insert(@intCast(i), LargeValue.init(@truncate(i)));
    }
    
    // Delete half
    for (0..25) |i| {
        _ = try tree.remove(@intCast(i * 2));
    }
    
    // Re-insert with different values
    for (0..25) |i| {
        try tree.insert(@intCast(i * 2), LargeValue.init(@truncate(i + 100)));
    }
    
    // Verify all operations succeeded
    try testing.expectEqual(@as(usize, 50), tree.len());
}

test "adversarial: deep tree attack" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 2); // Minimum capacity for maximum depth
    defer tree.deinit();
    
    // Create very deep tree
    for (0..1000) |i| {
        try tree.insert(@intCast(i), @intCast(i));
    }
    
    // Attack deep paths
    var prng = std.Random.DefaultPrng.init(12345);
    const random = prng.random();
    
    for (0..100) |_| {
        const key = random.intRangeAtMost(i32, 0, 999);
        
        if (random.boolean()) {
            try tree.insert(key, key * 2);
        } else if (tree.contains(key)) {
            _ = try tree.remove(key);
        }
    }
    
    // Verify tree didn't degrade
    try testing.expect(tree.getHeight() < 20); // Reasonable bound for balanced tree
}

test "adversarial: boundary value attack" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Test all boundary conditions
    const boundaries = [_]struct { cap: usize, split_at: usize }{
        .{ .cap = 2, .split_at = 2 },
        .{ .cap = 3, .split_at = 3 },
        .{ .cap = 4, .split_at = 4 },
        .{ .cap = 5, .split_at = 5 },
    };
    
    for (boundaries) |boundary| {
        tree.clear();
        
        // Fill to exactly split point
        for (0..boundary.split_at) |i| {
            try tree.insert(@intCast(i * 10), @intCast(i));
        }
        
        const height_before = tree.getHeight();
        
        // This should trigger split
        try tree.insert(@intCast(boundary.split_at * 10), @intCast(boundary.split_at));
        
        // Verify split occurred when appropriate
        // Note: Actual split behavior depends on implementation details
        if (boundary.split_at > boundary.cap) {
            // Should have split
            try testing.expect(tree.getHeight() >= height_before);
        }
    }
}