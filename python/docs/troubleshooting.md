# Troubleshooting Guide

## Installation Issues

### C Extension Build Failures

#### Problem: "Microsoft Visual C++ 14.0 is required" (Windows)

**Symptoms:**

```
error: Microsoft Visual C++ 14.0 is required. Get it with "Microsoft Visual C++ Build Tools"
```

**Solutions:**

1. **Install Build Tools:**

   - Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Install "Desktop development with C++"

2. **Use Conda (Alternative):**

   ```bash
   conda install -c conda-forge bplustree
   ```

3. **Force Pure Python:**
   ```python
   import os
   os.environ['BPLUSTREE_PURE_PYTHON'] = '1'
   import bplus_tree
   ```

#### Problem: "clang: error: unknown argument: '-mno-fused-madd'" (macOS)

**Symptoms:**

```
clang: error: unknown argument: '-mno-fused-madd'
```

**Solutions:**

1. **Update Xcode Command Line Tools:**

   ```bash
   xcode-select --install
   ```

2. **Set Environment Variable:**
   ```bash
   export CPPFLAGS=-Qunused-arguments
   export CFLAGS=-Qunused-arguments
   pip install bplustree
   ```

#### Problem: "gcc: command not found" (Linux)

**Symptoms:**

```
gcc: command not found
```

**Solutions:**

1. **Ubuntu/Debian:**

   ```bash
   sudo apt-get update
   sudo apt-get install build-essential python3-dev
   ```

2. **CentOS/RHEL:**

   ```bash
   sudo yum groupinstall "Development Tools"
   sudo yum install python3-devel
   ```

3. **Alpine Linux:**
   ```bash
   apk add gcc musl-dev python3-dev
   ```

### Import Errors

#### Problem: "ModuleNotFoundError: No module named 'bplus_tree'"

**Diagnosis:**

```python
import sys
print(sys.path)  # Check if installation directory is in path
```

**Solutions:**

1. **Verify Installation:**

   ```bash
   pip show bplustree
   pip list | grep bplustree
   ```

2. **Reinstall:**

   ```bash
   pip uninstall bplustree
   pip install bplustree
   ```

3. **Check Virtual Environment:**
   ```bash
   which python
   which pip
   ```

#### Problem: "ImportError: cannot import name 'BPlusTreeMap'"

**Symptoms:**

```python
from bplus_tree import BPlusTreeMap  # ImportError
```

**Solutions:**

1. **Check Import Style:**

   ```python
   # Correct imports
   from bplus_tree import BPlusTreeMap
   import bplus_tree

   # Check what's available
   import bplus_tree
   print(dir(bplus_tree))
   ```

2. **Clear Python Cache:**
   ```bash
   find . -name "*.pyc" -delete
   find . -name "__pycache__" -type d -exec rm -rf {} +
   ```

## Runtime Issues

### Performance Problems

#### Problem: B+ Tree is slower than expected

**Diagnosis:**

```python
from bplus_tree import get_implementation
print(f"Using: {get_implementation()}")

# Check capacity
tree = BPlusTreeMap()
if hasattr(tree, 'capacity'):
    print(f"Capacity: {tree.capacity}")
```

**Solutions:**

1. **Verify C Extension:**

   ```python
   # Should print "C extension"
   print(get_implementation())

   # If "Pure Python", rebuild:
   pip uninstall bplustree
   pip install --no-cache-dir bplustree
   ```

2. **Tune Capacity:**

   ```python
   # For large datasets
   tree = BPlusTreeMap(capacity=128)

   # For small datasets
   tree = BPlusTreeMap(capacity=8)
   ```

3. **Profile Your Usage:**
   ```python
   import cProfile
   cProfile.run('your_btree_code()')
   ```

#### Problem: Memory usage too high

**Diagnosis:**

```python
import sys
tree = BPlusTreeMap()
tree.update((i, f"value_{i}") for i in range(10000))
print(f"Tree size: {sys.getsizeof(tree)} bytes")
```

