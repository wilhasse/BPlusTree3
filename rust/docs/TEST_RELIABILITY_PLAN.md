# B+ Tree Reliability Test Plan

## Goal: Demonstrate Unreliability Through Adversarial Testing

### Philosophy
We're not trying to increase coverage numbers - we're trying to break the B+ Tree implementation by targeting the most complex, error-prone code paths that coverage analysis revealed as untested.

## Attack Vectors (Prioritized by Likelihood of Finding Bugs)

### 1. **Branch Rebalancing Under Stress** (HIGHEST RISK)
The coverage shows branch rebalancing operations are largely untested. These involve complex multi-node coordination.

**Attack Strategy:**
- Create trees where branch nodes are exactly at minimum capacity
- Force deletions that trigger cascading rebalances through multiple levels
- Target the "borrow from sibling" logic with adversarial node distributions
- Create scenarios where both siblings are at minimum capacity (forcing merges)

**Why This Will Break:**
- Complex coordination between parent and multiple children
- Multiple mutable borrows and arena updates
- Edge cases in determining which sibling to borrow from/merge with

### 2. **Arena Corruption Scenarios** (CRASH RISK)
The arena-based allocation has many untested error paths.

**Attack Strategy:**
- Trigger maximum arena growth by creating then deleting many nodes
- Force ID reuse patterns that might expose free list bugs
- Create trees that maximize arena fragmentation
- Test behavior when approaching u32::MAX node IDs

**Why This Will Break:**
- Free list management is complex and largely untested
- ID overflow handling is not tested
- Arena growth/shrink patterns could expose memory bugs

### 3. **Root Collapse Edge Cases** (DATA LOSS RISK)
Root collapse has special cases that "shouldn't happen" according to comments.

**Attack Strategy:**
- Create deep trees and delete in patterns that force repeated root collapses
- Target the "empty root branch" and "single child root" paths
- Combine with concurrent operations to expose race conditions

**Why This Will Break:**
- Special case handling that developers think "shouldn't happen"
- Complex state transitions during tree height changes
- Potential for orphaning entire subtrees

### 4. **Linked List Invariant Violations** (ITERATOR CORRUPTION)
The leaf linked list is maintained across complex operations.

**Attack Strategy:**
- Perform splits and merges while iterating
- Create patterns that might produce cycles in the linked list
- Test iterator behavior after tree modifications
- Target the exact moment when next pointers are updated

**Why This Will Break:**
- Linked list updates happen in multiple places
- No cycle detection in iterators
- Complex coordination during splits/merges

### 5. **Capacity Boundary Exploitation** (INVARIANT VIOLATIONS)
Operations at exact capacity boundaries are prone to off-by-one errors.

**Attack Strategy:**
- Insert exactly capacity items, then one more
- Delete down to exactly min_keys, then one more
- Alternate between operations that push nodes to exact boundaries
- Use capacities that expose integer division edge cases (e.g., capacity=5)

**Why This Will Break:**
- Off-by-one errors in split/merge decisions
- Integer division for min_keys calculation
- Boundary conditions in is_full/is_underfull checks

### 6. **Range Query Race Conditions** (INCORRECT RESULTS)
The optimized range iterator uses complex navigation.

**Attack Strategy:**
- Start range queries at keys that don't exist
- Use ranges that span exactly one node boundary
- Query ranges while modifying the tree
- Test with empty ranges, single-item ranges, full-tree ranges

**Why This Will Break:**
- Complex start position finding logic
- Assumptions about tree structure during iteration
- No protection against concurrent modifications

## Test Implementation Order

1. **Start with Branch Rebalancing** - Most complex, most likely to find bugs
2. **Then Arena Corruption** - Could cause crashes
3. **Root Collapse Patterns** - Special cases that "shouldn't happen"
4. **Linked List Invariants** - Critical for iterator correctness
5. **Capacity Boundaries** - Classic source of bugs
6. **Range Query Edge Cases** - User-visible bugs

## Success Metrics

- Find at least one panic/crash
- Find at least one invariant violation
- Find at least one data loss scenario
- Find at least one incorrect query result
- Demonstrate that the implementation is NOT reliable under adversarial conditions