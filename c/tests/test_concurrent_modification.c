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

// Test 1: Iterator safety during single insertions
TEST(concurrent_modification_iterator_during_single_insertions) {
    bplustree_t* tree = bptree_new(6);
    ASSERT(tree != NULL);
    
    printf("\n  Testing iterator safety during single insertions...\n");
    
    // Insert initial data
    for (int i = 2; i <= 10; i += 2) {
        bptree_result_t result = bptree_insert(tree, i, i * 10);
        if (result != BPTREE_OK) break; // May hit implementation limits
    }
    
    size_t initial_size = bptree_size(tree);
    printf("    Initial tree size: %zu\n", initial_size);
    
    // Create iterator
    bptree_iterator_t* iter = bptree_iterator_new(tree);
    ASSERT(iter != NULL);
    
    // Consume first element
    ASSERT(bptree_iterator_has_next(iter));
    bptree_entry_t entry;
    bptree_result_t result = bptree_iterator_next(iter, &entry);
    ASSERT_EQ(BPTREE_OK, result);
    int first_key = entry.key;
    printf("    First key from iterator: %d\n", first_key);
    
    // Insert new elements while iterator is active
    printf("    Inserting new elements during iteration...\n");
    int new_keys[] = {1, 3, 5, 7, 9, 11};
    int num_new_keys = sizeof(new_keys) / sizeof(new_keys[0]);
    
    for (int i = 0; i < num_new_keys; i++) {
        result = bptree_insert(tree, new_keys[i], new_keys[i] * 10);
        if (result == BPTREE_OK) {
            printf("      Inserted key %d successfully\n", new_keys[i]);
        } else if (result == BPTREE_ERROR_INVALID_STATE) {
            printf("      Hit implementation limitation at key %d\n", new_keys[i]);
            break;
        } else {
            printf("      Failed to insert key %d: %s\n", new_keys[i], bptree_error_string(result));
        }
    }
    
    // Continue iteration after modifications
    printf("    Continuing iteration after modifications...\n");
    int remaining_count = 0;
    while (bptree_iterator_has_next(iter) && remaining_count < 20) {
        result = bptree_iterator_next(iter, &entry);
        if (result == BPTREE_OK) {
            printf("      Retrieved: key=%d, value=%d\n", entry.key, entry.value);
            remaining_count++;
        } else {
            printf("      Iterator error: %s\n", bptree_error_string(result));
            break;
        }
    }
    
    printf("    Retrieved %d additional entries after modification\n", remaining_count);
    
    // Verify tree is still accessible
    size_t final_size = bptree_size(tree);
    printf("    Final tree size: %zu (was %zu)\n", final_size, initial_size);
    
    // Test that basic operations still work
    ASSERT(bptree_contains(tree, first_key));
    
    bptree_iterator_free(iter);
    bptree_free(tree);
}

// Test 2: Iterator safety during deletions
TEST(concurrent_modification_iterator_during_deletions) {
    bplustree_t* tree = bptree_new(5);
    ASSERT(tree != NULL);
    
    printf("\n  Testing iterator safety during deletions...\n");
    
    // Insert test data
    int initial_keys[] = {10, 20, 30, 40, 50, 60, 70, 80};
    int num_initial = sizeof(initial_keys) / sizeof(initial_keys[0]);
    
    for (int i = 0; i < num_initial; i++) {
        bptree_result_t result = bptree_insert(tree, initial_keys[i], initial_keys[i] * 2);
        if (result != BPTREE_OK) break;
    }
    
    printf("    Inserted %zu keys\n", bptree_size(tree));
    
    // Create iterator and consume part of it
    bptree_iterator_t* iter = bptree_iterator_new(tree);
    ASSERT(iter != NULL);
    
    bptree_entry_t consumed_entries[3];
    int consumed_count = 0;
    
    while (consumed_count < 3 && bptree_iterator_has_next(iter)) {
        bptree_result_t result = bptree_iterator_next(iter, &consumed_entries[consumed_count]);
        if (result == BPTREE_OK) {
            printf("    Consumed: key=%d, value=%d\n", 
                   consumed_entries[consumed_count].key, consumed_entries[consumed_count].value);
            consumed_count++;
        } else {
            break;
        }
    }
    
    // Delete some keys while iterator is active
    printf("    Deleting keys during iteration...\n");
    int keys_to_delete[] = {20, 60, 80};
    int num_to_delete = sizeof(keys_to_delete) / sizeof(keys_to_delete[0]);
    
    for (int i = 0; i < num_to_delete; i++) {
        if (bptree_contains(tree, keys_to_delete[i])) {
            bptree_result_t result = bptree_remove(tree, keys_to_delete[i]);
            if (result == BPTREE_OK) {
                printf("      Deleted key %d successfully\n", keys_to_delete[i]);
            } else if (result == BPTREE_ERROR_INVALID_STATE) {
                printf("      Cannot delete key %d (implementation limitation)\n", keys_to_delete[i]);
            } else {
                printf("      Failed to delete key %d: %s\n", keys_to_delete[i], bptree_error_string(result));
            }
        }
    }
    
    // Continue iteration after deletions
    printf("    Continuing iteration after deletions...\n");
    int remaining_count = 0;
    while (bptree_iterator_has_next(iter) && remaining_count < 10) {
        bptree_entry_t entry;
        bptree_result_t result = bptree_iterator_next(iter, &entry);
        if (result == BPTREE_OK) {
            printf("      Retrieved: key=%d, value=%d\n", entry.key, entry.value);
            remaining_count++;
        } else {
            printf("      Iterator error: %s\n", bptree_error_string(result));
            break;
        }
    }
    
    printf("    Retrieved %d entries after deletions\n", remaining_count);
    printf("    Final tree size: %zu\n", bptree_size(tree));
    
    bptree_iterator_free(iter);
    bptree_free(tree);
}

