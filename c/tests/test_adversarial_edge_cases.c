#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>
#include <limits.h>
#include "../src/bplustree.h"

// Test framework (same as other tests)
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

// Test 1: Root collapse infinite loop attack
TEST(adversarial_root_collapse_infinite_loop_attack) {
    bplustree_t* tree = bptree_new(8);
    ASSERT(tree != NULL);
    
    // Insert many keys to create a multi-level tree
    for (int i = 0; i < 64; i++) {
        bptree_result_t result = bptree_insert(tree, i, i * 100);
        ASSERT_EQ(BPTREE_OK, result);
    }
    
    ASSERT_EQ(64, bptree_size(tree));
    
    // Delete in a pattern that forces repeated root collapses
    for (int i = 63; i >= 0; i--) {
        if (i % 8 != 0) {
            bptree_result_t result = bptree_remove(tree, i);
            ASSERT_EQ(BPTREE_OK, result);
        }
    }
    
    // Tree should still be functional
    ASSERT_EQ(8, bptree_size(tree));
    
    // Verify remaining keys
    for (int i = 0; i < 64; i += 8) {
        ASSERT(bptree_contains(tree, i));
        int value;
        bptree_result_t result = bptree_get(tree, i, &value);
        ASSERT_EQ(BPTREE_OK, result);
        ASSERT_EQ(i * 100, value);
    }
    
    bptree_free(tree);
}

// Test 2: Minimum capacity edge cases
TEST(adversarial_minimum_capacity_edge_cases) {
    // Test with minimum possible capacity
    bplustree_t* tree = bptree_new(BPTREE_MIN_CAPACITY);
    ASSERT(tree != NULL);
    
    // Insert exactly enough keys to trigger multiple levels
    int max_keys = BPTREE_MIN_CAPACITY * BPTREE_MIN_CAPACITY + BPTREE_MIN_CAPACITY;
    
    for (int i = 0; i < max_keys; i++) {
        bptree_result_t result = bptree_insert(tree, i, i * 2);
        ASSERT_EQ(BPTREE_OK, result);
    }
    
    ASSERT_EQ(max_keys, bptree_size(tree));
    
    // Test iteration in order
    bptree_iterator_t* iter = bptree_iterator_new(tree);
    ASSERT(iter != NULL);
    
    int count = 0;
    int expected_key = 0;
    while (bptree_iterator_has_next(iter)) {
        bptree_entry_t entry;
        bptree_result_t result = bptree_iterator_next(iter, &entry);
        ASSERT_EQ(BPTREE_OK, result);
        ASSERT_EQ(expected_key, entry.key);
        ASSERT_EQ(expected_key * 2, entry.value);
        expected_key++;
        count++;
    }
    
    ASSERT_EQ(max_keys, count);
    bptree_iterator_free(iter);
    bptree_free(tree);
}

// Test 3: Odd capacity arithmetic edge cases
TEST(adversarial_odd_capacity_arithmetic_edge_cases) {
    // Test with odd capacity to stress arithmetic
    bplustree_t* tree = bptree_new(7); // Odd capacity
    ASSERT(tree != NULL);
    
    // Insert in reverse order to stress rebalancing
    for (int i = 100; i >= 1; i--) {
        bptree_result_t result = bptree_insert(tree, i, i * 3);
        ASSERT_EQ(BPTREE_OK, result);
    }
    
    ASSERT_EQ(100, bptree_size(tree));
    
    // Delete every third element to create gaps
    for (int i = 3; i <= 100; i += 3) {
        bptree_result_t result = bptree_remove(tree, i);
        ASSERT_EQ(BPTREE_OK, result);
    }
    
    size_t remaining = 100 - 33; // 33 elements divisible by 3
    ASSERT_EQ(remaining, bptree_size(tree));
    
    // Verify iteration still works correctly
    bptree_iterator_t* iter = bptree_iterator_new(tree);
    ASSERT(iter != NULL);
    
    int count = 0;
    int last_key = 0;
    while (bptree_iterator_has_next(iter)) {
        bptree_entry_t entry;
        bptree_result_t result = bptree_iterator_next(iter, &entry);
        ASSERT_EQ(BPTREE_OK, result);
        
        // Keys should be in ascending order
        ASSERT(entry.key > last_key);
        last_key = entry.key;
        
        // Key should not be divisible by 3
        ASSERT(entry.key % 3 != 0);
        
        count++;
    }
    
    ASSERT_EQ(remaining, count);
    bptree_iterator_free(iter);
    bptree_free(tree);
}

