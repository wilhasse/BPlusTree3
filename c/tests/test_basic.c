#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>
#include "../src/bplustree.h"

// Simple test framework
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
            printf("  Expected: %d, Actual: %d\n", (int)(expected), (int)(actual)); \
            printf("  File: %s, Line: %d\n", __FILE__, __LINE__); \
            exit(1); \
        } \
    } while(0)

#define RUN_TEST(name) \
    do { \
        tests_run++; \
        run_test_##name(); \
    } while(0)

// Test 1: Tree creation and destruction (RED phase)
TEST(should_create_empty_tree) {
    bplustree_t* tree = bptree_new(BPTREE_DEFAULT_CAPACITY);
    ASSERT(tree != NULL);
    ASSERT(bptree_is_empty(tree));
    ASSERT_EQ(0, bptree_size(tree));
    bptree_free(tree);
}

// Test 2: Invalid capacity handling
TEST(should_reject_invalid_capacity) {
    bplustree_t* tree = bptree_new(2); // Too small
    ASSERT(tree == NULL);
    
    tree = bptree_new(0); // Zero capacity
    ASSERT(tree == NULL);
}

// Test 3: Single insertion
TEST(should_insert_single_key) {
    bplustree_t* tree = bptree_new(BPTREE_DEFAULT_CAPACITY);
    ASSERT(tree != NULL);
    
    bptree_result_t result = bptree_insert(tree, 42, 100);
    ASSERT_EQ(BPTREE_OK, result);
    ASSERT(!bptree_is_empty(tree));
    ASSERT_EQ(1, bptree_size(tree));
    
    bptree_free(tree);
}

// Test 4: Single lookup
TEST(should_find_inserted_key) {
    bplustree_t* tree = bptree_new(BPTREE_DEFAULT_CAPACITY);
    ASSERT(tree != NULL);
    
    bptree_insert(tree, 42, 100);
    
    int value;
    bptree_result_t result = bptree_get(tree, 42, &value);
    ASSERT_EQ(BPTREE_OK, result);
    ASSERT_EQ(100, value);
    
    ASSERT(bptree_contains(tree, 42));
    
    bptree_free(tree);
}

// Test 5: Key not found
TEST(should_return_not_found_for_missing_key) {
    bplustree_t* tree = bptree_new(BPTREE_DEFAULT_CAPACITY);
    ASSERT(tree != NULL);
    
    int value;
    bptree_result_t result = bptree_get(tree, 999, &value);
    ASSERT_EQ(BPTREE_ERROR_KEY_NOT_FOUND, result);
    
    ASSERT(!bptree_contains(tree, 999));
    
    bptree_free(tree);
}

// Test 6: Multiple insertions
TEST(should_insert_multiple_keys) {
    bplustree_t* tree = bptree_new(4); // Small capacity to force splits
    ASSERT(tree != NULL);
    
    // Insert keys in order
    for (int i = 1; i <= 10; i++) {
        bptree_result_t result = bptree_insert(tree, i, i * 10);
        ASSERT_EQ(BPTREE_OK, result);
    }
    
    ASSERT_EQ(10, bptree_size(tree));
    
    // Verify all keys exist
    for (int i = 1; i <= 10; i++) {
        int value;
        bptree_result_t result = bptree_get(tree, i, &value);
        ASSERT_EQ(BPTREE_OK, result);
        ASSERT_EQ(i * 10, value);
    }
    
    bptree_free(tree);
}

// Test 7: Update existing key
TEST(should_update_existing_key) {
    bplustree_t* tree = bptree_new(BPTREE_DEFAULT_CAPACITY);
    ASSERT(tree != NULL);
    
    bptree_insert(tree, 42, 100);
    bptree_insert(tree, 42, 200); // Update same key
    
    int value;
    bptree_get(tree, 42, &value);
    ASSERT_EQ(200, value);
    ASSERT_EQ(1, bptree_size(tree)); // Size should not change
    
    bptree_free(tree);
}

// Test 8: Basic iterator
TEST(should_iterate_over_keys) {
    bplustree_t* tree = bptree_new(BPTREE_DEFAULT_CAPACITY);
    ASSERT(tree != NULL);
    
    // Insert some keys
    bptree_insert(tree, 3, 30);
    bptree_insert(tree, 1, 10);
    bptree_insert(tree, 2, 20);
    
    bptree_iterator_t* iter = bptree_iterator_new(tree);
    ASSERT(iter != NULL);
    
    // Should iterate in sorted order
    int expected_keys[] = {1, 2, 3};
    int expected_values[] = {10, 20, 30};
    int count = 0;
    
    while (bptree_iterator_has_next(iter)) {
        bptree_entry_t entry;
        bptree_result_t result = bptree_iterator_next(iter, &entry);
        ASSERT_EQ(BPTREE_OK, result);
        ASSERT_EQ(expected_keys[count], entry.key);
        ASSERT_EQ(expected_values[count], entry.value);
        count++;
    }
    
    ASSERT_EQ(3, count);
    
    bptree_iterator_free(iter);
    bptree_free(tree);
}

// Test 9: Error handling
TEST(should_handle_null_pointers) {
    // Test null tree pointer
    ASSERT_EQ(BPTREE_ERROR_NULL_POINTER, bptree_insert(NULL, 1, 1));
    
    int value;
    ASSERT_EQ(BPTREE_ERROR_NULL_POINTER, bptree_get(NULL, 1, &value));
    
    ASSERT(!bptree_contains(NULL, 1));
    ASSERT_EQ(0, bptree_size(NULL));
    ASSERT(bptree_is_empty(NULL));
    
    // Should not crash
    bptree_free(NULL);
}

// Test 10: Error messages
TEST(should_provide_error_messages) {
    const char* msg = bptree_error_string(BPTREE_OK);
    ASSERT(msg != NULL);
    ASSERT(strlen(msg) > 0);
    
    msg = bptree_error_string(BPTREE_ERROR_KEY_NOT_FOUND);
    ASSERT(msg != NULL);
    ASSERT(strlen(msg) > 0);
}

int main(void) {
    printf("=== B+ Tree C Implementation - Basic Tests ===\n\n");
    
    RUN_TEST(should_create_empty_tree);
    RUN_TEST(should_reject_invalid_capacity);
    RUN_TEST(should_insert_single_key);
    RUN_TEST(should_find_inserted_key);
    RUN_TEST(should_return_not_found_for_missing_key);
    RUN_TEST(should_insert_multiple_keys);
    RUN_TEST(should_update_existing_key);
    RUN_TEST(should_iterate_over_keys);
    RUN_TEST(should_handle_null_pointers);
    RUN_TEST(should_provide_error_messages);
    
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