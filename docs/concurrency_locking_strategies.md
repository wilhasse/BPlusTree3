# Concurrency Control in B+ Trees: Global Lock vs Fine-Grained Node Locking

This document analyzes two fundamental approaches to concurrent access in B+ tree implementations: using a single lock for the entire tree versus fine-grained locking at the node level.

## Overview

B+ trees are critical data structures in database systems where concurrent access is the norm. The choice of locking strategy profoundly impacts performance, scalability, and implementation complexity.

## Approach 1: Global Tree Lock

```rust
pub struct BPlusTreeMap<K, V> {
    root: NodeRef<K, V>,
    lock: RwLock<()>,  // Single lock for entire tree
    // ... other fields
}

impl<K, V> BPlusTreeMap<K, V> {
    pub fn get(&self, key: &K) -> Option<V> {
        let _guard = self.lock.read();
        // Perform search
    }
    
    pub fn insert(&mut self, key: K, value: V) -> Option<V> {
        let _guard = self.lock.write();
        // Perform insertion
    }
}
```

### Advantages

1. **Simplicity**: Trivial to implement correctly
2. **No Deadlocks**: Single lock eliminates possibility of deadlock
3. **Predictable Performance**: No lock contention overhead within operations
4. **Memory Efficiency**: Minimal memory overhead (one lock total)
5. **Cache Friendly**: No lock checking during traversal improves cache usage

### Disadvantages

1. **No Concurrency**: All operations are fully serialized
2. **Reader Blocking**: Even read-only operations block each other with write locks
3. **Poor Scalability**: Performance degrades linearly with thread count
4. **Long Write Latency**: Large operations block all other threads

## Approach 2: Fine-Grained Node Locking

```rust
pub struct LeafNode<K, V> {
    keys: Vec<K>,
    values: Vec<V>,
    lock: RwLock<()>,
    next: Arc<RwLock<NodeId>>,  // Locked separately for concurrent scans
}

pub struct BranchNode<K, V> {
    keys: Vec<K>,
    children: Vec<NodeRef<K, V>>,
    lock: RwLock<()>,
}
```

### Locking Protocols

#### 1. Lock Coupling (Hand-over-Hand)
```rust
fn search(&self, key: &K) -> Option<V> {
    let mut current_guard = self.root.read();
    
    loop {
        match current_node {
            Leaf(node) => {
                return node.get(key).cloned();
            }
            Branch(node) => {
                let child = node.find_child(key);
                let child_guard = child.read();
                drop(current_guard);  // Release parent before continuing
                current_guard = child_guard;
            }
        }
    }
}
```

#### 2. B-link Trees (Right-Link Pointers)
- Add "right-link" pointers at each level
- Allows recovery if node splits during traversal
- Enables lock-free readers in some implementations

#### 3. Optimistic Lock Coupling
```rust
fn search_optimistic(&self, key: &K) -> Option<V> {
    loop {
        // Read without locks
        let path = self.find_path_lockfree(key);
        
        // Verify path is still valid
        if self.validate_path(&path) {
            return path.leaf.get(key);
        }
        // Retry if tree changed
    }
}
```

### Advantages

1. **High Concurrency**: Multiple operations proceed in parallel
2. **Read Scalability**: Readers don't block each other in different subtrees
3. **Localized Contention**: Conflicts only occur on same nodes
4. **Better Multi-Core Utilization**: True parallel execution

### Disadvantages

1. **Complex Implementation**: Correct implementation is challenging
2. **Deadlock Risk**: Must carefully order lock acquisition
3. **Memory Overhead**: One lock per node (significant for small nodes)
4. **Lock Overhead**: Acquiring/releasing locks has CPU cost
5. **Harder Debugging**: Concurrency bugs are notoriously difficult

## Special Considerations for B+ Trees

### Split and Merge Operations

**Global Lock**: Trivial - already holding exclusive access

**Node Locking**: Complex protocol required:
```rust
fn split_leaf(&self, leaf: &LeafNode) {
    // Must lock:
    // 1. Leaf being split
    // 2. Parent node
    // 3. New sibling (once created)
    // 4. Next leaf pointer update
    // In correct order to avoid deadlock!
}
```

### Range Scans

**Global Lock**: Simple but blocks all other operations