**Solutions:**

1. **Reduce Capacity:**

   ```python
   memory_efficient_tree = BPlusTreeMap(capacity=8)
   ```

2. **Use Integer Keys:**

   ```python
   # Memory-heavy
   tree[f"key_{i}"] = value

   # Memory-light
   tree[i] = value
   ```

3. **Clear Unused Trees:**
   ```python
   tree.clear()  # Instead of creating new trees
   ```

### Data Integrity Issues

#### Problem: KeyError for keys that should exist

**Diagnosis:**

```python
# Check key types
tree = BPlusTreeMap()
tree[1] = "integer"
tree["1"] = "string"

print(1 in tree)    # True
print("1" in tree)  # True
print(1.0 in tree)  # False - different type!
```

**Solutions:**

1. **Consistent Key Types:**

   ```python
   # Bad: mixed types
   tree[1] = "value"
   tree["1"] = "value"  # Different key!

   # Good: consistent types
   tree[str(1)] = "value"
   tree[str(2)] = "value"
   ```

2. **Type Conversion:**

   ```python
   def safe_key(key):
       """Convert all keys to strings."""
       return str(key)

   tree[safe_key(1)] = "value"
   value = tree.get(safe_key(1))
   ```

#### Problem: Unexpected ordering

**Symptoms:**

```python
tree = BPlusTreeMap()
tree["10"] = "ten"
tree["2"] = "two"
print(list(tree.keys()))  # ['10', '2'] - lexicographic order!
```

**Solutions:**

1. **Use Numeric Keys:**

   ```python
   tree[10] = "ten"
   tree[2] = "two"
   print(list(tree.keys()))  # [2, 10] - numeric order
   ```

2. **Zero-Pad String Keys:**

   ```python
   tree["02"] = "two"
   tree["10"] = "ten"
   print(list(tree.keys()))  # ['02', '10'] - correct order
   ```

3. **Custom Key Function:**

   ```python
   def numeric_string_key(s):
       """Convert string to sortable format."""
       return int(s) if s.isdigit() else s

   # Sort manually if needed
   items = sorted(tree.items(), key=lambda x: numeric_string_key(x[0]))
   ```

### Concurrency Issues

#### Problem: Data corruption with multiple threads

**Symptoms:**

- Inconsistent tree state
- Random KeyErrors
- Segmentation faults (C extension)

**Diagnosis:**

```python
import threading
import time

def test_thread_safety():
    tree = BPlusTreeMap()
    errors = []

    def worker(thread_id):
        try:
            for i in range(1000):
                tree[f"{thread_id}_{i}"] = i
        except Exception as e:
            errors.append(f"Thread {thread_id}: {e}")

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"Errors: {len(errors)}")
    print(f"Tree size: {len(tree)} (expected: 10000)")

test_thread_safety()
```

**Solutions:**

1. **Use Locks:**

   ```python
   import threading

   tree = BPlusTreeMap()
   tree_lock = threading.RLock()

   def safe_insert(key, value):
       with tree_lock:
           tree[key] = value

   def safe_get(key, default=None):
       with tree_lock:
           return tree.get(key, default)
   ```

2. **Thread-Local Storage:**

   ```python
   import threading

   # Each thread gets its own tree
   local_data = threading.local()

   def get_thread_tree():
       if not hasattr(local_data, 'tree'):
           local_data.tree = BPlusTreeMap()
       return local_data.tree
   ```

