# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Rust Development
```bash
# Run tests (requires testing feature)
cargo test --features testing

# Run benchmarks
cargo bench

# Run specific benchmark
cargo bench -- deletion

# Build release version
cargo build --release

# Run a single test
cargo test test_name --features testing
```

### Python Development
```bash
# Install in development mode
cd python/
pip install -e .

# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=bplustree --cov-report=term-missing

# Run specific tests
python -m pytest tests/test_bplustree.py -v

# Run performance benchmarks
python tests/test_performance_vs_sorteddict.py

# Build C extension (optional)
BPLUSTREE_BUILD_C_EXTENSION=1 python setup.py build_ext --inplace

# Lint Python code
ruff check .
black .
mypy bplustree/
```

### Cross-Language Analysis
```bash
# Run cross-language benchmark comparison
python scripts/analyze_benchmarks.py
```

### Zig Development
```bash
# Build the Zig library
cd zig/
zig build

# Run all tests
zig build test

# Run specific test categories
zig build test-adversarial-edge    # Adversarial edge case tests
zig build test-adversarial-linked  # Adversarial linked list tests  
zig build test-bugs                # Bug reproduction tests
zig build test-critical-bugs       # Critical bug tests
zig build test-concurrent          # Concurrent modification tests
zig build test-deletion            # Advanced deletion tests
zig build test-edge                # Edge case tests
zig build test-error-handling      # Enhanced error handling tests
zig build test-fuzz                # Fuzz tests
zig build test-invariants          # Tree invariant tests
zig build test-iterator            # Iterator safety tests
zig build test-linked-list         # Linked list invariant tests
zig build test-memory              # Memory safety tests
zig build test-memory-safety       # Comprehensive memory safety tests
zig build test-range               # Range query tests
zig build test-stress              # Stress tests

# Run benchmarks
zig build benchmark

# Format code
zig fmt .

# Build release version
zig build -Doptimize=ReleaseFast
```

#### Zig Implementation Notes
The Zig implementation is undergoing TDD development to achieve feature parity with the Rust version. When implementing new features:

1. **Always write tests first** - Following TDD principles
2. **Use Rust implementation as reference** - The Rust version has been thoroughly tested and debugged
3. **Focus on missing features**:
   - Advanced range query syntax (unbounded, exclusive ranges)
   - Get with default value functionality
   - Comprehensive error handling and validation
   - Edge case handling (extreme values, capacity validation)
   - Advanced node balancing (borrowing from siblings)
   - Iterator safety and modification tracking
   - Fuzz testing framework

4. **Test categories (now fully implemented)**:
   - ✅ Core functionality
   - ✅ Edge cases and boundary conditions
   - ✅ Error handling and validation
   - ✅ Memory safety and leak detection
   - ✅ Adversarial test cases
   - ✅ Performance benchmarks
   - ✅ Linked list invariant validation
   - ✅ Bug reproduction tests
   - ✅ Critical bug tests
   - ✅ Fuzz testing framework
   - ✅ Concurrent modification simulation
   - ✅ Tree invariant validation
   
5. **Known issues and implementation priorities**:
   - ⚠️ Memory leaks on allocation failure - B+ tree doesn't properly clean up partially allocated nodes when allocation fails during split operations
   - ⚠️ Edge case handling for extreme integer values needs improvement
   - ✅ All test categories have been implemented
   - ✅ Comprehensive error handling tests added
   - ✅ Advanced deletion tests implemented
   - Future work: Fix allocation failure cleanup and extreme value handling

## High-Level Architecture

### Project Structure
This is a **dual-language B+ tree implementation** with both Rust and Python versions. The implementations share core design principles but are optimized for their respective ecosystems.

### Core Design Principles
1. **Arena-based memory management** - Both implementations use arena allocation for efficient node management
2. **Linked leaf nodes** - Leaf nodes are linked for efficient sequential access during range queries
3. **Hybrid navigation** - Combines tree traversal with linked list iteration for optimal range query performance
4. **Optimized rebalancing** - Reduced duplicate lookups during node splitting/merging operations

### Rust Implementation Architecture
- **Arena Allocator** (`src/arena.rs`): Custom memory management with NodeId-based references instead of pointers
- **Node Types**: Branch nodes store keys and child NodeIds; Leaf nodes store key-value pairs and next/prev links
- **Iterator System**: Multiple iterator types supporting Rust's range syntax (`3..7`, `3..=7`, etc.)
- **Error Handling**: Comprehensive error types with context for debugging

