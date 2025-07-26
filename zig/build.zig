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