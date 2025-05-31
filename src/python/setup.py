"""
Setup script for B+ Tree C extension.

Build with: python setup.py build_ext --inplace
"""

from setuptools import setup, Extension
import os

# Define the extension module
bplustree_c = Extension(
    'bplustree_c',
    sources=[
        'bplustree_c/bplustree_module.c',
        'bplustree_c/node_ops.c', 
        'bplustree_c/tree_ops.c'
    ],
    include_dirs=['bplustree_c'],
    extra_compile_args=[
        '-O3',        # Maximum optimization
        '-ffast-math', # Fast math operations
        '-Wall',      # All warnings
        '-Wextra',    # Extra warnings
    ],
    define_macros=[
        ('NDEBUG', '1'),  # Disable debug assertions
    ]
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