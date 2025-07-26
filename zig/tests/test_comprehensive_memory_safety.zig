const std = @import("std");
const testing = std.testing;
const bplustree = @import("bplustree");

test "memory safety: arena bounds checking" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, []const u8);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Test with a large number of items to verify no panics
    const test_size = 10000;
    
    for (0..test_size) |i| {
        const value = try std.fmt.allocPrint(allocator, "value_{}", .{i});
        defer allocator.free(value);
        try tree.insert(@intCast(i), value);
        
        // Verify bounds checking every 1000 items
        if (i % 1000 == 999) {
            try testing.expect(tree.len() == i + 1);
        }
    }
    
    // Verify all items are accessible
    for (0..test_size) |i| {
        try testing.expect(tree.contains(@intCast(i)));
    }
    
    // Test deletion with bounds checking
    for (0..test_size / 2) |i| {
        _ = try tree.remove(@intCast(i));
    }
    
    try testing.expectEqual(@as(usize, test_size / 2), tree.len());
    
    // Verify remaining items are still accessible
    for (test_size / 2..test_size) |i| {
        try testing.expect(tree.contains(@intCast(i)));
    }
}

test "memory safety: stack overflow prevention" {
    const allocator = testing.allocator;
    
    // Test with minimum capacity to create deep trees
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 2);
    defer tree.deinit();
    
    // Insert enough items to create a very deep tree
    const deep_test_size = 5000;
    
    for (0..deep_test_size) |i| {
        try tree.insert(@intCast(i), @intCast(i));
    }
    
    // If we don't stack overflow during insertion, test passed
    try testing.expect(tree.len() == deep_test_size);
    
    // Test deep traversal doesn't stack overflow
    var count: usize = 0;
    var iter = tree.iterator();
    while (iter.next()) |_| {
        count += 1;
    }
    
    try testing.expectEqual(deep_test_size, count);
}

test "memory safety: allocation failure handling" {
    // Custom allocator that fails after N allocations
    const FailingAllocator = struct {
        backing_allocator: std.mem.Allocator,
        allocations_until_failure: usize,
        current_allocations: usize,
        
        pub fn init(backing: std.mem.Allocator, fail_after: usize) @This() {
            return .{
                .backing_allocator = backing,
                .allocations_until_failure = fail_after,
                .current_allocations = 0,
            };
        }
        
        pub fn allocator(self: *@This()) std.mem.Allocator {
            return .{
                .ptr = self,
                .vtable = &.{
                    .alloc = alloc,
                    .resize = resize,
                    .free = free,
                    .remap = nopRemap,
                },
            };
        }
        
        fn nopRemap(ctx: *anyopaque, old_mem: []u8, old_alignment: std.mem.Alignment, new_size: usize, ret_addr: usize) ?[*]u8 {
            _ = ctx;
            _ = old_mem;
            _ = old_alignment;
            _ = new_size;
            _ = ret_addr;
            return null;
        }
        
        fn alloc(ctx: *anyopaque, len: usize, ptr_align: std.mem.Alignment, ret_addr: usize) ?[*]u8 {
            const self: *@This() = @ptrCast(@alignCast(ctx));
            self.current_allocations += 1;
            
            if (self.current_allocations > self.allocations_until_failure) {
                return null;
            }
            
            return self.backing_allocator.rawAlloc(len, ptr_align, ret_addr);
        }
        
        fn resize(ctx: *anyopaque, buf: []u8, log2_buf_align: std.mem.Alignment, new_len: usize, ret_addr: usize) bool {
            const self: *@This() = @ptrCast(@alignCast(ctx));
            return self.backing_allocator.rawResize(buf, log2_buf_align, new_len, ret_addr);
        }
        
        fn free(ctx: *anyopaque, buf: []u8, log2_buf_align: std.mem.Alignment, ret_addr: usize) void {
            const self: *@This() = @ptrCast(@alignCast(ctx));
            self.backing_allocator.rawFree(buf, log2_buf_align, ret_addr);
        }
    };
    
    var failing_alloc = FailingAllocator.init(testing.allocator, 50);
    const alloc = failing_alloc.allocator();
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(alloc, 4);
    defer tree.deinit();
    
    // Insert until allocation fails
    var i: i32 = 0;
    var allocation_failed = false;
    
    while (i < 1000) : (i += 1) {
        tree.insert(i, i * 10) catch {
            allocation_failed = true;
            break;
        };
    }
    
    // Should have failed at some point
    try testing.expect(allocation_failed);
    
    // Tree should still be functional with existing data
    var count: usize = 0;
    var iter = tree.iterator();
    while (iter.next()) |_| {
        count += 1;
    }
    
    try testing.expect(count > 0);
    try testing.expect(count < 1000);
}

test "memory safety: integer overflow prevention" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Test with large numbers that could cause overflow
    const large_numbers = [_]i32{
        std.math.maxInt(i32) - 1000,
        std.math.maxInt(i32) - 100,
        std.math.maxInt(i32) - 10,
        std.math.maxInt(i32) - 1,
    };
    
    for (large_numbers) |num| {
        try tree.insert(num, num);
    }
    
    // Verify they're all accessible
    for (large_numbers) |num| {
        try testing.expect(tree.contains(num));
    }
    
    // Test operations with these large numbers
    var items = std.ArrayList(i32).init(allocator);
    defer items.deinit();
    
    var iter = tree.iterator();
    while (iter.next()) |entry| {
        try items.append(entry.key);
    }
    
    try testing.expectEqual(@as(usize, 4), items.items.len);
    
    // Test range operations with large numbers
    var range_results = std.ArrayList(Tree.Entry).init(allocator);
    defer range_results.deinit();
    
    const range_start = std.math.maxInt(i32) - 500;
    try tree.rangeFrom(range_start, &range_results);
    
    try testing.expectEqual(@as(usize, 3), range_results.items.len);
}