**Node Locking**: 
- Can release locks on fully processed nodes
- Allows concurrent modifications outside scan range
- Must handle nodes splitting/merging during scan

### Root Node Changes

**Global Lock**: No special handling needed

**Node Locking**: Requires special protocol:
- Often uses a separate "root pointer" lock
- Or optimistic concurrency with CAS operations

## Performance Analysis

### Read-Heavy Workloads (95% reads, 5% writes)

**Global Lock (RwLock)**:
- Good: RwLock allows concurrent readers
- Bad: Any write blocks all readers
- Performance: Moderate

**Node Locking**:
- Excellent: Readers rarely conflict
- Near-linear scalability with core count
- Performance: Excellent

### Write-Heavy Workloads (50% writes)

**Global Lock**:
- Extremely poor scalability
- Effectively single-threaded execution
- Performance: Poor

**Node Locking**:
- Moderate: Depends on key distribution
- Hot nodes become bottlenecks
- Performance: Moderate to Good

### Mixed Workloads with Hotspots

**Global Lock**:
- Predictable but poor performance
- No benefit from key distribution

**Node Locking**:
- Can severely degrade if hotspot is near root
- Requires careful key distribution
- Performance: Highly Variable

## Implementation Complexity Comparison

### Global Lock
```rust
// Entire implementation in ~10 lines
pub fn insert(&mut self, key: K, value: V) -> Option<V> {
    let _guard = self.lock.write();
    self.insert_internal(key, value)
}
```

### Node Locking
```rust
// Requires hundreds of lines for correct implementation
pub fn insert(&mut self, key: K, value: V) -> Option<V> {
    let mut locks_held = Vec::new();
    let mut current_node = self.root.clone();
    
    // Complex traversal with lock management
    loop {
        // Lock coupling protocol
        // Handle node splits
        // Manage lock ordering
        // Deal with concurrent modifications
        // ... 100+ lines of intricate logic
    }
}
```

## Real-World Implementation Examples

### Global Lock Approach
- **SQLite**: Single writer, multiple readers via file locking
- **Early MySQL MyISAM**: Table-level locks
- **Redis**: Single-threaded with no locks needed

### Fine-Grained Locking
- **PostgreSQL**: Complex buffer manager with page-level locks
- **MySQL InnoDB**: Row-level locking with intention locks
- **Oracle**: Sophisticated multi-version concurrency control

### Hybrid Approaches
- **LMDB**: Copy-on-write with single writer, lockless readers
- **BerkeleyDB**: Page-level locks with deadlock detection
- **WiredTiger**: Hazard pointers and optimistic concurrency

## Recommendations

### Use Global Lock When:

1. **Simplicity is paramount**: Prototype or educational implementation
2. **Single writer model**: Only one thread modifies the tree
3. **Small trees**: Overhead of fine-grained locking exceeds benefits
4. **Read-heavy with RwLock**: 99%+ reads with very short writes
5. **Embedded systems**: Memory constraints prohibit per-node locks

### Use Fine-Grained Locking When:

1. **High concurrency required**: Multi-core systems with many threads
2. **Large trees**: Lock contention becomes significant bottleneck
3. **Mixed workloads**: Substantial read and write operations
4. **SLA requirements**: Need predictable latencies under load
5. **Production databases**: Where performance justifies complexity

### Alternative Approaches to Consider:

1. **Lock-Free Structures**: Using atomic operations and CAS
2. **Copy-on-Write**: MVCC-style approaches
3. **Sharding**: Multiple trees with key-based routing
4. **Hybrid Locking**: Global lock with optimistic reads

## Conclusion

For production B+ tree implementations, fine-grained locking is usually necessary to achieve acceptable performance under concurrent load. However, the implementation complexity is substantial and error-prone.

For this implementation, starting with a global RwLock is recommended because:

1. It allows the core B+ tree logic to be developed and tested without concurrency concerns
2. RwLock provides reasonable concurrency for read-heavy workloads
3. The implementation can later be enhanced with fine-grained locking if benchmarks show it's needed
4. Many successful systems (SQLite, Redis) demonstrate that global locking can be sufficient

The key insight is that **correctness trumps performance**. A correct implementation with global locking is infinitely better than a buggy implementation with fine-grained locking. Start simple, measure performance under realistic workloads, and only add complexity when data justifies it.