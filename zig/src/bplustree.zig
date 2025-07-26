const std = @import("std");

pub fn BPlusTree(comptime K: type, comptime V: type) type {
    return struct {
        const Self = @This();
        const KeyType = K;
        const ValueType = V;
        
        pub const Error = error{
            KeyNotFound,
            OutOfMemory,
        };
        
        pub const Entry = struct {
            key: KeyType,
            value: ValueType,
        };
        
        pub const Iterator = struct {
            current_node: ?*Node,
            current_index: usize,
            
            pub fn next(self: *Iterator) ?Entry {
                if (self.current_node == null) return null;
                
                const node = self.current_node.?;
                
                // Check if we have more items in current node
                if (self.current_index < node.keys.items.len) {
                    const entry = Entry{
                        .key = node.keys.items[self.current_index],
                        .value = node.values.?.items[self.current_index],
                    };
                    self.current_index += 1;
                    return entry;
                }
                
                // Move to next leaf node
                self.current_node = node.next;
                self.current_index = 0;
                
                // Try again with next node
                return self.next();
            }
        };
        
        pub const ReverseIterator = struct {
            current_node: ?*Node,
            current_index: usize,
            
            pub fn next(self: *ReverseIterator) ?Entry {
                if (self.current_node == null) return null;
                
                const node = self.current_node.?;
                
                // Check if we have more items in current node
                if (self.current_index > 0) {
                    self.current_index -= 1;
                    const entry = Entry{
                        .key = node.keys.items[self.current_index],
                        .value = node.values.?.items[self.current_index],
                    };
                    return entry;
                }
                
                // Move to previous leaf node
                self.current_node = node.prev;
                if (self.current_node) |prev_node| {
                    self.current_index = prev_node.keys.items.len;
                }
                
                // Try again with previous node
                return self.next();
            }
        };
        
        const NodeType = enum { leaf, branch };
        
        const Node = struct {
            node_type: NodeType,
            keys: std.ArrayList(KeyType),
            
            // For leaf nodes
            values: ?std.ArrayList(ValueType),
            next: ?*Node,  // Link to next leaf
            prev: ?*Node,  // Link to previous leaf
            
            // For branch nodes
            children: ?std.ArrayList(*Node),
            
            fn initLeaf(allocator: std.mem.Allocator) !*Node {
                const node = try allocator.create(Node);
                node.* = Node{
                    .node_type = .leaf,
                    .keys = std.ArrayList(KeyType).init(allocator),
                    .values = std.ArrayList(ValueType).init(allocator),
                    .children = null,
                    .next = null,
                    .prev = null,
                };
                return node;
            }
            
            fn initBranch(allocator: std.mem.Allocator) !*Node {
                const node = try allocator.create(Node);
                node.* = Node{
                    .node_type = .branch,
                    .keys = std.ArrayList(KeyType).init(allocator),
                    .values = null,
                    .children = std.ArrayList(*Node).init(allocator),
                    .next = null,
                    .prev = null,
                };
                return node;
            }
            
            fn deinit(self: *Node, allocator: std.mem.Allocator) void {
                self.keys.deinit();
                if (self.values) |*values| {
                    values.deinit();
                }
                if (self.children) |*children| {
                    for (children.items) |child| {
                        child.deinit(allocator);
                    }
                    children.deinit();
                }
                allocator.destroy(self);
            }
            
            fn isFull(self: *const Node, capacity: usize) bool {
                return self.keys.items.len >= capacity;
            }
        };
        
        allocator: std.mem.Allocator,
        capacity: usize,
        size: usize,
        root: ?*Node,
        
        pub fn init(allocator: std.mem.Allocator, capacity: usize) Self {
            return Self{
                .allocator = allocator,
                .capacity = capacity,
                .size = 0,
                .root = null,
            };
        }
        
        pub fn deinit(self: *Self) void {
            if (self.root) |root| {
                root.deinit(self.allocator);
            }
        }
        
        pub fn len(self: *const Self) usize {
            return self.size;
        }
        
        pub fn insert(self: *Self, key: KeyType, value: ValueType) !void {
            if (self.root == null) {
                self.root = try Node.initLeaf(self.allocator);
            }
            
            // If root is full and is a leaf, split it
            if (self.root.?.node_type == .leaf and self.root.?.isFull(self.capacity)) {
                const old_root = self.root.?;
                const new_leaf = try self.splitLeaf(old_root);
                
                // Create new root
                var new_root = try Node.initBranch(self.allocator);
                try new_root.keys.append(new_leaf.keys.items[0]);
                try new_root.children.?.append(old_root);
                try new_root.children.?.append(new_leaf);
                
                self.root = new_root;
            }
            
            // Now insert normally
            try self.insertIntoNode(self.root.?, key, value);
            self.size += 1;
        }
        
        fn insertIntoNode(self: *Self, node: *Node, key: KeyType, value: ValueType) !void {
            if (node.node_type == .leaf) {
                // Find the position to insert
                var insert_pos: usize = 0;
                var found = false;
                
                for (node.keys.items, 0..) |k, i| {
                    if (k == key) {
                        // Key already exists, update value
                        node.values.?.items[i] = value;
                        self.size -= 1; // Compensate for the increment in insert()
                        return;
                    }
                    if (k > key) {
                        insert_pos = i;
                        found = true;
                        break;
                    }
                }
                
                if (!found) {
                    insert_pos = node.keys.items.len;
                }
                
                // Insert at the correct position
                try node.keys.insert(insert_pos, key);
                try node.values.?.insert(insert_pos, value);
            } else {
                // Find child to insert into
                var child_idx: usize = 0;
                for (node.keys.items, 0..) |k, i| {
                    if (key < k) {
                        break;
                    }
                    child_idx = i + 1;
                }
                if (child_idx >= node.children.?.items.len) {
                    child_idx = node.children.?.items.len - 1;
                }
                
                const child = node.children.?.items[child_idx];
                
                // Check if child needs splitting before insertion
                if (child.isFull(self.capacity)) {
                    // Split the child
                    if (child.node_type == .leaf) {
                        const new_node = try self.splitLeaf(child);
                        
                        // Insert the new key into parent
                        const split_key = new_node.keys.items[0];
                        const insert_pos: usize = child_idx + 1;
                        
                        // Insert new key and child pointer
                        try node.keys.insert(child_idx, split_key);
                        try node.children.?.insert(insert_pos, new_node);
                        
                        // Decide which child to insert into
                        if (key >= split_key) {
                            try self.insertIntoNode(new_node, key, value);
                        } else {
                            try self.insertIntoNode(child, key, value);
                        }
                    }
                } else {
                    try self.insertIntoNode(child, key, value);
                }
            }
        }
        
        pub fn get(self: *const Self, key: KeyType) ?ValueType {
            if (self.root == null) return null;
            
            var current = self.root.?;
            
            // Navigate down the tree
            while (current.node_type == .branch) {
                var child_idx: usize = 0;
                for (current.keys.items, 0..) |k, i| {
                    if (key < k) {
                        break;
                    }
                    child_idx = i + 1;
                }
                if (child_idx >= current.children.?.items.len) {
                    child_idx = current.children.?.items.len - 1;
                }
                current = current.children.?.items[child_idx];
            }
            
            // Search in leaf node
            for (current.keys.items, 0..) |k, i| {
                if (k == key) {
                    return current.values.?.items[i];
                }
            }
            return null;
        }
        
        pub fn getHeight(self: *const Self) usize {
            if (self.root == null) return 0;
            
            var height: usize = 1;
            var current = self.root.?;
            
            while (current.node_type == .branch and current.children.?.items.len > 0) {
                height += 1;
                current = current.children.?.items[0];
            }
            
            return height;
        }
        
        fn splitLeaf(self: *Self, leaf: *Node) !*Node {
            const mid = leaf.keys.items.len / 2;
            
            // Create new leaf
            var new_leaf = try Node.initLeaf(self.allocator);
            
            // Move half the keys and values to new leaf
            for (mid..leaf.keys.items.len) |i| {
                try new_leaf.keys.append(leaf.keys.items[i]);
                try new_leaf.values.?.append(leaf.values.?.items[i]);
            }
            
            // Remove moved items from original leaf
            leaf.keys.shrinkRetainingCapacity(mid);
            leaf.values.?.shrinkRetainingCapacity(mid);
            
            // Update leaf links
            new_leaf.next = leaf.next;
            new_leaf.prev = leaf;
            if (leaf.next) |next| {
                next.prev = new_leaf;
            }
            leaf.next = new_leaf;
            
            return new_leaf;
        }
        
        pub fn remove(self: *Self, key: KeyType) !ValueType {
            if (self.root == null) {
                return Error.KeyNotFound;
            }
            
            // Remove from the tree starting at root
            const result = try self.removeFromNode(self.root.?, key);
            
            // If root is now empty and is a branch node, promote its only child
            if (self.root.?.node_type == .branch and self.root.?.keys.items.len == 0) {
                if (self.root.?.children.?.items.len > 0) {
                    const old_root = self.root.?;
                    self.root = self.root.?.children.?.items[0];
                    
                    // Clean up old root
                    old_root.keys.deinit();
                    old_root.children.?.deinit();
                    self.allocator.destroy(old_root);
                }
            }
            
            // If root is a leaf and empty, tree is now empty
            if (self.root.?.node_type == .leaf and self.root.?.keys.items.len == 0) {
                self.root.?.deinit(self.allocator);
                self.root = null;
            }
            
            self.size -= 1;
            return result;
        }
        
        fn removeFromNode(self: *Self, node: *Node, key: KeyType) !ValueType {
            if (node.node_type == .leaf) {
                // Find and remove the key from leaf
                for (node.keys.items, 0..) |k, i| {
                    if (k == key) {
                        const value = node.values.?.items[i];
                        
                        // Remove key and value
                        _ = node.keys.orderedRemove(i);
                        _ = node.values.?.orderedRemove(i);
                        
                        return value;
                    }
                }
                return Error.KeyNotFound;
            } else {
                // Find child that contains the key
                var child_idx: usize = 0;
                for (node.keys.items, 0..) |k, i| {
                    if (key < k) {
                        break;
                    }
                    child_idx = i + 1;
                }
                if (child_idx >= node.children.?.items.len) {
                    child_idx = node.children.?.items.len - 1;
                }
                
                var child = node.children.?.items[child_idx];
                const min_keys = (self.capacity + 1) / 2 - 1;
                
                // Check if child will underflow after deletion
                if (child.keys.items.len <= min_keys) {
                    // Try to borrow from siblings or merge
                    const new_child_idx = try self.handleUnderflow(node, child_idx);
                    // Update child reference after potential merge
                    if (new_child_idx < node.children.?.items.len) {
                        child = node.children.?.items[new_child_idx];
                        child_idx = new_child_idx;
                    }
                }
                
                // Now proceed with deletion
                return try self.removeFromNode(child, key);
            }
        }
        
        fn handleUnderflow(self: *Self, parent: *Node, child_idx: usize) !usize {
            const child = parent.children.?.items[child_idx];
            const min_keys = (self.capacity + 1) / 2 - 1;
            
            // Try borrowing from left sibling
            if (child_idx > 0) {
                const left_sibling = parent.children.?.items[child_idx - 1];
                if (left_sibling.keys.items.len > min_keys) {
                    // Borrow from left sibling
                    if (child.node_type == .leaf) {
                        // Move last key from left sibling to child
                        const last_idx = left_sibling.keys.items.len - 1;
                        const borrowed_key = left_sibling.keys.items[last_idx];
                        const borrowed_value = left_sibling.values.?.items[last_idx];
                        
                        _ = left_sibling.keys.pop();
                        _ = left_sibling.values.?.pop();
                        
                        try child.keys.insert(0, borrowed_key);
                        try child.values.?.insert(0, borrowed_value);
                        
                        // Update parent key
                        parent.keys.items[child_idx - 1] = child.keys.items[0];
                    }
                    return child_idx;
                }
            }
            
            // Try borrowing from right sibling
            if (child_idx < parent.children.?.items.len - 1) {
                const right_sibling = parent.children.?.items[child_idx + 1];
                if (right_sibling.keys.items.len > min_keys) {
                    // Borrow from right sibling
                    if (child.node_type == .leaf) {
                        // Move first key from right sibling to child
                        const borrowed_key = right_sibling.keys.orderedRemove(0);
                        const borrowed_value = right_sibling.values.?.orderedRemove(0);
                        try child.keys.append(borrowed_key);
                        try child.values.?.append(borrowed_value);
                        
                        // Update parent key
                        parent.keys.items[child_idx] = right_sibling.keys.items[0];
                    }
                    return child_idx;
                }
            }
            
            // If can't borrow, merge with a sibling
            if (child_idx > 0) {
                // Merge with left sibling
                try self.mergeNodes(parent, child_idx - 1, child_idx);
                return child_idx - 1;
            } else {
                // Merge with right sibling
                try self.mergeNodes(parent, child_idx, child_idx + 1);
                return child_idx;
            }
        }
        
        fn mergeNodes(self: *Self, parent: *Node, left_idx: usize, right_idx: usize) !void {
            const left = parent.children.?.items[left_idx];
            const right = parent.children.?.items[right_idx];
            
            if (left.node_type == .leaf) {
                // Merge leaf nodes
                for (right.keys.items, 0..) |key, i| {
                    try left.keys.append(key);
                    try left.values.?.append(right.values.?.items[i]);
                }
                
                // Update leaf links
                left.next = right.next;
                if (right.next) |next| {
                    next.prev = left;
                }
                
                // Remove the merged node from parent
                _ = parent.keys.orderedRemove(left_idx);
                _ = parent.children.?.orderedRemove(right_idx);
                
                // Clean up merged node
                right.deinit(self.allocator);
            }
        }
        
        pub fn range(self: *const Self, start: KeyType, end: KeyType, results: *std.ArrayList(Entry)) !void {
            if (self.root == null) {
                return;
            }
            
            // Find the leaf containing the start key
            var current = self.root.?;
            
            // Navigate to the leaf that would contain start
            while (current.node_type == .branch) {
                var child_idx: usize = 0;
                for (current.keys.items, 0..) |k, i| {
                    if (start < k) {
                        break;
                    }
                    child_idx = i + 1;
                }
                if (child_idx >= current.children.?.items.len) {
                    child_idx = current.children.?.items.len - 1;
                }
                current = current.children.?.items[child_idx];
            }
            
            // Now traverse through leaf nodes collecting values in range
            var leaf: ?*Node = current;
            while (leaf != null) {
                const node = leaf.?;
                
                // Process keys in this leaf
                for (node.keys.items, 0..) |k, i| {
                    if (k > end) {
                        // We've passed the end of the range
                        return;
                    }
                    if (k >= start) {
                        // Key is in range
                        try results.append(.{
                            .key = k,
                            .value = node.values.?.items[i],
                        });
                    }
                }
                
                // Move to next leaf
                leaf = node.next;
            }
        }
        
        pub fn iterator(self: *const Self) Iterator {
            if (self.root == null) {
                return Iterator{
                    .current_node = null,
                    .current_index = 0,
                };
            }
            
            // Find leftmost leaf
            var current = self.root.?;
            while (current.node_type == .branch) {
                current = current.children.?.items[0];
            }
            
            return Iterator{
                .current_node = current,
                .current_index = 0,
            };
        }
        
        pub fn reverseIterator(self: *const Self) ReverseIterator {
            if (self.root == null) {
                return ReverseIterator{
                    .current_node = null,
                    .current_index = 0,
                };
            }
            
            // Find rightmost leaf
            var current = self.root.?;
            while (current.node_type == .branch) {
                current = current.children.?.items[current.children.?.items.len - 1];
            }
            
            return ReverseIterator{
                .current_node = current,
                .current_index = current.keys.items.len,
            };
        }
        
        pub fn contains(self: *const Self, key: KeyType) bool {
            return self.get(key) != null;
        }
        
        pub fn clear(self: *Self) void {
            if (self.root) |root| {
                root.deinit(self.allocator);
                self.root = null;
            }
            self.size = 0;
        }
    };
}