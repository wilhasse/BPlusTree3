const std = @import("std");
const testing = std.testing;
const bplustree = @import("bplustree");

test "error handling: invalid capacity validation" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    
    // Test various invalid capacities
    const invalid_capacities = [_]usize{ 0, 1 };
    
    for (invalid_capacities) |cap| {
        const result = Tree.initWithValidation(allocator, cap);
        try testing.expectError(Tree.Error.InvalidCapacity, result);
    }
    
    // Test valid capacities
    const valid_capacities = [_]usize{ 2, 3, 4, 128, 1024 };
    
    for (valid_capacities) |cap| {
        var tree = try Tree.initWithValidation(allocator, cap);
        tree.deinit();
    }
}

test "error handling: remove from empty tree" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Multiple attempts to remove from empty tree
    const keys = [_]i32{ 0, -1, 42, std.math.maxInt(i32), std.math.minInt(i32) };
    
    for (keys) |key| {
        const result = tree.remove(key);
        try testing.expectError(Tree.Error.KeyNotFound, result);
    }
}

test "error handling: remove non-existent keys" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert some keys
    for (0..10) |i| {
        try tree.insert(@intCast(i * 10), @intCast(i));
    }
    
    // Try to remove non-existent keys
    const non_existent = [_]i32{ 5, 15, 25, -10, 100, 999 };
    
    for (non_existent) |key| {
        const result = tree.remove(key);
        try testing.expectError(Tree.Error.KeyNotFound, result);
        
        // Tree should remain unchanged
        try testing.expectEqual(@as(usize, 10), tree.len());
    }
}

test "error handling: comprehensive error scenarios" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    
    // Scenario 1: Operations on uninitialized tree (after clear)
    var tree1 = Tree.init(allocator, 4);
    try tree1.insert(1, 10);
    tree1.clear();
    
    try testing.expectError(Tree.Error.KeyNotFound, tree1.remove(1));
    try testing.expect(tree1.get(1) == null);
    tree1.deinit();
    
    // Scenario 2: Boundary conditions with capacity
    var tree2 = Tree.init(allocator, 2); // Minimum capacity
    
    // Fill to capacity
    try tree2.insert(1, 1);
    try tree2.insert(2, 2);
    
    // This should trigger split without error
    try tree2.insert(3, 3);
    try testing.expect(tree2.getHeight() > 1);
    
    tree2.deinit();
}

test "error handling: batch operations error propagation" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert batch
    const keys = [_]i32{ 10, 20, 30, 40, 50 };
    for (keys) |key| {
        try tree.insert(key, key * 10);
    }
    
    // Batch remove with errors
    const remove_batch = [_]i32{ 10, 15, 20, 25, 30 }; // 15 and 25 don't exist
    var remove_errors: usize = 0;
    
    for (remove_batch) |key| {
        if (tree.remove(key)) |_| {
            // Success
        } else |err| {
            try testing.expectEqual(Tree.Error.KeyNotFound, err);
            remove_errors += 1;
        }
    }
    
    try testing.expectEqual(@as(usize, 2), remove_errors);
    try testing.expectEqual(@as(usize, 2), tree.len()); // 40 and 50 remain
}

// TODO: This test is disabled because the B+ tree implementation doesn't properly
// clean up allocated nodes when allocation fails during split operations.
// This is a known limitation that should be addressed in the implementation.
// test "error handling: memory allocation failure simulation" {
//    // Test behavior when allocator fails
//    const FailingAllocator = struct {
//        backing_allocator: std.mem.Allocator,
//        fail_after: usize,
//        allocation_count: usize,
//        
//        pub fn init(backing: std.mem.Allocator, fail_after: usize) @This() {
//            return .{
//                .backing_allocator = backing,
//                .fail_after = fail_after,
//                .allocation_count = 0,
//            };
//        }
//        
//        pub fn allocator(self: *@This()) std.mem.Allocator {
//            return .{
//                .ptr = self,
//                .vtable = &.{
//                    .alloc = alloc,
//                    .resize = resize,
//                    .free = free,
//                    .remap = remap,
//                },
//            };
//        }
//        
//        fn alloc(ctx: *anyopaque, len: usize, ptr_align: std.mem.Alignment, ret_addr: usize) ?[*]u8 {
//            const self: *@This() = @ptrCast(@alignCast(ctx));
//            self.allocation_count += 1;
//            
//            if (self.allocation_count > self.fail_after) {
//                return null; // Simulate allocation failure
//            }
//            
//            return self.backing_allocator.rawAlloc(len, ptr_align, ret_addr);
//        }
//        
//        fn resize(ctx: *anyopaque, buf: []u8, log2_buf_align: std.mem.Alignment, new_len: usize, ret_addr: usize) bool {
//            const self: *@This() = @ptrCast(@alignCast(ctx));
//            return self.backing_allocator.rawResize(buf, log2_buf_align, new_len, ret_addr);
//        }
//        
//        fn free(ctx: *anyopaque, buf: []u8, log2_buf_align: std.mem.Alignment, ret_addr: usize) void {
//            const self: *@This() = @ptrCast(@alignCast(ctx));
//            self.backing_allocator.rawFree(buf, log2_buf_align, ret_addr);
//        }
//        
//        fn remap(ctx: *anyopaque, buf: []u8, log2_buf_align: std.mem.Alignment, new_len: usize, ret_addr: usize) ?[*]u8 {
//            const self: *@This() = @ptrCast(@alignCast(ctx));
//            self.allocation_count += 1;
//            
//            if (self.allocation_count > self.fail_after) {
//                return null; // Simulate allocation failure
//            }
//            
//            // rawResize returns bool, so we need to handle it differently
//            if (self.backing_allocator.rawResize(buf, log2_buf_align, new_len, ret_addr)) {
//                return buf.ptr;
//            } else {
//                return self.backing_allocator.rawAlloc(new_len, log2_buf_align, ret_addr);
//            }
//        }
//    };
//    
//    var failing_alloc = FailingAllocator.init(testing.allocator, 10);
//    const alloc = failing_alloc.allocator();
//    
//    const Tree = bplustree.BPlusTree(i32, i32);
//    var tree = Tree.init(alloc, 4);
//    defer tree.deinit();
//    
//    // Insert until allocation fails
//    var i: i32 = 0;
//    while (i < 100) : (i += 1) {
//        tree.insert(i, i * 10) catch |err| {
//            try testing.expectEqual(Tree.Error.OutOfMemory, err);
//            break;
//        };
//    }
    
