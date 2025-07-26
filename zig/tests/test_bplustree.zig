const std = @import("std");
const testing = std.testing;
const bplustree = @import("bplustree");

test "should create empty B+ tree" {
    const allocator = testing.allocator;
    
    // Create a B+ tree with capacity 4 for testing
    var tree = bplustree.BPlusTree(i32, i32).init(allocator, 4);
    defer tree.deinit();
    
    // Tree should be empty
    try testing.expectEqual(@as(usize, 0), tree.len());
}

test "should insert single key-value pair" {
    const allocator = testing.allocator;
    
    var tree = bplustree.BPlusTree(i32, i32).init(allocator, 4);
    defer tree.deinit();
    
    // Insert a key-value pair
    try tree.insert(42, 100);
    
    // Tree should have one element
    try testing.expectEqual(@as(usize, 1), tree.len());
}

test "should retrieve inserted value" {
    const allocator = testing.allocator;
    
    var tree = bplustree.BPlusTree(i32, i32).init(allocator, 4);
    defer tree.deinit();
    
    // Insert a key-value pair
    try tree.insert(42, 100);
    
    // Retrieve the value
    const value = tree.get(42);
    try testing.expect(value != null);
    try testing.expectEqual(@as(i32, 100), value.?);
}

test "should handle multiple insertions and maintain order" {
    const allocator = testing.allocator;
    
    var tree = bplustree.BPlusTree(i32, i32).init(allocator, 4);
    defer tree.deinit();
    
    // Insert multiple key-value pairs in random order
    try tree.insert(5, 50);
    try tree.insert(3, 30);
    try tree.insert(7, 70);
    try tree.insert(1, 10);
    
    // Tree should have four elements
    try testing.expectEqual(@as(usize, 4), tree.len());
    
    // All values should be retrievable
    try testing.expectEqual(@as(i32, 10), tree.get(1).?);
    try testing.expectEqual(@as(i32, 30), tree.get(3).?);
    try testing.expectEqual(@as(i32, 50), tree.get(5).?);
    try testing.expectEqual(@as(i32, 70), tree.get(7).?);
}

test "should update value for duplicate key" {
    const allocator = testing.allocator;
    
    var tree = bplustree.BPlusTree(i32, i32).init(allocator, 4);
    defer tree.deinit();
    
    // Insert a key-value pair
    try tree.insert(42, 100);
    
    // Insert same key with different value
    try tree.insert(42, 200);
    
    // Tree should still have one element
    try testing.expectEqual(@as(usize, 1), tree.len());
    
    // Value should be updated
    try testing.expectEqual(@as(i32, 200), tree.get(42).?);
}

test "should return null for non-existent key" {
    const allocator = testing.allocator;
    
    var tree = bplustree.BPlusTree(i32, i32).init(allocator, 4);
    defer tree.deinit();
    
    // Empty tree should return null
    try testing.expect(tree.get(42) == null);
    
    // Insert some values
    try tree.insert(10, 100);
    try tree.insert(20, 200);
    try tree.insert(30, 300);
    
    // Non-existent keys should return null
    try testing.expect(tree.get(5) == null);    // Before first
    try testing.expect(tree.get(15) == null);   // Between keys
    try testing.expect(tree.get(40) == null);   // After last
}

test "should handle node splitting when capacity exceeded" {
    const allocator = testing.allocator;
    
    var tree = bplustree.BPlusTree(i32, i32).init(allocator, 4);
    defer tree.deinit();
    
    // Insert more than capacity (4) to trigger split
    try tree.insert(10, 100);
    try tree.insert(20, 200);
    try tree.insert(30, 300);
    try tree.insert(40, 400);
    try tree.insert(50, 500); // This should trigger a split
    
    // Tree should have 5 elements
    try testing.expectEqual(@as(usize, 5), tree.len());
    
    // All values should still be retrievable
    try testing.expectEqual(@as(i32, 100), tree.get(10).?);
    try testing.expectEqual(@as(i32, 200), tree.get(20).?);
    try testing.expectEqual(@as(i32, 300), tree.get(30).?);
    try testing.expectEqual(@as(i32, 400), tree.get(40).?);
    try testing.expectEqual(@as(i32, 500), tree.get(50).?);
    
    // Tree should have proper structure (root should be branch node after split)
    try testing.expect(tree.getHeight() > 1);
}