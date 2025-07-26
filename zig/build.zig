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
}