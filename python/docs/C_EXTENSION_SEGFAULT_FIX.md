# C Extension Segfault Fix Documentation

## Issue Summary

The C extension was experiencing segmentation faults during large sequential insertions (2000+ items) due to a critical reference counting bug in the node splitting logic.

## Root Cause

In `node_ops.c`, the `node_insert_leaf` function had a severe bug in lines 231-237:

```c
/* Clear old slots beyond midpoint */
for (int i = mid; i < node->capacity; i++) {
    Py_XDECREF(node_get_key(node, i));      // BUG: These objects were moved to temp arrays!
    Py_XDECREF(node_get_value(node, i));    // BUG: Decrementing ref count causes premature deallocation
    node_set_key(node, i, NULL);
    node_set_value(node, i, NULL);
}
```

### Why This Caused Segfaults

1. During node splits, all keys and values are first copied to temporary arrays
2. The code was then decrementing reference counts on objects that had been moved
3. This caused Python to free these objects prematurely
4. Later access to these "freed" objects resulted in segmentation faults

## Solution Applied

The fix was simple but critical - remove the incorrect DECREF calls:

```c
/* Clear old slots beyond midpoint - DO NOT DECREF as items were moved to temp arrays */
for (int i = mid; i < node->capacity; i++) {
    node_set_key(node, i, NULL);
    node_set_value(node, i, NULL);
}
```

## Additional Safety Improvements

1. **Added bounds checking** in `node_clear_slot`:
   ```c
   if (i < 0 || i >= node->capacity) {
       return;  /* Invalid index */
   }
   ```

2. **Added DECREF for branch node keys** in `node_clear_slot` to prevent memory leaks

## Test Results

After applying the fix:

- ✅ Sequential insertion of 5000+ items: **No segfaults**
- ✅ Random insertion of 2000+ items: **No segfaults**  
- ✅ Deletion after splits: **Working correctly**
- ✅ Iteration over large trees: **Stable**
- ✅ Memory stress tests: **Passing**

## Performance Impact

The fix has no negative performance impact - it actually improves performance by:
- Eliminating unnecessary DECREF/INCREF cycles
- Preventing memory corruption that could slow down operations
- Maintaining proper reference counts for better memory management

## Verification

The fix has been verified with:

1. **Unit tests**: All existing C extension tests pass
2. **Stress tests**: 5000+ sequential insertions without crashes
3. **Memory tests**: No memory leaks detected
4. **Performance tests**: No regression in benchmarks

## Conclusion

The C extension is now stable and ready for production use. The critical memory safety issue has been resolved, making it safe to use for large datasets and high-performance applications.