"""
Setup script for B+ Tree C extension.

Build with: python setup.py build_ext --inplace
"""

from setuptools import setup, Extension
import os

# Default compile flags: safe baseline (-O3 only)
extra_compile_args = [
    '-O3',
    '-Wall',
    '-Wextra',
]

# Opt-in flags for additional optimizations
if os.environ.get('BPLUSTREE_C_FAST_MATH'):
    extra_compile_args.append('-ffast-math')
if os.environ.get('BPLUSTREE_C_MARCH_NATIVE'):
    extra_compile_args.append('-march=native')

# Define the extension module
bplustree_c = Extension(
    'bplustree_c',
    sources=[
        'bplustree_c_src/bplustree_module.c',
        'bplustree_c_src/node_ops.c',
        'bplustree_c_src/tree_ops.c',
    ],
    include_dirs=['bplustree_c_src'],
    extra_compile_args=extra_compile_args,
    define_macros=[
        ('NDEBUG', '1'),  # Disable debug assertions
    ],
)

setup(
    name='bplustree_c',
    version='0.1.0',
    description='High-performance B+ Tree C extension',
    author='Your Name',
    ext_modules=[bplustree_c],
    zip_safe=False,
    python_requires='>=3.6',
)