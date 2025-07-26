const std = @import("std");
const bplustree = @import("bplustree");

const BenchmarkResult = struct {
    name: []const u8,
    operations: usize,
    time_ns: u64,
    ops_per_sec: f64,
    ns_per_op: f64,
};

fn printResult(result: BenchmarkResult) void {
    std.debug.print("{s:35} {:>10} ops in {:>8.2}ms | {:>12.0} ops/sec | {:>8.2} ns/op\n", .{
        result.name,
        result.operations,
        @as(f64, @floatFromInt(result.time_ns)) / 1_000_000,
        result.ops_per_sec,
        result.ns_per_op,
    });
}

fn printComparison(name: []const u8, bplus_time: u64, hashmap_time: u64) void {
    const ratio = @as(f64, @floatFromInt(bplus_time)) / @as(f64, @floatFromInt(hashmap_time));
    const faster = if (ratio < 1.0) "faster" else "slower";
    const ratio_display = if (ratio < 1.0) 1.0 / ratio else ratio;
    
    std.debug.print("\n{s}: B+ tree is {:.2}x {s} than HashMap\n", .{
        name,
        ratio_display,
        faster,
    });
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    
    std.debug.print("\n=== B+ Tree vs HashMap Comparison ===\n\n", .{});
    
    const sizes = [_]usize{ 100, 1000, 10000, 100000 };
    const Tree = bplustree.BPlusTree(u32, u32);
    
    for (sizes) |size| {
        std.debug.print("\n--- Size: {} ---\n", .{size});
        
        // Sequential Insertion Comparison
        std.debug.print("\nSequential Insertion:\n", .{});
        
        // B+ Tree
        var tree = Tree.init(allocator, 128);
        defer tree.deinit();
        
        var timer = try std.time.Timer.start();
        for (0..size) |i| {
            try tree.insert(@intCast(i), @intCast(i * 2));
        }
        const bplus_insert_time = timer.read();
        
        printResult(.{
            .name = "  B+ Tree",
            .operations = size,
            .time_ns = bplus_insert_time,
            .ops_per_sec = @as(f64, @floatFromInt(size)) * 1_000_000_000 / @as(f64, @floatFromInt(bplus_insert_time)),
            .ns_per_op = @as(f64, @floatFromInt(bplus_insert_time)) / @as(f64, @floatFromInt(size)),
        });
        
        // HashMap
        var hashmap = std.AutoHashMap(u32, u32).init(allocator);
        defer hashmap.deinit();
        
        timer.reset();
        for (0..size) |i| {
            try hashmap.put(@intCast(i), @intCast(i * 2));
        }
        const hashmap_insert_time = timer.read();
        
        printResult(.{
            .name = "  HashMap",
            .operations = size,
            .time_ns = hashmap_insert_time,
            .ops_per_sec = @as(f64, @floatFromInt(size)) * 1_000_000_000 / @as(f64, @floatFromInt(hashmap_insert_time)),
            .ns_per_op = @as(f64, @floatFromInt(hashmap_insert_time)) / @as(f64, @floatFromInt(size)),
        });
        
        printComparison("Sequential insertion", bplus_insert_time, hashmap_insert_time);
        
        // Lookup Comparison
        std.debug.print("\nRandom Lookup:\n", .{});
        
        var prng = std.Random.DefaultPrng.init(42);
        const random = prng.random();
        
        // B+ Tree lookups
        timer.reset();
        for (0..size) |_| {
            const key = random.int(u32) % @as(u32, @intCast(size));
            _ = tree.get(key);
        }
        const bplus_lookup_time = timer.read();
        
        printResult(.{
            .name = "  B+ Tree",
            .operations = size,
            .time_ns = bplus_lookup_time,
            .ops_per_sec = @as(f64, @floatFromInt(size)) * 1_000_000_000 / @as(f64, @floatFromInt(bplus_lookup_time)),
            .ns_per_op = @as(f64, @floatFromInt(bplus_lookup_time)) / @as(f64, @floatFromInt(size)),
        });
        
        // HashMap lookups
        timer.reset();
        for (0..size) |_| {
            const key = random.int(u32) % @as(u32, @intCast(size));
            _ = hashmap.get(key);
        }
        const hashmap_lookup_time = timer.read();
        
        printResult(.{
            .name = "  HashMap",
            .operations = size,
            .time_ns = hashmap_lookup_time,
            .ops_per_sec = @as(f64, @floatFromInt(size)) * 1_000_000_000 / @as(f64, @floatFromInt(hashmap_lookup_time)),
            .ns_per_op = @as(f64, @floatFromInt(hashmap_lookup_time)) / @as(f64, @floatFromInt(size)),
        });
        
        printComparison("Random lookup", bplus_lookup_time, hashmap_lookup_time);
        
        // Iteration Comparison
        std.debug.print("\nIteration:\n", .{});
        
        // B+ Tree iteration
        timer.reset();
        var iter = tree.iterator();
        var count: usize = 0;
        while (iter.next()) |_| {
            count += 1;
        }
        const bplus_iter_time = timer.read();
        
        printResult(.{
            .name = "  B+ Tree",
            .operations = count,
            .time_ns = bplus_iter_time,
            .ops_per_sec = @as(f64, @floatFromInt(count)) * 1_000_000_000 / @as(f64, @floatFromInt(bplus_iter_time)),
            .ns_per_op = @as(f64, @floatFromInt(bplus_iter_time)) / @as(f64, @floatFromInt(count)),
        });
        
        // HashMap iteration
        timer.reset();
        var hashmap_iter = hashmap.iterator();
        count = 0;
        while (hashmap_iter.next()) |_| {
            count += 1;
        }
        const hashmap_iter_time = timer.read();
        
        printResult(.{
            .name = "  HashMap",
            .operations = count,
            .time_ns = hashmap_iter_time,
            .ops_per_sec = @as(f64, @floatFromInt(count)) * 1_000_000_000 / @as(f64, @floatFromInt(hashmap_iter_time)),
            .ns_per_op = @as(f64, @floatFromInt(hashmap_iter_time)) / @as(f64, @floatFromInt(count)),
        });
        
        printComparison("Iteration", bplus_iter_time, hashmap_iter_time);
        
        // Range Query (B+ Tree only)
        if (size <= 10000) {
            std.debug.print("\nRange Query (10% of data):\n", .{});
            
            const range_start = @as(u32, @intCast(size / 4));
            const range_end = range_start + @as(u32, @intCast(size / 10));
            
            var results = std.ArrayList(Tree.Entry).init(allocator);
            defer results.deinit();
            
            timer.reset();
            try tree.range(range_start, range_end, &results);
            const range_time = timer.read();
            
            printResult(.{
                .name = "  B+ Tree Range Query",
                .operations = results.items.len,
                .time_ns = range_time,
                .ops_per_sec = @as(f64, @floatFromInt(results.items.len)) * 1_000_000_000 / @as(f64, @floatFromInt(range_time)),
                .ns_per_op = @as(f64, @floatFromInt(range_time)) / @as(f64, @floatFromInt(results.items.len)),
            });
            
            std.debug.print("  HashMap: Not supported (would require O(n) scan)\n", .{});
        }
    }
    
    std.debug.print("\n\n=== Summary ===\n", .{});
    std.debug.print("B+ Tree advantages:\n", .{});
    std.debug.print("  - Ordered iteration\n", .{});
    std.debug.print("  - Efficient range queries\n", .{});
    std.debug.print("  - Better cache locality for sequential access\n", .{});
    std.debug.print("  - Predictable performance\n\n", .{});
    std.debug.print("HashMap advantages:\n", .{});
    std.debug.print("  - O(1) average case lookup\n", .{});
    std.debug.print("  - Faster for random access patterns\n", .{});
    std.debug.print("  - Lower memory overhead for small datasets\n", .{});
}