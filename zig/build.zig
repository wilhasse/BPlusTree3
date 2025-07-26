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
}