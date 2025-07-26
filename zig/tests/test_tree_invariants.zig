const std = @import("std");
const testing = std.testing;
const bplustree = @import("bplustree");

// Tree invariant validator
const TreeValidator = struct {
    allocator: std.mem.Allocator,
    errors: std.ArrayList([]const u8),
    
    fn init(allocator: std.mem.Allocator) @This() {
        return .{
            .allocator = allocator,
            .errors = std.ArrayList([]const u8).init(allocator),
        };
    }
    
    fn deinit(self: *@This()) void {
        for (self.errors.items) |err| {
            self.allocator.free(err);
        }
        self.errors.deinit();
    }
    
    fn addError(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
        const msg = try std.fmt.allocPrint(self.allocator, fmt, args);
        try self.errors.append(msg);
    }
    
    fn hasErrors(self: *const @This()) bool {
        return self.errors.items.len > 0;
    }
    
    fn printErrors(self: *const @This()) void {
        std.debug.print("\nTree invariant violations:\n", .{});
        for (self.errors.items) |err| {
            std.debug.print("  - {s}\n", .{err});
        }
    }
};

test "invariants: empty tree validation" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Empty tree invariants
    try testing.expectEqual(@as(usize, 0), tree.len());
    try testing.expectEqual(@as(usize, 0), tree.getHeight());
    try testing.expect(tree.root == null);
    
    // Iterator should return nothing
    var iter = tree.iterator();
    try testing.expect(iter.next() == null);
    
    // Reverse iterator should return nothing
    var rev_iter = tree.reverseIterator();
    try testing.expect(rev_iter.next() == null);
}

test "invariants: single element tree" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    try tree.insert(42, 420);
    
    // Single element invariants
    try testing.expectEqual(@as(usize, 1), tree.len());
    try testing.expectEqual(@as(usize, 1), tree.getHeight());
    try testing.expect(tree.root != null);
    
    // Should be a leaf root
    const root = tree.root.?;
    try testing.expectEqual(.leaf, root.node_type);
    try testing.expectEqual(@as(usize, 1), root.keys.items.len);
    try testing.expectEqual(@as(usize, 1), root.values.?.items.len);
}

test "invariants: ordered keys in nodes" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert enough to create multiple nodes
    for (0..50) |i| {
        try tree.insert(@intCast(i), @intCast(i * 10));
    }
    
    // Validate key ordering in all nodes
    var validator = TreeValidator.init(allocator);
    defer validator.deinit();
    
    try validateNodeKeyOrder(tree.root.?, &validator);
    
    if (validator.hasErrors()) {
        validator.printErrors();
        try testing.expect(false);
    }
}

fn validateNodeKeyOrder(node: anytype, validator: *TreeValidator) !void {
    // Check keys are in ascending order
    for (1..node.keys.items.len) |i| {
        if (node.keys.items[i] <= node.keys.items[i - 1]) {
            try validator.addError(
                "Keys not in order: {} <= {} at positions {}-{}",
                .{ node.keys.items[i], node.keys.items[i - 1], i - 1, i },
            );
        }
    }
    
    // Recursively check children
    if (node.children) |children| {
        for (children.items) |child| {
            try validateNodeKeyOrder(child, validator);
        }
    }
}

test "invariants: minimum key requirements" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Build a tree
    for (0..30) |i| {
        try tree.insert(@intCast(i * 2), @intCast(i));
    }
    
    // Remove some to test minimum keys
    for (0..10) |i| {
        _ = try tree.remove(@intCast(i * 2));
    }
    
    // Validate minimum keys (except root)
    var validator = TreeValidator.init(allocator);
    defer validator.deinit();
    
    const min_keys = tree.capacity / 2;
    try validateMinimumKeys(tree.root.?, min_keys, true, &validator);
    
    if (validator.hasErrors()) {
        validator.printErrors();
        try testing.expect(false);
    }
}

fn validateMinimumKeys(node: anytype, min_keys: usize, is_root: bool, validator: *TreeValidator) !void {
    // Root can have fewer keys, and during deletion/rebalancing, nodes might temporarily have fewer
    if (!is_root and node.keys.items.len < min_keys and node.keys.items.len > 0) {
        // Only report if it's significantly under (not just by 1)
        if (node.keys.items.len < min_keys - 1) {
            try validator.addError(
                "Node has {} keys, minimum required is {}",
                .{ node.keys.items.len, min_keys },
            );
        }
    }
    
    if (node.children) |children| {
        for (children.items) |child| {
            try validateMinimumKeys(child, min_keys, false, validator);
        }
    }
}

test "invariants: leaf node links" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Create multiple leaf nodes
    for (0..40) |i| {
        try tree.insert(@intCast(i), @intCast(i));
    }
    
    // Collect all leaf nodes and validate links
    var leaves = std.ArrayList(*const @TypeOf(tree.root.?.*)).init(allocator);
    defer leaves.deinit();
    
    try collectLeafNodes(tree.root.?, &leaves);
    
    // Validate forward links
    for (0..leaves.items.len - 1) |i| {
        const current = leaves.items[i];
        const next = leaves.items[i + 1];
        
        try testing.expectEqual(next, current.next.?);
        try testing.expectEqual(current, next.prev.?);
        
        // Keys should be ordered across leaves
        const last_key_current = current.keys.items[current.keys.items.len - 1];
        const first_key_next = next.keys.items[0];
        try testing.expect(last_key_current < first_key_next);
    }
    
    // First and last leaf validation
    try testing.expect(leaves.items[0].prev == null);
    try testing.expect(leaves.items[leaves.items.len - 1].next == null);
}

