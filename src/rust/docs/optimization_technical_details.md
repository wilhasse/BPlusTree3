# B+ Tree Optimization Technical Details

## Memory Layout Optimizations

### Current Memory Layout Issues

```rust
// Current inefficient layout
struct LeafNode<K, V> {
    capacity: usize,
    keys: Vec<K>,      // Separate allocation
    values: Vec<V>,    // Separate allocation
}
```

**Problems**:

- Two separate heap allocations per node
- Poor cache locality when accessing key-value pairs
- Memory fragmentation
- Extra indirection overhead

### Proposed Optimized Layout

```rust
// Option 1: Interleaved storage
struct LeafNode<K, V> {
    capacity: usize,
    len: usize,
    data: Box<[(K, V)]>,  // Single allocation, interleaved
}

// Option 2: Arena-based allocation
struct BPlusTreeArena<K, V> {
    // All nodes in contiguous memory
    leaf_arena: Vec<LeafNodeData<K, V>>,
    branch_arena: Vec<BranchNodeData<K, V>>,
    free_lists: FreeLists,
}

// Option 3: Hybrid approach with small object optimization
enum NodeStorage<K, V> {
    Inline([MaybeUninit<(K, V)>; 8]),  // For small nodes
    Heap(Box<[(K, V)]>),               // For larger nodes
}
```

### Implementation Strategy

```rust
impl<K, V> LeafNode<K, V> {
    // Optimized insertion with minimal copying
    fn insert_optimized(&mut self, index: usize, key: K, value: V) {
        if self.len < self.capacity {
            // In-place insertion using ptr::copy
            unsafe {
                let ptr = self.data.as_mut_ptr().add(index);
                ptr::copy(ptr, ptr.add(1), self.len - index);
                ptr::write((key, value));
            }
            self.len += 1;
        } else {
            self.split_and_insert(index, key, value);
        }
    }
}
```

## Iterator Optimization Details

### Current Iterator Problems

```rust
// Current inefficient iteration
impl<K, V> Iterator for BPlusTreeIterator<K, V> {
    fn next(&mut self) -> Option<Self::Item> {
        // Traverses tree structure for each element
        // Excessive bounds checking
        // No prefetching
    }
}
```

### Proposed Cursor-Based Iterator

```rust
struct BPlusTreeCursor<'a, K, V> {
    current_leaf: Option<&'a LeafNode<K, V>>,
    leaf_index: usize,
    tree: &'a BPlusTreeMap<K, V>,
    // Cache for next leaf to avoid tree traversal
    next_leaf_cache: Option<&'a LeafNode<K, V>>,
}

impl<'a, K, V> BPlusTreeCursor<'a, K, V> {
    fn advance(&mut self) {
        self.leaf_index += 1;

        if let Some(leaf) = self.current_leaf {
            if self.leaf_index >= leaf.len() {
                // Move to next leaf using cached pointer or linked list
                self.current_leaf = self.next_leaf_cache.take();
                self.leaf_index = 0;
                self.prefetch_next_leaf();
            }
        }
    }

    fn prefetch_next_leaf(&mut self) {
        // Prefetch next leaf to avoid cache misses
        if let Some(leaf) = self.current_leaf {
            self.next_leaf_cache = leaf.next_sibling;
        }
    }
}
```

### Bulk Range Operations

```rust
impl<K, V> BPlusTreeMap<K, V> {
    fn range_bulk<R>(&self, range: R) -> BulkRangeIterator<K, V>
    where
        R: RangeBounds<K>,
    {
        let start_leaf = self.find_leaf_for_range_start(&range);
        let end_leaf = self.find_leaf_for_range_end(&range);

        BulkRangeIterator {
            current_leaf: start_leaf,
            end_leaf,
            current_index: 0,
            range,
            // Pre-calculate iteration bounds to minimize checks
            remaining_items: self.estimate_range_size(&range),
        }
    }
}
```

## Deletion Algorithm Optimization

### Current Deletion Issues

```rust
// Current naive deletion
fn remove(&mut self, key: &K) -> Option<V> {
    // 1. Find leaf (tree traversal)
    // 2. Remove key (immediate rebalancing)
    // 3. Propagate changes up (multiple traversals)
    // 4. Rebalance at each level
}
```

### Proposed Lazy Deletion with Batching

