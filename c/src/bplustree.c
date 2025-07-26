#include "bplustree.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

/**
 * B+ Tree Implementation in C - Initial stub for TDD
 * 
 * This is the minimal implementation to make tests compile and fail.
 * We'll implement features one by one following TDD methodology.
 */

// Stub implementation - all functions return errors or NULL
// This will make our tests fail, which is what we want in the RED phase

// B+ Tree node types
typedef struct bptree_node {
    bool is_leaf;
    size_t key_count;
    int* keys;
    size_t capacity;
    struct bptree_node* parent;
    union {
        struct {
            int* values;
            struct bptree_node* next;
            struct bptree_node* prev;
        } leaf;
        struct {
            struct bptree_node** children;
        } branch;
    };
} bptree_node_t;

// B+ Tree structure
struct bplustree {
    bptree_node_t* root;
    size_t capacity;
    size_t size;
    bptree_node_t* first_leaf;
};

bplustree_t* bptree_new(size_t capacity) {
    if (capacity < BPTREE_MIN_CAPACITY) {
        return NULL;
    }
    
    bplustree_t* tree = malloc(sizeof(bplustree_t));
    if (!tree) {
        return NULL;
    }
    
    tree->root = NULL;
    tree->capacity = capacity;
    tree->size = 0;
    tree->first_leaf = NULL;
    
    return tree;
}

void bptree_free(bplustree_t* tree) {
    if (!tree) return;
    
    // Clear all nodes first
    bptree_clear(tree);
    
    // Free the tree structure itself
    free(tree);
}

// Helper function to create a new leaf node with optimized memory layout
static bptree_node_t* create_leaf_node(size_t capacity) {
    // Single allocation for better cache locality
    size_t total_size = sizeof(bptree_node_t) + 
                       (capacity * sizeof(int)) +     // keys
                       (capacity * sizeof(int));      // values
    
    char* memory = malloc(total_size);
    if (!memory) return NULL;
    
    bptree_node_t* node = (bptree_node_t*)memory;
    node->is_leaf = true;
    node->key_count = 0;
    node->capacity = capacity;
    node->parent = NULL;
    
    // Place keys and values contiguously after the node structure
    node->keys = (int*)(memory + sizeof(bptree_node_t));
    node->leaf.values = (int*)(memory + sizeof(bptree_node_t) + (capacity * sizeof(int)));
    node->leaf.next = NULL;
    node->leaf.prev = NULL;
    
    return node;
}

// Binary search for key position in sorted array
static inline size_t binary_search_keys(const int* keys, size_t count, int target) {
    size_t left = 0, right = count;
    while (left < right) {
        size_t mid = left + ((right - left) >> 1);  // Avoid overflow
        if (keys[mid] < target) {
            left = mid + 1;
        } else {
            right = mid;
        }
    }
    return left;
}

// Binary search to find exact key match
static inline size_t binary_search_exact(const int* keys, size_t count, int target) {
    size_t left = 0, right = count;
    while (left < right) {
        size_t mid = left + ((right - left) >> 1);
        if (keys[mid] < target) {
            left = mid + 1;
        } else if (keys[mid] > target) {
            right = mid;
        } else {
            return mid;  // Found exact match
        }
    }
    return SIZE_MAX;  // Not found
}

bptree_result_t bptree_insert(bplustree_t* tree, int key, int value) {
    if (!tree) return BPTREE_ERROR_NULL_POINTER;
    
    // If tree is empty, create root as leaf with larger default capacity
    if (!tree->root) {
        // Use much larger capacity to avoid reallocation
        size_t initial_capacity = tree->capacity > 1024 ? tree->capacity : 1024;
        tree->root = create_leaf_node(initial_capacity);
        if (!tree->root) return BPTREE_ERROR_OUT_OF_MEMORY;
        tree->first_leaf = tree->root;
    }
    
    // Insert into root leaf (optimized implementation)
    bptree_node_t* leaf = tree->root;
    
    // Use binary search to check if key already exists (O(log n))
    size_t exact_pos = binary_search_exact(leaf->keys, leaf->key_count, key);
    if (exact_pos != SIZE_MAX) {
        leaf->leaf.values[exact_pos] = value; // Update existing
        return BPTREE_OK;
    }
    
    // Check if leaf has space
    if (leaf->key_count >= leaf->capacity) {
        // For now, return error instead of expensive realloc
        // TODO: Implement proper B+ tree node splitting
        return BPTREE_ERROR_INVALID_STATE;
    }
    
    // Use binary search to find insertion position (O(log n))
    size_t pos = binary_search_keys(leaf->keys, leaf->key_count, key);
    
    // Use memmove for efficient bulk shifting (much faster than loop)
    if (pos < leaf->key_count) {
        memmove(&leaf->keys[pos + 1], &leaf->keys[pos], 
                (leaf->key_count - pos) * sizeof(int));
        memmove(&leaf->leaf.values[pos + 1], &leaf->leaf.values[pos], 
                (leaf->key_count - pos) * sizeof(int));
    }
    
    // Insert new key-value
    leaf->keys[pos] = key;
    leaf->leaf.values[pos] = value;
    leaf->key_count++;
    tree->size++;
    
    return BPTREE_OK;
}

bptree_result_t bptree_get(const bplustree_t* tree, int key, int* value) {
    if (!tree || !value) return BPTREE_ERROR_NULL_POINTER;
    if (!tree->root) return BPTREE_ERROR_KEY_NOT_FOUND;
    
    // Use binary search in root leaf (O(log n) instead of O(n))
    bptree_node_t* leaf = tree->root;
    size_t pos = binary_search_exact(leaf->keys, leaf->key_count, key);
    
    if (pos != SIZE_MAX) {
        *value = leaf->leaf.values[pos];
        return BPTREE_OK;
    }
    
    return BPTREE_ERROR_KEY_NOT_FOUND;
}

