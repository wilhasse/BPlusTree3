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

// Helper function to create a new branch node
static bptree_node_t* create_branch_node(size_t capacity) {
    // Single allocation for better cache locality
    size_t total_size = sizeof(bptree_node_t) +
                       (capacity * sizeof(int)) +                    // keys
                       ((capacity + 1) * sizeof(bptree_node_t*));    // children (capacity + 1)

    char* memory = malloc(total_size);
    if (!memory) return NULL;

    bptree_node_t* node = (bptree_node_t*)memory;
    node->is_leaf = false;
    node->key_count = 0;
    node->capacity = capacity;
    node->parent = NULL;

    // Place keys and children contiguously after the node structure
    node->keys = (int*)(memory + sizeof(bptree_node_t));
    node->branch.children = (bptree_node_t**)(memory + sizeof(bptree_node_t) + (capacity * sizeof(int)));

    return node;
}

// Helper function to free a node (optimized for single allocation)
static void free_node(bptree_node_t* node) {
    if (!node) return;

    // Since we now use single allocation, just free the node
    // The keys and values are part of the same memory block
    free(node);
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

// Split a full leaf node and return the new right node
static bptree_node_t* split_leaf_node(bptree_node_t* left_leaf) {
    if (!left_leaf || !left_leaf->is_leaf) return NULL;

    // Create new right leaf
    bptree_node_t* right_leaf = create_leaf_node(left_leaf->capacity);
    if (!right_leaf) return NULL;

    // Calculate split point (middle)
    size_t split_point = left_leaf->capacity / 2;
    size_t right_count = left_leaf->key_count - split_point;

    // Copy right half to new node
    memcpy(right_leaf->keys, &left_leaf->keys[split_point], right_count * sizeof(int));
    memcpy(right_leaf->leaf.values, &left_leaf->leaf.values[split_point], right_count * sizeof(int));
    right_leaf->key_count = right_count;

    // Update left node count
    left_leaf->key_count = split_point;

    // Update linked list pointers
    right_leaf->leaf.next = left_leaf->leaf.next;
    right_leaf->leaf.prev = left_leaf;
    if (left_leaf->leaf.next) {
        left_leaf->leaf.next->leaf.prev = right_leaf;
    }
    left_leaf->leaf.next = right_leaf;

    // Set parent (will be updated by caller)
    right_leaf->parent = left_leaf->parent;

    return right_leaf;
}

bptree_result_t bptree_insert(bplustree_t* tree, int key, int value) {
    if (!tree) return BPTREE_ERROR_NULL_POINTER;

    // If tree is empty, create root as leaf with specified capacity
    if (!tree->root) {
        tree->root = create_leaf_node(tree->capacity);
        if (!tree->root) return BPTREE_ERROR_OUT_OF_MEMORY;
        tree->first_leaf = tree->root;
    }

    // Navigate to the correct leaf node
    bptree_node_t* current = tree->root;
    while (!current->is_leaf) {
        size_t pos = binary_search_keys(current->keys, current->key_count, key);
        if (pos < current->key_count && current->keys[pos] == key) {
            pos++; // Go to right child if key exists
        }
        current = current->branch.children[pos];
    }

    bptree_node_t* leaf = current;

    // Use binary search to check if key already exists (O(log n))
    size_t exact_pos = binary_search_exact(leaf->keys, leaf->key_count, key);
    if (exact_pos != SIZE_MAX) {
        leaf->leaf.values[exact_pos] = value; // Update existing
        return BPTREE_OK;
    }
    
    // Check if leaf has space
    if (leaf->key_count >= leaf->capacity) {
        // Need to split the leaf
        bptree_node_t* right_leaf = split_leaf_node(leaf);
        if (!right_leaf) return BPTREE_ERROR_OUT_OF_MEMORY;

        // If this was the root, create new root
        if (!leaf->parent) {
            bptree_node_t* new_root = create_branch_node(tree->capacity);
            if (!new_root) {
                free_node(right_leaf);
                return BPTREE_ERROR_OUT_OF_MEMORY;
            }

            // Set up new root
            new_root->keys[0] = right_leaf->keys[0];
            new_root->branch.children[0] = leaf;
            new_root->branch.children[1] = right_leaf;
            new_root->key_count = 1;

            // Update parent pointers
            leaf->parent = new_root;
            right_leaf->parent = new_root;

            // Update tree root
            tree->root = new_root;
        } else {
            // Insert the split key into the parent branch node
            bptree_node_t* parent = leaf->parent;
            int split_key = right_leaf->keys[0];
            
            // Check if parent has space (should handle branch splits too, but simplified for now)
            if (parent->key_count >= parent->capacity) {
                // For now, return error - proper branch splitting would be needed here
                free_node(right_leaf);
                return BPTREE_ERROR_INVALID_STATE;
            }
            
            // Find position to insert the split key in parent
            size_t insert_pos = 0;
            for (size_t i = 0; i < parent->key_count; i++) {
                if (split_key < parent->keys[i]) {
                    insert_pos = i;
                    break;
                }
                insert_pos = i + 1;
            }
            
            // Shift keys and children to make space
            if (insert_pos < parent->key_count) {
                memmove(&parent->keys[insert_pos + 1], &parent->keys[insert_pos],
                        (parent->key_count - insert_pos) * sizeof(int));
                memmove(&parent->branch.children[insert_pos + 2], &parent->branch.children[insert_pos + 1],
                        (parent->key_count - insert_pos) * sizeof(bptree_node_t*));
            }
            
            // Insert the split key and right child
            parent->keys[insert_pos] = split_key;
            parent->branch.children[insert_pos + 1] = right_leaf;
            parent->key_count++;
            
            // Set parent for the new right leaf
            right_leaf->parent = parent;
        }

        // After splitting, we need to navigate again to find the correct leaf
        // because the tree structure has changed
        bptree_node_t* current = tree->root;
        while (!current->is_leaf) {
            size_t pos = binary_search_keys(current->keys, current->key_count, key);
            if (pos < current->key_count && current->keys[pos] == key) {
                pos++; // Go to right child if key exists
            }
            current = current->branch.children[pos];
        }
        leaf = current;
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
    
    // Navigate to leaf node
    bptree_node_t* current = tree->root;
    while (!current->is_leaf) {
        size_t pos = binary_search_keys(current->keys, current->key_count, key);
        if (pos < current->key_count && current->keys[pos] == key) {
            pos++; // Go to right child if key exists
        }
        current = current->branch.children[pos];
    }
    
    // Search in leaf
    size_t pos = binary_search_exact(current->keys, current->key_count, key);
    if (pos != SIZE_MAX) {
        *value = current->leaf.values[pos];
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

    // For now, implement simple removal for single-node trees only
    bptree_node_t* leaf = tree->root;
    if (!leaf->is_leaf) {
        // TODO: Implement removal for multi-level trees
        return BPTREE_ERROR_INVALID_STATE;
    }

    // Find the key using binary search
    size_t pos = binary_search_exact(leaf->keys, leaf->key_count, key);
    if (pos == SIZE_MAX) {
        return BPTREE_ERROR_KEY_NOT_FOUND;
    }

    // Remove the key by shifting elements left
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

// Helper function to recursively free all nodes
static void free_subtree(bptree_node_t* node) {
    if (!node) return;

    if (!node->is_leaf) {
        // Free all children first
        for (size_t i = 0; i <= node->key_count; i++) {
            free_subtree(node->branch.children[i]);
        }
    }

    free_node(node);
}

void bptree_clear(bplustree_t* tree) {
    if (!tree) return;

    if (tree->root) {
        free_subtree(tree->root);
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
    iter->start_key = start_key;
    iter->end_key = end_key;
    iter->has_range = true;
    
    // Find starting leaf
    iter->current_node = tree->first_leaf;
    iter->current_index = 0;
    
    // Skip to start_key
    while (iter->current_node && iter->current_index < iter->current_node->key_count) {
        if (iter->current_node->keys[iter->current_index] >= start_key) {
            break;
        }
        iter->current_index++;
        if (iter->current_index >= iter->current_node->key_count) {
            iter->current_node = iter->current_node->leaf.next;
            iter->current_index = 0;
        }
    }
    
    return iter;
}

bool bptree_iterator_has_next(const bptree_iterator_t* iter) {
    if (!iter || !iter->current_node) return false;
    
    if (iter->current_index >= iter->current_node->key_count) return false;
    
    if (iter->has_range) {
        return iter->current_node->keys[iter->current_index] < iter->end_key;
    }
    
    return true;
}

bptree_result_t bptree_iterator_next(bptree_iterator_t* iter, bptree_entry_t* entry) {
    if (!iter || !entry) return BPTREE_ERROR_NULL_POINTER;
    if (!bptree_iterator_has_next(iter)) return BPTREE_ERROR_INVALID_STATE;
    
    entry->key = iter->current_node->keys[iter->current_index];
    entry->value = iter->current_node->leaf.values[iter->current_index];
    
    // Advance iterator
    iter->current_index++;
    if (iter->current_index >= iter->current_node->key_count) {
        iter->current_node = iter->current_node->leaf.next;
        iter->current_index = 0;
    }
    
    return BPTREE_OK;
}

void bptree_iterator_free(bptree_iterator_t* iter) {
    free(iter);
}

// Utility functions
const char* bptree_error_string(bptree_result_t result) {
    switch (result) {
        case BPTREE_OK: return "Success";
        case BPTREE_ERROR_NULL_POINTER: return "Null pointer error";
        case BPTREE_ERROR_KEY_NOT_FOUND: return "Key not found";
        case BPTREE_ERROR_OUT_OF_MEMORY: return "Out of memory";
        case BPTREE_ERROR_INVALID_STATE: return "Invalid state";
        default: return "Unknown error";
    }
}

static void print_node(bptree_node_t* node, int depth) {
    if (!node) return;

    for (int i = 0; i < depth; i++) printf("  ");

    if (node->is_leaf) {
        printf("Leaf[%zu]: ", node->key_count);
        for (size_t i = 0; i < node->key_count; i++) {
            printf("%d ", node->keys[i]);
        }
        printf("\n");
    } else {
        printf("Branch[%zu]: ", node->key_count);
        for (size_t i = 0; i < node->key_count; i++) {
            printf("%d ", node->keys[i]);
        }
        printf("\n");

        // Print children
        for (size_t i = 0; i <= node->key_count; i++) {
            print_node(node->branch.children[i], depth + 1);
        }
    }
}

void bptree_debug_print(const bplustree_t* tree) {
    if (!tree) {
        printf("Tree is NULL\n");
        return;
    }

    printf("Tree size: %zu, capacity: %zu\n", tree->size, tree->capacity);

    if (!tree->root) {
        printf("Root is NULL\n");
        return;
    }

    print_node(tree->root, 0);
}

bool bptree_validate(const bplustree_t* tree) {
    (void)tree;
    return true; // Assume valid for now
}
