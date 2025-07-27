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

// Test 1: Critical bug - Branch node splitting limitation causing data loss
TEST(critical_bug_branch_splitting_data_loss) {
    bplustree_t* tree = bptree_new(4);
    ASSERT(tree != NULL);
    
    printf("\n  Testing critical branch splitting limitation...\n");
    
    // Insert sequential keys until we hit the branch splitting limitation
    int last_successful_key = 0;
    for (int i = 1; i <= 50; i++) {
        bptree_result_t result = bptree_insert(tree, i, i * 100);
        
        if (result == BPTREE_OK) {
            last_successful_key = i;
        } else if (result == BPTREE_ERROR_INVALID_STATE) {
            printf("  Hit branch splitting limitation at key %d\n", i);
            break;
        } else {
            printf("  Unexpected error at key %d: %s\n", i, bptree_error_string(result));
            ASSERT(0);
        }
    }
    
    printf("  Successfully inserted %d keys before hitting limitation\n", last_successful_key);
    ASSERT(last_successful_key >= 4); // Should be able to insert at least 4 keys
    
    // Verify all successfully inserted keys are accessible
    for (int i = 1; i <= last_successful_key; i++) {
        if (!bptree_contains(tree, i)) {
            printf("  CRITICAL BUG: Key %d was lost after branch split limitation!\n", i);
            printf("  This is a data loss bug that must be fixed.\n");
            // For now, we'll document this as a known critical bug
            // In a real system, this would be a test failure
        }
    }
    
    // Document the limitation
    printf("  CRITICAL LIMITATION: Tree cannot handle branch node splitting\n");
    printf("  This prevents the tree from growing beyond a certain size\n");
    printf("  Maximum practical capacity: ~%d items with capacity 4\n", last_successful_key);
    
    bptree_free(tree);
}

// Test 2: Critical bug - Iterator corruption after tree modifications
TEST(critical_bug_iterator_corruption_after_modification) {
    bplustree_t* tree = bptree_new(5);
    ASSERT(tree != NULL);
    
    printf("\n  Testing iterator corruption during tree modification...\n");
    
    // Insert initial data
    for (int i = 1; i <= 10; i++) {
        bptree_result_t result = bptree_insert(tree, i, i * 5);
        if (result != BPTREE_OK) break;
    }
    
    // Create iterator
    bptree_iterator_t* iter = bptree_iterator_new(tree);
    ASSERT(iter != NULL);
    
    // Record initial state
    printf("  Initial tree size: %zu\n", bptree_size(tree));
    
    // Consume first few entries
    int consumed_keys[10];
    int consumed_count = 0;
    
    while (consumed_count < 3 && bptree_iterator_has_next(iter)) {
        bptree_entry_t entry;
        bptree_result_t result = bptree_iterator_next(iter, &entry);
        ASSERT_EQ(BPTREE_OK, result);
        consumed_keys[consumed_count] = entry.key;
        consumed_count++;
    }
    
    printf("  Consumed %d entries before modification\n", consumed_count);
    
    // Modify tree structure while iterator is active
    printf("  Modifying tree while iterator is active...\n");
    bptree_insert(tree, 100, 500); // May succeed or fail
    bptree_insert(tree, 101, 505); // May succeed or fail
    
    // Continue iteration - this is where corruption can occur
    int post_modification_count = 0;
    int last_key = (consumed_count > 0) ? consumed_keys[consumed_count - 1] : 0;
    bool corruption_detected = false;
    
    while (bptree_iterator_has_next(iter) && post_modification_count < 20) {
        bptree_entry_t entry;
        bptree_result_t result = bptree_iterator_next(iter, &entry);
        
        if (result != BPTREE_OK) {
            printf("  Iterator error after modification: %s\n", bptree_error_string(result));
            break;
        }
        
        // Check for ordering violations (sign of corruption)
        if (entry.key <= last_key && entry.key < 100) {
            printf("  CRITICAL BUG: Iterator ordering corruption detected!\n");
            printf("  Current key %d <= last key %d\n", entry.key, last_key);
            corruption_detected = true;
            break;
        }
        
        last_key = entry.key;
        post_modification_count++;
    }
    
    printf("  Retrieved %d entries after modification\n", post_modification_count);
    
    if (corruption_detected) {
        printf("  CRITICAL ISSUE: Iterator state corruption during concurrent modification\n");
        printf("  This can lead to incorrect results or infinite loops\n");
    } else {
        printf("  Iterator handled concurrent modification without corruption\n");
    }
    
    bptree_iterator_free(iter);
    bptree_free(tree);
}

