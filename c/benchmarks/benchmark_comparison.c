#define _POSIX_C_SOURCE 199309L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include "../src/bplustree.h"

// Simple timing utility
typedef struct {
    struct timespec start;
    struct timespec end;
} bench_timer_t;

static void timer_start(bench_timer_t* timer) {
    clock_gettime(CLOCK_MONOTONIC, &timer->start);
}

static double timer_end(bench_timer_t* timer) {
    clock_gettime(CLOCK_MONOTONIC, &timer->end);
    double start_ns = timer->start.tv_sec * 1e9 + timer->start.tv_nsec;
    double end_ns = timer->end.tv_sec * 1e9 + timer->end.tv_nsec;
    return (end_ns - start_ns) / 1000.0; // Return microseconds
}

// Benchmark configuration
static const size_t WARMUP_RUNS = 3;
static const size_t BENCH_RUNS = 10;
static const size_t SIZES[] = {100, 1000, 10000, 100000};
static const size_t NUM_SIZES = sizeof(SIZES) / sizeof(SIZES[0]);

// Simple hash table for comparison
#define HASH_SIZE 1024
typedef struct hash_entry {
    int key;
    int value;
    struct hash_entry* next;
} hash_entry_t;

typedef struct {
    hash_entry_t* buckets[HASH_SIZE];
    size_t size;
} hash_table_t;

static unsigned int hash_func(int key) {
    return ((unsigned int)key * 2654435761u) % HASH_SIZE;
}

static hash_table_t* hash_table_new(void) {
    hash_table_t* table = calloc(1, sizeof(hash_table_t));
    return table;
}

static void hash_table_free(hash_table_t* table) {
    if (!table) return;
    
    for (size_t i = 0; i < HASH_SIZE; i++) {
        hash_entry_t* entry = table->buckets[i];
        while (entry) {
            hash_entry_t* next = entry->next;
            free(entry);
            entry = next;
        }
    }
    free(table);
}

static void hash_table_insert(hash_table_t* table, int key, int value) {
    unsigned int index = hash_func(key);
    hash_entry_t* entry = table->buckets[index];
    
    // Check if key exists
    while (entry) {
        if (entry->key == key) {
            entry->value = value;
            return;
        }
        entry = entry->next;
    }
    
    // Create new entry
    entry = malloc(sizeof(hash_entry_t));
    entry->key = key;
    entry->value = value;
    entry->next = table->buckets[index];
    table->buckets[index] = entry;
    table->size++;
}

static int hash_table_get(hash_table_t* table, int key, int* value) {
    unsigned int index = hash_func(key);
    hash_entry_t* entry = table->buckets[index];
    
    while (entry) {
        if (entry->key == key) {
            *value = entry->value;
            return 1;
        }
        entry = entry->next;
    }
    return 0;
}

// Benchmark functions
static double benchmark_bptree_sequential_insert(size_t size) {
    bench_timer_t timer;
    double total_time = 0.0;
    
    for (size_t run = 0; run < BENCH_RUNS; run++) {
        bplustree_t* tree = bptree_new(128); // Use larger capacity for better performance
        
        timer_start(&timer);
        for (size_t i = 1; i <= size; i++) {
            bptree_insert(tree, (int)i, (int)(i * 2));
        }
        total_time += timer_end(&timer);
        
        bptree_free(tree);
    }
    
    return total_time / BENCH_RUNS;
}

static double benchmark_hash_sequential_insert(size_t size) {
    bench_timer_t timer;
    double total_time = 0.0;
    
    for (size_t run = 0; run < BENCH_RUNS; run++) {
        hash_table_t* table = hash_table_new();
        
        timer_start(&timer);
        for (size_t i = 1; i <= size; i++) {
            hash_table_insert(table, (int)i, (int)(i * 2));
        }
        total_time += timer_end(&timer);
        
        hash_table_free(table);
    }
    
    return total_time / BENCH_RUNS;
}

static double benchmark_bptree_lookup(size_t size) {
    bench_timer_t timer;
    double total_time = 0.0;
    
    // Setup: Create tree with data
    bplustree_t* tree = bptree_new(128);
    for (size_t i = 1; i <= size; i++) {
        bptree_insert(tree, (int)i, (int)(i * 2));
    }
    
    for (size_t run = 0; run < BENCH_RUNS; run++) {
        timer_start(&timer);
        for (size_t i = 1; i <= size; i++) {
            int value;
            bptree_get(tree, (int)i, &value);
        }
        total_time += timer_end(&timer);
    }
    
    bptree_free(tree);
    return total_time / BENCH_RUNS;
}

static double benchmark_hash_lookup(size_t size) {
    bench_timer_t timer;
    double total_time = 0.0;
    
    // Setup: Create hash table with data
    hash_table_t* table = hash_table_new();
    for (size_t i = 1; i <= size; i++) {
        hash_table_insert(table, (int)i, (int)(i * 2));
    }
    
    for (size_t run = 0; run < BENCH_RUNS; run++) {
        timer_start(&timer);
        for (size_t i = 1; i <= size; i++) {
            int value;
            hash_table_get(table, (int)i, &value);
        }
        total_time += timer_end(&timer);
    }
    
    hash_table_free(table);
    return total_time / BENCH_RUNS;
}