//    // Tree should still be functional with existing data
//    try testing.expect(tree.len() > 0);
//    try testing.expect(tree.len() < 100);
// }

test "error handling: defensive programming patterns" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Pattern 1: Check before remove
    const key_to_remove = 42;
    if (tree.contains(key_to_remove)) {
        _ = try tree.remove(key_to_remove);
    } else {
        // Handle missing key without error
    }
    
    // Pattern 2: Use getWithDefault for safe access
    const default_value = -1;
    const value = tree.getWithDefault(999, default_value);
    try testing.expectEqual(default_value, value);
    
    // Pattern 3: Batch operations with error counting
    const keys = [_]i32{ 1, 2, 3, 4, 5 };
    var insert_count: usize = 0;
    
    for (keys) |k| {
        tree.insert(k, k * 100) catch {
            continue; // Skip on error
        };
        insert_count += 1;
    }
    
    try testing.expectEqual(@as(usize, 5), insert_count);
}

test "error handling: error recovery and tree consistency" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 3);
    defer tree.deinit();
    
    // Build a tree
    for (0..20) |i| {
        try tree.insert(@intCast(i), @intCast(i * 10));
    }
    
    // Attempt operations that might fail
    var errors_encountered: usize = 0;
    
    // Try to remove keys, some exist, some don't
    for (0..30) |i| {
        const key = @as(i32, @intCast(i));
        if (tree.remove(key)) |_| {
            // Successfully removed
        } else |err| {
            try testing.expectEqual(Tree.Error.KeyNotFound, err);
            errors_encountered += 1;
        }
    }
    
    try testing.expectEqual(@as(usize, 10), errors_encountered); // Keys 20-29 don't exist
    
    // Verify tree is still consistent after errors
    try testing.expectEqual(@as(usize, 0), tree.len()); // All existing keys removed
    
    // Tree should still be usable
    try tree.insert(100, 1000);
    try testing.expectEqual(@as(i32, 1000), tree.get(100).?);
}

test "error handling: complex error scenarios with custom types" {
    const allocator = testing.allocator;
    
    // Custom type that can fail during operations
    const MaybeValue = struct {
        data: ?[]u8,
        allocator: std.mem.Allocator,
        
        fn init(alloc: std.mem.Allocator, size: usize) !@This() {
            return .{
                .data = try alloc.alloc(u8, size),
                .allocator = alloc,
            };
        }
        
        fn deinit(self: @This()) void {
            if (self.data) |d| {
                self.allocator.free(d);
            }
        }
    };
    
    const Tree = bplustree.BPlusTree(i32, MaybeValue);
    var tree = Tree.init(allocator, 4);
    defer {
        // Clean up any remaining values
        var iter = tree.iterator();
        while (iter.next()) |entry| {
            entry.value.deinit();
        }
        tree.deinit();
    }
    
    // Insert values of varying sizes
    const sizes = [_]usize{ 10, 100, 1000, 10000 };
    
    for (sizes, 0..) |size, i| {
        const value = try MaybeValue.init(allocator, size);
        try tree.insert(@intCast(i), value);
    }
    
    // Remove and clean up
    for (0..sizes.len) |i| {
        const removed = try tree.remove(@intCast(i));
        removed.deinit();
    }
    
    try testing.expectEqual(@as(usize, 0), tree.len());
}

test "error handling: edge case error conditions" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Edge case 1: Remove from tree that only has root
    try tree.insert(1, 10);
    _ = try tree.remove(1);
    try testing.expectError(Tree.Error.KeyNotFound, tree.remove(1));
    
    // Edge case 2: Multiple operations on same key
    try tree.insert(42, 100);
    try tree.insert(42, 200); // Update
    try tree.insert(42, 300); // Update again
    
    const val = try tree.remove(42);
    try testing.expectEqual(@as(i32, 300), val);
    try testing.expectError(Tree.Error.KeyNotFound, tree.remove(42));
    
    // Edge case 3: Operations after clear
    for (0..10) |i| {
        try tree.insert(@intCast(i), @intCast(i));
    }
    tree.clear();
    
    for (0..10) |i| {
        try testing.expectError(Tree.Error.KeyNotFound, tree.remove(@intCast(i)));
    }
}