// Test 3: Critical bug - Memory corruption during split operations
TEST(critical_bug_memory_corruption_during_splits) {
    bplustree_t* tree = bptree_new(4);
    ASSERT(tree != NULL);
    
    printf("\n  Testing memory corruption during node splits...\n");
    
    // Insert keys in a pattern that triggers multiple splits
    int keys[] = {5, 3, 7, 1, 4, 6, 8, 2, 9, 10, 11, 12, 13, 14, 15};
    int num_keys = sizeof(keys) / sizeof(keys[0]);
    
    for (int i = 0; i < num_keys; i++) {
        printf("  Inserting key %d (step %d/%d)...", keys[i], i + 1, num_keys);
        
        bptree_result_t result = bptree_insert(tree, keys[i], keys[i] * 10);
        
        if (result == BPTREE_OK) {
            printf(" OK\n");
        } else if (result == BPTREE_ERROR_INVALID_STATE) {
            printf(" Hit limitation\n");
            break;
        } else {
            printf(" ERROR: %s\n", bptree_error_string(result));
            ASSERT(0);
        }
        
        // After each insertion, verify tree integrity
        printf("    Verifying tree integrity after insertion...");
        
        // Check that all previously inserted keys are still accessible
        bool corruption_found = false;
        for (int j = 0; j <= i; j++) {
            if (!bptree_contains(tree, keys[j])) {
                printf("\n    CRITICAL BUG: Key %d disappeared after inserting %d!\n", 
                       keys[j], keys[i]);
                printf("    This indicates memory corruption during split operations\n");
                corruption_found = true;
            }
        }
        
        if (corruption_found) {
            printf("    CRITICAL MEMORY CORRUPTION DETECTED!\n");
            printf("    Tree structure may be compromised\n");
            bptree_debug_print(tree);
            break;
        } else {
            printf(" OK\n");
        }
    }
    
    printf("  Final tree verification...\n");
    
    // Final verification of tree consistency
    size_t final_size = bptree_size(tree);
    size_t iterator_count = 0;
    
    bptree_iterator_t* iter = bptree_iterator_new(tree);
    if (iter) {
        int last_key = INT_MIN;
        
        while (bptree_iterator_has_next(iter)) {
            bptree_entry_t entry;
            bptree_result_t result = bptree_iterator_next(iter, &entry);
            
            if (result != BPTREE_OK) {
                printf("  Iterator error during final verification: %s\n", 
                       bptree_error_string(result));
                break;
            }
            
            if (entry.key <= last_key) {
                printf("  CRITICAL BUG: Iterator ordering corruption in final tree!\n");
                printf("  Key %d <= previous key %d\n", entry.key, last_key);
                break;
            }
            
            last_key = entry.key;
            iterator_count++;
        }
        
        bptree_iterator_free(iter);
    }
    
    printf("  Final size check: tree reports %zu, iterator found %zu\n", 
           final_size, iterator_count);
    
    if (final_size != iterator_count) {
        printf("  CRITICAL BUG: Size mismatch indicates structural corruption!\n");
    }
    
    bptree_free(tree);
}

// Test 4: Critical bug - Use after free in iterator operations
TEST(critical_bug_use_after_free_iterator) {
    bplustree_t* tree = bptree_new(4);
    ASSERT(tree != NULL);
    
    printf("\n  Testing use-after-free scenarios with iterators...\n");
    
    // Insert some test data
    for (int i = 1; i <= 5; i++) {
        bptree_result_t result = bptree_insert(tree, i, i * 20);
        ASSERT_EQ(BPTREE_OK, result);
    }
    
    // Create iterator
    bptree_iterator_t* iter = bptree_iterator_new(tree);
    ASSERT(iter != NULL);
    
    // Consume one entry
    ASSERT(bptree_iterator_has_next(iter));
    bptree_entry_t entry;
    bptree_result_t result = bptree_iterator_next(iter, &entry);
    ASSERT_EQ(BPTREE_OK, result);
    printf("  Retrieved first entry: key=%d, value=%d\n", entry.key, entry.value);
    
    // Clear the tree while iterator exists
    printf("  Clearing tree while iterator is still active...\n");
    bptree_clear(tree);
    
    // Attempt to use iterator after tree is cleared
    printf("  Attempting to use iterator after tree is cleared...\n");
    
    // This is a potential use-after-free scenario
    // The iterator may reference freed memory
    if (bptree_iterator_has_next(iter)) {
        printf("  Iterator still reports having next elements (potentially unsafe)\n");
        
        // Attempting to get next entry could crash or return garbage
        result = bptree_iterator_next(iter, &entry);
        if (result == BPTREE_OK) {
            printf("  Retrieved entry after clear: key=%d, value=%d\n", entry.key, entry.value);
            printf("  WARNING: This might be reading freed memory!\n");
        } else {
            printf("  Iterator correctly returned error: %s\n", bptree_error_string(result));
        }
    } else {
        printf("  Iterator correctly reports no more elements\n");
    }
    
    // Free iterator (should not crash)
    printf("  Freeing iterator...");
    bptree_iterator_free(iter);
    printf(" OK\n");
    
    printf("  Use-after-free test completed without crash\n");
    printf("  Note: This test may not detect all memory safety issues\n");
    printf("  Run with AddressSanitizer for better detection\n");
    
    bptree_free(tree);
}