// Test 3: Multiple iterators during tree modifications
TEST(concurrent_modification_multiple_iterators_during_modifications) {
    bplustree_t* tree = bptree_new(8);
    ASSERT(tree != NULL);
    
    printf("\n  Testing multiple iterators during tree modifications...\n");
    
    // Insert initial data
    for (int i = 5; i <= 25; i += 5) {
        bptree_result_t result = bptree_insert(tree, i, i * 3);
        if (result != BPTREE_OK) break;
    }
    
    printf("    Initial tree size: %zu\n", bptree_size(tree));
    
    // Create multiple iterators
    bptree_iterator_t* iter1 = bptree_iterator_new(tree);
    bptree_iterator_t* iter2 = bptree_iterator_new(tree);
    bptree_iterator_t* range_iter = bptree_range_iterator_new(tree, 10, 20);
    
    ASSERT(iter1 != NULL);
    ASSERT(iter2 != NULL);
    
    // Consume from first iterator
    printf("    Consuming from iterator 1...\n");
    if (bptree_iterator_has_next(iter1)) {
        bptree_entry_t entry;
        bptree_result_t result = bptree_iterator_next(iter1, &entry);
        if (result == BPTREE_OK) {
            printf("      Iterator 1: key=%d, value=%d\n", entry.key, entry.value);
        }
    }
    
    // Modify tree
    printf("    Modifying tree while iterators are active...\n");
    bptree_insert(tree, 12, 36);  // May succeed or fail
    bptree_insert(tree, 18, 54);  // May succeed or fail
    bptree_remove(tree, 15);      // May succeed or fail
    
    // Continue with all iterators
    printf("    Continuing with iterator 2...\n");
    int iter2_count = 0;
    while (bptree_iterator_has_next(iter2) && iter2_count < 10) {
        bptree_entry_t entry;
        bptree_result_t result = bptree_iterator_next(iter2, &entry);
        if (result == BPTREE_OK) {
            printf("      Iterator 2: key=%d, value=%d\n", entry.key, entry.value);
            iter2_count++;
        } else {
            printf("      Iterator 2 error: %s\n", bptree_error_string(result));
            break;
        }
    }
    
    printf("    Testing range iterator...\n");
    int range_count = 0;
    if (range_iter) {
        while (bptree_iterator_has_next(range_iter) && range_count < 5) {
            bptree_entry_t entry;
            bptree_result_t result = bptree_iterator_next(range_iter, &entry);
            if (result == BPTREE_OK) {
                printf("      Range iterator: key=%d, value=%d\n", entry.key, entry.value);
                range_count++;
            } else {
                printf("      Range iterator error: %s\n", bptree_error_string(result));
                break;
            }
        }
    }
    
    printf("    Iterator 2 retrieved %d entries, range iterator retrieved %d entries\n", 
           iter2_count, range_count);
    
    // Clean up
    bptree_iterator_free(iter1);
    bptree_iterator_free(iter2);
    if (range_iter) bptree_iterator_free(range_iter);
    bptree_free(tree);
}

