# BPlusTree Implementation Plan

## Overall Strategy: Internal Nodes with Get & Insert First

We'll implement BranchNodes (internal nodes) focusing on get & insert operations first, including all edge cases around splitting leaves. Remove operations will come later once the tree structure is solid.

## Phase 1: BranchNode Foundation (Get & Insert Focus)

### Step 1: Create Node Trait and BranchNode Structure ⏳ (In Progress)

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

## Comprehensive Test Case Lists

### Insertion Test Cases

#### Basic Insertion (Single LeafNode)

- [ ] `test_insert_into_empty_tree` - Insert first key-value pair
- [ ] `test_insert_at_beginning` - Insert key smaller than existing keys
- [ ] `test_insert_in_middle` - Insert key between existing keys
- [ ] `test_insert_at_end` - Insert key larger than existing keys
- [ ] `test_insert_duplicate_key_updates_value` - Update existing key
- [ ] `test_insert_maintains_sorted_order` - Keys remain sorted after insertions
- [ ] `test_insert_up_to_branching_factor` - Fill node to capacity without splitting

#### Leaf Splitting (Linked List Structure)

- [ ] `test_leaf_split_basic` - Split when exceeding branching factor
- [ ] `test_leaf_split_even_distribution` - Keys distributed evenly between nodes
- [ ] `test_leaf_split_maintains_order` - Order preserved across split nodes
- [ ] `test_leaf_split_preserves_linked_list` - Next pointers updated correctly
- [ ] `test_multiple_leaf_splits` - Sequential splits create proper chain
- [ ] `test_insert_after_split` - Insertions work correctly after splitting
- [ ] `test_split_with_different_branching_factors` - Various branching factors (2, 3, 4, 8, 16)

#### BranchNode Insertion

- [ ] `test_insert_through_branch_node` - Insert via BranchNode to correct leaf
- [ ] `test_insert_updates_branch_keys` - BranchNode keys updated after leaf split
- [ ] `test_insert_into_multiple_leaves` - Insert into different leaves via same BranchNode
- [ ] `test_branch_node_key_insertion` - Insert separator keys into BranchNode
- [ ] `test_branch_node_maintains_sorted_keys` - BranchNode keys remain sorted

#### Root Promotion

- [ ] `test_root_promotion_single_leaf_split` - LeafNode root becomes BranchNode
- [ ] `test_root_promotion_preserves_data` - All data accessible after promotion
- [ ] `test_root_promotion_correct_separator` - Correct separator key chosen
- [ ] `test_operations_after_root_promotion` - Get/insert work after promotion

#### BranchNode Splitting

- [ ] `test_branch_node_split_basic` - Split BranchNode when full
- [ ] `test_branch_node_split_creates_new_level` - New root level created
- [ ] `test_branch_node_split_separator_promotion` - Separator key promoted correctly
- [ ] `test_multi_level_tree_creation` - Multiple levels created through splits
- [ ] `test_deep_tree_insertion` - Insertions in trees with 3+ levels

#### Edge Cases

- [ ] `test_insert_sequential_ascending` - Insert 1, 2, 3, 4, ... (worst case)
- [ ] `test_insert_sequential_descending` - Insert ..., 4, 3, 2, 1 (worst case)
- [ ] `test_insert_alternating_pattern` - Insert 1, 100, 2, 99, 3, 98, ...
- [ ] `test_insert_random_order` - Insert keys in random order
- [ ] `test_insert_with_small_branching_factor` - Branching factor = 2
- [ ] `test_insert_with_large_branching_factor` - Branching factor = 64
- [ ] `test_insert_duplicate_keys_extensively` - Many updates to same keys
- [ ] `test_insert_boundary_values` - Min/max integer values
- [ ] `test_insert_large_dataset` - 1000+ keys to stress test structure

### Removal Test Cases

#### Basic Removal (Single LeafNode)

- [x] `test_remove_existing_key` - Remove key that exists, verify value returned
- [x] `test_remove_nonexistent_key` - Remove key that doesn't exist, return None
- [ ] `test_remove_first_key` - Remove smallest key from node
- [ ] `test_remove_last_key` - Remove largest key from node
- [ ] `test_remove_middle_key` - Remove key from middle of node
- [x] `test_remove_all_keys_from_single_node` - Remove all keys one by one
- [x] `test_remove_last_key_from_tree` - Remove final key, tree becomes empty

#### Removal with Underflow (Linked List Structure)

- [x] `test_remove_with_underflow` - Remove causing underflow, trigger rebalancing
- [ ] `test_remove_with_redistribution` - Underflow fixed by borrowing from sibling
- [ ] `test_remove_with_merge` - Underflow fixed by merging with sibling
- [x] `test_remove_from_first_node_causing_empty` - First node becomes empty
- [ ] `test_remove_from_last_node_causing_empty` - Last node becomes empty
- [ ] `test_remove_causing_chain_collapse` - Multiple nodes merge into one