```rust
struct LazyDeletionNode<K, V> {
    keys: Vec<Option<K>>,
    values: Vec<Option<V>>,
    deleted_count: usize,
    deletion_threshold: usize,  // When to trigger cleanup
}

impl<K, V> LazyDeletionNode<K, V> {
    fn mark_deleted(&mut self, index: usize) -> Option<V> {
        if let Some(value) = self.values[index].take() {
            self.keys[index] = None;
            self.deleted_count += 1;

            // Trigger cleanup if too many deletions
            if self.deleted_count > self.deletion_threshold {
                self.compact();
            }

            Some(value)
        } else {
            None
        }
    }

    fn compact(&mut self) {
        // Bulk compaction to remove all deleted entries
        let mut write_index = 0;
        for read_index in 0..self.keys.len() {
            if self.keys[read_index].is_some() {
                if write_index != read_index {
                    self.keys[write_index] = self.keys[read_index].take();
                    self.values[write_index] = self.values[read_index].take();
                }
                write_index += 1;
            }
        }
        self.keys.truncate(write_index);
        self.values.truncate(write_index);
        self.deleted_count = 0;
    }
}
```

### Bulk Rebalancing Strategy

```rust
struct RebalanceContext<K, V> {
    nodes_to_rebalance: Vec<NodeId>,
    rebalance_operations: Vec<RebalanceOp<K, V>>,
}

enum RebalanceOp<K, V> {
    Merge { left: NodeId, right: NodeId },
    Split { node: NodeId, split_point: usize },
    Redistribute { from: NodeId, to: NodeId, count: usize },
}

impl<K, V> BPlusTreeMap<K, V> {
    fn bulk_rebalance(&mut self, context: RebalanceContext<K, V>) {
        // Sort operations by tree level (bottom-up)
        context.rebalance_operations.sort_by_key(|op| self.node_level(op.node_id()));

        // Execute all operations in batch
        for operation in context.rebalance_operations {
            self.execute_rebalance_operation(operation);
        }

        // Update parent pointers in single pass
        self.update_parent_pointers_bulk(&context.nodes_to_rebalance);
    }
}
```

## SIMD and Vectorization Optimizations

### Vectorized Key Comparison

```rust
#[cfg(target_arch = "x86_64")]
use std::arch::x86_64::*;

impl<K: Ord> LeafNode<K, i32> {
    // Specialized implementation for i32 keys
    fn binary_search_simd(&self, target: &K) -> Result<usize, usize> {
        if self.len <= 8 {
            // Use SIMD for small arrays
            self.linear_search_simd(target)
        } else {
            // Fall back to binary search for larger arrays
            self.keys.binary_search(target)
        }
    }

    #[cfg(target_arch = "x86_64")]
    fn linear_search_simd(&self, target: &i32) -> Result<usize, usize> {
        unsafe {
            let target_vec = _mm256_set1_epi32(*target);
            let keys_ptr = self.keys.as_ptr() as *const i32;

            // Load 8 keys at once
            let keys_vec = _mm256_loadu_si256(keys_ptr as *const __m256i);

            // Compare all 8 keys simultaneously
            let cmp_result = _mm256_cmpeq_epi32(keys_vec, target_vec);
            let mask = _mm256_movemask_epi8(cmp_result);

            if mask != 0 {
                // Found exact match
                let index = mask.trailing_zeros() / 4;
                Ok(index as usize)
            } else {
                // Find insertion point
                let lt_result = _mm256_cmpgt_epi32(target_vec, keys_vec);
                let lt_mask = _mm256_movemask_epi8(lt_result);
                let index = (lt_mask.count_ones()) as usize;
                Err(index)
            }
        }
    }
}
```

### Vectorized Memory Operations

```rust
impl<K: Copy, V: Copy> LeafNode<K, V> {
    fn bulk_copy_simd(&mut self, src: &[(K, V)], dst_index: usize) {
        if src.len() >= 4 && std::mem::size_of::<(K, V)>() == 8 {
            // Use SIMD for bulk copying when beneficial
            unsafe {
                let src_ptr = src.as_ptr() as *const u8;
                let dst_ptr = self.data.as_mut_ptr().add(dst_index) as *mut u8;

                // Copy 32 bytes (4 key-value pairs) at a time
                for i in (0..src.len()).step_by(4) {
                    let chunk = _mm256_loadu_si256(src_ptr.add(i * 8) as *const __m256i);
                    _mm256_storeu_si256(dst_ptr.add(i * 8) as *mut __m256i, chunk);
                }
            }
        } else {
            // Fall back to standard copy
            self.data[dst_index..dst_index + src.len()].copy_from_slice(src);
        }
    }
}
```

