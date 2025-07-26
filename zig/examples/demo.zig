const std = @import("std");
const BPlusTree = @import("bplustree").BPlusTree;

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    
    std.debug.print("=== B+ Tree Demo ===\n", .{});
    
    // Create a B+ tree
    var tree = BPlusTree(i32, []const u8).init(allocator, 4);
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
    
    std.debug.print("\nDemo complete!\n", .{});
}