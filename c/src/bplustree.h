#ifndef BPLUSTREE_H
#define BPLUSTREE_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

/**
 * B+ Tree Implementation in C
 * 
 * High-performance B+ tree with arena-based memory management,
 * following the same design principles as the Rust implementation.
 */

// Forward declarations
typedef struct bplustree bplustree_t;
typedef struct bptree_iterator bptree_iterator_t;

// Key-value pair for iteration
typedef struct {
    int key;
    int value;
} bptree_entry_t;

// Result types for error handling
typedef enum {
    BPTREE_OK = 0,
    BPTREE_ERROR_NULL_POINTER,
    BPTREE_ERROR_INVALID_CAPACITY,
    BPTREE_ERROR_KEY_NOT_FOUND,
    BPTREE_ERROR_OUT_OF_MEMORY,
    BPTREE_ERROR_INVALID_STATE
} bptree_result_t;

// Configuration constants
#define BPTREE_MIN_CAPACITY 4
#define BPTREE_DEFAULT_CAPACITY 16

/**
 * Create a new B+ tree with specified capacity.
 * 
 * @param capacity Maximum number of keys per node (minimum 4)
 * @return Pointer to new B+ tree, or NULL on error
 */
bplustree_t* bptree_new(size_t capacity);

/**
 * Free a B+ tree and all associated memory.
 * 
 * @param tree Pointer to B+ tree to free
 */
void bptree_free(bplustree_t* tree);

/**
 * Insert a key-value pair into the tree.
 * 
 * @param tree Pointer to B+ tree
 * @param key Key to insert
 * @param value Value to associate with key
 * @return BPTREE_OK on success, error code on failure
 */
bptree_result_t bptree_insert(bplustree_t* tree, int key, int value);

/**
 * Get the value associated with a key.
 * 
 * @param tree Pointer to B+ tree
 * @param key Key to look up
 * @param value Pointer to store the found value
 * @return BPTREE_OK if found, BPTREE_ERROR_KEY_NOT_FOUND if not found
 */
bptree_result_t bptree_get(const bplustree_t* tree, int key, int* value);

/**
 * Check if a key exists in the tree.
 * 
 * @param tree Pointer to B+ tree
 * @param key Key to check
 * @return true if key exists, false otherwise
 */
bool bptree_contains(const bplustree_t* tree, int key);

/**
 * Remove a key-value pair from the tree.
 * 
 * @param tree Pointer to B+ tree
 * @param key Key to remove
 * @return BPTREE_OK if removed, BPTREE_ERROR_KEY_NOT_FOUND if not found
 */
bptree_result_t bptree_remove(bplustree_t* tree, int key);

/**
 * Get the number of key-value pairs in the tree.
 * 
 * @param tree Pointer to B+ tree
 * @return Number of entries, or 0 if tree is NULL
 */
size_t bptree_size(const bplustree_t* tree);

/**
 * Check if the tree is empty.
 * 
 * @param tree Pointer to B+ tree
 * @return true if empty or NULL, false otherwise
 */
bool bptree_is_empty(const bplustree_t* tree);

/**
 * Clear all entries from the tree.
 * 
 * @param tree Pointer to B+ tree
 */
void bptree_clear(bplustree_t* tree);

// Iterator functions

/**
 * Create an iterator for the entire tree.
 * 
 * @param tree Pointer to B+ tree
 * @return Pointer to iterator, or NULL on error
 */
bptree_iterator_t* bptree_iterator_new(const bplustree_t* tree);

/**
 * Create an iterator for a range of keys.
 * 
 * @param tree Pointer to B+ tree
 * @param start_key Start of range (inclusive)
 * @param end_key End of range (exclusive)
 * @return Pointer to iterator, or NULL on error
 */
bptree_iterator_t* bptree_range_iterator_new(const bplustree_t* tree, int start_key, int end_key);

/**
 * Check if iterator has more elements.
 * 
 * @param iter Pointer to iterator
 * @return true if more elements available, false otherwise
 */
bool bptree_iterator_has_next(const bptree_iterator_t* iter);

/**
 * Get the next key-value pair from iterator.
 * 
 * @param iter Pointer to iterator
 * @param entry Pointer to store the next entry
 * @return BPTREE_OK if entry retrieved, error code otherwise
 */
bptree_result_t bptree_iterator_next(bptree_iterator_t* iter, bptree_entry_t* entry);

/**
 * Free an iterator.
 * 
 * @param iter Pointer to iterator to free
 */
void bptree_iterator_free(bptree_iterator_t* iter);

// Utility functions

/**
 * Get a human-readable error message.
 * 
 * @param result Error code
 * @return String description of error
 */
const char* bptree_error_string(bptree_result_t result);

/**
 * Print tree structure for debugging.
 * 
 * @param tree Pointer to B+ tree
 */
void bptree_debug_print(const bplustree_t* tree);

/**
 * Validate tree invariants (debug builds only).
 * 
 * @param tree Pointer to B+ tree
 * @return true if tree is valid, false otherwise
 */
bool bptree_validate(const bplustree_t* tree);

#endif // BPLUSTREE_H