## Capacity and Splitting Optimizations

### Adaptive Capacity Selection

```rust
struct CapacityOptimizer {
    insertion_pattern: InsertionPattern,
    access_pattern: AccessPattern,
    memory_pressure: MemoryPressure,
}

enum InsertionPattern {
    Sequential,
    Random,
    Clustered { cluster_size: usize },
    Mixed,
}

impl CapacityOptimizer {
    fn optimal_capacity(&self, node_type: NodeType) -> usize {
        match (self.insertion_pattern, node_type) {
            (InsertionPattern::Sequential, NodeType::Leaf) => 128,
            (InsertionPattern::Random, NodeType::Leaf) => 64,
            (InsertionPattern::Clustered { cluster_size }, NodeType::Leaf) => {
                (cluster_size * 2).min(128).max(32)
            }
            (_, NodeType::Branch) => 64, // Branches benefit from higher capacity
        }
    }
}
```

### Intelligent Split Point Selection

```rust
impl<K: Ord, V> LeafNode<K, V> {
    fn optimal_split_point(&self, new_key: &K, insertion_pattern: &InsertionPattern) -> usize {
        match insertion_pattern {
            InsertionPattern::Sequential => {
                // For sequential inserts, split closer to the end
                (self.len * 3) / 4
            }
            InsertionPattern::Random => {
                // For random inserts, split in the middle
                self.len / 2
            }
            InsertionPattern::Clustered { .. } => {
                // Find the split point that minimizes future splits
                self.find_cluster_boundary(new_key)
            }
        }
    }

    fn find_cluster_boundary(&self, new_key: &K) -> usize {
        // Analyze key distribution to find natural split points
        let mut best_split = self.len / 2;
        let mut min_variance = f64::INFINITY;

        for split_point in (self.len / 4)..(3 * self.len / 4) {
            let variance = self.calculate_split_variance(split_point, new_key);
            if variance < min_variance {
                min_variance = variance;
                best_split = split_point;
            }
        }

        best_split
    }
}
```

## Benchmarking and Profiling Infrastructure

### Micro-benchmark Framework

```rust
#[cfg(feature = "bench")]
mod micro_benchmarks {
    use criterion::{criterion_group, criterion_main, Criterion, BenchmarkId};

    fn bench_memory_layout(c: &mut Criterion) {
        let mut group = c.benchmark_group("memory_layout");

        for size in [16, 32, 64, 128, 256].iter() {
            group.bench_with_input(
                BenchmarkId::new("interleaved", size),
                size,
                |b, &size| {
                    b.iter(|| {
                        let mut node = InterleavedLeafNode::new(*size);
                        for i in 0..*size {
                            node.insert(i, i * 2);
                        }
                    });
                },
            );

            group.bench_with_input(
                BenchmarkId::new("separate_vecs", size),
                size,
                |b, &size| {
                    b.iter(|| {
                        let mut node = SeparateVecsLeafNode::new(*size);
                        for i in 0..*size {
                            node.insert(i, i * 2);
                        }
                    });
                },
            );
        }
    }
}
```

### Performance Monitoring

```rust
#[cfg(feature = "perf_monitoring")]
struct PerformanceMonitor {
    operation_counts: HashMap<Operation, u64>,
    timing_data: HashMap<Operation, Duration>,
    memory_usage: MemoryStats,
}

impl PerformanceMonitor {
    fn record_operation<F, R>(&mut self, op: Operation, f: F) -> R
    where
        F: FnOnce() -> R,
    {
        let start = Instant::now();
        let result = f();
        let duration = start.elapsed();

        *self.operation_counts.entry(op).or_insert(0) += 1;
        *self.timing_data.entry(op).or_insert(Duration::ZERO) += duration;

        result
    }
}
```

## Concurrent Access Optimization

### Lock-Free Read Operations

