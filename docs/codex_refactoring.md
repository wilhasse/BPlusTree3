# Refactoring Plan: Helper APIs & Code Simplification

This document outlines a phased approach to introduce reusable helper functions
and traits in `src/lib.rs`, with the goal of eliminating boilerplate and
clarifying the core B+‑tree operations (`get`, `insert`, `remove`, rebalance,
merge, etc.). By encapsulating common patterns (node lookup, child dispatch,
rebalance logic, merges, and split insertion) into small, well‑tested utilities,
we can shrink and simplify the implementation surface and reduce risks of
memory or logic errors.

## Phase 2: `find_child` / `find_child_mut`

**Objective:** Collapse the two-step computation of child index and child enum
(`NodeRef`) into a single helper.

**Implementation steps:**

1. Implement:
   ```rust
   fn find_child(&self, branch_id: NodeId, key: &K)
     -> Option<(usize, NodeRef<K, V>)>;
   fn find_child_mut(&mut self, branch_id: NodeId, key: &K)
     -> Option<(usize, NodeRef<K, V>)>;
   ```
2. Write tests covering branch lookups and out-of-range indices.
3. Replace manual `branch.find_child_index` + `branch.children.get(idx)` code
   in `get`, `insert`, `remove`, and rebalance routines.

## Phase 3: `NodeRef` Helper Methods

**Objective:** Provide ergonomic accessors on `NodeRef<K,V>` to reduce pattern matches.

**Implementation steps:**

1. On `NodeRef<K, V>`, add:
   ```rust
   fn id(&self) -> NodeId;
   fn is_leaf(&self) -> bool;
   ```
2. Update code that matches on `NodeRef::Leaf` / `NodeRef::Branch` to use the new
   helpers for dispatching to child nodes.

## Phase 4: `RebalanceableNode` Trait

**Objective:** Unify leaf and branch rebalance logic under a single driver using a
trait, reducing near-duplicate implementations.

**Implementation steps:**

1. Define a trait `RebalanceableNode<K, V>` with methods:
   ```rust
   fn can_donate(&self) -> bool;
   fn is_underfull(&self) -> bool;
   fn borrow_from(&mut self, sibling: &mut Self, sep_key: &mut K, from_left: bool);
   fn merge_with(&mut self, sibling: &mut Self, sep_key: Option<K>, from_left: bool);
   ```
2. Implement the trait for `LeafNode<K, V>` and `BranchNode<K, V>`.
3. Write a generic `rebalance_child` driver that calls into `RebalanceableNode`.

## Phase 5: `move_node_contents` Helper for Merges

**Objective:** Factor out the repeated take-then-append merge pattern across four
merge routines (left/right × leaf/branch).

**Implementation steps:**

1. Add a generic helper:
   ```rust
   fn move_node_contents<N, F>(
     arena: &mut Vec<Option<N>>, from: NodeId, to: NodeId, merge_fn: F
   ) -> Option<()> where F: FnOnce(&mut N, N);
   ```
2. Refactor each of `merge_with_left_leaf`, `merge_with_right_leaf`,
   `merge_with_left_branch`, and `merge_with_right_branch` to use `move_node_contents`.

## Phase 6: `BranchNode::insert_child` API

**Objective:** Centralize branch-child insertion and split logic into a single method
on `BranchNode<K,V>`, eliminating repetitive arena bookkeeping and root-update code.

**Implementation steps:**

1. On `BranchNode<K, V>`, implement:
   ```rust
   fn insert_child(
     &mut self,
     idx: usize,
     sep_key: K,
     right: NodeRef<K, V>,
     capacity: usize
   ) -> Option<(BranchNode<K, V>, K)>;
   ```
2. Refactor all calling sites in the tree map logic (`insert`/split handlers) to use
   this new helper and simplify root creation.

## Phase 7: Cleanup, Testing, and Benchmark Validation

1. Remove now‑unused macros and old helper functions (e.g. `ENTER_TREE_LOOP`).
2. Run unit tests and benchmarks to ensure no behavioral or performance regressions.
3. Update `README.md` and other documentation to reflect the new APIs.
4. Submit a single cohesive PR with related tests and doc updates for review.

---

By following this plan, we will transform the current ~2,000 lines of tightly coupled tree
logic in `src/lib.rs` into a modular, maintainable codebase where complex operations
are expressed via small, composable utilities.
