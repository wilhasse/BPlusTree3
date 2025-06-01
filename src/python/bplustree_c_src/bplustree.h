/*
 * B+ Tree C Extension Header
 * 
 * Optimized C structures for high-performance B+ tree operations.
 * Uses single array layout for better cache locality.
 */

#ifndef BPLUSTREE_H
#define BPLUSTREE_H

#include <Python.h>
#include <stdint.h>
#include <stdbool.h>

/* Cache optimization support */
#ifdef __GNUC__
    #define LIKELY(x)   __builtin_expect(!!(x), 1)
    #define UNLIKELY(x) __builtin_expect(!!(x), 0)
    #define PREFETCH(addr, rw, locality) __builtin_prefetch(addr, rw, locality)
#else
    #define LIKELY(x)   (x)
    #define UNLIKELY(x) (x)
    #define PREFETCH(addr, rw, locality) ((void)0)
#endif

/* Configuration constants */
#define DEFAULT_CAPACITY 8
#define MIN_CAPACITY 4
#define CACHE_LINE_SIZE 64

/* Node types */
typedef enum {
    NODE_LEAF = 0,
    NODE_BRANCH = 1
} NodeType;

/* Forward declarations */
typedef struct BPlusNode BPlusNode;
typedef struct BPlusTree BPlusTree;

/* 
 * Single array node structure optimized for cache locality.
 * Layout: [metadata][keys...][values/children...]
 * 
 * For leaf nodes: keys[0:capacity], values[capacity:capacity*2]
 * For branch nodes: keys[0:capacity], children[capacity:capacity*2+1]
 */
typedef struct BPlusNode {
    /* Metadata (fits in single cache line) */
    uint16_t num_keys;          /* Number of keys currently in node */
    uint16_t capacity;          /* Maximum keys this node can hold */
    NodeType type;              /* Leaf or branch node */
    uint8_t _unused;            /* Reserved for future use */
    uint8_t _padding[2];        /* Alignment padding */
    
    /* Links */
    struct BPlusNode *next;     /* Next leaf (for leaf nodes only) */
    
    /* Flexible array member for keys and values/children */
    /* Actual size allocated: capacity * 2 * sizeof(PyObject*) for leaves */
    /*                        (capacity * 2 + 1) * sizeof(PyObject*) for branches */
    PyObject *data[];
} BPlusNode;

/* B+ Tree structure */
typedef struct BPlusTree {
    PyObject_HEAD               /* Python object header */
    BPlusNode *root;           /* Root node */
    BPlusNode *leaves;         /* Leftmost leaf (for iteration) */
    uint16_t capacity;         /* Node capacity */
    uint16_t min_keys;         /* Minimum keys per node (capacity/2) */
    size_t size;               /* Total number of key-value pairs */
    
} BPlusTree;

/* Inline functions for fast array access */
static inline PyObject* node_get_key(BPlusNode *node, int index) {
    return node->data[index];
}

static inline PyObject* node_get_value(BPlusNode *node, int index) {
    return node->data[node->capacity + index];
}

static inline BPlusNode* node_get_child(BPlusNode *node, int index) {
    return (BPlusNode*)node->data[node->capacity + index];
}

static inline void node_set_key(BPlusNode *node, int index, PyObject *key) {
    node->data[index] = key;
}

static inline void node_set_value(BPlusNode *node, int index, PyObject *value) {
    node->data[node->capacity + index] = value;
}

static inline void node_set_child(BPlusNode *node, int index, BPlusNode *child) {
    node->data[node->capacity + index] = (PyObject*)child;
}

/* Function prototypes */

/* Fast comparison functions */
int fast_compare_lt(PyObject *a, PyObject *b);
int fast_compare_eq(PyObject *a, PyObject *b);

/* Cache optimization functions */
void* cache_aligned_alloc(size_t size);
void cache_aligned_free(void* ptr);

/* Node creation and destruction */
BPlusNode* node_create(NodeType type, uint16_t capacity);
void node_destroy(BPlusNode *node);

/* Node operations */
int node_find_position(BPlusNode *node, PyObject *key);
int node_insert_leaf(BPlusNode *node, PyObject *key, PyObject *value, 
                     BPlusNode **new_node, PyObject **split_key);
int node_insert_branch(BPlusNode *node, PyObject *key, BPlusNode *right_child,
                       BPlusNode **new_node, PyObject **split_key);
int node_delete(BPlusNode *node, PyObject *key);
PyObject* node_get(BPlusNode *node, PyObject *key);

/* Tree operations */
int tree_insert(BPlusTree *tree, PyObject *key, PyObject *value);
int tree_delete(BPlusTree *tree, PyObject *key);
PyObject* tree_get(BPlusTree *tree, PyObject *key);
BPlusNode* tree_find_leaf(BPlusTree *tree, PyObject *key);

/* Memory pool operations (removed) */

/* Utility functions */
void node_split_leaf(BPlusNode *node, BPlusNode *new_node);
void node_split_branch(BPlusNode *node, BPlusNode *new_node, PyObject **promoted_key);
int node_redistribute(BPlusNode *left, BPlusNode *right, PyObject *separator);
int node_merge(BPlusNode *left, BPlusNode *right, PyObject *separator);

/* Python C API functions */
PyObject* BPlusTree_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
int BPlusTree_init(BPlusTree *self, PyObject *args, PyObject *kwds);
void BPlusTree_dealloc(BPlusTree *self);
PyObject* BPlusTree_getitem(BPlusTree *self, PyObject *key);
int BPlusTree_setitem(BPlusTree *self, PyObject *key, PyObject *value);
int BPlusTree_delitem(BPlusTree *self, PyObject *key);
Py_ssize_t BPlusTree_length(BPlusTree *self);
int BPlusTree_contains(BPlusTree *self, PyObject *key);

#endif /* BPLUSTREE_H */