```rust
use std::sync::atomic::{AtomicPtr, AtomicUsize, Ordering};
use std::sync::Arc;

struct ConcurrentBPlusTree<K, V> {
    root: AtomicPtr<Node<K, V>>,
    epoch: AtomicUsize,
    capacity: usize,
}

// Epoch-based memory management for lock-free operations
struct EpochManager {
    global_epoch: AtomicUsize,
    thread_epochs: ThreadLocal<AtomicUsize>,
    garbage_lists: Vec<Mutex<Vec<Box<dyn Send + Sync>>>>,
}

impl<K: Ord + Clone, V: Clone> ConcurrentBPlusTree<K, V> {
    fn get_concurrent(&self, key: &K) -> Option<V> {
        let epoch_guard = self.enter_epoch();

        loop {
            let root_ptr = self.root.load(Ordering::Acquire);
            if root_ptr.is_null() {
                return None;
            }

            let root = unsafe { &*root_ptr };
            let result = self.get_from_node(root, key, &epoch_guard);

            // Validate that root hasn't changed during traversal
            if self.root.load(Ordering::Acquire) == root_ptr {
                return result;
            }
            // Root changed, retry
        }
    }

    fn get_from_node(&self, node: &Node<K, V>, key: &K, _epoch: &EpochGuard) -> Option<V> {
        match node {
            Node::Leaf(leaf) => {
                // Lock-free binary search in leaf
                leaf.get_lock_free(key)
            }
            Node::Branch(branch) => {
                let child_index = branch.find_child_index_lock_free(key);
                let child_ptr = branch.children[child_index].load(Ordering::Acquire);
                if child_ptr.is_null() {
                    return None;
                }
                let child = unsafe { &*child_ptr };
                self.get_from_node(child, key, _epoch)
            }
        }
    }
}
```

### Optimistic Concurrency for Writes

```rust
struct OptimisticNode<K, V> {
    version: AtomicUsize,
    data: RwLock<NodeData<K, V>>,
}

impl<K: Ord, V> OptimisticNode<K, V> {
    fn insert_optimistic(&self, key: K, value: V) -> Result<Option<V>, RetryError> {
        let initial_version = self.version.load(Ordering::Acquire);

        // Try to acquire read lock for validation
        let data = self.data.read().map_err(|_| RetryError::LockContention)?;

        // Validate version hasn't changed
        if self.version.load(Ordering::Acquire) != initial_version {
            return Err(RetryError::VersionMismatch);
        }

        // Check if we need to split
        if data.needs_split() {
            drop(data);
            return self.insert_with_split(key, value);
        }

        // Try to upgrade to write lock
        drop(data);
        let mut data = self.data.write().map_err(|_| RetryError::LockContention)?;

        // Double-check version after acquiring write lock
        if self.version.load(Ordering::Acquire) != initial_version {
            return Err(RetryError::VersionMismatch);
        }

        let old_value = data.insert_in_place(key, value);

        // Increment version to signal change
        self.version.fetch_add(1, Ordering::Release);

        Ok(old_value)
    }
}
```

## Advanced Memory Management

### Custom Allocator for B+ Tree Nodes

```rust
use std::alloc::{GlobalAlloc, Layout, System};
use std::ptr::NonNull;

struct BPlusTreeAllocator {
    node_pools: [NodePool; 8], // Different sizes for different capacities
    fallback: System,
}

struct NodePool {
    capacity: usize,
    node_size: usize,
    free_list: Mutex<Vec<NonNull<u8>>>,
    allocated_chunks: Mutex<Vec<NonNull<u8>>>,
}

impl NodePool {
    fn allocate_node(&self) -> Option<NonNull<u8>> {
        let mut free_list = self.free_list.lock().unwrap();

        if let Some(ptr) = free_list.pop() {
            Some(ptr)
        } else {
            // Allocate new chunk of nodes
            self.allocate_chunk()
        }
    }

    fn allocate_chunk(&self) -> Option<NonNull<u8>> {
        const CHUNK_SIZE: usize = 64; // Allocate 64 nodes at once
        let total_size = self.node_size * CHUNK_SIZE;
        let layout = Layout::from_size_align(total_size, std::mem::align_of::<usize>()).ok()?;

        let chunk = unsafe { System.alloc(layout) };
        if chunk.is_null() {
            return None;
        }

        let chunk_ptr = NonNull::new(chunk)?;
        self.allocated_chunks.lock().unwrap().push(chunk_ptr);

        // Add all but the first node to free list
        let mut free_list = self.free_list.lock().unwrap();
        for i in 1..CHUNK_SIZE {
            let node_ptr = unsafe {
                NonNull::new_unchecked(chunk.add(i * self.node_size))
            };
            free_list.push(node_ptr);
        }

        Some(chunk_ptr)
    }
}
```