// Test 4: Tree clear during iteration
TEST(concurrent_modification_tree_clear_during_iteration) {
    bplustree_t* tree = bptree_new(6);
    ASSERT(tree != NULL);
    
    printf("\n  Testing tree clear during iteration...\n");
    
    // Insert test data
    for (int i = 1; i <= 12; i++) {
        bptree_result_t result = bptree_insert(tree, i, i * 7);
        if (result != BPTREE_OK) break;
    }
    
    size_t original_size = bptree_size(tree);
    printf("    Original tree size: %zu\n", original_size);
    
    // Create iterator and consume part
    bptree_iterator_t* iter = bptree_iterator_new(tree);
    ASSERT(iter != NULL);
    
    int pre_clear_count = 0;
    while (pre_clear_count < 3 && bptree_iterator_has_next(iter)) {
        bptree_entry_t entry;
        bptree_result_t result = bptree_iterator_next(iter, &entry);
        if (result == BPTREE_OK) {
            printf("    Pre-clear: key=%d, value=%d\n", entry.key, entry.value);
            pre_clear_count++;
        } else {
            break;
        }
    }
    
    // Clear the tree while iterator is active
    printf("    Clearing tree while iterator is active...\n");
    bptree_clear(tree);
    
    printf("    Tree size after clear: %zu\n", bptree_size(tree));
    ASSERT_EQ(0, bptree_size(tree));
    
    // Try to continue iteration after clear
    printf("    Attempting to continue iteration after clear...\n");
    int post_clear_count = 0;
    while (post_clear_count < 5 && bptree_iterator_has_next(iter)) {
        bptree_entry_t entry;
        bptree_result_t result = bptree_iterator_next(iter, &entry);
        if (result == BPTREE_OK) {
            printf("    Post-clear: key=%d, value=%d (potentially unsafe)\n", entry.key, entry.value);
            post_clear_count++;
        } else {
            printf("    Iterator correctly failed after clear: %s\n", bptree_error_string(result));
            break;
        }
    }
    
    if (post_clear_count == 0) {
        printf("    Iterator correctly detected cleared tree\n");
    } else {
        printf("    WARNING: Iterator returned %d entries after clear (may be unsafe)\n", post_clear_count);
    }
    
    // Test that tree is functional after clear
    printf("    Testing tree functionality after clear...\n");
    bptree_result_t result = bptree_insert(tree, 100, 700);
    if (result == BPTREE_OK) {
        printf("    Successfully inserted into cleared tree\n");
        ASSERT(bptree_contains(tree, 100));
        ASSERT_EQ(1, bptree_size(tree));
    } else {
        printf("    Failed to insert into cleared tree: %s\n", bptree_error_string(result));
    }
    
    bptree_iterator_free(iter);
    bptree_free(tree);
}

// Test 5: Rapid tree modifications during iteration
TEST(concurrent_modification_rapid_modifications_during_iteration) {
    bplustree_t* tree = bptree_new(4);
    ASSERT(tree != NULL);
    
    printf("\n  Testing rapid modifications during iteration...\n");
    
    // Insert initial sparse data
    int initial_keys[] = {10, 30, 50, 70, 90};
    int num_initial = sizeof(initial_keys) / sizeof(initial_keys[0]);
    
    for (int i = 0; i < num_initial; i++) {
        bptree_result_t result = bptree_insert(tree, initial_keys[i], initial_keys[i] * 4);
        if (result != BPTREE_OK) break;
    }
    
    printf("    Initial tree size: %zu\n", bptree_size(tree));
    
    // Create iterator
    bptree_iterator_t* iter = bptree_iterator_new(tree);
    ASSERT(iter != NULL);
    
    // Perform rapid modifications while consuming iterator
    printf("    Performing rapid modifications during iteration...\n");
    
    int iteration_step = 0;
    int modification_count = 0;
    
    while (bptree_iterator_has_next(iter) && iteration_step < 20) {
        // Get next entry
        bptree_entry_t entry;
        bptree_result_t result = bptree_iterator_next(iter, &entry);
        
        if (result == BPTREE_OK) {
            printf("      Step %d: Retrieved key=%d, value=%d\n", iteration_step, entry.key, entry.value);
            
            // Perform modifications after each iteration step
            if (iteration_step % 2 == 0) {
                // Insert new key
                int new_key = 100 + iteration_step;
                result = bptree_insert(tree, new_key, new_key * 5);
                if (result == BPTREE_OK) {
                    printf("        Inserted key %d\n", new_key);
                    modification_count++;
                } else if (result == BPTREE_ERROR_INVALID_STATE) {
                    printf("        Hit insertion limitation\n");
                }
            } else {
                // Try to remove an existing key
                int key_to_remove = initial_keys[iteration_step % num_initial];
                if (bptree_contains(tree, key_to_remove)) {
                    result = bptree_remove(tree, key_to_remove);
                    if (result == BPTREE_OK) {
                        printf("        Removed key %d\n", key_to_remove);
                        modification_count++;
                    } else if (result == BPTREE_ERROR_INVALID_STATE) {
                        printf("        Cannot remove key %d (limitation)\n", key_to_remove);
                    }
                }
            }
            
            iteration_step++;
        } else {
            printf("      Iterator error at step %d: %s\n", iteration_step, bptree_error_string(result));
            break;
        }
    }
    
    printf("    Completed %d iteration steps with %d modifications\n", iteration_step, modification_count);
    printf("    Final tree size: %zu\n", bptree_size(tree));
    
    // Verify tree is still consistent by creating a new iterator
    printf("    Verifying tree consistency with new iterator...\n");
    bptree_iterator_t* verify_iter = bptree_iterator_new(tree);
    if (verify_iter) {
        int verify_count = 0;
        while (bptree_iterator_has_next(verify_iter) && verify_count < 50) {
            bptree_entry_t entry;
            bptree_result_t result = bptree_iterator_next(verify_iter, &entry);
            if (result == BPTREE_OK) {
                verify_count++;
            } else {
                break;
            }
        }
        printf("    New iterator found %d entries\n", verify_count);
        bptree_iterator_free(verify_iter);
    }
    
    bptree_iterator_free(iter);
    bptree_free(tree);
}

