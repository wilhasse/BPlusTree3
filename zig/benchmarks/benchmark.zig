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
    std.debug.print("{s:30} {:>10} ops in {:>8.2}ms | {:>12.0} ops/sec | {:>8.2} ns/op\n", .{
        result.name,
        result.operations,
        @as(f64, @floatFromInt(result.time_ns)) / 1_000_000,
        result.ops_per_sec,
        result.ns_per_op,
    });
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    
    std.debug.print("\n=== B+ Tree Performance Benchmarks ===\n\n", .{});
    
    // Test different capacities
    const capacities = [_]usize{ 8, 16, 32, 64, 128, 256 };
    const n = 100_000;
    
    std.debug.print("Insertion performance with different capacities (n = {}):\n", .{n});
    std.debug.print("{s:30} {s:>10} {s:>10} {s:>15} {s:>15}\n", .{
        "Capacity",
        "Time (ms)",
        "Height",
        "Ops/sec",
        "ns/op",
    });
    for (0..90) |_| std.debug.print("-", .{});
    std.debug.print("\n", .{});
    
    for (capacities) |capacity| {
        const Tree = bplustree.BPlusTree(u32, u32);
        var tree = Tree.init(allocator, capacity);
        defer tree.deinit();
        
        var timer = try std.time.Timer.start();
        for (0..n) |i| {
            try tree.insert(@intCast(i), @intCast(i));
        }
        const insert_time = timer.read();
        
        const ops_per_sec = @as(f64, @floatFromInt(n)) * 1_000_000_000 / @as(f64, @floatFromInt(insert_time));
        const ns_per_op = @as(f64, @floatFromInt(insert_time)) / @as(f64, @floatFromInt(n));
        
        std.debug.print("Capacity {:>4}              {:>10.2} {:>10} {:>15.0} {:>15.2}\n", .{
            capacity,
            @as(f64, @floatFromInt(insert_time)) / 1_000_000,
            tree.getHeight(),
            ops_per_sec,
            ns_per_op,
        });
    }
    
    // Benchmark different operations
    std.debug.print("\n\nOperation benchmarks (capacity = 128, n = 100000):\n", .{});
    for (0..90) |_| std.debug.print("-", .{});
    std.debug.print("\n", .{});
    
    const Tree = bplustree.BPlusTree(u32, u32);
    
    // Sequential insertion
    {
        var tree = Tree.init(allocator, 128);
        defer tree.deinit();
        
        var timer = try std.time.Timer.start();
        for (0..n) |i| {
            try tree.insert(@intCast(i), @intCast(i));
        }
        const time = timer.read();
        
        printResult(.{
            .name = "Sequential insertion",
            .operations = n,
            .time_ns = time,
            .ops_per_sec = @as(f64, @floatFromInt(n)) * 1_000_000_000 / @as(f64, @floatFromInt(time)),
            .ns_per_op = @as(f64, @floatFromInt(time)) / @as(f64, @floatFromInt(n)),
        });
    }
    
    // Random insertion
    {
        var tree = Tree.init(allocator, 128);
        defer tree.deinit();
        
        var prng = std.Random.DefaultPrng.init(12345);
        const random = prng.random();
        
        var timer = try std.time.Timer.start();
        for (0..n) |_| {
            const key = random.int(u32);
            try tree.insert(key, key);
        }
        const time = timer.read();
        
        printResult(.{
            .name = "Random insertion",
            .operations = n,
            .time_ns = time,
            .ops_per_sec = @as(f64, @floatFromInt(n)) * 1_000_000_000 / @as(f64, @floatFromInt(time)),
            .ns_per_op = @as(f64, @floatFromInt(time)) / @as(f64, @floatFromInt(n)),
        });
    }
    
    // Lookup benchmark
    {
        var tree = Tree.init(allocator, 128);
        defer tree.deinit();
        
        // Pre-populate
        for (0..n) |i| {
            try tree.insert(@intCast(i), @intCast(i));
        }
        
        var prng = std.Random.DefaultPrng.init(54321);
        const random = prng.random();
        
        var timer = try std.time.Timer.start();
        for (0..n) |_| {
            const key = random.int(u32) % n;
            _ = tree.get(key);
        }
        const time = timer.read();
        
        printResult(.{
            .name = "Random lookup (hit)",
            .operations = n,
            .time_ns = time,
            .ops_per_sec = @as(f64, @floatFromInt(n)) * 1_000_000_000 / @as(f64, @floatFromInt(time)),
            .ns_per_op = @as(f64, @floatFromInt(time)) / @as(f64, @floatFromInt(n)),
        });
    }
    
    // Contains benchmark
    {
        var tree = Tree.init(allocator, 128);
        defer tree.deinit();
        
        // Pre-populate
        for (0..n) |i| {
            try tree.insert(@intCast(i), @intCast(i));
        }
        
        var timer = try std.time.Timer.start();
        for (0..n) |i| {
            _ = tree.contains(@intCast(i));
        }
        const time = timer.read();
        
        printResult(.{
            .name = "Sequential contains",
            .operations = n,
            .time_ns = time,
            .ops_per_sec = @as(f64, @floatFromInt(n)) * 1_000_000_000 / @as(f64, @floatFromInt(time)),
            .ns_per_op = @as(f64, @floatFromInt(time)) / @as(f64, @floatFromInt(n)),
        });
    }
    
    // Deletion benchmark
    {
        var tree = Tree.init(allocator, 128);
        defer tree.deinit();
        
        // Pre-populate
        for (0..n) |i| {
            try tree.insert(@intCast(i), @intCast(i));
        }
        
        var prng = std.Random.DefaultPrng.init(99999);
        const random = prng.random();
        
        const delete_count = n / 10;
        var timer = try std.time.Timer.start();
        for (0..delete_count) |_| {
            const key = random.int(u32) % n;
            _ = tree.remove(key) catch {};
        }
        const time = timer.read();
        
        printResult(.{
            .name = "Random deletion",
            .operations = delete_count,
            .time_ns = time,
            .ops_per_sec = @as(f64, @floatFromInt(delete_count)) * 1_000_000_000 / @as(f64, @floatFromInt(time)),
            .ns_per_op = @as(f64, @floatFromInt(time)) / @as(f64, @floatFromInt(delete_count)),
        });
    }
    
    // Range query benchmark
    {
        var tree = Tree.init(allocator, 128);
        defer tree.deinit();
        
        // Pre-populate
        for (0..n) |i| {
            try tree.insert(@intCast(i), @intCast(i));
        }
        
        var results = std.ArrayList(Tree.Entry).init(allocator);
        defer results.deinit();
        
        const range_size = 1000;
        const num_ranges = 100;
        
        var timer = try std.time.Timer.start();
        for (0..num_ranges) |i| {
            results.clearRetainingCapacity();
            const start = i * (n / num_ranges);
            const end = start + range_size;
            try tree.range(@intCast(start), @intCast(end), &results);
        }
        const time = timer.read();
        
        printResult(.{
            .name = "Range query (1000 items)",
            .operations = num_ranges,
            .time_ns = time,
            .ops_per_sec = @as(f64, @floatFromInt(num_ranges)) * 1_000_000_000 / @as(f64, @floatFromInt(time)),
            .ns_per_op = @as(f64, @floatFromInt(time)) / @as(f64, @floatFromInt(num_ranges)),
        });
    }
    
    // Iteration benchmark
    {
        var tree = Tree.init(allocator, 128);
        defer tree.deinit();
        
        // Pre-populate
        for (0..n) |i| {
            try tree.insert(@intCast(i), @intCast(i));
        }
        
        var timer = try std.time.Timer.start();
        var iter = tree.iterator();
        var count: usize = 0;
        while (iter.next()) |_| {
            count += 1;
        }
        const time = timer.read();
        
        printResult(.{
            .name = "Full iteration",
            .operations = count,
            .time_ns = time,
            .ops_per_sec = @as(f64, @floatFromInt(count)) * 1_000_000_000 / @as(f64, @floatFromInt(time)),
            .ns_per_op = @as(f64, @floatFromInt(time)) / @as(f64, @floatFromInt(count)),
        });
    }
    
    std.debug.print("\n", .{});
}