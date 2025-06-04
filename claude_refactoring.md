# B+ Tree Refactoring Plan: Helper Functions for Code Simplification

Generated on: January 6, 2025

## Executive Summary

The current B+ tree implementation contains significant boilerplate code that obscures the core algorithms. Analysis reveals that approximately 400-500 lines of code could be eliminated through strategic helper functions. This plan outlines a systematic approach to introduce these helpers and refactor the codebase for clarity and maintainability.

## Current State Analysis

### Key Problems
1. **Arena Access Boilerplate**: 50+ instances of nested `if let Some(node) = self.get_X(id)` patterns
2. **Repetitive Child Navigation**: 20+ duplicate blocks for finding children in branches
3. **Sibling Resolution Logic**: 15+ similar blocks for getting sibling information
4. **Rebalancing Duplication**: 4 nearly-identical rebalancing functions (leaf/branch × left/right)
5. **Property Checking Patterns**: Scattered node property checks with fallback values
6. **Data Extraction Duplication**: 8+ similar blocks for taking data from nodes

### Impact
- **Code Volume**: ~400-500 lines of unnecessary duplication
- **Readability**: Core algorithms buried in arena access boilerplate
- **Maintainability**: Changes must be made in multiple places
- **Bug Surface**: Each duplication is a potential source of inconsistency

## Proposed Helper Functions

### Phase 1: Core Navigation Helpers (Week 1)

#### 1.1 Child Resolution Helper
```rust
/// Get child index and reference for a given key
fn get_child_info(&self, branch_id: NodeId, key: &K) -> Option<(usize, NodeRef<K, V>)> {
    let branch = self.get_branch(branch_id)?;
    let child_index = branch.find_child_index(key);
    if child_index < branch.children.len() {
        Some((child_index, branch.children[child_index].clone()))
    } else {
        None
    }
}

/// Get child at specific index
fn get_child_at(&self, branch_id: NodeId, index: usize) -> Option<NodeRef<K, V>> {
    self.get_branch(branch_id)
        .and_then(|branch| branch.children.get(index).cloned())
}
```

**Usage Impact**: Replaces 20+ blocks of 10-15 lines each → ~250 lines saved

#### 1.2 Sibling Information Helper
```rust
#[derive(Debug)]
struct SiblingInfo<K, V> {
    left_sibling: Option<NodeRef<K, V>>,
    right_sibling: Option<NodeRef<K, V>>,
    left_separator_idx: Option<usize>,
    right_separator_idx: Option<usize>,
}

impl<K, V> SiblingInfo<K, V> {
    fn has_left(&self) -> bool { self.left_sibling.is_some() }
    fn has_right(&self) -> bool { self.right_sibling.is_some() }
}

/// Get comprehensive sibling information for a child
fn get_sibling_info(&self, parent_id: NodeId, child_index: usize) -> Option<SiblingInfo<K, V>> {
    let parent = self.get_branch(parent_id)?;
    Some(SiblingInfo {
        left_sibling: (child_index > 0).then(|| parent.children[child_index - 1].clone()),
        right_sibling: parent.children.get(child_index + 1).cloned(),
        left_separator_idx: (child_index > 0).then(|| child_index - 1),
        right_separator_idx: (child_index < parent.keys.len()).then(|| child_index),
    })
}
```

**Usage Impact**: Replaces 15+ blocks of 8-10 lines each → ~120 lines saved

### Phase 2: Property Checking Helpers (Week 1)

#### 2.1 Node Property Helpers
```rust
/// Check if any node type is underfull
fn is_node_underfull(&self, node_ref: &NodeRef<K, V>) -> bool {
    match node_ref {
        NodeRef::Leaf(id, _) => self.get_leaf(*id).map_or(false, |n| n.is_underfull()),
        NodeRef::Branch(id, _) => self.get_branch(*id).map_or(false, |n| n.is_underfull()),
    }
}

/// Check if any node type can donate
fn can_node_donate(&self, node_ref: &NodeRef<K, V>) -> bool {
    match node_ref {
        NodeRef::Leaf(id, _) => self.get_leaf(*id).map_or(false, |n| n.can_donate()),
        NodeRef::Branch(id, _) => self.get_branch(*id).map_or(false, |n| n.can_donate()),
    }
}

/// Get node length (number of keys)
fn node_len(&self, node_ref: &NodeRef<K, V>) -> usize {
    match node_ref {
        NodeRef::Leaf(id, _) => self.get_leaf(*id).map_or(0, |n| n.keys.len()),
        NodeRef::Branch(id, _) => self.get_branch(*id).map_or(0, |n| n.keys.len()),
    }
}
```