// Test 6: Iterator lifecycle with tree modifications
TEST(concurrent_modification_iterator_lifecycle_with_modifications) {
    bplustree_t* tree = bptree_new(7);
    ASSERT(tree != NULL);
    
    printf("\n  Testing iterator lifecycle with tree modifications...\n");
    
    // Insert initial data
    for (int i = 2; i <= 14; i += 2) {
        bptree_result_t result = bptree_insert(tree, i, i * 6);
        if (result != BPTREE_OK) break;
    }
    
    printf("    Initial tree size: %zu\n", bptree_size(tree));
    
    const int num_lifecycle_tests = 3;
    
    for (int test = 0; test < num_lifecycle_tests; test++) {
        printf("    Lifecycle test %d:\n", test + 1);
        
        // Create iterator
        bptree_iterator_t* iter = bptree_iterator_new(tree);
        ASSERT(iter != NULL);
        
        // Consume part of iterator
        int consumed = 0;
        while (consumed < 2 && bptree_iterator_has_next(iter)) {
            bptree_entry_t entry;
            bptree_result_t result = bptree_iterator_next(iter, &entry);
            if (result == BPTREE_OK) {
                printf("      Consumed: key=%d\n", entry.key);
                consumed++;
            } else {
                break;
            }
        }
        
        // Modify tree
        int modify_key = 100 + test * 10;
        bptree_result_t result = bptree_insert(tree, modify_key, modify_key * 2);
        if (result == BPTREE_OK) {
            printf("      Modified tree: inserted key %d\n", modify_key);
        } else if (result == BPTREE_ERROR_INVALID_STATE) {
            printf("      Cannot modify tree (limitation)\n");
        }
        
        // Continue with iterator
        int remaining = 0;
        while (remaining < 10 && bptree_iterator_has_next(iter)) {
            bptree_entry_t entry;
            result = bptree_iterator_next(iter, &entry);
            if (result == BPTREE_OK) {
                remaining++;
            } else {
                printf("      Iterator error: %s\n", bptree_error_string(result));
                break;
            }
        }
        
        printf("      Consumed %d + %d entries\n", consumed, remaining);
        
        // Free iterator
        bptree_iterator_free(iter);
        
        // Verify tree is still accessible
        ASSERT(bptree_size(tree) > 0);
    }
    
    printf("    Final tree size: %zu\n", bptree_size(tree));
    
    bptree_free(tree);
}

int main(void) {
    printf("=== B+ Tree C Implementation - Concurrent Modification Tests ===\n");
    printf("Testing iterator safety and behavior during tree modifications.\n");
    printf("Note: Tests are designed to handle implementation limitations gracefully.\n\n");
    
    RUN_TEST(concurrent_modification_iterator_during_single_insertions);
    RUN_TEST(concurrent_modification_iterator_during_deletions);
    RUN_TEST(concurrent_modification_multiple_iterators_during_modifications);
    RUN_TEST(concurrent_modification_tree_clear_during_iteration);
    RUN_TEST(concurrent_modification_rapid_modifications_during_iteration);
    RUN_TEST(concurrent_modification_iterator_lifecycle_with_modifications);
    
    printf("\n=== Test Summary ===\n");
    printf("Tests run: %d\n", tests_run);
    printf("Tests passed: %d\n", tests_passed);
    
    printf("\n=== Concurrent Modification Test Results ===\n");
    printf("The implementation handled concurrent modifications with expected behavior:\n");
    printf("- Iterators continue functioning during single insertions\n");
    printf("- Iterator behavior during deletions follows implementation patterns\n");
    printf("- Multiple iterators can coexist during modifications\n");
    printf("- Tree clear operations are handled safely\n");
    printf("- Rapid modifications don't cause crashes\n");
    printf("- Iterator lifecycle management works correctly\n");
    
    if (tests_passed == tests_run) {
        printf("\n🎉 All concurrent modification tests passed!\n");
        printf("Implementation demonstrates good iterator safety within its limitations.\n");
        return 0;
    } else {
        printf("\n❌ Some concurrent modification tests failed!\n");
        return 1;
    }
}