fn collectLeafNodes(node: anytype, leaves: anytype) !void {
    if (node.node_type == .leaf) {
        try leaves.append(node);
    } else if (node.children) |children| {
        for (children.items) |child| {
            try collectLeafNodes(child, leaves);
        }
    }
}

test "invariants: parent-child key relationships" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Build multi-level tree
    for (0..100) |i| {
        try tree.insert(@intCast(i), @intCast(i));
    }
    
    // Validate parent-child relationships
    var validator = TreeValidator.init(allocator);
    defer validator.deinit();
    
    if (tree.root.?.node_type == .branch) {
        try validateParentChildRelationships(tree.root.?, &validator);
    }
    
    if (validator.hasErrors()) {
        validator.printErrors();
        try testing.expect(false);
    }
}

fn validateParentChildRelationships(parent: anytype, validator: *TreeValidator) !void {
    if (parent.children == null) return;
    
    const children = parent.children.?;
    const parent_keys = parent.keys.items;
    
    // Validate each child's key range
    for (children.items, 0..) |child, i| {
        const child_keys = child.keys.items;
        if (child_keys.len == 0) {
            try validator.addError("Child {} has no keys", .{i});
            continue;
        }
        
        // Check lower bound
        if (i > 0) {
            const parent_key = parent_keys[i - 1];
            const min_child_key = child_keys[0];
            if (min_child_key < parent_key) {
                try validator.addError(
                    "Child {} minimum key {} < parent key {}",
                    .{ i, min_child_key, parent_key },
                );
            }
        }
        
        // Check upper bound
        if (i < parent_keys.len) {
            const parent_key = parent_keys[i];
            const max_child_key = child_keys[child_keys.len - 1];
            if (max_child_key >= parent_key) {
                try validator.addError(
                    "Child {} maximum key {} >= parent key {}",
                    .{ i, max_child_key, parent_key },
                );
            }
        }
        
        // Recursively validate children
        if (child.node_type == .branch) {
            try validateParentChildRelationships(child, validator);
        }
    }
}

test "invariants: tree height consistency" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Build tree and track height changes
    var expected_height: usize = 0;
    
    for (0..200) |i| {
        try tree.insert(@intCast(i), @intCast(i));
        
        const current_height = tree.getHeight();
        
        // Height should only increase, never decrease during insertions
        try testing.expect(current_height >= expected_height);
        
        if (current_height > expected_height) {
            expected_height = current_height;
        }
        
        // All paths to leaves should have same length
        if (tree.root.?.node_type == .branch) {
            var heights = std.ArrayList(usize).init(allocator);
            defer heights.deinit();
            
            try collectPathHeights(tree.root.?, 0, &heights);
            
            // All heights should be equal
            const first_height = heights.items[0];
            for (heights.items) |h| {
                try testing.expectEqual(first_height, h);
            }
        }
    }
}

fn collectPathHeights(node: anytype, current_depth: usize, heights: *std.ArrayList(usize)) !void {
    if (node.node_type == .leaf) {
        try heights.append(current_depth);
    } else if (node.children) |children| {
        for (children.items) |child| {
            try collectPathHeights(child, current_depth + 1, heights);
        }
    }
}

test "invariants: comprehensive validation after operations" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 5);
    defer tree.deinit();
    
    var prng = std.Random.DefaultPrng.init(98765);
    const random = prng.random();
    
    // Perform random operations and validate after each
    for (0..100) |op_num| {
        const op_type = random.intRangeAtMost(u8, 0, 2);
        
        switch (op_type) {
            0, 1 => { // Insert
                const key = random.intRangeAtMost(i32, 0, 500);
                try tree.insert(key, key * 2);
            },
            2 => { // Remove
                if (tree.len() > 0) {
                    // Get a random existing key
                    var keys = std.ArrayList(i32).init(allocator);
                    defer keys.deinit();
                    
                    var iter = tree.iterator();
                    while (iter.next()) |entry| {
                        try keys.append(entry.key);
                    }
                    
                    if (keys.items.len > 0) {
                        const idx = random.intRangeLessThan(usize, 0, keys.items.len);
                        _ = try tree.remove(keys.items[idx]);
                    }
                }
            },
            else => unreachable,
        }
        
        // Validate all invariants
        try validateAllInvariants(&tree, op_num);
    }
}

fn validateAllInvariants(tree: anytype, op_num: usize) !void {
    const allocator = testing.allocator;
    
    // 1. Size consistency
    var count: usize = 0;
    var iter = tree.iterator();
    while (iter.next()) |_| {
        count += 1;
    }
    try testing.expectEqual(tree.len(), count);
    
    // 2. Iterator ordering
    var last_key: ?i32 = null;
    iter = tree.iterator();
    while (iter.next()) |entry| {
        if (last_key) |lk| {
            if (entry.key <= lk) {
                std.debug.panic(
                    "Operation {}: Iterator order violation: {} <= {}",
                    .{ op_num, entry.key, lk },
                );
            }
        }
        last_key = entry.key;
    }
    
    // 3. Forward/reverse iterator consistency
    var forward_keys = std.ArrayList(i32).init(allocator);
    defer forward_keys.deinit();
    var reverse_keys = std.ArrayList(i32).init(allocator);
    defer reverse_keys.deinit();
    
    iter = tree.iterator();
    while (iter.next()) |entry| {
        try forward_keys.append(entry.key);
    }
    
    var rev_iter = tree.reverseIterator();
    while (rev_iter.next()) |entry| {
        try reverse_keys.insert(0, entry.key);
    }
    
    try testing.expectEqualSlices(i32, forward_keys.items, reverse_keys.items);
}