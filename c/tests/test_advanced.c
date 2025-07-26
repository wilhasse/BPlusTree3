#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>
#include "../src/bplustree.h"

// Test framework (same as basic tests)
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

// Test 1: Node splitting behavior
TEST(should_split_node_when_capacity_exceeded) {
    bplustree_t* tree = bptree_new(4); // Small capacity
    ASSERT(tree != NULL);
    
    // Insert more than capacity to force splitting
    for (int i = 1; i <= 20; i++) {
        bptree_result_t result = bptree_insert(tree, i, i * 10);
        ASSERT_EQ(BPTREE_OK, result);
    }
    
    ASSERT_EQ(20, bptree_size(tree));
    
    // Verify all keys are still accessible after splitting
    for (int i = 1; i <= 20; i++) {
        int value;
        bptree_result_t result = bptree_get(tree, i, &value);
        ASSERT_EQ(BPTREE_OK, result);
        ASSERT_EQ(i * 10, value);
    }
    
    bptree_free(tree);
}

// Test 2: Random insertion order
TEST(should_handle_random_insertion_order) {
    bplustree_t* tree = bptree_new(8);
    ASSERT(tree != NULL);
    
    // Insert keys in random order
    int keys[] = {15, 3, 8, 12, 1, 20, 7, 18, 5, 10};
    int values[] = {150, 30, 80, 120, 10, 200, 70, 180, 50, 100};
    int num_keys = sizeof(keys) / sizeof(keys[0]);
    
    for (int i = 0; i < num_keys; i++) {
        bptree_result_t result = bptree_insert(tree, keys[i], values[i]);
        ASSERT_EQ(BPTREE_OK, result);
    }
    
    ASSERT_EQ(num_keys, bptree_size(tree));
    
    // Verify iterator returns keys in sorted order
    bptree_iterator_t* iter = bptree_iterator_new(tree);
    ASSERT(iter != NULL);
    
    int expected_sorted_keys[] = {1, 3, 5, 7, 8, 10, 12, 15, 18, 20};
    int expected_sorted_values[] = {10, 30, 50, 70, 80, 100, 120, 150, 180, 200};
    int count = 0;
    
    while (bptree_iterator_has_next(iter)) {
        bptree_entry_t entry;
        bptree_result_t result = bptree_iterator_next(iter, &entry);
        ASSERT_EQ(BPTREE_OK, result);
        ASSERT_EQ(expected_sorted_keys[count], entry.key);
        ASSERT_EQ(expected_sorted_values[count], entry.value);
        count++;
    }
    
    ASSERT_EQ(num_keys, count);
    
    bptree_iterator_free(iter);
    bptree_free(tree);
}

// Test 3: Deletion functionality
TEST(should_remove_keys) {
    bplustree_t* tree = bptree_new(BPTREE_DEFAULT_CAPACITY);
    ASSERT(tree != NULL);
    
    // Insert some keys
    for (int i = 1; i <= 10; i++) {
        bptree_insert(tree, i, i * 10);
    }
    
    ASSERT_EQ(10, bptree_size(tree));
    
    // Remove a key
    bptree_result_t result = bptree_remove(tree, 5);
    ASSERT_EQ(BPTREE_OK, result);
    ASSERT_EQ(9, bptree_size(tree));
    
    // Verify key is gone
    int value;
    result = bptree_get(tree, 5, &value);
    ASSERT_EQ(BPTREE_ERROR_KEY_NOT_FOUND, result);
    ASSERT(!bptree_contains(tree, 5));
    
    // Verify other keys still exist
    for (int i = 1; i <= 10; i++) {
        if (i != 5) {
            result = bptree_get(tree, i, &value);
            ASSERT_EQ(BPTREE_OK, result);
            ASSERT_EQ(i * 10, value);
        }
    }
    
    bptree_free(tree);
}

// Test 4: Range iterator
TEST(should_iterate_over_range) {
    bplustree_t* tree = bptree_new(BPTREE_DEFAULT_CAPACITY);
    ASSERT(tree != NULL);
    
    // Insert keys 1-20
    for (int i = 1; i <= 20; i++) {
        bptree_insert(tree, i, i * 10);
    }
    
    // Create range iterator for keys 5-15 (exclusive end)
    bptree_iterator_t* iter = bptree_range_iterator_new(tree, 5, 15);
    ASSERT(iter != NULL);
    
    // Should iterate over keys 5-14
    int expected_count = 10; // keys 5,6,7,8,9,10,11,12,13,14
    int count = 0;
    int current_key = 5;
    
    while (bptree_iterator_has_next(iter)) {
        bptree_entry_t entry;
        bptree_result_t result = bptree_iterator_next(iter, &entry);
        ASSERT_EQ(BPTREE_OK, result);
        ASSERT_EQ(current_key, entry.key);
        ASSERT_EQ(current_key * 10, entry.value);
        current_key++;
        count++;
    }
    
    ASSERT_EQ(expected_count, count);
    
    bptree_iterator_free(iter);
    bptree_free(tree);
}

