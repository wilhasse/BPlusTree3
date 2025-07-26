const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    // Library
    const lib = b.addStaticLibrary(.{
        .name = "bplustree",
        .root_source_file = b.path("src/bplustree.zig"),
        .target = target,
        .optimize = optimize,
    });
    b.installArtifact(lib);

    // Module for tests
    const bplustree_module = b.addModule("bplustree", .{
        .root_source_file = b.path("src/bplustree.zig"),
    });
    
    // Tests
    const test_step = b.step("test", "Run library tests");
    
    const lib_tests = b.addTest(.{
        .root_source_file = b.path("tests/test_bplustree.zig"),
        .target = target,
        .optimize = optimize,
    });
    lib_tests.root_module.addImport("bplustree", bplustree_module);
    
    const run_lib_tests = b.addRunArtifact(lib_tests);
    test_step.dependOn(&run_lib_tests.step);
    
    // Stress tests
    const stress_tests = b.addTest(.{
        .root_source_file = b.path("tests/test_stress.zig"),
        .target = target,
        .optimize = optimize,
    });
    stress_tests.root_module.addImport("bplustree", bplustree_module);
    
    const run_stress_tests = b.addRunArtifact(stress_tests);
    test_step.dependOn(&run_stress_tests.step);
    
    // Separate step for just stress tests
    const stress_step = b.step("test-stress", "Run stress tests");
    stress_step.dependOn(&run_stress_tests.step);
    
    // Iterator safety tests
    const iterator_tests = b.addTest(.{
        .root_source_file = b.path("tests/test_iterator_safety.zig"),
        .target = target,
        .optimize = optimize,
    });
    iterator_tests.root_module.addImport("bplustree", bplustree_module);
    
    const run_iterator_tests = b.addRunArtifact(iterator_tests);
    test_step.dependOn(&run_iterator_tests.step);
    
    // Separate step for iterator safety tests
    const iterator_step = b.step("test-iterator", "Run iterator safety tests");
    iterator_step.dependOn(&run_iterator_tests.step);
    
    // Advanced deletion tests
    const deletion_tests = b.addTest(.{
        .root_source_file = b.path("tests/test_deletion_advanced.zig"),
        .target = target,
        .optimize = optimize,
    });
    deletion_tests.root_module.addImport("bplustree", bplustree_module);
    
    const run_deletion_tests = b.addRunArtifact(deletion_tests);
    test_step.dependOn(&run_deletion_tests.step);
    
    // Separate step for deletion tests
    const deletion_step = b.step("test-deletion", "Run advanced deletion tests");
    deletion_step.dependOn(&run_deletion_tests.step);
    
    // Memory safety tests
    const memory_tests = b.addTest(.{
        .root_source_file = b.path("tests/test_memory_safety.zig"),
        .target = target,
        .optimize = optimize,
    });
    memory_tests.root_module.addImport("bplustree", bplustree_module);
    
    const run_memory_tests = b.addRunArtifact(memory_tests);
    test_step.dependOn(&run_memory_tests.step);
    
    // Separate step for memory safety tests
    const memory_step = b.step("test-memory", "Run memory safety tests");
    memory_step.dependOn(&run_memory_tests.step);
    
    // Range query tests
    const range_tests = b.addTest(.{
        .root_source_file = b.path("tests/test_range_queries.zig"),
        .target = target,
        .optimize = optimize,
    });
    range_tests.root_module.addImport("bplustree", bplustree_module);
    
    const run_range_tests = b.addRunArtifact(range_tests);
    test_step.dependOn(&run_range_tests.step);
    
    // Separate step for range query tests
    const range_step = b.step("test-range", "Run range query tests");
    range_step.dependOn(&run_range_tests.step);
    
    // Edge cases tests
    const edge_tests = b.addTest(.{
        .root_source_file = b.path("tests/test_edge_cases.zig"),
        .target = target,
        .optimize = optimize,
    });
    edge_tests.root_module.addImport("bplustree", bplustree_module);
    
    const run_edge_tests = b.addRunArtifact(edge_tests);
    test_step.dependOn(&run_edge_tests.step);
    
    // Separate step for edge case tests
    const edge_step = b.step("test-edge", "Run edge case tests");
    edge_step.dependOn(&run_edge_tests.step);
    
    // Linked list invariants tests
    const linked_list_tests = b.addTest(.{
        .root_source_file = b.path("tests/test_linked_list_invariants.zig"),
        .target = target,
        .optimize = optimize,
    });
    linked_list_tests.root_module.addImport("bplustree", bplustree_module);
    
    const run_linked_list_tests = b.addRunArtifact(linked_list_tests);
    test_step.dependOn(&run_linked_list_tests.step);
    
    // Separate step for linked list invariants tests
    const linked_list_step = b.step("test-linked-list", "Run linked list invariants tests");
    linked_list_step.dependOn(&run_linked_list_tests.step);
    
    // Adversarial edge case tests
    const adversarial_edge_tests = b.addTest(.{
        .root_source_file = b.path("tests/test_adversarial_edge_cases.zig"),
        .target = target,
        .optimize = optimize,
    });
    adversarial_edge_tests.root_module.addImport("bplustree", bplustree_module);
    
    const run_adversarial_edge_tests = b.addRunArtifact(adversarial_edge_tests);
    test_step.dependOn(&run_adversarial_edge_tests.step);
    
    // Separate step for adversarial edge case tests
    const adversarial_edge_step = b.step("test-adversarial-edge", "Run adversarial edge case tests");
    adversarial_edge_step.dependOn(&run_adversarial_edge_tests.step);
    
    // Adversarial linked list tests
    const adversarial_linked_tests = b.addTest(.{
        .root_source_file = b.path("tests/test_adversarial_linked_list.zig"),
        .target = target,
        .optimize = optimize,
    });
    adversarial_linked_tests.root_module.addImport("bplustree", bplustree_module);
    
    const run_adversarial_linked_tests = b.addRunArtifact(adversarial_linked_tests);
    test_step.dependOn(&run_adversarial_linked_tests.step);
    
    // Separate step for adversarial linked list tests
    const adversarial_linked_step = b.step("test-adversarial-linked", "Run adversarial linked list tests");
    adversarial_linked_step.dependOn(&run_adversarial_linked_tests.step);
    
    // Enhanced error handling tests
    const error_handling_tests = b.addTest(.{
        .root_source_file = b.path("tests/test_enhanced_error_handling.zig"),
        .target = target,
        .optimize = optimize,
    });
    error_handling_tests.root_module.addImport("bplustree", bplustree_module);
    
    const run_error_handling_tests = b.addRunArtifact(error_handling_tests);
    test_step.dependOn(&run_error_handling_tests.step);
    
    // Separate step for error handling tests
    const error_handling_step = b.step("test-error-handling", "Run enhanced error handling tests");
    error_handling_step.dependOn(&run_error_handling_tests.step);
    
    // Fuzz tests
    const fuzz_tests = b.addTest(.{
        .root_source_file = b.path("tests/test_fuzz.zig"),
        .target = target,
        .optimize = optimize,
    });
    fuzz_tests.root_module.addImport("bplustree", bplustree_module);
    
    const run_fuzz_tests = b.addRunArtifact(fuzz_tests);
    test_step.dependOn(&run_fuzz_tests.step);
    
    // Separate step for fuzz tests
    const fuzz_step = b.step("test-fuzz", "Run fuzz tests");
    fuzz_step.dependOn(&run_fuzz_tests.step);
    
    // Tree invariant tests
    const invariant_tests = b.addTest(.{
        .root_source_file = b.path("tests/test_tree_invariants.zig"),
        .target = target,
        .optimize = optimize,
    });
    invariant_tests.root_module.addImport("bplustree", bplustree_module);
    
    const run_invariant_tests = b.addRunArtifact(invariant_tests);
    test_step.dependOn(&run_invariant_tests.step);
    
    // Separate step for invariant tests
    const invariant_step = b.step("test-invariants", "Run tree invariant tests");
    invariant_step.dependOn(&run_invariant_tests.step);
    
    // Bug reproduction tests
    const bug_tests = b.addTest(.{
        .root_source_file = b.path("tests/test_bug_reproduction.zig"),
        .target = target,
        .optimize = optimize,
    });
    bug_tests.root_module.addImport("bplustree", bplustree_module);
    
    const run_bug_tests = b.addRunArtifact(bug_tests);
    test_step.dependOn(&run_bug_tests.step);
    
    // Separate step for bug reproduction tests
    const bug_step = b.step("test-bugs", "Run bug reproduction tests");
    bug_step.dependOn(&run_bug_tests.step);
    
    // Critical bug tests
    const critical_bug_tests = b.addTest(.{
        .root_source_file = b.path("tests/test_critical_bugs.zig"),
        .target = target,
        .optimize = optimize,
    });
    critical_bug_tests.root_module.addImport("bplustree", bplustree_module);
    
    const run_critical_bug_tests = b.addRunArtifact(critical_bug_tests);
    test_step.dependOn(&run_critical_bug_tests.step);
    
    // Separate step for critical bug tests
    const critical_bug_step = b.step("test-critical-bugs", "Run critical bug tests");
    critical_bug_step.dependOn(&run_critical_bug_tests.step);
    
    // Comprehensive memory safety tests
    const memory_safety_tests = b.addTest(.{
        .root_source_file = b.path("tests/test_comprehensive_memory_safety.zig"),
        .target = target,
        .optimize = optimize,
    });
    memory_safety_tests.root_module.addImport("bplustree", bplustree_module);
    
    const run_memory_safety_tests = b.addRunArtifact(memory_safety_tests);
    test_step.dependOn(&run_memory_safety_tests.step);
    
    // Separate step for memory safety tests
    const memory_safety_step = b.step("test-memory-safety", "Run comprehensive memory safety tests");
    memory_safety_step.dependOn(&run_memory_safety_tests.step);
    
    // Concurrent modification tests
    const concurrent_tests = b.addTest(.{
        .root_source_file = b.path("tests/test_concurrent_modifications.zig"),
        .target = target,
        .optimize = optimize,
    });
    concurrent_tests.root_module.addImport("bplustree", bplustree_module);
    
    const run_concurrent_tests = b.addRunArtifact(concurrent_tests);
    test_step.dependOn(&run_concurrent_tests.step);
    
    // Separate step for concurrent tests
    const concurrent_step = b.step("test-concurrent", "Run concurrent modification tests");
    concurrent_step.dependOn(&run_concurrent_tests.step);
    
    // Demo executable
    const demo = b.addExecutable(.{
        .name = "demo",
        .root_source_file = b.path("examples/demo.zig"),
        .target = target,
        .optimize = optimize,
    });
    demo.root_module.addImport("bplustree", bplustree_module);
    
    const run_demo = b.addRunArtifact(demo);
    const demo_step = b.step("demo", "Run the demo");
    demo_step.dependOn(&run_demo.step);
    
    // Benchmark executable
    const benchmark = b.addExecutable(.{
        .name = "benchmark",
        .root_source_file = b.path("benchmarks/benchmark.zig"),
        .target = target,
        .optimize = .ReleaseFast,
    });
    benchmark.root_module.addImport("bplustree", bplustree_module);
    
    const run_benchmark = b.addRunArtifact(benchmark);
    const benchmark_step = b.step("benchmark", "Run performance benchmarks");
    benchmark_step.dependOn(&run_benchmark.step);
    
    // Comparison benchmark executable
    const comparison = b.addExecutable(.{
        .name = "comparison",
        .root_source_file = b.path("benchmarks/comparison.zig"),
        .target = target,
        .optimize = .ReleaseFast,
    });
    comparison.root_module.addImport("bplustree", bplustree_module);
    
    const run_comparison = b.addRunArtifact(comparison);
    const comparison_step = b.step("compare", "Run comparison benchmarks");
    comparison_step.dependOn(&run_comparison.step);
}