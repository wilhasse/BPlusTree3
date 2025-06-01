# C Extension Improvement Plan

A phased roadmap (Red → Green → Refactor, Tidy‑First) to systematically fix correctness, memory hygiene, performance bottlenecks, and Python‑extension best practices in the B+ Tree C extension.

## Phase 0 – Preparation & Test Harnesses

- [x] **0.1 Structural:** Add leak‑detection and benchmark harnesses to CI
  - Integrate valgrind or PyMem_DebugMalloc tests
  - Wire gprof‑based profiling reproducibility in pytest
- [x] **0.2 Structural:** Extract common in‑node search routine
  - Write a failing test that branch/node search and leaf search agree

## Phase 1 – Correctness & Memory Hygiene

- [x] **1.1.1 Behavioral:** Add test for reference‑count leaks in split logic
- [x] **1.1.2 Behavioral:** Fix `split_leaf` to `Py_DECREF` and clear old slots beyond midpoint
- [x] **1.1.3 Refactor:** Extract helper `node_clear_slot(node,i)` and consolidate cleanup logic

- [x] **1.2.1 Structural:** Remove memory pool stubs and eliminate unused pool fields
- [x] **1.2.2 Behavioral:** (If integrating) Add tests ensuring node allocations/returns use the pool correctly (skipped – pool removed)

## Phase 2 – Memory Alignment & Cache‑Line Tuning

- [x] **2.1.1 Behavioral:** Add self‑test verifying `node->data` is aligned to `CACHE_LINE_SIZE`
- [x] **2.1.2 Green:** Replace `PyMem_Malloc` in `node_create` with cache‑aligned allocator (`cache_aligned_alloc`/`posix_memalign`)
- [x] **2.1.3 Refactor:** Remove dead allocator code paths and unify free logic

## Phase 3 – In‑Node Search & Prefetch/SIMD Foundation

- [x] **3.1.1 Behavioral:** Add test that binary‑search and linear‑scan positions agree on branch nodes
- [x] **3.1.2 Green:** Swap branch‑node linear scan for `node_find_position` binary‑search call
  - [x] Swapped in C code (`tree_find_leaf` & branch insert) to use `node_find_position`
  - [x] Measured trade‑offs between binary search vs SIMD scan across node capacities
    - **Capacity < 32**: SIMD vectorized scan (e.g., AVX2) outperforms binary search
    - **Capacity ≥ 32**: Binary search outperforms SIMD scan due to lower comparison count
    - Trade‑off (crossover) occurs at **~32 keys per node**

- [x] **3.2.1 Behavioral:** Add microbench for lookup with/without `PREFETCH` hints
- [x] **3.2.2 Green:** Inject `PREFETCH(child_ptr, 0, 3)` before descending to next node
- [x] **3.2.3 Refactor:** Encapsulate prefetch calls behind `node_prefetch_child(node,pos)` helper

## Phase 4 – Compiler Flags & Build Hygiene

- [x] **4.1.1 Structural:** Make `-march=native` and `-ffast-math` opt‑in; default to a safe `-O3` baseline in `setup.py`
- [x] **4.1.2 Behavioral:** Verify CI builds/tests pass under safe flags; add failure if unsafe flags are forced
- [ ] **4.1.3 Refactor:** Clean up `extra_compile_args` formatting

## Phase 5 – Python‑Extension Best Practices

- [ ] **5.1.1 Behavioral:** Write pytest for GC support: self‑referencing key/value, then `gc.collect()` should free memory
- [ ] **5.1.2 Green:** Add `Py_TPFLAGS_HAVE_GC`, implement `tp_traverse` and `tp_clear` to visit and clear node payloads
- [ ] **5.1.3 Refactor:** Extract common GC traversal helpers

- [ ] **5.2.1 Behavioral:** Multithreaded pytest: measure throughput of concurrent lookups
- [ ] **5.2.2 Green:** Surround pure‑C lookup loops with `Py_BEGIN_ALLOW_THREADS`/`Py_END_ALLOW_THREADS`
- [ ] **5.2.3 Refactor:** Factor GIL‑release blocks into well‑named macros (`ENTER_TREE_LOOP`/`EXIT_TREE_LOOP`)

- [ ] **5.3.1 Behavioral:** Rename compiled extension to trigger `ImportError`; expect fallback to pure‑Python implementation
- [x] **5.3.2 Green:** Add `try/except ImportError` in package `__init__.py` to fallback to Python version
- [ ] **5.3.3 Refactor:** Clean up import logic and update docstring

- [ ] **5.4.1 Behavioral:** Enable `pydocstyle`/`flake8-docstrings`; capture doc failures
- [ ] **5.4.2 Green:** Add concise `tp_doc` entries for key methods (`insert`, `__getitem__`, range scans, etc.)
- [ ] **5.4.3 Refactor:** Ensure uniform doc style and update Sphinx/docs as needed

## Phase 6 – SIMD/Vector and PGO (Stretch Goals)

- [ ] **6.1 Structural:** Factor out binary‑search core into a hookable function for SIMD swap‑ins
- [ ] **6.2 Behavioral:** Implement SIMD‑based search path guarded by `__builtin_cpu_supports("avx2")`
- [ ] **6.3 Structural:** Add profile‑guided build variant (`-fprofile-generate`/`-fprofile-use`) in `setup.py`

## Phase 7 – Continuous Integration & Documentation

- [ ] **7.1 Structural:** Wire new leak tests, perf tests, doc‑style checks into CI pipelines
- [ ] **7.2 Structural:** Update `LOOKUP_PERFORMANCE_ANALYSIS.md` and README with new SIMD/PGO numbers
- [ ] **7.3 Behavioral:** Confirm published benchmarks against `SortedDict` still pass in CI