### Memory-Mapped B+ Trees for Large Datasets

```rust
use memmap2::{MmapMut, MmapOptions};
use std::fs::OpenOptions;

struct MmapBPlusTree<K, V> {
    mmap: MmapMut,
    header: *mut TreeHeader,
    node_arena: *mut u8,
    capacity: usize,
}

#[repr(C)]
struct TreeHeader {
    magic: u64,
    version: u32,
    node_count: u32,
    root_offset: u64,
    free_list_head: u64,
    capacity: u32,
    key_size: u32,
    value_size: u32,
}

impl<K: Copy, V: Copy> MmapBPlusTree<K, V> {
    fn new(file_path: &str, initial_size: usize) -> Result<Self, std::io::Error> {
        let file = OpenOptions::new()
            .read(true)
            .write(true)
            .create(true)
            .open(file_path)?;

        file.set_len(initial_size as u64)?;

        let mmap = unsafe { MmapOptions::new().map_mut(&file)? };

        let header = mmap.as_ptr() as *mut TreeHeader;
        let node_arena = unsafe { mmap.as_ptr().add(std::mem::size_of::<TreeHeader>()) };

        // Initialize header if new file
        unsafe {
            if (*header).magic != 0xB17E_TREE_MAGIC {
                *header = TreeHeader {
                    magic: 0xB17E_TREE_MAGIC,
                    version: 1,
                    node_count: 0,
                    root_offset: 0,
                    free_list_head: 0,
                    capacity: 64,
                    key_size: std::mem::size_of::<K>() as u32,
                    value_size: std::mem::size_of::<V>() as u32,
                };
            }
        }

        Ok(Self {
            mmap,
            header,
            node_arena: node_arena as *mut u8,
            capacity: unsafe { (*header).capacity as usize },
        })
    }

    fn allocate_node(&mut self) -> u64 {
        unsafe {
            if (*self.header).free_list_head != 0 {
                // Reuse from free list
                let offset = (*self.header).free_list_head;
                let node_ptr = self.node_arena.add(offset as usize) as *mut u64;
                (*self.header).free_list_head = *node_ptr;
                offset
            } else {
                // Allocate new node
                let node_size = self.calculate_node_size();
                let offset = (*self.header).node_count as u64 * node_size;
                (*self.header).node_count += 1;
                offset
            }
        }
    }
}
```

## Profiling and Monitoring Infrastructure

### Real-time Performance Monitoring