3. **Message Passing:**

   ```python
   import queue
   import threading

   class TreeManager:
       def __init__(self):
           self.tree = BPlusTreeMap()
           self.queue = queue.Queue()
           self.running = True
           self.thread = threading.Thread(target=self._worker)
           self.thread.start()

       def _worker(self):
           while self.running:
               try:
                   operation, args, result_queue = self.queue.get(timeout=1)
                   if operation == 'insert':
                       key, value = args
                       self.tree[key] = value
                       result_queue.put(None)
                   elif operation == 'get':
                       key, default = args
                       result = self.tree.get(key, default)
                       result_queue.put(result)
               except queue.Empty:
                   continue

       def insert(self, key, value):
           result_queue = queue.Queue()
           self.queue.put(('insert', (key, value), result_queue))
           result_queue.get()  # Wait for completion

       def get(self, key, default=None):
           result_queue = queue.Queue()
           self.queue.put(('get', (key, default), result_queue))
           return result_queue.get()
   ```

## Performance Debugging

### Slow Insertions

**Diagnosis:**

```python
import time

def diagnose_insertion_performance():
    sizes = [1000, 10000, 100000]
    capacities = [8, 32, 128]

    for size in sizes:
        for capacity in capacities:
            tree = BPlusTreeMap(capacity=capacity)

            start = time.perf_counter()
            for i in range(size):
                tree[i] = i
            duration = time.perf_counter() - start

            print(f"Size {size:6d}, Capacity {capacity:3d}: "
                  f"{duration:.3f}s ({size/duration:.0f} ops/sec)")

diagnose_insertion_performance()
```

**Solutions:**

1. **Increase Capacity:**

   ```python
   # Slow for large datasets
   tree = BPlusTreeMap(capacity=8)

   # Faster for large datasets
   tree = BPlusTreeMap(capacity=128)
   ```

2. **Batch Operations:**

   ```python
   # Slow
   for key, value in large_dataset:
       tree[key] = value

   # Faster
   tree.update(large_dataset)
   ```

### Slow Range Queries

**Diagnosis:**

```python
def diagnose_range_performance():
    tree = BPlusTreeMap()
    tree.update((i, i**2) for i in range(100000))

    # Test different range sizes
    for range_size in [10, 100, 1000, 10000]:
        start_key = 50000
        end_key = start_key + range_size

        start_time = time.perf_counter()
        results = list(tree.items(start_key, end_key))
        duration = time.perf_counter() - start_time

        print(f"Range size {range_size:5d}: "
              f"{duration:.4f}s ({len(results)} items)")

diagnose_range_performance()
```

**Solutions:**

1. **Use Specific Ranges:**

   ```python
   # Slow: iterate all then filter
   results = [(k, v) for k, v in tree.items() if condition(k)]

   # Fast: use range query
   results = list(tree.items(start_key, end_key))
   ```

2. **Early Termination:**
   ```python
   # Process during iteration for early exit
   count = 0
   for key, value in tree.items(start_key, end_key):
       process(key, value)
       count += 1
       if count >= limit:
           break
   ```

## Environment-Specific Issues

### Docker Containers

#### Problem: C extension fails to build in container

**Dockerfile Solution:**

```dockerfile
FROM python:3.11-slim

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install package
COPY requirements.txt .
RUN pip install -r requirements.txt

# Verify installation
RUN python -c "from bplus_tree import BPlusTreeMap, get_implementation; print(get_implementation())"
```

### Jupyter Notebooks

#### Problem: Kernel crashes when using C extension

**Solutions:**

1. **Force Pure Python:**

   ```python
   import os
   os.environ['BPLUSTREE_PURE_PYTHON'] = '1'

   # Restart kernel and reimport
   from bplus_tree import BPlusTreeMap
   ```

2. **Increase Memory Limits:**
   ```bash
   jupyter notebook --NotebookApp.max_buffer_size=1000000000
   ```

### Virtual Environments

#### Problem: Different behavior in virtual environment

**Diagnosis:**

```python
import sys
print("Python executable:", sys.executable)
print("Python path:", sys.path)

import bplus_tree
print("Module location:", bplus_tree.__file__)
print("Implementation:", bplus_tree.get_implementation())
```

**Solutions:**

1. **Clean Install:**

   ```bash
   pip uninstall bplustree
   pip cache purge
   pip install --no-cache-dir bplustree
   ```