// Test 4: Sequential key exhaustion patterns
TEST(adversarial_sequential_key_exhaustion_patterns) {
    bplustree_t* tree = bptree_new(5);
    ASSERT(tree != NULL);
    
    // Pattern 1: Insert ascending, delete descending
    for (int i = 1; i <= 50; i++) {
        bptree_result_t result = bptree_insert(tree, i, i * 10);
        ASSERT_EQ(BPTREE_OK, result);
    }
    
    for (int i = 50; i >= 26; i--) {
        bptree_result_t result = bptree_remove(tree, i);
        ASSERT_EQ(BPTREE_OK, result);
    }
    
    ASSERT_EQ(25, bptree_size(tree));
    
    // Pattern 2: Insert gaps, then fill them
    for (int i = 51; i <= 75; i += 2) {
        bptree_result_t result = bptree_insert(tree, i, i * 10);
        ASSERT_EQ(BPTREE_OK, result);
    }
    
    for (int i = 52; i <= 74; i += 2) {
        bptree_result_t result = bptree_insert(tree, i, i * 10);
        ASSERT_EQ(BPTREE_OK, result);
    }
    
    // Verify all keys 1-25 and 51-75 exist
    for (int i = 1; i <= 25; i++) {
        ASSERT(bptree_contains(tree, i));
    }
    for (int i = 51; i <= 75; i++) {
        ASSERT(bptree_contains(tree, i));
    }
    
    ASSERT_EQ(50, bptree_size(tree));
    bptree_free(tree);
}