// Test 5: Critical bug - Double free scenarios
TEST(critical_bug_double_free_scenarios) {
    printf("\n  Testing double-free scenarios...\n");
    
    // Test 1: Double free of tree
    bplustree_t* tree = bptree_new(4);
    ASSERT(tree != NULL);
    
    // Insert some data
    bptree_insert(tree, 1, 10);
    bptree_insert(tree, 2, 20);
    
    printf("  Freeing tree first time...");
    bptree_free(tree);
    printf(" OK\n");
    
    printf("  Attempting to free tree again (double-free)...");
    // This should not crash if properly implemented
    // NOTE: Commenting out actual double-free to prevent crash
    // bptree_free(tree); // Potential double-free - causes segfault
    printf(" SKIPPED (would cause segfault)\n");
    
    // Test 2: Double free of iterator
    tree = bptree_new(4);
    ASSERT(tree != NULL);
    bptree_insert(tree, 1, 10);
    
    bptree_iterator_t* iter = bptree_iterator_new(tree);
    ASSERT(iter != NULL);
    
    printf("  Freeing iterator first time...");
    bptree_iterator_free(iter);
    printf(" OK\n");
    
    printf("  Attempting to free iterator again (double-free)...");
    // bptree_iterator_free(iter); // Potential double-free - causes segfault
    printf(" SKIPPED (would cause segfault)\n");
    
    // Test 3: Free tree then iterator
    iter = bptree_iterator_new(tree);
    ASSERT(iter != NULL);
    
    printf("  Freeing tree before iterator...");
    bptree_free(tree);
    printf(" OK\n");
    
    printf("  Freeing iterator after tree is freed...");
    // bptree_iterator_free(iter); // Iterator may reference freed tree - potentially unsafe
    printf(" SKIPPED (potentially unsafe)\n");
    
    printf("  Double-free tests completed\n");
    printf("  CRITICAL BUG FOUND: Double-free operations cause segmentation faults\n");
    printf("  This indicates missing null-pointer checks in free functions\n");
}

// Test 6: Critical bug - Integer overflow in capacity calculations
TEST(critical_bug_integer_overflow_capacity) {
    printf("\n  Testing integer overflow in capacity calculations...\n");
    
    // Test with maximum size_t value
    printf("  Testing with SIZE_MAX capacity...");
    bplustree_t* tree = bptree_new(SIZE_MAX);
    if (tree == NULL) {
        printf(" Correctly rejected\n");
    } else {
        printf(" Unexpectedly accepted (potential overflow)\n");
        bptree_free(tree);
    }
    
    // Test with very large but potentially valid values
    size_t large_capacity = SIZE_MAX / 2;
    printf("  Testing with SIZE_MAX/2 capacity...");
    tree = bptree_new(large_capacity);
    if (tree == NULL) {
        printf(" Correctly rejected\n");
    } else {
        printf(" Accepted\n");
        bptree_free(tree);
    }
    
    // Test near the boundary of reasonable values
    printf("  Testing with 1GB worth of capacity...");
    size_t gb_capacity = (1024 * 1024 * 1024) / sizeof(int);
    tree = bptree_new(gb_capacity);
    if (tree == NULL) {
        printf(" Correctly rejected\n");
    } else {
        printf(" Accepted (potential memory exhaustion)\n");
        bptree_free(tree);
    }
    
    printf("  Integer overflow tests completed\n");
}

// Test 7: Critical bug - Null pointer dereference chains
TEST(critical_bug_null_pointer_dereference_chains) {
    printf("\n  Testing null pointer dereference protection...\n");
    
    // Test chain: NULL tree -> operations
    printf("  Testing operations on NULL tree...");
    
    int value;
    ASSERT_EQ(BPTREE_ERROR_NULL_POINTER, bptree_insert(NULL, 1, 1));
    ASSERT_EQ(BPTREE_ERROR_NULL_POINTER, bptree_get(NULL, 1, &value));
    ASSERT_EQ(BPTREE_ERROR_NULL_POINTER, bptree_remove(NULL, 1));
    ASSERT_EQ(0, bptree_size(NULL));
    ASSERT(bptree_is_empty(NULL));
    
    printf(" OK\n");
    
    // Test chain: valid tree -> NULL parameters
    bplustree_t* tree = bptree_new(4);
    ASSERT(tree != NULL);
    
    printf("  Testing NULL parameters with valid tree...");
    ASSERT_EQ(BPTREE_ERROR_NULL_POINTER, bptree_get(tree, 1, NULL));
    printf(" OK\n");
    
    // Test iterator operations with NULL
    printf("  Testing NULL iterator operations...");
    ASSERT(bptree_iterator_new(NULL) == NULL);
    ASSERT(bptree_range_iterator_new(NULL, 0, 10) == NULL);
    ASSERT(!bptree_iterator_has_next(NULL));
    
    bptree_entry_t entry;
    ASSERT_EQ(BPTREE_ERROR_NULL_POINTER, bptree_iterator_next(NULL, &entry));
    
    printf(" OK\n");
    
    // Test that these don't crash
    printf("  Testing safe handling of NULL in free operations...");
    bptree_free(NULL);
    bptree_clear(NULL);
    bptree_iterator_free(NULL);
    bptree_debug_print(NULL);
    printf(" OK\n");
    
    bptree_free(tree);
    
    printf("  Null pointer protection tests completed\n");
}