static double benchmark_bptree_iteration(size_t size) {
    bench_timer_t timer;
    double total_time = 0.0;
    
    // Setup: Create tree with data
    bplustree_t* tree = bptree_new(128);
    for (size_t i = 1; i <= size; i++) {
        bptree_insert(tree, (int)i, (int)(i * 2));
    }
    
    for (size_t run = 0; run < BENCH_RUNS; run++) {
        timer_start(&timer);
        
        bptree_iterator_t* iter = bptree_iterator_new(tree);
        volatile size_t count = 0; // volatile to prevent optimization
        
        while (bptree_iterator_has_next(iter)) {
            bptree_entry_t entry;
            bptree_iterator_next(iter, &entry);
            count++;
        }
        
        bptree_iterator_free(iter);
        total_time += timer_end(&timer);
    }
    
    bptree_free(tree);
    return total_time / BENCH_RUNS;
}

static double benchmark_hash_iteration(size_t size) {
    bench_timer_t timer;
    double total_time = 0.0;
    
    // Setup: Create hash table with data
    hash_table_t* table = hash_table_new();
    for (size_t i = 1; i <= size; i++) {
        hash_table_insert(table, (int)i, (int)(i * 2));
    }
    
    for (size_t run = 0; run < BENCH_RUNS; run++) {
        timer_start(&timer);
        
        volatile size_t count = 0; // volatile to prevent optimization
        for (size_t i = 0; i < HASH_SIZE; i++) {
            hash_entry_t* entry = table->buckets[i];
            while (entry) {
                count++; // Count the entry
                entry = entry->next;
            }
        }
        
        total_time += timer_end(&timer);
    }
    
    hash_table_free(table);
    return total_time / BENCH_RUNS;
}

int main(void) {
    printf("C B+ Tree vs Hash Table Benchmark\n");
    printf("==================================\n\n");
    
    printf("Configuration:\n");
    printf("- Warmup runs: %zu\n", WARMUP_RUNS);
    printf("- Benchmark runs: %zu\n", BENCH_RUNS);
    printf("- B+ Tree capacity: 128\n");
    printf("- Hash table buckets: %d\n\n", HASH_SIZE);
    
    // Sequential Insert Benchmark
    printf("=== Sequential Insert ===\n");
    for (size_t i = 0; i < NUM_SIZES; i++) {
        size_t size = SIZES[i];
        
        // Warmup
        for (size_t w = 0; w < WARMUP_RUNS; w++) {
            benchmark_bptree_sequential_insert(size > 1000 ? 1000 : size);
            benchmark_hash_sequential_insert(size > 1000 ? 1000 : size);
        }
        
        double bptree_time = benchmark_bptree_sequential_insert(size);
        double hash_time = benchmark_hash_sequential_insert(size);
        
        printf("B+ Tree    %zu ops in %8.2fms | %8.0f ops/sec | %8.2f ns/op\n",
               size, bptree_time / 1000.0, size * 1e6 / bptree_time, bptree_time * 1000.0 / size);
        printf("Hash Table %zu ops in %8.2fms | %8.0f ops/sec | %8.2f ns/op\n",
               size, hash_time / 1000.0, size * 1e6 / hash_time, hash_time * 1000.0 / size);
        printf("\n");
    }
    
    // Lookup Benchmark
    printf("=== Lookup ===\n");
    for (size_t i = 0; i < NUM_SIZES; i++) {
        size_t size = SIZES[i];
        
        // Warmup
        for (size_t w = 0; w < WARMUP_RUNS; w++) {
            benchmark_bptree_lookup(size > 1000 ? 1000 : size);
            benchmark_hash_lookup(size > 1000 ? 1000 : size);
        }
        
        double bptree_time = benchmark_bptree_lookup(size);
        double hash_time = benchmark_hash_lookup(size);
        
        printf("B+ Tree    %zu ops in %8.2fms | %8.0f ops/sec | %8.2f ns/op\n",
               size, bptree_time / 1000.0, size * 1e6 / bptree_time, bptree_time * 1000.0 / size);
        printf("Hash Table %zu ops in %8.2fms | %8.0f ops/sec | %8.2f ns/op\n",
               size, hash_time / 1000.0, size * 1e6 / hash_time, hash_time * 1000.0 / size);
        printf("\n");
    }
    
    // Iteration Benchmark
    printf("=== Iteration ===\n");
    for (size_t i = 0; i < NUM_SIZES; i++) {
        size_t size = SIZES[i];
        
        // Warmup
        for (size_t w = 0; w < WARMUP_RUNS; w++) {
            benchmark_bptree_iteration(size > 1000 ? 1000 : size);
            benchmark_hash_iteration(size > 1000 ? 1000 : size);
        }
        
        double bptree_time = benchmark_bptree_iteration(size);
        double hash_time = benchmark_hash_iteration(size);
        
        printf("B+ Tree    %zu ops in %8.2fms | %8.0f ops/sec | %8.2f ns/op\n",
               size, bptree_time / 1000.0, size * 1e6 / bptree_time, bptree_time * 1000.0 / size);
        printf("Hash Table %zu ops in %8.2fms | %8.0f ops/sec | %8.2f ns/op\n",
               size, hash_time / 1000.0, size * 1e6 / hash_time, hash_time * 1000.0 / size);
        printf("\n");
    }
    
    printf("Benchmark completed!\n");
    return 0;
}