#### Removal from BranchNode Trees

- [ ] `test_remove_through_branch_node` - Remove via BranchNode traversal
- [ ] `test_remove_updates_branch_keys` - BranchNode keys updated after leaf changes
- [ ] `test_remove_leaf_underflow_with_branch_parent` - Leaf underflow in tree structure
- [ ] `test_remove_causes_leaf_merge_updates_branch` - Leaf merge updates parent
- [ ] `test_remove_from_multiple_levels` - Remove from trees with 2+ levels

#### BranchNode Underflow and Merging

- [ ] `test_branch_node_underflow_redistribution` - BranchNode borrows from sibling
- [ ] `test_branch_node_underflow_merge` - BranchNode merges with sibling
- [ ] `test_remove_causes_tree_height_reduction` - Tree becomes shorter
- [ ] `test_remove_branch_node_becomes_leaf` - BranchNode root becomes LeafNode
- [ ] `test_deep_tree_underflow_propagation` - Underflow propagates up multiple levels

#### Edge Cases

- [ ] `test_remove_sequential_ascending` - Remove 1, 2, 3, 4, ... (worst case)
- [ ] `test_remove_sequential_descending` - Remove ..., 4, 3, 2, 1 (worst case)
- [ ] `test_remove_alternating_pattern` - Remove every other key
- [ ] `test_remove_random_order` - Remove keys in random order
- [ ] `test_remove_with_small_branching_factor` - Branching factor = 2
- [ ] `test_remove_with_large_branching_factor` - Branching factor = 64
- [ ] `test_remove_after_many_insertions` - Remove from large, complex tree
- [ ] `test_remove_and_reinsert_same_keys` - Remove then reinsert same keys
- [ ] `test_remove_boundary_values` - Remove min/max integer values

### Get Operation Test Cases

#### Basic Get Operations

- [x] `test_get_existing_key` - Get key that exists
- [x] `test_get_nonexistent_key` - Get key that doesn't exist
- [ ] `test_get_from_empty_tree` - Get from empty tree
- [ ] `test_get_after_insertions` - Get after various insertions
- [ ] `test_get_after_removals` - Get after various removals

#### Get Through BranchNodes

- [ ] `test_get_through_single_branch` - Get via one BranchNode
- [ ] `test_get_through_multiple_branches` - Get via multiple BranchNode levels
- [ ] `test_get_from_different_leaves` - Get keys from different leaf nodes
- [ ] `test_get_boundary_keys` - Get smallest/largest keys in tree
- [ ] `test_get_after_tree_restructuring` - Get after splits/merges change structure

#### Range and Slice Operations

- [x] `test_range_basic` - Get range of keys
- [x] `test_slice_all_keys` - Get all keys in sorted order
- [ ] `test_range_across_multiple_leaves` - Range spans multiple leaf nodes
- [ ] `test_range_across_branch_boundaries` - Range crosses BranchNode boundaries
- [ ] `test_range_empty_result` - Range with no matching keys
- [ ] `test_range_single_key` - Range containing exactly one key
- [ ] `test_slice_after_complex_operations` - Slice after many insert/remove operations

### Validation and Invariant Test Cases

#### Tree Structure Validation

- [ ] `test_validate_empty_tree` - Empty tree passes validation
- [ ] `test_validate_single_leaf` - Single LeafNode tree passes validation
- [ ] `test_validate_after_insertions` - Tree valid after various insertions
- [ ] `test_validate_after_removals` - Tree valid after various removals
- [ ] `test_validate_after_splits` - Tree valid after leaf/branch splits
- [ ] `test_validate_after_merges` - Tree valid after node merges
- [ ] `test_validate_multi_level_tree` - Complex tree structure validation

#### B+ Tree Invariants

- [ ] `test_leaf_node_key_count_invariant` - Leaf nodes have correct key counts
- [ ] `test_branch_node_key_count_invariant` - Branch nodes have correct key counts
- [ ] `test_key_ordering_invariant` - All keys in correct sorted order
- [ ] `test_leaf_chain_invariant` - Leaf nodes properly linked
- [ ] `test_branch_child_invariant` - Branch nodes point to correct children
- [ ] `test_separator_key_invariant` - Separator keys correctly partition children
- [ ] `test_tree_height_balance_invariant` - All leaves at same level

#### Stress Tests and Fuzz Testing

- [x] `fuzz_test_bplus_tree` - Random operations against BTreeMap reference
- [x] `fuzz_test_with_updates` - Extensive key updates and modifications
- [ ] `fuzz_test_with_removals` - Random insert/remove patterns
- [ ] `stress_test_large_dataset` - 10,000+ keys with various operations
- [ ] `stress_test_small_branching_factor` - Stress test with branching factor 2
- [ ] `stress_test_sequential_operations` - Worst-case sequential patterns
- [ ] `stress_test_concurrent_like_operations` - Simulate concurrent access patterns
- [ ] `performance_test_insertion_speed` - Measure insertion performance
- [ ] `performance_test_lookup_speed` - Measure get operation performance
- [ ] `performance_test_range_queries` - Measure range operation performance