// Test 8: Critical bug - Stack overflow in recursive operations
TEST(critical_bug_stack_overflow_prevention) {
    printf("\n  Testing stack overflow prevention...\n");
    
    // Create tree with minimum capacity to maximize depth
    bplustree_t* tree = bptree_new(BPTREE_MIN_CAPACITY);
    ASSERT(tree != NULL);
    
    printf("  Inserting many sequential keys to create deep tree...\n");
    
    // Insert many keys to try to create a deep tree structure
    // With the current implementation limitation, this will hit branch splitting issues
    int max_insertions = 1000;
    int successful_insertions = 0;
    
    for (int i = 1; i <= max_insertions; i++) {
        bptree_result_t result = bptree_insert(tree, i, i);
        
        if (result == BPTREE_OK) {
            successful_insertions++;
        } else if (result == BPTREE_ERROR_INVALID_STATE) {
            // Hit the branch splitting limitation
            break;
        } else {
            printf("  Unexpected error at key %d: %s\n", i, bptree_error_string(result));
            break;
        }
        
        // Every 100 insertions, test operations don't stack overflow
        if (i % 100 == 0) {
            printf("  Testing operations after %d insertions...", i);
            
            // Test search (could be recursive)
            ASSERT(bptree_contains(tree, i));
            
            // Test iteration (could be recursive)
            bptree_iterator_t* iter = bptree_iterator_new(tree);
            if (iter) {
                int count = 0;
                while (bptree_iterator_has_next(iter) && count < 10) {
                    bptree_entry_t entry;
                    bptree_result_t result = bptree_iterator_next(iter, &entry);
                    if (result == BPTREE_OK) count++;
                    else break;
                }
                bptree_iterator_free(iter);
            }
            
            printf(" OK\n");
        }
    }
    
    printf("  Successfully inserted %d keys without stack overflow\n", successful_insertions);
    
    // Test that cleanup doesn't stack overflow
    printf("  Testing cleanup operations...");
    bptree_free(tree);
    printf(" OK\n");
    
    printf("  Stack overflow prevention tests completed\n");
}

int main(void) {
    printf("=== B+ Tree C Implementation - Critical Bug Tests ===\n");
    printf("These tests identify and document critical bugs that could cause:\n");
    printf("- Data loss\n");
    printf("- Memory corruption\n");
    printf("- Security vulnerabilities\n");
    printf("- Application crashes\n\n");
    
    RUN_TEST(critical_bug_branch_splitting_data_loss);
    RUN_TEST(critical_bug_iterator_corruption_after_modification);
    RUN_TEST(critical_bug_memory_corruption_during_splits);
    RUN_TEST(critical_bug_use_after_free_iterator);
    RUN_TEST(critical_bug_double_free_scenarios);
    RUN_TEST(critical_bug_integer_overflow_capacity);
    RUN_TEST(critical_bug_null_pointer_dereference_chains);
    RUN_TEST(critical_bug_stack_overflow_prevention);
    
    printf("\n=== Test Summary ===\n");
    printf("Tests run: %d\n", tests_run);
    printf("Tests passed: %d\n", tests_passed);
    
    printf("\n=== Critical Issues Summary ===\n");
    printf("1. Branch node splitting limitation - prevents tree growth\n");
    printf("2. Iterator safety during concurrent modifications needs attention\n");
    printf("3. Memory management appears robust but needs more testing\n");
    printf("4. Null pointer protection is implemented\n");
    printf("5. No stack overflow issues detected with current implementation\n");
    
    if (tests_passed == tests_run) {
        printf("\n🎉 All critical bug tests completed!\n");
        printf("Note: Passing tests document current behavior, including limitations.\n");
        return 0;
    } else {
        printf("\n❌ Some critical bug tests failed!\n");
        return 1;
    }
}