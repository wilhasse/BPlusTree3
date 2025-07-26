# Makefile for B+ Tree C Implementation

CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -O2 -g
TESTFLAGS = -Wall -Wextra -std=c99 -g -DDEBUG
BENCHFLAGS = -Wall -Wextra -std=c99 -O3 -DNDEBUG -march=native

SRCDIR = src
TESTDIR = tests
BENCHDIR = benchmarks
BUILDDIR = build

# Source files
SOURCES = $(wildcard $(SRCDIR)/*.c)
OBJECTS = $(SOURCES:$(SRCDIR)/%.c=$(BUILDDIR)/%.o)

# Test files
TEST_SOURCES = $(wildcard $(TESTDIR)/*.c)
TEST_OBJECTS = $(TEST_SOURCES:$(TESTDIR)/%.c=$(BUILDDIR)/test_%.o)
TEST_BINARIES = $(TEST_SOURCES:$(TESTDIR)/%.c=$(BUILDDIR)/%)

# Benchmark files
BENCH_SOURCES = $(wildcard $(BENCHDIR)/*.c)
BENCH_BINARIES = $(BENCH_SOURCES:$(BENCHDIR)/%.c=$(BUILDDIR)/%)

.PHONY: all clean test benchmark demo

all: $(BUILDDIR) $(OBJECTS)

$(BUILDDIR):
	mkdir -p $(BUILDDIR)

# Build object files
$(BUILDDIR)/%.o: $(SRCDIR)/%.c
	$(CC) $(CFLAGS) -c $< -o $@

# Build test object files
$(BUILDDIR)/test_%.o: $(TESTDIR)/%.c
	$(CC) $(TESTFLAGS) -c $< -o $@

# Build test binaries
$(BUILDDIR)/test_%: $(BUILDDIR)/test_%.o $(OBJECTS)
	$(CC) $(TESTFLAGS) $^ -o $@

# Special rules for test files
$(BUILDDIR)/test_basic: $(BUILDDIR)/test_test_basic.o $(OBJECTS)
	$(CC) $(TESTFLAGS) $^ -o $@

$(BUILDDIR)/test_advanced: $(BUILDDIR)/test_test_advanced.o $(OBJECTS)
	$(CC) $(TESTFLAGS) $^ -o $@

# Build benchmark binaries
$(BUILDDIR)/benchmark_%: $(BENCHDIR)/benchmark_%.c $(OBJECTS)
	$(CC) $(BENCHFLAGS) $^ -o $@

# Run tests
test: $(TEST_BINARIES)
	@echo "Running C B+ Tree Tests..."
	@for test in $(TEST_BINARIES); do \
		echo "Running $$test..."; \
		$$test || exit 1; \
	done
	@echo "All tests passed!"

# Run benchmarks
benchmark: $(BENCH_BINARIES)
	@echo "Running C B+ Tree Benchmarks..."
	@for bench in $(BENCH_BINARIES); do \
		echo "Running $$bench..."; \
		$$bench; \
	done

# Build demo
demo: $(BUILDDIR)/demo
	$(BUILDDIR)/demo

$(BUILDDIR)/demo: examples/demo.c $(OBJECTS)
	$(CC) $(CFLAGS) $^ -o $@

# Clean build artifacts
clean:
	rm -rf $(BUILDDIR)

# Development targets
dev-test: CFLAGS += -fsanitize=address -fsanitize=undefined
dev-test: test

valgrind-test: $(TEST_BINARIES)
	@for test in $(TEST_BINARIES); do \
		echo "Running $$test with valgrind..."; \
		valgrind --leak-check=full --error-exitcode=1 $$test || exit 1; \
	done

# Help target
help:
	@echo "Available targets:"
	@echo "  all       - Build all object files"
	@echo "  test      - Build and run all tests"
	@echo "  benchmark - Build and run benchmarks"
	@echo "  demo      - Build and run demo"
	@echo "  clean     - Remove build artifacts"
	@echo "  dev-test  - Run tests with sanitizers"
	@echo "  valgrind-test - Run tests with valgrind"