// Test 5: Extreme boundary value insertions
TEST(adversarial_extreme_boundary_value_insertions) {
    bplustree_t* tree = bptree_new(4);
    ASSERT(tree != NULL);
    
    // Test with extreme integer values
    int extreme_keys[] = {
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
    int num_keys = sizeof(extreme_keys) / sizeof(extreme_keys[0]);
    
    // Insert in random order
    int insert_order[] = {4, 8, 0, 6, 2, 7, 1, 5, 3};
    
    for (int i = 0; i < num_keys; i++) {
        int key = extreme_keys[insert_order[i]];
        bptree_result_t result = bptree_insert(tree, key, key / 2);
        ASSERT_EQ(BPTREE_OK, result);
    }
    
    ASSERT_EQ(num_keys, bptree_size(tree));
    
    // Verify iteration returns keys in sorted order
    bptree_iterator_t* iter = bptree_iterator_new(tree);
    ASSERT(iter != NULL);
    
    int count = 0;
    int last_key = INT_MIN;
    bool first = true;
    
    while (bptree_iterator_has_next(iter)) {
        bptree_entry_t entry;
        bptree_result_t result = bptree_iterator_next(iter, &entry);
        ASSERT_EQ(BPTREE_OK, result);
        
        if (!first) {
            ASSERT(entry.key > last_key);
        }
        last_key = entry.key;
        first = false;
        count++;
    }
    
    ASSERT_EQ(num_keys, count);
    bptree_iterator_free(iter);
    bptree_free(tree);
}

// Test 6: Pathological split cascade patterns
TEST(adversarial_pathological_split_cascade_patterns) {
    bplustree_t* tree = bptree_new(4);
    ASSERT(tree != NULL);
    
    // Create a scenario that forces cascading splits
    // Insert keys that will cause maximum split cascading
    for (int round = 0; round < 5; round++) {
        int base = round * 100;
        
        // Insert in a pattern that maximizes split propagation
        for (int i = 0; i < 20; i++) {
            int key = base + (i * 13) % 20; // Pseudo-random pattern
            bptree_result_t result = bptree_insert(tree, key, key * 7);
            ASSERT_EQ(BPTREE_OK, result);
        }
    }
    
    ASSERT_EQ(100, bptree_size(tree));
    
    // Verify all keys are accessible
    for (int round = 0; round < 5; round++) {
        int base = round * 100;
        for (int i = 0; i < 20; i++) {
            int key = base + (i * 13) % 20;
            int value;
            bptree_result_t result = bptree_get(tree, key, &value);
            ASSERT_EQ(BPTREE_OK, result);
            ASSERT_EQ(key * 7, value);
        }
    }
    
    bptree_free(tree);
}

// Test 7: Iterator invalidation stress test
TEST(adversarial_iterator_invalidation_stress_test) {
    bplustree_t* tree = bptree_new(6);
    ASSERT(tree != NULL);
    
    // Insert initial data
    for (int i = 0; i < 30; i++) {
        bptree_result_t result = bptree_insert(tree, i, i * 5);
        ASSERT_EQ(BPTREE_OK, result);
    }
    
    // Create iterator and partially consume it
    bptree_iterator_t* iter = bptree_iterator_new(tree);
    ASSERT(iter != NULL);
    
    // Consume first 10 entries
    for (int i = 0; i < 10; i++) {
        ASSERT(bptree_iterator_has_next(iter));
        bptree_entry_t entry;
        bptree_result_t result = bptree_iterator_next(iter, &entry);
        ASSERT_EQ(BPTREE_OK, result);
        ASSERT_EQ(i, entry.key);
    }
    
    // Modify tree structure (should not crash iterator)
    for (int i = 100; i < 120; i++) {
        bptree_result_t result = bptree_insert(tree, i, i * 5);
        ASSERT_EQ(BPTREE_OK, result);
    }
    
    // Continue iteration (may skip some elements due to modifications)
    int remaining_count = 0;
    while (bptree_iterator_has_next(iter)) {
        bptree_entry_t entry;
        bptree_result_t result = bptree_iterator_next(iter, &entry);
        ASSERT_EQ(BPTREE_OK, result);
        remaining_count++;
    }
    
    // Should have seen some remaining elements
    ASSERT(remaining_count > 0);
    
    bptree_iterator_free(iter);
    bptree_free(tree);
}

// Test 8: Memory pressure simulation
TEST(adversarial_memory_pressure_simulation) {
    // Create many small trees to stress memory allocation
    const int num_trees = 100;
    bplustree_t* trees[num_trees];
    
    // Create trees
    for (int t = 0; t < num_trees; t++) {
        trees[t] = bptree_new(4 + (t % 8)); // Varying capacities
        ASSERT(trees[t] != NULL);
        
        // Add some data to each tree
        for (int i = 0; i < 10; i++) {
            int key = t * 1000 + i;
            bptree_result_t result = bptree_insert(trees[t], key, key * 2);
            ASSERT_EQ(BPTREE_OK, result);
        }
    }
    
    // Randomly access trees to stress memory
    for (int access = 0; access < 1000; access++) {
        int tree_idx = access % num_trees;
        int key = tree_idx * 1000 + (access % 10);
        
        int value;
        bptree_result_t result = bptree_get(trees[tree_idx], key, &value);
        ASSERT_EQ(BPTREE_OK, result);
        ASSERT_EQ(key * 2, value);
    }
    
    // Clean up
    for (int t = 0; t < num_trees; t++) {
        bptree_free(trees[t]);
    }
}

// Test 9: Duplicate key update patterns
TEST(adversarial_duplicate_key_update_patterns) {
    bplustree_t* tree = bptree_new(5);
    ASSERT(tree != NULL);
    
    // Insert initial keys
    for (int i = 0; i < 20; i++) {
        bptree_result_t result = bptree_insert(tree, i, i);
        ASSERT_EQ(BPTREE_OK, result);
    }
    
    // Pattern 1: Update every key multiple times
    for (int round = 1; round <= 5; round++) {
        for (int i = 0; i < 20; i++) {
            bptree_result_t result = bptree_insert(tree, i, i * round);
            ASSERT_EQ(BPTREE_OK, result);
        }
        
        // Size should remain constant
        ASSERT_EQ(20, bptree_size(tree));
        
        // Verify values were updated
        for (int i = 0; i < 20; i++) {
            int value;
            bptree_result_t result = bptree_get(tree, i, &value);
            ASSERT_EQ(BPTREE_OK, result);
            ASSERT_EQ(i * round, value);
        }
    }
    
    bptree_free(tree);
}

// Test 10: Range query boundary attack
TEST(adversarial_range_query_boundary_attack) {
    bplustree_t* tree = bptree_new(6);
    ASSERT(tree != NULL);
    
    // Insert keys with gaps to stress range queries
    for (int i = 0; i < 100; i += 5) {
        bptree_result_t result = bptree_insert(tree, i, i * 10);
        ASSERT_EQ(BPTREE_OK, result);
    }
    
    // Test edge case ranges
    struct {
        int start, end;
        int expected_count;
    } test_cases[] = {
        {0, 5, 1},      // Single element
        {0, 6, 2},      // Two elements
        {-10, 0, 0},    // Before range
        {100, 110, 0},  // After range
        {-10, 110, 20}, // Entire range
        {47, 53, 2},    // Mid-range
        {48, 52, 1},    // Between elements
    };
    
    int num_cases = sizeof(test_cases) / sizeof(test_cases[0]);
    
    for (int tc = 0; tc < num_cases; tc++) {
        bptree_iterator_t* iter = bptree_range_iterator_new(tree, 
            test_cases[tc].start, test_cases[tc].end);
        ASSERT(iter != NULL);
        
        int count = 0;
        while (bptree_iterator_has_next(iter)) {
            bptree_entry_t entry;
            bptree_result_t result = bptree_iterator_next(iter, &entry);
            ASSERT_EQ(BPTREE_OK, result);
            
            // Verify key is in range
            ASSERT(entry.key >= test_cases[tc].start);
            ASSERT(entry.key < test_cases[tc].end);
            count++;
        }
        
        ASSERT_EQ(test_cases[tc].expected_count, count);
        bptree_iterator_free(iter);
    }
    
    bptree_free(tree);
}

int main(void) {
    printf("=== B+ Tree C Implementation - Adversarial Edge Cases Tests ===\n\n");
    
    RUN_TEST(adversarial_root_collapse_infinite_loop_attack);
    RUN_TEST(adversarial_minimum_capacity_edge_cases);
    RUN_TEST(adversarial_odd_capacity_arithmetic_edge_cases);
    RUN_TEST(adversarial_sequential_key_exhaustion_patterns);
    RUN_TEST(adversarial_extreme_boundary_value_insertions);
    RUN_TEST(adversarial_pathological_split_cascade_patterns);
    RUN_TEST(adversarial_iterator_invalidation_stress_test);
    RUN_TEST(adversarial_memory_pressure_simulation);
    RUN_TEST(adversarial_duplicate_key_update_patterns);
    RUN_TEST(adversarial_range_query_boundary_attack);
    
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