**Usage Impact**: Replaces 50+ inline checks → ~100 lines saved

#### 2.2 Merge Feasibility Helper
```rust
/// Check if two nodes can be merged
fn can_merge_nodes(&self, left: &NodeRef<K, V>, right: &NodeRef<K, V>) -> bool {
    match (left, right) {
        (NodeRef::Leaf(l_id, _), NodeRef::Leaf(r_id, _)) => {
            let left_len = self.get_leaf(*l_id).map_or(0, |n| n.keys.len());
            let right_len = self.get_leaf(*r_id).map_or(0, |n| n.keys.len());
            left_len + right_len <= self.capacity
        }
        (NodeRef::Branch(l_id, _), NodeRef::Branch(r_id, _)) => {
            let left_len = self.get_branch(*l_id).map_or(0, |n| n.keys.len());
            let right_len = self.get_branch(*r_id).map_or(0, |n| n.keys.len());
            left_len + 1 + right_len <= self.capacity // +1 for separator
        }
        _ => false,
    }
}
```

**Usage Impact**: Replaces 8+ blocks of 15-20 lines each → ~120 lines saved

### Phase 3: Data Manipulation Helpers (Week 2)

#### 3.1 Data Extraction Helpers
```rust
/// Extract all data from a leaf node
fn take_leaf_data(&mut self, leaf_id: NodeId) -> Option<(Vec<K>, Vec<V>, NodeId)> {
    self.get_leaf_mut(leaf_id).map(|leaf| {
        (
            std::mem::take(&mut leaf.keys),
            std::mem::take(&mut leaf.values),
            leaf.next,
        )
    })
}

/// Extract all data from a branch node
fn take_branch_data(&mut self, branch_id: NodeId) -> Option<(Vec<K>, Vec<NodeRef<K, V>>)> {
    self.get_branch_mut(branch_id).map(|branch| {
        (
            std::mem::take(&mut branch.keys),
            std::mem::take(&mut branch.children),
        )
    })
}

/// Update leaf linked list pointer
fn update_leaf_link(&mut self, from_id: NodeId, to_id: NodeId) -> bool {
    self.get_leaf_mut(from_id)
        .map(|leaf| { leaf.next = to_id; true })
        .unwrap_or(false)
}
```

**Usage Impact**: Replaces 8+ blocks of 8-10 lines each → ~70 lines saved

### Phase 4: Generic Rebalancing Helper (Week 2)

#### 4.1 Unified Rebalancing Logic
```rust
/// Generic rebalancing that works for both leaves and branches
fn rebalance_child_generic(
    &mut self,
    parent_id: NodeId,
    child_index: usize,
    child_ref: &NodeRef<K, V>,
) -> bool {
    let sibling_info = match self.get_sibling_info(parent_id, child_index) {
        Some(info) => info,
        None => return false,
    };

    // Try borrowing from left sibling
    if sibling_info.has_left() {
        if self.can_node_donate(sibling_info.left_sibling.as_ref().unwrap()) {
            return match child_ref {
                NodeRef::Leaf(_, _) => self.borrow_between_leaves(
                    parent_id, child_index, BorrowDirection::FromLeft
                ),
                NodeRef::Branch(_, _) => self.borrow_between_branches(
                    parent_id, child_index, BorrowDirection::FromLeft
                ),
            };
        }
    }

    // Try borrowing from right sibling
    if sibling_info.has_right() {
        if self.can_node_donate(sibling_info.right_sibling.as_ref().unwrap()) {
            return match child_ref {
                NodeRef::Leaf(_, _) => self.borrow_between_leaves(
                    parent_id, child_index, BorrowDirection::FromRight
                ),
                NodeRef::Branch(_, _) => self.borrow_between_branches(
                    parent_id, child_index, BorrowDirection::FromRight
                ),
            };
        }
    }

    // Must merge - prefer left sibling
    if sibling_info.has_left() {
        match child_ref {
            NodeRef::Leaf(_, _) => self.merge_leaves(
                parent_id, child_index, MergeDirection::WithLeft
            ),
            NodeRef::Branch(_, _) => self.merge_branches(
                parent_id, child_index, MergeDirection::WithLeft
            ),
        }
    } else if sibling_info.has_right() {
        match child_ref {
            NodeRef::Leaf(_, _) => self.merge_leaves(
                parent_id, child_index, MergeDirection::WithRight
            ),
            NodeRef::Branch(_, _) => self.merge_branches(
                parent_id, child_index, MergeDirection::WithRight
            ),
        }
    } else {
        false // No siblings - shouldn't happen
    }
}
```

