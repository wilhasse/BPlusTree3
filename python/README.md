# BPlusTree3 - Python Implementation

A high-performance B+ tree implementation for Python with competitive performance against highly optimized libraries like SortedDict.

## 🚀 Quick Start

### Installation

**Option 1: Install from source (current)**
```bash
git clone https://github.com/KentBeck/BPlusTree3.git
cd BPlusTree3/python
pip install -e .
```

**Option 2: Install from PyPI (coming soon)**
```bash
pip install bplustree3
```

### Requirements
- Python 3.8 or higher
- C compiler (for C extension, optional)

### Implementation Selection
The library automatically selects the best available implementation:
1. **C Extension** (preferred): 2-4x faster, used automatically if available
2. **Pure Python**: Fallback implementation, no compilation required

Check which implementation is being used:
```python
from bplus_tree import get_implementation
print(get_implementation())  # "C extension" or "Pure Python"
```

## 📖 Basic Usage

```python
from bplus_tree import BPlusTreeMap

# Create a B+ tree
tree = BPlusTreeMap(capacity=128)  # Higher capacity = better performance

# Insert data
tree[1] = "one"
tree[3] = "three" 
tree[2] = "two"

# Lookups
print(tree[2])        # "two"
print(len(tree))      # 3
print(2 in tree)      # True

# Range queries
for key, value in tree.range(1, 3):
    print(f"{key}: {value}")

# Iteration
for key, value in tree.items():
    print(f"{key}: {value}")
```

## ⚡ Performance Highlights

Our benchmarks against SortedDict show **significant advantages** in specific scenarios:

### 🏆 **Where B+ Tree Excels**

| Scenario | B+ Tree Advantage | Use Cases |
|----------|------------------|-----------|
| **Partial Range Scans** | **Up to 2.5x faster** | Database LIMIT queries, pagination |
| **Large Dataset Iteration** | **1.1x - 1.4x faster** | Data export, bulk processing |
| **Medium Range Queries** | **1.4x faster** | Time-series analysis, batch processing |

### 📊 **Benchmark Results**

**Partial Range Scans (Early Termination):**
```
Limit  10 items: B+ Tree 1.18x faster
Limit  50 items: B+ Tree 2.50x faster  ⭐ Best performance  
Limit 100 items: B+ Tree 1.52x faster
Limit 500 items: B+ Tree 1.15x faster
```

**Large Dataset Iteration:**
```
200K items: B+ Tree 1.29x faster
300K items: B+ Tree 1.12x faster  
500K items: B+ Tree 1.39x faster  ⭐ Scales well
```

**Optimal Configuration:**
- **Capacity 128** provides best performance (3.3x faster than capacity 4)
- Performance continues improving with larger capacities

## 🎯 **When to Choose B+ Tree**

**Excellent for:**
- Database-like workloads with range queries
- Analytics dashboards ("top 100 users")
- Search systems with pagination  
- Time-series data processing
- Data export and ETL operations
- Any scenario with "LIMIT" or early termination patterns

**Use SortedDict when:**
- Random access dominates (37x faster individual lookups)
- Small datasets (< 100K items)
- Memory efficiency is critical
- General-purpose sorted container needs

## 🔧 Configuration

```python
# Small capacity: More splits, good for testing
tree = BPlusTree(capacity=4)

# Medium capacity: Balanced performance  
tree = BPlusTree(capacity=16)

# Large capacity: Optimal for most use cases
tree = BPlusTree(capacity=128)  # Recommended!
```

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/

# Run performance benchmarks
python tests/test_performance_vs_sorteddict.py

# Run specific tests
python -m pytest tests/test_bplus_tree.py -v
```

## 📖 API Reference

### Basic Operations
```python
tree = BPlusTree(capacity=128)

# Dictionary-like interface
tree[key] = value
value = tree[key]        # Raises KeyError if not found
del tree[key]           # Raises KeyError if not found
key in tree             # Returns bool
len(tree)               # Returns int

# Safe operations
tree.get(key, default=None)
tree.pop(key, default=None) 
```

### Iteration and Ranges
```python
# Full iteration
for key, value in tree.items():
    pass

for key in tree.keys():
    pass
    
for value in tree.values():
    pass

# Range queries
for key, value in tree.range(start_key, end_key):
    pass

# Range with None bounds
for key, value in tree.range(start_key, None):  # From start_key to end
    pass
    
for key, value in tree.range(None, end_key):    # From beginning to end_key
    pass
```

## 🏗️ Architecture

- **Arena-based memory management** for efficiency
- **Linked leaf nodes** for fast sequential access  
- **Optimized rebalancing** algorithms
- **Hybrid navigation** for range queries

## 📚 Documentation & Examples

- **[API Reference](./docs/API_REFERENCE.md)** - Complete API documentation
- **[Examples](./examples/)** - Comprehensive usage examples:
  - [Basic Usage](./examples/basic_usage.py) - Fundamental operations
  - [Range Queries](./examples/range_queries.py) - Range query patterns  
  - [Performance Demo](./examples/performance_demo.py) - Benchmarks vs alternatives
  - [Migration Guide](./examples/migration_guide.py) - Migrating from dict/SortedDict

## 🔗 Links

- [Main Project](../) - Dual Rust/Python implementation
- [Rust Implementation](../rust/) - Core Rust library
- [Technical Documentation](../rust/docs/) - Architecture and benchmarks

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.