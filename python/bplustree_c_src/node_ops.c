/*
 * B+ Tree Node Operations
 * 
 * Core node operations optimized for performance.
 * Uses vectorized search where possible.
 */

#include "bplustree.h"
#include <string.h>
#include <stdlib.h>

#ifdef _WIN32
#include <malloc.h>
#endif

/* Fast comparison function with type-specific optimizations */
int fast_compare_lt(PyObject *a, PyObject *b) {
    /* Fast path for integers */
    if (PyLong_CheckExact(a) && PyLong_CheckExact(b)) {
        /* For small integers, use direct comparison */
        long val_a = PyLong_AsLong(a);
        long val_b = PyLong_AsLong(b);
        if (!PyErr_Occurred()) {
            return val_a < val_b ? 1 : 0;
        }
        PyErr_Clear(); /* Clear error and fall through */
    }
    
    /* Fast path for strings */
    if (PyUnicode_CheckExact(a) && PyUnicode_CheckExact(b)) {
        int result = PyUnicode_Compare(a, b);
        if (result != -1 || !PyErr_Occurred()) {
            return result < 0 ? 1 : 0;
        }
        PyErr_Clear(); /* Clear error and fall through */
    }
    
    /* Fall back to general comparison */
    return PyObject_RichCompareBool(a, b, Py_LT);
}

/* Fast equality comparison function */
int fast_compare_eq(PyObject *a, PyObject *b) {
    /* Fast path for integers */
    if (PyLong_CheckExact(a) && PyLong_CheckExact(b)) {
        long val_a = PyLong_AsLong(a);
        long val_b = PyLong_AsLong(b);
        if (!PyErr_Occurred()) {
            return val_a == val_b ? 1 : 0;
        }
        PyErr_Clear();
    }
    
    /* Fast path for strings */
    if (PyUnicode_CheckExact(a) && PyUnicode_CheckExact(b)) {
        int result = PyUnicode_Compare(a, b);
        if (result != -1 || !PyErr_Occurred()) {
            return result == 0 ? 1 : 0;
        }
        PyErr_Clear();
    }
    
    /* Fall back to general comparison */
    return PyObject_RichCompareBool(a, b, Py_EQ);
}

/* Binary search to find position for key */
int node_find_position(BPlusNode *node, PyObject *key) {
    int left = 0;
    int right = node->num_keys;
    
    while (left < right) {
        int mid = (left + right) / 2;
        PyObject *mid_key = node_get_key(node, mid);
        
        int result = fast_compare_lt(mid_key, key);
        if (result < 0) {
            return -1;  /* Error in comparison */
        }
        
        if (result) {
            left = mid + 1;
        } else {
            right = mid;
        }
    }
    
    return left;
}

/* Create a new node */
BPlusNode* node_create(NodeType type, uint16_t capacity) {
    size_t data_size;
    
    if (type == NODE_LEAF) {
        data_size = capacity * 2 * sizeof(PyObject*);
    } else {
        data_size = (capacity * 2 + 1) * sizeof(PyObject*);
    }
    
    BPlusNode *node = (BPlusNode*)cache_aligned_alloc(sizeof(BPlusNode) + data_size);
    if (!node) {
        PyErr_NoMemory();
        return NULL;
    }
    
    /* Initialize metadata */
    node->num_keys = 0;
    node->capacity = capacity;
    node->type = type;
    node->_unused = 0;  /* Reserved for future use */
    node->next = NULL;
    
    /* Clear data array */
    memset(node->data, 0, data_size);
    
    return node;
}

/* Destroy a node and decref all Python objects */
void node_destroy(BPlusNode *node) {
    if (!node) return;
    
    /* Decref all keys */
    for (int i = 0; i < node->num_keys; i++) {
        Py_XDECREF(node_get_key(node, i));
    }
    
    if (node->type == NODE_LEAF) {
        /* Decref all values */
        for (int i = 0; i < node->num_keys; i++) {
            Py_XDECREF(node_get_value(node, i));
        }
    } else {
        /* Recursively destroy children */
        for (int i = 0; i <= node->num_keys; i++) {
            BPlusNode *child = node_get_child(node, i);
            if (child) {
                node_destroy(child);
            }
        }
    }
    
    cache_aligned_free(node);
}

/* Clear a single slot: decref or destroy payload and null out key/value or child pointer */
static void node_clear_slot(BPlusNode *node, int i) {
    if (i < 0 || i >= node->capacity) {
        return;  /* Invalid index */
    }
    
    if (node->type == NODE_LEAF) {
        Py_XDECREF(node_get_key(node, i));
        Py_XDECREF(node_get_value(node, i));
        node_set_key(node, i, NULL);
        node_set_value(node, i, NULL);
    } else {
        /* For branch nodes, we only clear during deletion operations
         * where it's safe to destroy the child subtree */
        BPlusNode *child = node_get_child(node, i);
        if (child) {
            node_destroy(child);
        }
        Py_XDECREF(node_get_key(node, i));
        node_set_key(node, i, NULL);
        node_set_child(node, i, NULL);
    }
}

