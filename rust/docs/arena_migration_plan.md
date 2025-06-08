# Plan for Removing Non-Arena Node Variants

## Current State Analysis
The codebase currently has four `NodeRef` variants:
- `Leaf(Box<LeafNode<K, V>>)` - heap-allocated leaf nodes
- `Branch(Box<BranchNode<K, V>>)` - heap-allocated branch nodes  
- `ArenaLeaf(NodeId)` - arena-allocated leaf nodes
- `ArenaBranch(NodeId)` - arena-allocated branch nodes

## Migration Strategy

### 1. Root Initialization
The tree starts with a `Leaf` variant. We need to change initialization to create an arena leaf from the start.

### 2. Remove Leaf Variant:
- Change `BPlusTreeMap::new()` to allocate the initial root in the arena
- Update all match statements that handle `NodeRef::Leaf`
- Remove the `Leaf` variant from the enum

### 3. Remove Branch Variant:
- Update root promotion logic to create arena branches directly
- Remove all handling of `NodeRef::Branch` 
- Remove the `Branch` variant from the enum

### 4. Simplify Code:
- Remove migration code paths that convert Box nodes to arena nodes
- Simplify insert/remove logic that currently handles both types
- Remove unused helper functions

### 5. Clean Up:
- Update NodeRef enum to only have two variants
- Remove Box imports if no longer needed
- Update documentation

## Benefits
- Simpler code with fewer branches
- Consistent memory management 
- Better cache locality
- Reduced allocator pressure
- Smaller code size

## Risk Mitigation
- Make changes incrementally, testing after each step
- Keep the existing arena allocation logic intact
- Ensure all 70 tests continue to pass