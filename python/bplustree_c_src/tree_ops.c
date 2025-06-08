/*
 * B+ Tree Operations
 * 
 * High-level tree operations that coordinate node operations.
 */

#include "bplustree.h"

/* Find leaf node that should contain the key */
/* Find leaf node that should contain the key */
BPlusNode* tree_find_leaf(BPlusTree *tree, PyObject *key) {
    BPlusNode *node = tree->root;
    
    while (node->type == NODE_BRANCH) {
        int pos = node_find_position(node, key);
        if (pos < 0) {
            return NULL;
        }
        /* bisect_right semantics: advance past equal keys */
        if (pos < node->num_keys) {
            PyObject *node_key = node_get_key(node, pos);
            int eq = fast_compare_eq(node_key, key);
            if (eq < 0) {
                return NULL;
            }
            if (eq) {
                pos++;
            }
        }
        {
            node = node_prefetch_child(node, pos);
        }
    }
    
    return node;
}

/* Recursive insert helper */
static int tree_insert_recursive(BPlusNode *node, PyObject *key, PyObject *value,
                                BPlusNode **new_node, PyObject **split_key) {
    if (node->type == NODE_LEAF) {
        return node_insert_leaf(node, key, value, new_node, split_key);
    }
    
    /* Find child to insert into */
    int child_pos = node_find_position(node, key);
    if (child_pos < 0) {
        return -1;
    }
    /* bisect_right semantics: advance past equal keys */
    if (child_pos < node->num_keys) {
        PyObject *node_key = node_get_key(node, child_pos);
        int eq = fast_compare_eq(node_key, key);
        if (eq < 0) {
            return -1;
        }
        if (eq) {
            child_pos++;
        }
    }
    BPlusNode *child = node_get_child(node, child_pos);
    BPlusNode *new_child = NULL;
    PyObject *new_key = NULL;
    
    int result = tree_insert_recursive(child, key, value, &new_child, &new_key);
    if (result < 0) return result;  /* Error or update - propagate as-is */
    if (result == 0) return 0;      /* No split */
    
    /* Child was split, need to insert new_key and new_child into this node */
    return node_insert_branch(node, new_key, new_child, new_node, split_key);
}

/* Insert key-value pair into tree */
int tree_insert(BPlusTree *tree, PyObject *key, PyObject *value) {
    BPlusNode *new_node = NULL;
    PyObject *split_key = NULL;
    
    int result = tree_insert_recursive(tree->root, key, value, &new_node, &split_key);
    if (result == -1) return -1;  /* Error */
    if (result == -2) return 0;   /* Update - don't increment size */
    
    if (result > 0) {
        /* Root was split, create new root */
        BPlusNode *new_root = node_create(NODE_BRANCH, tree->capacity);
        if (!new_root) {
            Py_XDECREF(split_key);
            return -1;
        }
        
        /* Set up new root with old root as first child */
        node_set_child(new_root, 0, tree->root);
        node_set_key(new_root, 0, split_key);
        node_set_child(new_root, 1, new_node);
        new_root->num_keys = 1;
        
        tree->root = new_root;
    }
    
    /* Increment size for new insertions (result == 0 or result > 0) */
    tree->size++;
    
    return 0;
}

/* Delete key from tree */
int tree_delete(BPlusTree *tree, PyObject *key) {
    BPlusNode *leaf = tree_find_leaf(tree, key);
    if (!leaf) return -1;
    
    int result = node_delete(leaf, key);
    if (result == 1) {
        tree->size--;  /* Successfully deleted */
    }
    
    return result;
}

/* Get value for key */
PyObject* tree_get(BPlusTree *tree, PyObject *key) {
    BPlusNode *leaf = tree_find_leaf(tree, key);
    if (!leaf) return NULL;
    return node_get(leaf, key);
}

/* Insert into branch node */
int node_insert_branch(BPlusNode *node, PyObject *key, BPlusNode *right_child,
                       BPlusNode **new_node, PyObject **split_key) {
    int pos = node_find_position(node, key);
    if (pos < 0) return -1;
    
    /* Check if split is needed */
    if (node->num_keys >= node->capacity) {
        /* Create new node */
        *new_node = node_create(NODE_BRANCH, node->capacity);
        if (!*new_node) return -1;
        
        /* Temporary arrays for redistribution */
        PyObject **temp_keys = PyMem_Malloc((node->capacity + 1) * sizeof(PyObject*));
        BPlusNode **temp_children = PyMem_Malloc((node->capacity + 2) * sizeof(BPlusNode*));
        if (!temp_keys || !temp_children) {
            PyMem_Free(temp_keys);
            PyMem_Free(temp_children);
            node_destroy(*new_node);
            PyErr_NoMemory();
            return -1;
        }
        
        /* Copy existing + new into temp arrays */
        temp_children[0] = node_get_child(node, 0);
        
        int j = 0;
        for (int i = 0; i < pos; i++) {
            temp_keys[j] = node_get_key(node, i);
            temp_children[j + 1] = node_get_child(node, i + 1);
            j++;
        }
        temp_keys[j] = key;
        temp_children[j + 1] = right_child;
        j++;
        for (int i = pos; i < node->num_keys; i++) {
            temp_keys[j] = node_get_key(node, i);
            temp_children[j + 1] = node_get_child(node, i + 1);
            j++;
        }
        
        /* Split at midpoint */
        int mid = node->capacity / 2;
        *split_key = temp_keys[mid];
        Py_INCREF(*split_key);
        
        /* Keep first half in current node */
        node->num_keys = mid;
        for (int i = 0; i < mid; i++) {
            Py_INCREF(temp_keys[i]);
            node_set_key(node, i, temp_keys[i]);
        }
        for (int i = 0; i <= mid; i++) {
            node_set_child(node, i, temp_children[i]);
        }
        
        /* Move second half to new node */
        (*new_node)->num_keys = node->capacity - mid;
        for (int i = 0; i < (*new_node)->num_keys; i++) {
            Py_INCREF(temp_keys[mid + 1 + i]);
            node_set_key(*new_node, i, temp_keys[mid + 1 + i]);
        }
        for (int i = 0; i <= (*new_node)->num_keys; i++) {
            node_set_child(*new_node, i, temp_children[mid + 1 + i]);
        }
        
        /* Clean up temps */
        PyMem_Free(temp_keys);
        PyMem_Free(temp_children);
        
        return 1;  /* Split occurred */
    }
    
    /* Normal insert - shift elements right */
    for (int i = node->num_keys; i > pos; i--) {
        node_set_key(node, i, node_get_key(node, i - 1));
        node_set_child(node, i + 1, node_get_child(node, i));
    }
    
    /* Insert new key and child */
    Py_INCREF(key);
    node_set_key(node, pos, key);
    node_set_child(node, pos + 1, right_child);
    node->num_keys++;
    
    return 0;  /* No split */
}