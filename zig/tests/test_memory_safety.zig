const std = @import("std");
const testing = std.testing;
const bplustree = @import("bplustree");

test "memory leak detection - basic operations" {
    // Use a test allocator that tracks memory leaks
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    
    // Test 1: Create and destroy empty tree
    {
        var tree = Tree.init(allocator, 16);
        defer tree.deinit();
    }
    
    // Test 2: Insert and then deinit
    {
        var tree = Tree.init(allocator, 16);
        defer tree.deinit();
        
        for (0..100) |i| {
            try tree.insert(@intCast(i), @intCast(i * 10));
        }
    }
    
    // Test 3: Insert and remove all
    {
        var tree = Tree.init(allocator, 8);
        defer tree.deinit();
        
        for (0..50) |i| {
            try tree.insert(@intCast(i), @intCast(i));
        }
        
        for (0..50) |i| {
            _ = try tree.remove(@intCast(i));
        }
    }
    
    // Test 4: Clear operation
    {
        var tree = Tree.init(allocator, 16);
        defer tree.deinit();
        
        for (0..200) |i| {
            try tree.insert(@intCast(i), @intCast(i));
        }
        
        tree.clear();
        
        // Insert again after clear
        for (0..100) |i| {
            try tree.insert(@intCast(i), @intCast(i * 2));
        }
    }
}

test "memory leak detection - heavy node splitting" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(u32, u32);
    var tree = Tree.init(allocator, 4); // Small capacity for more splits
    defer tree.deinit();
    
    // Insert many items to cause multiple splits
    for (0..1000) |i| {
        try tree.insert(@intCast(i), @intCast(i));
    }
    
    // Verify tree integrity
    try testing.expectEqual(@as(usize, 1000), tree.len());
}

test "memory leak detection - heavy node merging" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 6);
    defer tree.deinit();
    
    // Insert items
    for (0..500) |i| {
        try tree.insert(@intCast(i), @intCast(i));
    }
    
    // Delete every other item to cause merging
    var i: i32 = 0;
    while (i < 500) : (i += 2) {
        _ = try tree.remove(i);
    }
    
    // Verify final count
    try testing.expectEqual(@as(usize, 250), tree.len());
}

test "memory leak detection - repeated tree operations" {
    const allocator = testing.allocator;
    
    // Perform many cycles of tree creation/destruction
    for (0..10) |_| {
        const Tree = bplustree.BPlusTree(i32, []const u8);
        var tree = Tree.init(allocator, 32);
        defer tree.deinit();
        
        // Insert some string values
        try tree.insert(1, "one");
        try tree.insert(2, "two");
        try tree.insert(3, "three");
        try tree.insert(4, "four");
        try tree.insert(5, "five");
        
        // Remove some
        _ = try tree.remove(2);
        _ = try tree.remove(4);
        
        // Clear and insert again
        tree.clear();
        
        try tree.insert(10, "ten");
        try tree.insert(20, "twenty");
    }
}

test "memory leak detection - iterator lifecycle" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 16);
    defer tree.deinit();
    
    // Insert data
    for (0..100) |i| {
        try tree.insert(@intCast(i), @intCast(i * 100));
    }
    
    // Create and use multiple iterators
    for (0..5) |_| {
        var iter = tree.iterator();
        var count: usize = 0;
        while (iter.next()) |_| {
            count += 1;
            if (count > 10) break;
        }
    }
    
    // Create and use reverse iterators
    for (0..5) |_| {
        var rev_iter = tree.reverseIterator();
        var count: usize = 0;
        while (rev_iter.next()) |_| {
            count += 1;
            if (count > 10) break;
        }
    }
    
    // Use range queries
    var results = std.ArrayList(Tree.Entry).init(allocator);
    defer results.deinit();
    
    for (0..10) |i| {
        results.clearRetainingCapacity();
        const start = @as(i32, @intCast(i * 10));
        const end = start + 5;
        try tree.range(start, end, &results);
    }
}

test "memory leak detection - stress test with allocator" {
    const allocator = testing.allocator;
    var prng = std.Random.DefaultPrng.init(12345);
    const random = prng.random();
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 16);
    defer tree.deinit();
    
    // Perform many random operations
    for (0..10000) |i| {
        const op = random.int(u8) % 100;
        const key = @as(i32, @intCast(@mod(random.int(i32), 1000)));
        
        if (op < 60) { // 60% insert
            try tree.insert(key, key * 2);
        } else if (op < 80) { // 20% remove
            _ = tree.remove(key) catch {};
        } else if (op < 90) { // 10% lookup
            _ = tree.get(key);
        } else { // 10% contains
            _ = tree.contains(key);
        }
        
        // Occasionally clear the tree
        if (i % 2500 == 0 and i > 0) {
            tree.clear();
        }
    }
}

// This test helps verify memory is properly managed
// The testing allocator will automatically detect leaks
test "memory safety audit - all operations" {
    const allocator = testing.allocator;
    
    std.debug.print("\n=== Memory Safety Audit ===\n", .{});
    
    const Tree = bplustree.BPlusTree(u64, u64);
    var tree = Tree.init(allocator, 64);
    defer tree.deinit();
    
    // Phase 1: Build a large tree
    std.debug.print("Phase 1: Building tree with 10000 items...\n", .{});
    for (0..10000) |i| {
        try tree.insert(i, i * i);
    }
    
    // Phase 2: Perform various operations
    std.debug.print("Phase 2: Mixed operations...\n", .{});
    
    // Range queries
    var results = std.ArrayList(Tree.Entry).init(allocator);
    defer results.deinit();
    
    for (0..100) |i| {
        results.clearRetainingCapacity();
        try tree.range(i * 100, (i + 1) * 100, &results);
    }
    
    // Deletions
    for (0..5000) |i| {
        _ = try tree.remove(i * 2);
    }
    
    // Iterations
    var iter = tree.iterator();
    var iter_count: usize = 0;
    while (iter.next()) |_| {
        iter_count += 1;
    }
    
    std.debug.print("Phase 3: Final state - {} items iterated\n", .{iter_count});
    
    // Clear and rebuild
    tree.clear();
    
    for (0..1000) |i| {
        try tree.insert(i, i);
    }
    
    std.debug.print("Memory safety audit complete\n", .{});
}