2. **Check Dependencies:**
   ```bash
   pip check
   pip list --outdated
   ```

## Common Errors and Solutions

### TypeError: '<' not supported between instances

**Problem:**

```python
tree = BPlusTreeMap()
tree[1] = "number"
tree["a"] = "string"
# TypeError when iterating - can't compare int and str
```

**Solution:**

```python
# Use consistent key types
tree_int = BPlusTreeMap()
tree_int[1] = "number"
tree_int[2] = "another number"

tree_str = BPlusTreeMap()
tree_str["a"] = "string"
tree_str["b"] = "another string"
```

### MemoryError with large datasets

**Solutions:**

1. **Increase Virtual Memory (Linux/Mac):**

   ```bash
   sudo sysctl vm.overcommit_memory=1
   ```

2. **Process in Chunks:**

   ```python
   def process_large_dataset(data, chunk_size=10000):
       tree = BPlusTreeMap(capacity=128)

       for i in range(0, len(data), chunk_size):
           chunk = data[i:i + chunk_size]
           tree.update(chunk)

           # Process this chunk
           yield from tree.items()
           tree.clear()  # Free memory
   ```

### RecursionError in large trees

**Problem:** Deep tree structures causing stack overflow.

**Solutions:**

1. **Increase Capacity:**

   ```python
   # Reduces tree depth
   tree = BPlusTreeMap(capacity=256)
   ```

2. **Increase Recursion Limit:**
   ```python
   import sys
   sys.setrecursionlimit(10000)  # Default is usually 1000
   ```

## Getting Help

### Collecting Debug Information

```python
def collect_debug_info():
    """Collect system and library information."""
    import sys
    import platform

    print("=== System Information ===")
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()}")

    print("\n=== BPlusTree Information ===")
    try:
        from bplus_tree import get_implementation, BPlusTreeMap
        print(f"Implementation: {get_implementation()}")

        tree = BPlusTreeMap()
        if hasattr(tree, 'capacity'):
            print(f"Default capacity: {tree.capacity}")

        print(f"Module location: {tree.__class__.__module__}")
    except Exception as e:
        print(f"Import error: {e}")

    print("\n=== Performance Test ===")
    try:
        tree = BPlusTreeMap()
        import time
        start = time.perf_counter()
        for i in range(1000):
            tree[i] = i
        duration = time.perf_counter() - start
        print(f"1000 insertions: {duration:.4f}s")
    except Exception as e:
        print(f"Performance test failed: {e}")

collect_debug_info()
```

### Filing Bug Reports

Include this information when reporting issues:

1. **System Information** (from `collect_debug_info()` above)
2. **Minimal Reproduction Case:**

   ```python
   from bplus_tree import BPlusTreeMap

   tree = BPlusTreeMap()
   # ... minimal code that reproduces the issue
   ```

3. **Expected vs. Actual Behavior**
4. **Error Messages and Stack Traces**
5. **Installation Method** (pip, conda, source)

### Community Resources

- **GitHub Issues**: https://github.com/KentBeck/BPlusTree/issues
- **Documentation**: See other files in this docs/ directory
- **Examples**: Check the examples/ directory for working code

## Quick Reference

### Performance Checklist

- [ ] Using C extension? (`get_implementation() == "C extension"`)
- [ ] Appropriate capacity for dataset size?
- [ ] Consistent key types?
- [ ] Using range queries instead of filtering?
- [ ] Avoiding unnecessary tree copies?

### Memory Checklist

- [ ] Clearing unused trees with `tree.clear()`?
- [ ] Using integer keys when possible?
- [ ] Appropriate capacity (not too high for small datasets)?
- [ ] Not holding references to deleted items?

### Thread Safety Checklist

- [ ] Using locks for multi-threaded access?
- [ ] Not modifying tree during iteration?
- [ ] Each thread has its own tree instance?
- [ ] Using message passing for coordination?