test "memory safety: stress test with allocations and deallocations" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, []const u8);
    var tree = Tree.init(allocator, 8);
    defer tree.deinit();
    
    // Stress test with many allocations/deallocations
    for (0..100) |round| {
        // Allocate a batch
        const base = @as(i32, @intCast(round * 1000));
        
        for (0..500) |i| {
            const value = try std.fmt.allocPrint(allocator, "stress_{}_{}", .{ round, i });
            defer allocator.free(value);
            try tree.insert(base + @as(i32, @intCast(i)), value);
        }
        
        // Deallocate some items
        for (100..400) |i| {
            _ = try tree.remove(base + @as(i32, @intCast(i)));
        }
        
        // Every 20 rounds, verify integrity
        if (round % 20 == 19) {
            var count: usize = 0;
            var iter = tree.iterator();
            while (iter.next()) |_| {
                count += 1;
            }
            
            try testing.expectEqual(tree.len(), count);
        }
    }
}

test "memory safety: value ownership and lifetime" {
    const allocator = testing.allocator;
    
    // Test with owned heap-allocated values
    const OwnedValue = struct {
        data: []u8,
        allocator: std.mem.Allocator,
        id: u32,
        
        fn init(alloc: std.mem.Allocator, id: u32) !@This() {
            const data = try alloc.alloc(u8, 256);
            @memset(data, @truncate(id));
            return .{
                .data = data,
                .allocator = alloc,
                .id = id,
            };
        }
        
        fn deinit(self: @This()) void {
            self.allocator.free(self.data);
        }
        
        fn validate(self: @This()) bool {
            for (self.data) |byte| {
                if (byte != @as(u8, @truncate(self.id))) {
                    return false;
                }
            }
            return true;
        }
    };
    
    const Tree = bplustree.BPlusTree(i32, OwnedValue);
    var tree = Tree.init(allocator, 4);
    defer {
        // Clean up all remaining values
        var iter = tree.iterator();
        while (iter.next()) |entry| {
            entry.value.deinit();
        }
        tree.deinit();
    }
    
    // Insert values
    for (0..50) |i| {
        const value = try OwnedValue.init(allocator, @intCast(i));
        try tree.insert(@intCast(i), value);
    }
    
    // Verify all values are intact
    for (0..50) |i| {
        const value = tree.get(@intCast(i));
        try testing.expect(value != null);
        try testing.expect(value.?.validate());
    }
    
    // Remove some values (must clean up)
    for (10..30) |i| {
        if (tree.remove(@intCast(i))) |removed_value| {
            try testing.expect(removed_value.validate());
            removed_value.deinit();
        } else |_| {
            unreachable;
        }
    }
    
    // Verify remaining values are still intact
    var remaining_count: usize = 0;
    var iter = tree.iterator();
    while (iter.next()) |entry| {
        try testing.expect(entry.value.validate());
        remaining_count += 1;
    }
    
    try testing.expectEqual(@as(usize, 30), remaining_count);
}

test "memory safety: concurrent-like access patterns" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Simulate concurrent-like access patterns
    const num_threads = 4;
    const ops_per_thread = 1000;
    
    // Each "thread" works on different key ranges
    for (0..num_threads) |thread_id| {
        const base_key = @as(i32, @intCast(thread_id * 10000));
        
        // Insert phase
        for (0..ops_per_thread / 2) |i| {
            const key = base_key + @as(i32, @intCast(i));
            try tree.insert(key, key * 2);
        }
        
        // Mixed operations phase
        for (0..ops_per_thread / 2) |i| {
            const key = base_key + @as(i32, @intCast(i));
            
            switch (i % 3) {
                0 => _ = tree.get(key),
                1 => _ = tree.remove(key) catch {},
                2 => try tree.insert(key + @as(i32, @intCast(ops_per_thread)), key),
                else => unreachable,
            }
        }
    }
    
    // Verify tree consistency
    var last_key: ?i32 = null;
    var iter = tree.iterator();
    while (iter.next()) |entry| {
        if (last_key) |lk| {
            try testing.expect(entry.key > lk);
        }
        last_key = entry.key;
    }
}

test "memory safety: edge case key values" {
    const allocator = testing.allocator;
    
    // Test with various integer types
    inline for (.{ u8, u16, u32, i8, i16, i32 }) |IntType| {
        const Tree = bplustree.BPlusTree(IntType, IntType);
        var tree = Tree.init(allocator, 4);
        defer tree.deinit();
        
        const edge_values = if (@typeInfo(IntType).int.signedness == .signed)
            [_]IntType{
                std.math.minInt(IntType),
                std.math.minInt(IntType) + 1,
                0,
                std.math.maxInt(IntType) - 1,
                std.math.maxInt(IntType),
            }
        else
            [_]IntType{
                std.math.minInt(IntType),
                std.math.minInt(IntType) + 1,
                std.math.maxInt(IntType) / 2,
                std.math.maxInt(IntType) - 1,
                std.math.maxInt(IntType),
            };
        
        // Insert edge values
        for (edge_values) |val| {
            try tree.insert(val, val);
        }
        
        // Verify all values are present
        for (edge_values) |val| {
            try testing.expect(tree.contains(val));
            try testing.expectEqual(val, tree.get(val).?);
        }
        
        // Test iteration with edge values
        var count: usize = 0;
        var iter = tree.iterator();
        while (iter.next()) |_| {
            count += 1;
        }
        try testing.expectEqual(@as(usize, edge_values.len), count);
    }
}

// Note: Test with zero-sized value type (void) removed due to Zig standard library
// issues with void types in arrays causing division by zero errors.