```rust
use std::time::{Duration, Instant};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};

#[derive(Debug, Clone)]
pub struct PerformanceMetrics {
    pub operation_counts: HashMap<Operation, u64>,
    pub total_times: HashMap<Operation, Duration>,
    pub min_times: HashMap<Operation, Duration>,
    pub max_times: HashMap<Operation, Duration>,
    pub cache_hits: u64,
    pub cache_misses: u64,
    pub node_splits: u64,
    pub node_merges: u64,
    pub tree_height: usize,
    pub memory_usage: usize,
}

#[derive(Debug, Clone, Copy, Hash, Eq, PartialEq)]
pub enum Operation {
    Insert,
    Get,
    Remove,
    RangeQuery,
    Iteration,
    Split,
    Merge,
    Rebalance,
}

pub struct PerformanceMonitor {
    metrics: Arc<Mutex<PerformanceMetrics>>,
    enabled: bool,
}

impl PerformanceMonitor {
    pub fn new() -> Self {
        Self {
            metrics: Arc::new(Mutex::new(PerformanceMetrics::default())),
            enabled: cfg!(feature = "performance_monitoring"),
        }
    }

    pub fn time_operation<F, R>(&self, op: Operation, f: F) -> R
    where
        F: FnOnce() -> R,
    {
        if !self.enabled {
            return f();
        }

        let start = Instant::now();
        let result = f();
        let duration = start.elapsed();

        let mut metrics = self.metrics.lock().unwrap();
        *metrics.operation_counts.entry(op).or_insert(0) += 1;
        *metrics.total_times.entry(op).or_insert(Duration::ZERO) += duration;

        // Update min/max times
        let min_entry = metrics.min_times.entry(op).or_insert(duration);
        if duration < *min_entry {
            *min_entry = duration;
        }

        let max_entry = metrics.max_times.entry(op).or_insert(duration);
        if duration > *max_entry {
            *max_entry = duration;
        }

        result
    }

    pub fn record_cache_hit(&self) {
        if self.enabled {
            self.metrics.lock().unwrap().cache_hits += 1;
        }
    }

    pub fn record_cache_miss(&self) {
        if self.enabled {
            self.metrics.lock().unwrap().cache_misses += 1;
        }
    }

    pub fn get_metrics(&self) -> PerformanceMetrics {
        self.metrics.lock().unwrap().clone()
    }

    pub fn reset_metrics(&self) {
        *self.metrics.lock().unwrap() = PerformanceMetrics::default();
    }

    pub fn print_summary(&self) {
        let metrics = self.get_metrics();

        println!("=== B+ Tree Performance Summary ===");
        println!("Cache hit rate: {:.2}%",
            100.0 * metrics.cache_hits as f64 /
            (metrics.cache_hits + metrics.cache_misses) as f64);

        for (op, count) in &metrics.operation_counts {
            let total_time = metrics.total_times.get(op).unwrap_or(&Duration::ZERO);
            let avg_time = *total_time / (*count as u32);
            let min_time = metrics.min_times.get(op).unwrap_or(&Duration::ZERO);
            let max_time = metrics.max_times.get(op).unwrap_or(&Duration::ZERO);

            println!("{:?}: {} ops, avg: {:?}, min: {:?}, max: {:?}",
                op, count, avg_time, min_time, max_time);
        }

        println!("Tree height: {}", metrics.tree_height);
        println!("Memory usage: {} bytes", metrics.memory_usage);
        println!("Node splits: {}", metrics.node_splits);
        println!("Node merges: {}", metrics.node_merges);
    }
}
```

### Automated Benchmark Suite

```rust
use criterion::{criterion_group, criterion_main, Criterion, BenchmarkId, Throughput};
use std::collections::BTreeMap;

fn comprehensive_benchmarks(c: &mut Criterion) {
    benchmark_insertion_patterns(c);
    benchmark_lookup_patterns(c);
    benchmark_deletion_patterns(c);
    benchmark_range_queries(c);
    benchmark_mixed_workloads(c);
    benchmark_capacity_optimization(c);
    benchmark_memory_usage(c);
}

fn benchmark_insertion_patterns(c: &mut Criterion) {
    let mut group = c.benchmark_group("insertion_patterns");

    for &size in &[100, 1000, 10000, 100000] {
        group.throughput(Throughput::Elements(size));

        // Sequential insertion
        group.bench_with_input(
            BenchmarkId::new("sequential_bplus", size),
            &size,
            |b, &size| {
                b.iter(|| {
                    let mut tree = BPlusTreeMap::new(64).unwrap();
                    for i in 0..size {
                        tree.insert(i, i * 2);
                    }
                });
            },
        );

        group.bench_with_input(
            BenchmarkId::new("sequential_btree", size),
            &size,
            |b, &size| {
                b.iter(|| {
                    let mut tree = BTreeMap::new();
                    for i in 0..size {
                        tree.insert(i, i * 2);
                    }
                });
            },
        );

        // Random insertion
        let random_keys: Vec<u64> = (0..size).map(|_| rand::random()).collect();

        group.bench_with_input(
            BenchmarkId::new("random_bplus", size),
            &random_keys,
            |b, keys| {
                b.iter(|| {
                    let mut tree = BPlusTreeMap::new(64).unwrap();
                    for &key in keys {
                        tree.insert(key, key * 2);
                    }
                });
            },
        );

        group.bench_with_input(
            BenchmarkId::new("random_btree", size),
            &random_keys,
            |b, keys| {
                b.iter(|| {
                    let mut tree = BTreeMap::new();
                    for &key in keys {
                        tree.insert(key, key * 2);
                    }
                });
            },
        );
    }

    group.finish();
}

fn benchmark_capacity_optimization(c: &mut Criterion) {
    let mut group = c.benchmark_group("capacity_optimization");

    for &capacity in &[4, 8, 16, 32, 64, 128, 256] {
        group.bench_with_input(
            BenchmarkId::new("insertion", capacity),
            &capacity,
            |b, &capacity| {
                b.iter(|| {
                    let mut tree = BPlusTreeMap::new(capacity).unwrap();
                    for i in 0..10000 {
                        tree.insert(i, i * 2);
                    }
                });
            },
        );

        // Pre-populate tree for lookup benchmarks
        let mut tree = BPlusTreeMap::new(capacity).unwrap();
        for i in 0..10000 {
            tree.insert(i, i * 2);
        }

        group.bench_with_input(
            BenchmarkId::new("lookup", capacity),
            &tree,
            |b, tree| {
                b.iter(|| {
                    for i in (0..10000).step_by(100) {
                        criterion::black_box(tree.get(&i));
                    }
                });
            },
        );
    }

    group.finish();
}

fn benchmark_memory_usage(c: &mut Criterion) {
    let mut group = c.benchmark_group("memory_usage");

    group.bench_function("memory_efficiency", |b| {
        b.iter(|| {
            let mut tree = BPlusTreeMap::new(64).unwrap();
            let mut btree = BTreeMap::new();

            // Insert same data into both trees
            for i in 0..10000 {
                tree.insert(i, format!("value_{}", i));
                btree.insert(i, format!("value_{}", i));
            }

            // Measure memory usage (simplified)
            let bplus_size = std::mem::size_of_val(&tree);
            let btree_size = std::mem::size_of_val(&btree);

            (bplus_size, btree_size)
        });
    });

    group.finish();
}

criterion_group!(benches, comprehensive_benchmarks);
criterion_main!(benches);
```