### Integration Test Cases

#### Mixed Operations

- [ ] `test_mixed_insert_remove_get` - Interleaved operations
- [ ] `test_build_tree_then_destroy` - Insert many, then remove all
- [ ] `test_alternating_build_destroy` - Build up, tear down, repeat
- [ ] `test_update_heavy_workload` - Many updates to same keys
- [ ] `test_range_queries_during_modifications` - Range queries while modifying

#### Regression Tests

- [ ] `test_all_existing_functionality_preserved` - All current tests pass
- [ ] `test_api_compatibility` - Public API unchanged
- [ ] `test_performance_regression` - Performance not significantly degraded
- [ ] `test_memory_usage` - Memory usage reasonable for tree size

#### Error Handling and Edge Cases

- [ ] `test_operations_on_empty_tree` - All operations work on empty tree
- [ ] `test_operations_after_clear` - Operations work after clearing tree
- [ ] `test_extreme_branching_factors` - Very small (2) and large (1000) factors
- [ ] `test_integer_overflow_keys` - Keys near integer limits
- [ ] `test_zero_and_negative_keys` - Handle zero and negative integers

## Test Case Summary

### Current Status (✅ = Implemented, ⏳ = In Progress, ❌ = Not Started)

**Insertion Tests**: 7/34 implemented (20%)

- ✅ Basic single-node insertion (7 tests)
- ❌ Leaf splitting (7 tests)
- ❌ BranchNode insertion (5 tests)
- ❌ Root promotion (4 tests)
- ❌ BranchNode splitting (5 tests)
- ❌ Edge cases (9 tests)

**Removal Tests**: 5/25 implemented (20%)

- ✅ Basic single-node removal (5 tests)
- ❌ Underflow handling (6 tests)
- ❌ BranchNode removal (5 tests)
- ❌ BranchNode underflow (5 tests)
- ❌ Edge cases (9 tests)

**Get Operation Tests**: 2/12 implemented (17%)

- ✅ Basic get operations (2 tests)
- ❌ BranchNode traversal (5 tests)
- ❌ Range operations (5 tests)

**Validation Tests**: 2/32 implemented (6%)

- ❌ Structure validation (7 tests)
- ❌ Invariant checking (7 tests)
- ✅ Stress/fuzz testing (2 tests)
- ❌ Integration tests (5 tests)
- ❌ Regression tests (4 tests)
- ❌ Error handling (7 tests)

**Total**: 16/103 test cases implemented (16%)

### Priority Order for Implementation

1. **Phase 1 (BranchNode Foundation)**: Focus on get & insert with BranchNodes

   - BranchNode creation and basic operations
   - LeafFinder updates for polymorphic nodes
   - Basic get operations through BranchNodes
   - Simple insertion through BranchNodes

2. **Phase 2 (Splitting Logic)**: Handle all splitting scenarios

   - Leaf splitting with parent updates
   - Root promotion scenarios
   - BranchNode splitting and tree growth
   - Edge cases for splitting

3. **Phase 3 (Remove Operations)**: Implement removal with BranchNodes

   - Basic removal through BranchNodes
   - Underflow handling in tree structure
   - BranchNode underflow and merging
   - Complex removal scenarios

4. **Phase 4 (Validation & Testing)**: Comprehensive testing
   - Invariant validation for tree structure
   - Stress testing and performance validation
   - Integration and regression testing
   - Edge case and error handling

## Implementation Notes

### Key Principles

- Follow TDD: Write tests first, implement code to pass, then generalize
- After making test pass: Consider ways to simplify code so other tests will also pass
- Goal: Simpler, more general code rather than minimal specific solutions
- Tidy First: Separate structural changes from behavioral changes
- Small steps: Each commit should leave all tests passing
- Comprehensive validation: Use fuzz tests to catch edge cases

### Implementation Strategy

1. **One Test at a Time**: Implement exactly one failing test, then make it pass
2. **Generalize After Passing**: After making test pass, consider simplifications that make other tests pass too
3. **Seek General Solutions**: Prefer simpler, more general code over minimal specific implementations
4. **Structural vs Behavioral**: Separate trait/struct definitions (structural) from algorithm implementations (behavioral)
5. **Path Tracking**: LeafFinder path will be crucial for future remove operations
6. **Backward Compatibility**: All existing tests must continue to pass

### TDD Cycle with Generalization

1. **Red**: Write a failing test for the next small increment of functionality
2. **Green**: Write just enough code to make the test pass (may be specific/hacky)
3. **Generalize**: Look for ways to simplify the code so it's more general and would handle other similar cases
4. **Refactor**: Clean up the code while keeping all tests passing
5. **Commit**: Commit when all tests pass and code is clean

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
