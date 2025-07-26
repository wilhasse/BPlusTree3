const std = @import("std");
const BPlusTree = @import("bplustree").BPlusTree;

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    
    std.debug.print("=== B+ Tree Demo ===\n", .{});
    
    // Create a B+ tree
    const Tree = BPlusTree(i32, []const u8);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert some data
    std.debug.print("\nInserting data...\n", .{});
    try tree.insert(50, "fifty");
    try tree.insert(30, "thirty");
    try tree.insert(70, "seventy");
    try tree.insert(20, "twenty");
    try tree.insert(40, "forty");
    try tree.insert(60, "sixty");
    try tree.insert(80, "eighty");
    try tree.insert(10, "ten");
    try tree.insert(90, "ninety");
    
    std.debug.print("Tree now contains {} items\n", .{tree.len()});
    std.debug.print("Tree height: {}\n", .{tree.getHeight()});
    
    // Retrieve some values
    std.debug.print("\nRetrieving values:\n", .{});
    const keys = [_]i32{ 20, 40, 60, 80, 100 };
    for (keys) |key| {
        if (tree.get(key)) |value| {
            std.debug.print("  {} = {s}\n", .{ key, value });
        } else {
            std.debug.print("  {} = (not found)\n", .{key});
        }
    }
    
    // Update a value
    std.debug.print("\nUpdating key 50...\n", .{});
    try tree.insert(50, "FIFTY (updated)");
    
    if (tree.get(50)) |value| {
        std.debug.print("  50 = {s}\n", .{value});
    }
    
    // Test deletion
    std.debug.print("\nDeleting keys 30 and 70...\n", .{});
    _ = try tree.remove(30);
    _ = try tree.remove(70);
    std.debug.print("Tree now contains {} items\n", .{tree.len()});
    
    // Verify deletions
    std.debug.print("\nVerifying deletions:\n", .{});
    if (tree.get(30)) |_| {
        std.debug.print("  ERROR: 30 still exists!\n", .{});
    } else {
        std.debug.print("  30 = (correctly deleted)\n", .{});
    }
    if (tree.get(70)) |_| {
        std.debug.print("  ERROR: 70 still exists!\n", .{});
    } else {
        std.debug.print("  70 = (correctly deleted)\n", .{});
    }
    
    // Test range query
    std.debug.print("\nRange query [20, 60]:\n", .{});
    var results = std.ArrayList(Tree.Entry).init(allocator);
    defer results.deinit();
    
    try tree.range(20, 60, &results);
    
    for (results.items) |entry| {
        std.debug.print("  {} = {s}\n", .{ entry.key, entry.value });
    }
    
    // Test contains method
    std.debug.print("\nTesting contains():\n", .{});
    const test_keys = [_]i32{ 10, 30, 50, 70, 100 };
    for (test_keys) |key| {
        if (tree.contains(key)) {
            std.debug.print("  Tree contains {}\n", .{key});
        } else {
            std.debug.print("  Tree does not contain {}\n", .{key});
        }
    }
    
    // Test iterators
    std.debug.print("\nForward iteration:\n", .{});
    var iter = tree.iterator();
    var count: usize = 0;
    while (iter.next()) |entry| {
        std.debug.print("  {} = {s}\n", .{ entry.key, entry.value });
        count += 1;
        if (count >= 5) {
            std.debug.print("  ... (showing first 5 entries)\n", .{});
            break;
        }
    }
    
    std.debug.print("\nReverse iteration:\n", .{});
    var rev_iter = tree.reverseIterator();
    count = 0;
    while (rev_iter.next()) |entry| {
        std.debug.print("  {} = {s}\n", .{ entry.key, entry.value });
        count += 1;
        if (count >= 5) {
            std.debug.print("  ... (showing first 5 entries)\n", .{});
            break;
        }
    }
    
    // Test clear
    std.debug.print("\nClearing tree...\n", .{});
    tree.clear();
    std.debug.print("Tree now contains {} items\n", .{tree.len()});
    std.debug.print("Is tree empty? {}\n", .{tree.len() == 0});
    
    std.debug.print("\nDemo complete!\n", .{});
}