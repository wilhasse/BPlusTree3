# BPlusTree Implementation Plan

## Overall Strategy: Remove First, Then Internal Nodes

We'll implement remove operations in the current linked-list structure first, then add internal nodes later. This allows us to master rebalancing algorithms in a simpler context before adding tree complexity.

## Phase 1: Structural Preparation for Remove

### Step 1: Prepare for Remove Operations ✅

**Status**: Complete - Simplified approach
**Why**: Remove operations need to access previous siblings for rebalancing
**Decision**: Keep simple `Box<T>` ownership, find previous nodes by traversal when needed
**Rationale**: Simpler ownership model, sufficient for remove operations
**Changes**:

- [x] Add `prev` field to LeafNode (for future use, currently unused)
- [x] All existing tests still pass
- [x] Ready to implement remove infrastructure

### Step 2: Add Remove Infrastructure

**Status**: Not Started
**Changes**:

- [ ] Add underflow detection methods to LeafNode
- [ ] Add sibling access methods (get_prev_sibling, get_next_sibling)
- [ ] Create RemovalResult enum
- [ ] Add basic remove_key method to LeafNode (without rebalancing)

### Step 3: Add Rebalancing Operations

**Status**: Not Started
**Changes**:

- [ ] Implement redistribute_from_next_sibling
- [ ] Implement redistribute_from_prev_sibling
- [ ] Implement merge_with_next_sibling
- [ ] Implement merge_with_prev_sibling
- [ ] Add helper methods for moving entries between nodes

## Phase 2: Implement Remove with Rebalancing

### Step 4: Basic Remove Implementation

**Status**: Not Started
**Changes**:

- [ ] Implement BPlusTree::remove method
- [ ] Handle simple cases (no underflow)
- [ ] Add comprehensive tests for basic removal

### Step 5: Add Underflow Handling

**Status**: Not Started
**Changes**:

- [ ] Implement underflow detection in remove
- [ ] Add redistribute logic (try siblings first)
- [ ] Add merge logic (when redistribute fails)
- [ ] Handle chain updates when nodes are removed
- [ ] Add tests for all rebalancing scenarios

### Step 6: Handle Edge Cases

**Status**: Not Started
**Changes**:

- [ ] Handle removing from single-node tree
- [ ] Handle removing last key from tree
- [ ] Handle removing from first/last nodes in chain
- [ ] Add comprehensive edge case tests

## Phase 3: Prepare for Internal Nodes (Future)

### Step 7: Extract Rebalancing Abstractions

**Status**: Not Started
**Changes**:

- [ ] Create Rebalanceable trait
- [ ] Extract rebalancing logic into reusable components
- [ ] Create Node trait for polymorphism
- [ ] Refactor BPlusTree to use trait objects

### Step 8: Add Internal Node Structure

**Status**: Not Started
**Changes**:

- [ ] Implement IndexNode struct
- [ ] Implement Node trait for IndexNode
- [ ] Update insertion to create internal nodes
- [ ] Extend rebalancing to handle internal nodes

## Testing Strategy

### Existing Tests

- All current tests must continue to pass after each step
- Fuzz tests provide comprehensive validation

### New Tests Needed

- [ ] Doubly linked list traversal tests
- [ ] Remove operation tests (basic cases)
- [ ] Underflow and rebalancing tests
- [ ] Edge case tests for remove
- [ ] Performance tests for remove operations

## Implementation Notes

### Key Principles

- Follow TDD: Write tests first, implement minimal code to pass
- Tidy First: Separate structural changes from behavioral changes
- Small steps: Each commit should leave all tests passing
- Comprehensive validation: Use fuzz tests to catch edge cases

### Risk Mitigation

- Doubly linked list changes are structural - low risk
- Remove implementation is high complexity - implement incrementally
- Maintain existing API compatibility throughout
- Use fuzz tests to validate against BTreeMap behavior

## Current Focus

**Next Action**: Implement doubly linked list structure (Step 1)

- This is a pure structural change
- Should not break any existing functionality
- Enables efficient backward traversal needed for remove operations