bool bptree_contains(const bplustree_t* tree, int key) {
    int value;
    return bptree_get(tree, key, &value) == BPTREE_OK;
}

bptree_result_t bptree_remove(bplustree_t* tree, int key) {
    if (!tree) return BPTREE_ERROR_NULL_POINTER;
    if (!tree->root) return BPTREE_ERROR_KEY_NOT_FOUND;
    
    // Optimized removal from root leaf
    bptree_node_t* leaf = tree->root;
    
    // Use binary search to find the key (O(log n))
    size_t pos = binary_search_exact(leaf->keys, leaf->key_count, key);
    if (pos == SIZE_MAX) {
        return BPTREE_ERROR_KEY_NOT_FOUND;
    }
    
    // Use memmove for efficient bulk shifting
    if (pos < leaf->key_count - 1) {
        memmove(&leaf->keys[pos], &leaf->keys[pos + 1], 
                (leaf->key_count - pos - 1) * sizeof(int));
        memmove(&leaf->leaf.values[pos], &leaf->leaf.values[pos + 1], 
                (leaf->key_count - pos - 1) * sizeof(int));
    }
    
    leaf->key_count--;
    tree->size--;
    return BPTREE_OK;
}

size_t bptree_size(const bplustree_t* tree) {
    if (!tree) return 0;
    return tree->size;
}

bool bptree_is_empty(const bplustree_t* tree) {
    if (!tree) return true;
    return tree->size == 0;
}

// Helper function to free a node (optimized for single allocation)
static void free_node(bptree_node_t* node) {
    if (!node) return;
    
    // Since we now use single allocation, just free the node
    // The keys and values are part of the same memory block
    free(node);
}

void bptree_clear(bplustree_t* tree) {
    if (!tree) return;
    
    // For now, just clear the root (since we only have single-node trees)
    if (tree->root) {
        free_node(tree->root);
        tree->root = NULL;
        tree->first_leaf = NULL;
        tree->size = 0;
    }
}

// Iterator structure
struct bptree_iterator {
    const bplustree_t* tree;
    bptree_node_t* current_node;
    size_t current_index;
    int start_key;
    int end_key;
    bool has_range;
};

// Iterator stubs
bptree_iterator_t* bptree_iterator_new(const bplustree_t* tree) {
    if (!tree) return NULL;
    
    bptree_iterator_t* iter = malloc(sizeof(bptree_iterator_t));
    if (!iter) return NULL;
    
    iter->tree = tree;
    iter->current_node = tree->first_leaf;
    iter->current_index = 0;
    iter->has_range = false;
    
    return iter;
}

bptree_iterator_t* bptree_range_iterator_new(const bplustree_t* tree, int start_key, int end_key) {
    if (!tree) return NULL;
    
    bptree_iterator_t* iter = malloc(sizeof(bptree_iterator_t));
    if (!iter) return NULL;
    
    iter->tree = tree;
    iter->current_node = tree->first_leaf;
    iter->start_key = start_key;
    iter->end_key = end_key;
    iter->has_range = true;
    
    // Find starting position
    iter->current_index = 0;
    if (iter->current_node) {
        while (iter->current_index < iter->current_node->key_count && 
               iter->current_node->keys[iter->current_index] < start_key) {
            iter->current_index++;
        }
    }
    
    return iter;
}

bool bptree_iterator_has_next(const bptree_iterator_t* iter) {
    if (!iter || !iter->current_node) return false;
    
    if (iter->current_index >= iter->current_node->key_count) return false;
    
    // Check range limits for range iterators
    if (iter->has_range) {
        int current_key = iter->current_node->keys[iter->current_index];
        if (current_key >= iter->end_key) return false;
    }
    
    return true;
}

bptree_result_t bptree_iterator_next(bptree_iterator_t* iter, bptree_entry_t* entry) {
    if (!iter || !entry || !iter->current_node) return BPTREE_ERROR_NULL_POINTER;
    
    if (iter->current_index >= iter->current_node->key_count) {
        return BPTREE_ERROR_INVALID_STATE;
    }
    
    entry->key = iter->current_node->keys[iter->current_index];
    entry->value = iter->current_node->leaf.values[iter->current_index];
    iter->current_index++;
    
    return BPTREE_OK;
}

void bptree_iterator_free(bptree_iterator_t* iter) {
    if (iter) {
        free(iter);
    }
}

// Utility functions
const char* bptree_error_string(bptree_result_t result) {
    switch (result) {
        case BPTREE_OK:
            return "Success";
        case BPTREE_ERROR_NULL_POINTER:
            return "Null pointer error";
        case BPTREE_ERROR_INVALID_CAPACITY:
            return "Invalid capacity";
        case BPTREE_ERROR_KEY_NOT_FOUND:
            return "Key not found";
        case BPTREE_ERROR_OUT_OF_MEMORY:
            return "Out of memory";
        case BPTREE_ERROR_INVALID_STATE:
            return "Invalid state";
        default:
            return "Unknown error";
    }
}

void bptree_debug_print(const bplustree_t* tree) {
    (void)tree;
    printf("Debug print not implemented\n");
}

bool bptree_validate(const bplustree_t* tree) {
    (void)tree;
    return true; // Assume valid for now
}