### Python Implementation Architecture
- **Dual Implementation Strategy**: 
  - Pure Python fallback (`bplus_tree.py`) for compatibility
  - C extension (`bplustree_c_src/`) for 2-4x performance improvement
- **Dict-like API**: Full compatibility with Python's dict interface
- **Iterator Safety**: C extension tracks modifications to prevent segfaults during iteration

### Key Performance Optimizations
1. **Capacity Tuning**: Default capacity of 128 provides optimal performance (3.3x faster than capacity 4)
2. **Range Query Optimization**: Hybrid navigation reduces comparisons by up to 30%
3. **Deletion Optimization**: Rebalancing improvements yield 19-41% faster deletions
4. **Cache Locality**: Arena allocation improves cache utilization

## Development Philosophy - Test-Driven Development (TDD)

This is a **Test-Driven Development (TDD) project** following Kent Beck's methodology. The development process is strictly:

### TDD Cycle: Red → Green → Refactor
1. **Red**: Write a failing test that defines a small increment of functionality
2. **Green**: Implement the minimum code needed to make the test pass
3. **Refactor**: Improve code structure while keeping tests passing

### Key TDD Principles
- **One test at a time**: Write and implement one test before moving to the next
- **Minimal implementation**: Write just enough code to make tests pass - no more
- **Meaningful test names**: Use descriptive names like `test_should_handle_empty_tree`
- **Test first for bugs**: When fixing defects, first write a failing test that reproduces the issue

### Tidy First Approach
Separate all changes into two distinct types:
- **Structural changes**: Refactoring without changing behavior (renaming, extracting methods)
- **Behavioral changes**: Adding or modifying functionality
- Never mix structural and behavioral changes in the same commit

### Commit Discipline
Only commit when:
- ALL tests are passing
- ALL compiler/linter warnings are resolved
- Commit messages clearly state whether changes are structural or behavioral

See `rust/docs/CLAUDE.md` for complete TDD guidelines and workflow examples.

## Testing Structure

### Rust Testing
- **Test files**: Located in `rust/tests/` directory
- **Test categories**:
  - Core functionality: `bplus_tree.rs`
  - Edge cases: `adversarial_*.rs` files
  - Bug reproductions: `bug_reproduction_tests.rs`, `critical_bug_test.rs`
  - Memory safety: `memory_leak_detection.rs`, `memory_safety_audit.rs`
  - Fuzzing: `fuzz_tests.rs`
- **Run tests**: `cargo test --features testing`

### Python Testing
- **Test files**: Located in `python/tests/` directory
- **Test categories**:
  - Core functionality: `test_bplus_tree.py`
  - C extension: `test_c_extension*.py`
  - Performance: `test_performance_*.py`
  - Thread safety: `test_multithreaded_lookup.py`
  - Iterator safety: `test_iterator_modification_safety.py`
- **Run tests**: `python -m pytest tests/`

### Zig Testing
- **Test files**: Located in `zig/tests/` directory
- **Total tests**: 153 tests across 18 test files
- **Test categories (✅ fully implemented)**:
  - ✅ Core functionality: `test_bplustree.zig`
  - ✅ Stress tests: `test_stress.zig`
  - ✅ Iterator safety: `test_iterator_safety.zig`
  - ✅ Advanced deletion: `test_deletion_advanced.zig`
  - ✅ Memory safety: `test_memory_safety.zig`
  - ✅ Range queries: `test_range_queries.zig`
  - ✅ Edge cases: `test_edge_cases.zig`
  - ✅ Linked list invariants: `test_linked_list_invariants.zig`
  - ✅ Adversarial edge cases: `test_adversarial_edge_cases.zig`
  - ✅ Adversarial linked list: `test_adversarial_linked_list.zig`
  - ✅ Enhanced error handling: `test_enhanced_error_handling.zig`
  - ✅ Fuzz testing: `test_fuzz.zig`
  - ✅ Tree invariants: `test_tree_invariants.zig`
  - ✅ Bug reproduction: `test_bug_reproduction.zig`
  - ✅ Critical bugs: `test_critical_bugs.zig`
  - ✅ Memory safety (comprehensive): `test_comprehensive_memory_safety.zig`
  - ✅ Concurrent modifications: `test_concurrent_modifications.zig`
- **Run tests**: `zig build test`
- **Status**: All major test categories implemented with proper memory leak handling and edge case coverage