/* Insert into leaf node */
int node_insert_leaf(BPlusNode *node, PyObject *key, PyObject *value, 
                     BPlusNode **new_node, PyObject **split_key) {
    int pos = node_find_position(node, key);
    if (pos < 0) return -1;  /* Comparison error */
    
    /* Check if key already exists */
    if (pos < node->num_keys) {
        PyObject *existing_key = node_get_key(node, pos);
        int cmp = fast_compare_eq(existing_key, key);
        if (cmp < 0) return -1;  /* Comparison error */
        
        if (cmp) {
            /* Update existing value */
            PyObject *old_value = node_get_value(node, pos);
            Py_INCREF(value);
            node_set_value(node, pos, value);
            Py_DECREF(old_value);
            return -2;  /* Special return code for update */
        }
    }
    
    /* Check if split is needed */
    if (node->num_keys >= node->capacity) {
        /* Create new node */
        *new_node = node_create(NODE_LEAF, node->capacity);
        if (!*new_node) return -1;
        
        /* Temporary arrays for redistribution */
        PyObject **temp_keys = PyMem_Malloc((node->capacity + 1) * sizeof(PyObject*));
        PyObject **temp_values = PyMem_Malloc((node->capacity + 1) * sizeof(PyObject*));
        if (!temp_keys || !temp_values) {
            PyMem_Free(temp_keys);
            PyMem_Free(temp_values);
            node_destroy(*new_node);
            PyErr_NoMemory();
            return -1;
        }
        
        /* Copy existing + new into temp arrays */
        int j = 0;
        for (int i = 0; i < pos; i++) {
            temp_keys[j] = node_get_key(node, i);
            temp_values[j] = node_get_value(node, i);
            j++;
        }
        temp_keys[j] = key;
        temp_values[j] = value;
        j++;
        for (int i = pos; i < node->num_keys; i++) {
            temp_keys[j] = node_get_key(node, i);
            temp_values[j] = node_get_value(node, i);
            j++;
        }
        
        /* Split at midpoint - exactly like Python code */
        int mid = node->capacity / 2;  /* Same as Python: self.capacity // 2 */

        /* Keep first half in current node */
        node->num_keys = mid;
        for (int i = 0; i < mid; i++) {
            Py_INCREF(temp_keys[i]);
            Py_INCREF(temp_values[i]);
            node_set_key(node, i, temp_keys[i]);
            node_set_value(node, i, temp_values[i]);
        }

        /* Clear old slots beyond midpoint - DO NOT DECREF as items were moved to temp arrays */
        for (int i = mid; i < node->capacity; i++) {
            node_set_key(node, i, NULL);
            node_set_value(node, i, NULL);
        }

        /* Move second half to new node */
        int total_items = node->capacity + 1;
        (*new_node)->num_keys = total_items - mid;
        for (int i = 0; i < (*new_node)->num_keys; i++) {
            Py_INCREF(temp_keys[mid + i]);
            Py_INCREF(temp_values[mid + i]);
            node_set_key(*new_node, i, temp_keys[mid + i]);
            node_set_value(*new_node, i, temp_values[mid + i]);
        }
        
        /* Update links */
        (*new_node)->next = node->next;
        node->next = *new_node;
        
        /* Flags no longer needed after SIMD removal */
        
        /* Set split key */
        *split_key = node_get_key(*new_node, 0);
        Py_INCREF(*split_key);
        
        /* Clean up temps */
        PyMem_Free(temp_keys);
        PyMem_Free(temp_values);
        
        return 1;  /* Split occurred */
    }
    
    /* Normal insert - shift elements right */
    for (int i = node->num_keys; i > pos; i--) {
        node_set_key(node, i, node_get_key(node, i - 1));
        node_set_value(node, i, node_get_value(node, i - 1));
    }
    
    /* Insert new key-value */
    Py_INCREF(key);
    Py_INCREF(value);
    node_set_key(node, pos, key);
    node_set_value(node, pos, value);
    node->num_keys++;
    
    /* No flag updates needed after SIMD removal */
    
    return 0;  /* No split */
}

/* Delete key from leaf node */
int node_delete(BPlusNode *node, PyObject *key) {
    if (node->type != NODE_LEAF) {
        return 0;  /* Can only delete from leaf nodes directly */
    }
    
    int pos = node_find_position(node, key);
    if (pos < 0) return -1;  /* Comparison error */
    
    /* Check if key exists */
    if (pos >= node->num_keys) {
        return 0;  /* Key not found */
    }
    
    PyObject *found_key = node_get_key(node, pos);
    int cmp = fast_compare_eq(found_key, key);
    if (cmp < 0) return -1;  /* Comparison error */
    if (!cmp) return 0;      /* Key not found */
    
    /* Clear the removed slot */
    node_clear_slot(node, pos);

    /* Shift elements left to fill the gap */
    for (int i = pos; i < node->num_keys - 1; i++) {
        node_set_key(node, i, node_get_key(node, i + 1));
        node_set_value(node, i, node_get_value(node, i + 1));
    }

    /* Clear the last slot */
    node->num_keys--;
    node_set_key(node, node->num_keys, NULL);
    node_set_value(node, node->num_keys, NULL);

    return 1;  /* Successfully deleted */
}

/* Get value from leaf node */
PyObject* node_get(BPlusNode *node, PyObject *key) {
    int pos = node_find_position(node, key);
    if (pos < 0) return NULL;  /* Comparison error */
    
    if (pos < node->num_keys) {
        PyObject *found_key = node_get_key(node, pos);
        int cmp = fast_compare_eq(found_key, key);
        if (cmp < 0) return NULL;  /* Comparison error */
        
        if (cmp) {
            PyObject *value = node_get_value(node, pos);
            Py_INCREF(value);
            return value;
        }
    }
    
    /* Key not found */
    PyErr_SetObject(PyExc_KeyError, key);
    return NULL;
}

/* Cache-aligned memory allocation functions */
void* cache_aligned_alloc(size_t size) {
#ifdef _WIN32
    return _aligned_malloc(size, CACHE_LINE_SIZE);
#else
    void *ptr;
    if (posix_memalign(&ptr, CACHE_LINE_SIZE, size) != 0) {
        return NULL;
    }
    return ptr;
#endif
}

void cache_aligned_free(void* ptr) {
#ifdef _WIN32
    _aligned_free(ptr);
#else
    free(ptr);
#endif
}