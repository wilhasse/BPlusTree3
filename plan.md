# BPlusTree Implementation Plan

## Overall Strategy: Internal Nodes with Get & Insert First

We'll implement BranchNodes (internal nodes) focusing on get & insert operations first, including all edge cases around splitting leaves. Remove operations will come later once the tree structure is solid.

## Phase 1: BranchNode Foundation (Get & Insert Focus)

### Step 1: Create Node Trait and BranchNode Structure ⏳ (Next)

**Goal**: Define polymorphic node structure for LeafNode and BranchNode
**Test**: `test_branch_node_creation_and_basic_operations`

**Changes**:

- [ ] Create `Node<K, V>` trait with common operations
- [ ] Implement `BranchNode<K, V>` struct for internal nodes
- [ ] Implement `Node` trait for both `LeafNode` and `BranchNode`
- [ ] Test basic BranchNode creation and operations

### Step 2: Update LeafFinder for Polymorphic Nodes ⏳

**Goal**: Make LeafFinder work with both node types and track path
**Test**: `test_leaf_finder_with_branch_nodes_simple`

**Changes**:

- [ ] Update LeafFinder to store traversal path
- [ ] Modify find_leaf methods to accept trait objects
- [ ] Handle both BranchNode and LeafNode traversal
- [ ] Test path tracking through BranchNodes

### Step 3: Update BPlusTree Root to Use Trait Objects ⏳

**Goal**: Allow tree root to be either LeafNode or BranchNode
**Test**: `test_tree_with_branch_root_basic_get`

**Changes**:

- [ ] Change BPlusTree.leaves to root: Box<dyn Node<K, V>>
- [ ] Update get() method to work with trait objects
- [ ] Ensure existing functionality works with new structure
- [ ] Test get operations through BranchNode root

### Step 4: Implement BranchNode Key Navigation ⏳

**Goal**: Enable finding correct child nodes for keys
**Test**: `test_branch_node_find_child_for_key`

**Changes**:

- [ ] Add find_child_index method to BranchNode
- [ ] Add get_child and get_child_mut methods
- [ ] Test key-to-child mapping with various scenarios
- [ ] Handle boundary conditions correctly

### Step 5: Implement Basic Insert Through BranchNodes ⏳

**Goal**: Support insertion that traverses BranchNodes to reach leaves
**Test**: `test_insert_through_branch_node`

**Changes**:

- [ ] Update BPlusTree::insert to traverse BranchNodes
- [ ] Ensure LeafFinder works correctly for insertions
- [ ] Test inserting into existing leaves through BranchNode
- [ ] Verify no splitting occurs yet (simple case)

### Step 6: Implement Leaf Splitting with Parent Updates ⏳

**Goal**: Handle leaf splits that require updating parent BranchNode
**Test**: `test_leaf_split_updates_parent_branch`

**Changes**:

- [ ] Detect when leaf split requires parent key update
- [ ] Add separator key insertion to parent BranchNode
- [ ] Handle BranchNode key insertion and shifting
- [ ] Test that split leaves are properly linked to parent

### Step 7: Implement Root Promotion (Leaf to Branch) ⏳

**Goal**: Convert single LeafNode root to BranchNode when it splits
**Test**: `test_root_promotion_leaf_to_branch`

**Changes**:

- [ ] Detect when root LeafNode needs to split
- [ ] Create new BranchNode root with separator key
- [ ] Link split leaves as children of new root
- [ ] Update BPlusTree.root to point to BranchNode

### Step 8: Implement BranchNode Splitting ⏳

**Goal**: Handle BranchNode overflow by splitting internal nodes
**Test**: `test_branch_node_split_creates_new_level`

**Changes**:

- [ ] Add split() method to BranchNode
- [ ] Handle separator key promotion to parent
- [ ] Create new tree level when root BranchNode splits
- [ ] Test multi-level tree creation

### Step 9: Comprehensive Insert Testing ⏳

**Goal**: Ensure all insert scenarios work correctly
**Test**: `test_comprehensive_insert_scenarios`

**Changes**:

- [ ] Test insertions causing multiple levels of splits
- [ ] Verify tree maintains B+ tree invariants
- [ ] Test with various branching factors
- [ ] Ensure all existing tests still pass

## Phase 2: Remove Operations (Future)

### Step 10: Implement Remove Through BranchNodes ⏳

**Goal**: Support remove operations in multi-level trees
**Status**: Future work after get/insert is complete

**Changes**:

- [ ] Update remove to traverse BranchNodes
- [ ] Handle underflow in leaves with BranchNode parents
- [ ] Implement key removal from BranchNodes
- [ ] Handle BranchNode underflow and merging

## Testing Strategy

### Existing Tests

- All current tests must continue to pass after each step
- Focus on get & insert operations initially
- Remove operation tests will be updated later

### New Tests for BranchNodes

- [ ] BranchNode creation and basic operations
- [ ] LeafFinder path tracking through BranchNodes
- [ ] Get operations through multi-level trees
- [ ] Insert operations with leaf splitting
- [ ] Root promotion scenarios
- [ ] BranchNode splitting and tree growth

## Implementation Notes

### Key Principles

- Follow TDD: Write tests first, implement minimal code to pass
- Tidy First: Separate structural changes from behavioral changes
- Small steps: Each commit should leave all tests passing
- Comprehensive validation: Use fuzz tests to catch edge cases

### Risk Mitigation

- ~~Doubly linked list changes are structural - low risk~~ - Using singly linked list
- Remove implementation is high complexity - implement incrementally
- Maintain existing API compatibility throughout
- Use fuzz tests to validate against BTreeMap behavior

## Current Focus

**Next Action**: Implement Step 1 - Create Node Trait and BranchNode Structure

Ready to begin BranchNode implementation:

- Remove operations are complete for linked-list structure
- All existing tests pass and provide regression protection
- Focus shifts to get & insert operations with internal nodes
- Remove operations will be updated after BranchNode foundation is solid
