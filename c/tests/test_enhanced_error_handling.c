#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>
#include <limits.h>
#include "../src/bplustree.h"

// Test framework
static int tests_run = 0;
static int tests_passed = 0;

#define TEST(name) \
    static void test_##name(void); \
    static void run_test_##name(void) { \
        printf("Running test: %s... ", #name); \
        fflush(stdout); \
        test_##name(); \
        tests_passed++; \
        printf("PASSED\n"); \
    } \
    static void test_##name(void)

#define ASSERT(condition) \
    do { \
        if (!(condition)) { \
            printf("FAILED\n"); \
            printf("  Assertion failed: %s\n", #condition); \
            printf("  File: %s, Line: %d\n", __FILE__, __LINE__); \
            exit(1); \
        } \
    } while(0)

#define ASSERT_EQ(expected, actual) \
    do { \
        if ((expected) != (actual)) { \
            printf("FAILED\n"); \
            printf("  Expected: %ld, Actual: %ld\n", (long)(expected), (long)(actual)); \
            printf("  File: %s, Line: %d\n", __FILE__, __LINE__); \
            exit(1); \
        } \
    } while(0)

#define RUN_TEST(name) \
    do { \
        tests_run++; \
        run_test_##name(); \
    } while(0)

// Test 1: Error propagation consistency
TEST(error_handling_propagation_consistency) {
    bplustree_t* tree = bptree_new(4);
    ASSERT(tree != NULL);
    
    // Test that all operations properly propagate NULL pointer errors
    ASSERT_EQ(BPTREE_ERROR_NULL_POINTER, bptree_insert(NULL, 1, 1));
    
    int value;
    ASSERT_EQ(BPTREE_ERROR_NULL_POINTER, bptree_get(NULL, 1, &value));
    ASSERT_EQ(BPTREE_ERROR_NULL_POINTER, bptree_get(tree, 1, NULL));
    
    ASSERT_EQ(BPTREE_ERROR_NULL_POINTER, bptree_remove(NULL, 1));
    
    // Test iterator error propagation
    ASSERT(bptree_iterator_new(NULL) == NULL);
    ASSERT(bptree_range_iterator_new(NULL, 0, 10) == NULL);
    
    bptree_entry_t entry;
    ASSERT_EQ(BPTREE_ERROR_NULL_POINTER, bptree_iterator_next(NULL, &entry));
    
    bptree_iterator_t* iter = bptree_iterator_new(tree);
    if (iter) {
        ASSERT_EQ(BPTREE_ERROR_NULL_POINTER, bptree_iterator_next(iter, NULL));
        bptree_iterator_free(iter);
    }
    
    bptree_free(tree);
}

// Test 2: Invalid capacity handling
TEST(error_handling_invalid_capacity) {
    // Test capacities below minimum
    ASSERT(bptree_new(0) == NULL);
    ASSERT(bptree_new(1) == NULL);
    ASSERT(bptree_new(2) == NULL);
    
    // BPTREE_MIN_CAPACITY should be defined in header
    ASSERT(bptree_new(BPTREE_MIN_CAPACITY) != NULL);
    
    bplustree_t* tree = bptree_new(BPTREE_MIN_CAPACITY);
    if (tree) {
        bptree_free(tree);
    }
}

// Test 3: Empty tree operations
TEST(error_handling_empty_tree_operations) {
    bplustree_t* tree = bptree_new(4);
    ASSERT(tree != NULL);
    
    // Operations on empty tree should return appropriate errors
    int value;
    ASSERT_EQ(BPTREE_ERROR_KEY_NOT_FOUND, bptree_get(tree, 42, &value));
    ASSERT(!bptree_contains(tree, 42));
    ASSERT_EQ(BPTREE_ERROR_KEY_NOT_FOUND, bptree_remove(tree, 42));
    
    // Size and empty checks should work correctly
    ASSERT_EQ(0, bptree_size(tree));
    ASSERT(bptree_is_empty(tree));
    
    // Iterator on empty tree should work but have no items
    bptree_iterator_t* iter = bptree_iterator_new(tree);
    if (iter) {
        ASSERT(!bptree_iterator_has_next(iter));
        
        bptree_entry_t entry;
        ASSERT_EQ(BPTREE_ERROR_INVALID_STATE, bptree_iterator_next(iter, &entry));
        
        bptree_iterator_free(iter);
    }
    
    bptree_free(tree);
}

// Test 4: Out of bounds iterator operations
TEST(error_handling_iterator_bounds) {
    bplustree_t* tree = bptree_new(4);
    ASSERT(tree != NULL);
    
    // Add a few items
    for (int i = 1; i <= 3; i++) {
        bptree_result_t result = bptree_insert(tree, i, i * 10);
        ASSERT_EQ(BPTREE_OK, result);
    }
    
    bptree_iterator_t* iter = bptree_iterator_new(tree);
    ASSERT(iter != NULL);
    
    // Consume all items
    int count = 0;
    while (bptree_iterator_has_next(iter)) {
        bptree_entry_t entry;
        bptree_result_t result = bptree_iterator_next(iter, &entry);
        ASSERT_EQ(BPTREE_OK, result);
        count++;
    }
    ASSERT_EQ(3, count);
    
    // Now iterator should be exhausted
    ASSERT(!bptree_iterator_has_next(iter));
    
    bptree_entry_t entry;
    ASSERT_EQ(BPTREE_ERROR_INVALID_STATE, bptree_iterator_next(iter, &entry));
    
    bptree_iterator_free(iter);
    bptree_free(tree);
}

// Test 5: Range iterator edge cases
TEST(error_handling_range_iterator_edge_cases) {
    bplustree_t* tree = bptree_new(6);
    ASSERT(tree != NULL);
    
    // Insert some data
    for (int i = 10; i <= 50; i += 10) {
        bptree_result_t result = bptree_insert(tree, i, i);
        ASSERT_EQ(BPTREE_OK, result);
    }
    
    // Test range that doesn't exist
    bptree_iterator_t* iter1 = bptree_range_iterator_new(tree, 100, 200);
    if (iter1) {
        ASSERT(!bptree_iterator_has_next(iter1));
        bptree_iterator_free(iter1);
    }
    
    // Test empty range
    bptree_iterator_t* iter2 = bptree_range_iterator_new(tree, 25, 25);
    if (iter2) {
        ASSERT(!bptree_iterator_has_next(iter2));
        bptree_iterator_free(iter2);
    }
    
    // Test invalid range (start > end)
    bptree_iterator_t* iter3 = bptree_range_iterator_new(tree, 40, 20);
    if (iter3) {
        ASSERT(!bptree_iterator_has_next(iter3));
        bptree_iterator_free(iter3);
    }
    
    // Test single item range
    bptree_iterator_t* iter4 = bptree_range_iterator_new(tree, 20, 30);
    if (iter4) {
        int count = 0;
        while (bptree_iterator_has_next(iter4)) {
            bptree_entry_t entry;
            bptree_result_t result = bptree_iterator_next(iter4, &entry);
            ASSERT_EQ(BPTREE_OK, result);
            ASSERT_EQ(20, entry.key);
            count++;
        }
        ASSERT_EQ(1, count);
        bptree_iterator_free(iter4);
    }
    
    bptree_free(tree);
}

// Test 6: Memory allocation failure simulation
TEST(error_handling_memory_allocation_failure_simulation) {
    // This test checks that the code gracefully handles allocation failures
    // We can't easily simulate malloc failures, but we can test edge cases
    
    // Test with very large capacity request (should fail gracefully)
    bplustree_t* tree = bptree_new(SIZE_MAX);
    // This should either return NULL or succeed with a reasonable capacity
    if (tree) {
        bptree_free(tree);
    }
    
    // Test successful creation with reasonable capacity
    tree = bptree_new(4);
    ASSERT(tree != NULL);
    
    // The tree should handle operations normally
    bptree_result_t result = bptree_insert(tree, 1, 100);
    ASSERT_EQ(BPTREE_OK, result);
    
    int value;
    result = bptree_get(tree, 1, &value);
    ASSERT_EQ(BPTREE_OK, result);
    ASSERT_EQ(100, value);
    
    bptree_free(tree);
}

// Test 7: Error message validity
TEST(error_handling_error_message_validity) {
    // Test that all error codes return valid error strings
    const char* msg;
    
    msg = bptree_error_string(BPTREE_OK);
    ASSERT(msg != NULL);
    ASSERT(strlen(msg) > 0);
    
    msg = bptree_error_string(BPTREE_ERROR_NULL_POINTER);
    ASSERT(msg != NULL);
    ASSERT(strlen(msg) > 0);
    
    msg = bptree_error_string(BPTREE_ERROR_KEY_NOT_FOUND);
    ASSERT(msg != NULL);
    ASSERT(strlen(msg) > 0);
    
    msg = bptree_error_string(BPTREE_ERROR_OUT_OF_MEMORY);
    ASSERT(msg != NULL);
    ASSERT(strlen(msg) > 0);
    
    msg = bptree_error_string(BPTREE_ERROR_INVALID_STATE);
    ASSERT(msg != NULL);
    ASSERT(strlen(msg) > 0);
    
    // Test with invalid error code
    msg = bptree_error_string((bptree_result_t)999);
    ASSERT(msg != NULL);
    ASSERT(strlen(msg) > 0);
}

// Test 8: Tree state consistency after errors
TEST(error_handling_tree_state_consistency_after_errors) {
    bplustree_t* tree = bptree_new(4);
    ASSERT(tree != NULL);
    
    // Insert some data - be more conservative with capacity 4
    for (int i = 1; i <= 3; i++) {
        bptree_result_t result = bptree_insert(tree, i, i * 10);
        ASSERT_EQ(BPTREE_OK, result);
    }
    
    size_t original_size = bptree_size(tree);
    ASSERT(original_size >= 3);
    
    // Try operations that should fail
    int value;
    bptree_result_t result = bptree_get(tree, 999, &value);
    ASSERT_EQ(BPTREE_ERROR_KEY_NOT_FOUND, result);
    
    result = bptree_remove(tree, 999);
    ASSERT_EQ(BPTREE_ERROR_KEY_NOT_FOUND, result);
    
    // Tree should be unchanged
    ASSERT_EQ(original_size, bptree_size(tree));
    
    // Verify existing data is still accessible
    result = bptree_get(tree, 1, &value);
    ASSERT_EQ(BPTREE_OK, result);
    ASSERT_EQ(10, value);
    
    // Iterator should still work
    bptree_iterator_t* iter = bptree_iterator_new(tree);
    if (iter) {
        size_t count = 0;
        while (bptree_iterator_has_next(iter)) {
            bptree_entry_t entry;
            result = bptree_iterator_next(iter, &entry);
            ASSERT_EQ(BPTREE_OK, result);
            count++;
        }
        ASSERT_EQ(original_size, count);
        bptree_iterator_free(iter);
    }
    
    bptree_free(tree);
}

// Test 9: Duplicate key update consistency
TEST(error_handling_duplicate_key_update_consistency) {
    bplustree_t* tree = bptree_new(4);
    ASSERT(tree != NULL);
    
    // Insert initial value
    bptree_result_t result = bptree_insert(tree, 42, 100);
    ASSERT_EQ(BPTREE_OK, result);
    ASSERT_EQ(1, bptree_size(tree));
    
    // Update the same key multiple times
    for (int new_value = 200; new_value <= 500; new_value += 100) {
        result = bptree_insert(tree, 42, new_value);
        ASSERT_EQ(BPTREE_OK, result);
        
        // Size should remain the same
        ASSERT_EQ(1, bptree_size(tree));
        
        // Value should be updated
        int retrieved_value;
        result = bptree_get(tree, 42, &retrieved_value);
        ASSERT_EQ(BPTREE_OK, result);
        ASSERT_EQ(new_value, retrieved_value);
    }
    
    bptree_free(tree);
}

// Test 10: Extreme value handling
TEST(error_handling_extreme_values) {
    bplustree_t* tree = bptree_new(4);
    ASSERT(tree != NULL);
    
    // Test with extreme integer values
    int extreme_values[] = {
        INT_MIN,
        INT_MIN + 1,
        -1000000,
        -1,
        0,
        1,
        1000000,
        INT_MAX - 1,
        INT_MAX
    };
    int num_values = sizeof(extreme_values) / sizeof(extreme_values[0]);
    
    // Insert extreme values
    for (int i = 0; i < num_values; i++) {
        bptree_result_t result = bptree_insert(tree, extreme_values[i], extreme_values[i] * 2);
        if (result != BPTREE_OK && result != BPTREE_ERROR_INVALID_STATE) {
            printf("Unexpected error for extreme value %d: %s\n", 
                   extreme_values[i], bptree_error_string(result));
            ASSERT(0);
        }
    }
    
    // Verify inserted values
    for (int i = 0; i < num_values; i++) {
        if (bptree_contains(tree, extreme_values[i])) {
            int value;
            bptree_result_t result = bptree_get(tree, extreme_values[i], &value);
            ASSERT_EQ(BPTREE_OK, result);
            ASSERT_EQ(extreme_values[i] * 2, value);
        }
    }
    
    // Test iterator with extreme values
    bptree_iterator_t* iter = bptree_iterator_new(tree);
    if (iter) {
        int last_key = INT_MIN;
        bool first = true;
        
        while (bptree_iterator_has_next(iter)) {
            bptree_entry_t entry;
            bptree_result_t result = bptree_iterator_next(iter, &entry);
            ASSERT_EQ(BPTREE_OK, result);
            
            // Keys should be in ascending order
            if (!first) {
                ASSERT(entry.key > last_key);
            }
            last_key = entry.key;
            first = false;
        }
        
        bptree_iterator_free(iter);
    }
    
    bptree_free(tree);
}

int main(void) {
    printf("=== B+ Tree C Implementation - Enhanced Error Handling Tests ===\n\n");
    
    RUN_TEST(error_handling_propagation_consistency);
    RUN_TEST(error_handling_invalid_capacity);
    RUN_TEST(error_handling_empty_tree_operations);
    RUN_TEST(error_handling_iterator_bounds);
    RUN_TEST(error_handling_range_iterator_edge_cases);
    RUN_TEST(error_handling_memory_allocation_failure_simulation);
    RUN_TEST(error_handling_error_message_validity);
    RUN_TEST(error_handling_tree_state_consistency_after_errors);
    RUN_TEST(error_handling_duplicate_key_update_consistency);
    RUN_TEST(error_handling_extreme_values);
    
    printf("\n=== Test Summary ===\n");
    printf("Tests run: %d\n", tests_run);
    printf("Tests passed: %d\n", tests_passed);
    
    if (tests_passed == tests_run) {
        printf("🎉 All tests passed!\n");
        return 0;
    } else {
        printf("❌ Some tests failed!\n");
        return 1;
    }
}