## Implementation Validation Framework

### Correctness Testing

```rust
#[cfg(test)]
mod validation_tests {
    use super::*;
    use proptest::prelude::*;

    proptest! {
        #[test]
        fn property_insert_get_consistency(
            operations in prop::collection::vec(
                (any::<u32>(), any::<String>()),
                0..1000
            )
        ) {
            let mut tree = BPlusTreeMap::new(64).unwrap();
            let mut reference = std::collections::BTreeMap::new();

            for (key, value) in operations {
                let tree_result = tree.insert(key, value.clone());
                let ref_result = reference.insert(key, value);

                prop_assert_eq!(tree_result, ref_result);
                prop_assert!(tree.check_invariants());
            }

            // Verify all keys are accessible
            for (key, expected_value) in &reference {
                prop_assert_eq!(tree.get(key), Some(expected_value));
            }
        }

        #[test]
        fn property_remove_consistency(
            initial_data in prop::collection::vec(
                (any::<u32>(), any::<String>()),
                0..500
            ),
            remove_keys in prop::collection::vec(any::<u32>(), 0..100)
        ) {
            let mut tree = BPlusTreeMap::new(32).unwrap();
            let mut reference = std::collections::BTreeMap::new();

            // Insert initial data
            for (key, value) in initial_data {
                tree.insert(key, value.clone());
                reference.insert(key, value);
            }

            // Remove keys
            for key in remove_keys {
                let tree_result = tree.remove(&key);
                let ref_result = reference.remove(&key);

                prop_assert_eq!(tree_result, ref_result);
                prop_assert!(tree.check_invariants());
            }
        }
    }

    #[test]
    fn stress_test_large_dataset() {
        const SIZE: usize = 1_000_000;
        let mut tree = BPlusTreeMap::new(128).unwrap();

        // Insert large dataset
        for i in 0..SIZE {
            tree.insert(i, format!("value_{}", i));

            if i % 10000 == 0 {
                assert!(tree.check_invariants(), "Invariants violated at insert {}", i);
            }
        }

        // Verify all data
        for i in 0..SIZE {
            assert_eq!(tree.get(&i), Some(&format!("value_{}", i)));
        }

        // Remove half the data
        for i in (0..SIZE).step_by(2) {
            tree.remove(&i);

            if i % 10000 == 0 {
                assert!(tree.check_invariants(), "Invariants violated at remove {}", i);
            }
        }

        // Verify remaining data
        for i in 0..SIZE {
            if i % 2 == 0 {
                assert_eq!(tree.get(&i), None);
            } else {
                assert_eq!(tree.get(&i), Some(&format!("value_{}", i)));
            }
        }
    }
}
```

This comprehensive technical specification provides all the detailed implementation guidance needed to execute the performance optimization plan effectively, covering memory management, concurrency, profiling, and validation strategies.