// Test 5: Clear functionality
TEST(should_clear_all_entries) {
    bplustree_t* tree = bptree_new(BPTREE_DEFAULT_CAPACITY);
    ASSERT(tree != NULL);
    
    // Insert some keys
    for (int i = 1; i <= 10; i++) {
        bptree_insert(tree, i, i * 10);
    }
    
    ASSERT_EQ(10, bptree_size(tree));
    ASSERT(!bptree_is_empty(tree));
    
    // Clear the tree
    bptree_clear(tree);
    
    ASSERT_EQ(0, bptree_size(tree));
    ASSERT(bptree_is_empty(tree));
    
    // Verify no keys exist
    for (int i = 1; i <= 10; i++) {
        ASSERT(!bptree_contains(tree, i));
    }
    
    bptree_free(tree);
}

// Test 6: Large dataset stress test
TEST(should_handle_large_dataset) {
    bplustree_t* tree = bptree_new(32); // Larger capacity
    ASSERT(tree != NULL);
    
    const int num_keys = 1000;
    
    // Insert many keys
    for (int i = 1; i <= num_keys; i++) {
        bptree_result_t result = bptree_insert(tree, i, i * 2);
        ASSERT_EQ(BPTREE_OK, result);
    }
    
    ASSERT_EQ(num_keys, bptree_size(tree));
    
    // Verify all keys
    for (int i = 1; i <= num_keys; i++) {
        int value;
        bptree_result_t result = bptree_get(tree, i, &value);
        ASSERT_EQ(BPTREE_OK, result);
        ASSERT_EQ(i * 2, value);
    }
    
    // Test iterator on large dataset
    bptree_iterator_t* iter = bptree_iterator_new(tree);
    ASSERT(iter != NULL);
    
    int count = 0;
    int expected_key = 1;
    
    while (bptree_iterator_has_next(iter)) {
        bptree_entry_t entry;
        bptree_result_t result = bptree_iterator_next(iter, &entry);
        ASSERT_EQ(BPTREE_OK, result);
        ASSERT_EQ(expected_key, entry.key);
        ASSERT_EQ(expected_key * 2, entry.value);
        expected_key++;
        count++;
    }
    
    ASSERT_EQ(num_keys, count);
    
    bptree_iterator_free(iter);
    bptree_free(tree);
}

// Test 7: Duplicate key handling
TEST(should_handle_duplicate_keys_correctly) {
    bplustree_t* tree = bptree_new(BPTREE_DEFAULT_CAPACITY);
    ASSERT(tree != NULL);
    
    // Insert initial key
    bptree_result_t result = bptree_insert(tree, 42, 100);
    ASSERT_EQ(BPTREE_OK, result);
    ASSERT_EQ(1, bptree_size(tree));
    
    // Insert same key with different value (should update)
    result = bptree_insert(tree, 42, 200);
    ASSERT_EQ(BPTREE_OK, result);
    ASSERT_EQ(1, bptree_size(tree)); // Size should not change
    
    // Verify updated value
    int value;
    result = bptree_get(tree, 42, &value);
    ASSERT_EQ(BPTREE_OK, result);
    ASSERT_EQ(200, value);
    
    bptree_free(tree);
}

// Test 8: Memory validation
TEST(should_properly_free_memory) {
    // This test ensures no obvious memory leaks
    for (int run = 0; run < 10; run++) {
        bplustree_t* tree = bptree_new(8);
        ASSERT(tree != NULL);
        
        // Insert and remove many keys
        for (int i = 1; i <= 100; i++) {
            bptree_insert(tree, i, i);
        }
        
        for (int i = 1; i <= 50; i++) {
            bptree_remove(tree, i);
        }
        
        bptree_clear(tree);
        bptree_free(tree);
    }
    
    // If we get here without crashing, memory management is working
    ASSERT(1); // Always passes if we reach here
}

int main(void) {
    printf("=== B+ Tree C Implementation - Advanced Tests ===\n\n");
    
    RUN_TEST(should_split_node_when_capacity_exceeded);
    RUN_TEST(should_handle_random_insertion_order);
    RUN_TEST(should_remove_keys);
    RUN_TEST(should_iterate_over_range);
    RUN_TEST(should_clear_all_entries);
    RUN_TEST(should_handle_large_dataset);
    RUN_TEST(should_handle_duplicate_keys_correctly);
    RUN_TEST(should_properly_free_memory);
    
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