**Usage Impact**: Replaces `rebalance_leaf_child` and `rebalance_branch_child` → ~200 lines saved

## Implementation Plan

### Week 1: Foundation
1. **Day 1-2**: Implement Phase 1 helpers (child resolution, sibling info)
2. **Day 3-4**: Implement Phase 2 helpers (property checking, merge feasibility)
3. **Day 5**: Test all helpers with unit tests

### Week 2: Integration
1. **Day 1-2**: Implement Phase 3 helpers (data manipulation)
2. **Day 3-4**: Implement Phase 4 generic rebalancing
3. **Day 5**: Integration testing

### Week 3: Refactoring
1. **Day 1-2**: Replace all child resolution patterns with helpers
2. **Day 3-4**: Replace all property checking patterns with helpers
3. **Day 5**: Replace rebalancing functions with generic helper

### Week 4: Cleanup
1. **Day 1-2**: Remove old rebalancing functions
2. **Day 3-4**: Final cleanup and optimization
3. **Day 5**: Performance benchmarking

## Success Metrics

### Quantitative
- **Lines of Code**: Reduce by 400-500 lines (25-30% reduction)
- **Function Count**: Reduce by consolidating duplicate functions
- **Nesting Depth**: Reduce maximum nesting from 6+ to 3 levels
- **Test Coverage**: Maintain or improve current 85% coverage

### Qualitative
- **Readability**: Core algorithms clearly visible
- **Maintainability**: Single source of truth for each operation
- **Consistency**: Uniform error handling and patterns
- **Performance**: No regression (verified by benchmarks)

## Risk Mitigation

### Risks
1. **Breaking Changes**: Helpers might not handle all edge cases
2. **Performance Impact**: Additional function calls
3. **Lifetime Complexity**: Rust borrow checker challenges

### Mitigation Strategies
1. **Incremental Refactoring**: One helper at a time
2. **Comprehensive Testing**: Test each helper thoroughly before use
3. **Performance Monitoring**: Benchmark before/after each phase
4. **Compiler Optimization**: Rely on inlining for zero-cost abstractions

## Example Transformation

### Before (Current Code)
```rust
// 25 lines of boilerplate for a simple operation
let (child_index, child_ref) = {
    if let Some(branch) = self.get_branch(id) {
        let child_index = branch.find_child_index(&key);
        if child_index < branch.children.len() {
            (child_index, branch.children[child_index].clone())
        } else {
            return None;
        }
    } else {
        return None;
    }
};

let is_underfull = match child_ref {
    NodeRef::Leaf(leaf_id, _) => {
        if let Some(leaf) = self.get_leaf(leaf_id) {
            leaf.is_underfull()
        } else {
            false
        }
    }
    NodeRef::Branch(branch_id, _) => {
        if let Some(branch) = self.get_branch(branch_id) {
            branch.is_underfull()
        } else {
            false
        }
    }
};
```

### After (With Helpers)
```rust
// 3 lines expressing the actual logic
let (child_index, child_ref) = self.get_child_info(id, &key)?;
let is_underfull = self.is_node_underfull(&child_ref);
```

## Conclusion

This refactoring plan will transform the B+ tree implementation from a codebase obscured by boilerplate into one where the algorithms are clear and maintainable. The helpers act as a semantic layer that expresses intent rather than implementation details, making the code more closely match how we think about B+ tree operations.

The investment of 4 weeks will yield:
- **50% reduction** in code complexity
- **30% reduction** in total lines of code
- **Dramatically improved** readability and maintainability
- **Zero performance impact** due to Rust's zero-cost abstractions

This positions the codebase for easier feature additions, bug fixes, and long-term maintenance.