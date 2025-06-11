#!/usr/bin/env python3
"""
Basic usage examples for BPlusTree.

This example demonstrates the fundamental operations you can perform
with the B+ Tree implementation, showing how it works as a drop-in
replacement for Python dictionaries with additional performance benefits.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bplustree import BPlusTreeMap


def main():
    print("=== B+ Tree Basic Usage Examples ===\n")

    # Create a B+ tree with specified capacity
    print("1. Creating a B+ Tree")
    tree = BPlusTreeMap(capacity=16)  # Higher capacity = better performance
    print(f"   Created empty tree with capacity {tree.capacity}")
    print(f"   Length: {len(tree)}")
    print(f"   Is empty: {not bool(tree)}")

    print("\n2. Adding data (dictionary-like syntax)")
    # Use dictionary-like syntax to add data
    tree[1] = "apple"
    tree[5] = "banana"
    tree[3] = "cherry"
    tree[8] = "date"
    tree[2] = "elderberry"

    print(f"   Added 5 items")
    print(f"   Length: {len(tree)}")
    print(f"   Keys are automatically sorted!")

    print("\n3. Accessing data")
    # Get values using dictionary syntax
    print(f"   tree[3] = {tree[3]}")
    print(f"   tree.get(5) = {tree.get(5)}")
    print(f"   tree.get(10, 'not found') = {tree.get(10, 'not found')}")

    # Check if keys exist
    print(f"   3 in tree: {3 in tree}")
    print(f"   10 in tree: {10 in tree}")

    print("\n4. Iterating over data")
    print("   All items (automatically sorted by key):")
    for key, value in tree.items():
        print(f"     {key}: {value}")

    print("\n   Just keys:")
    for key in tree.keys():
        print(f"     {key}")

    print("\n   Just values:")
    for value in tree.values():
        print(f"     {value}")

    print("\n5. Dictionary methods")

    # setdefault - get value or set default
    result = tree.setdefault(10, "fig")
    print(f"   setdefault(10, 'fig'): {result}")
    print(f"   Length now: {len(tree)}")

    # pop - remove and return value
    removed = tree.pop(5)
    print(f"   pop(5): {removed}")
    print(f"   Length now: {len(tree)}")

    # popitem - remove and return arbitrary item (first in B+ tree)
    key, value = tree.popitem()
    print(f"   popitem(): ({key}, {value})")
    print(f"   Length now: {len(tree)}")

    # update - add multiple items at once
    tree.update({15: "grape", 12: "honeydew", 20: "kiwi"})
    print(f"   After update with 3 items, length: {len(tree)}")

    print("\n6. Copying")
    # Create a shallow copy
    tree_copy = tree.copy()
    print(f"   Created copy with {len(tree_copy)} items")

    # Modify original
    tree[100] = "modified"
    print(
        f"   After modifying original: len(tree)={len(tree)}, len(copy)={len(tree_copy)}"
    )

    print("\n7. Removing data")
    del tree[3]  # Remove specific key
    print(f"   Removed key 3, length: {len(tree)}")

    try:
        del tree[999]  # Try to remove non-existent key
    except KeyError:
        print("   KeyError raised when trying to remove non-existent key (as expected)")

    print("\n8. Clearing all data")
    print(f"   Before clear: {len(tree)} items")
    tree.clear()
    print(f"   After clear: {len(tree)} items")
    print(f"   Copy still has: {len(tree_copy)} items")

    print("\n9. Performance characteristics")
    print("   B+ Tree excels at:")
    print("   - Range queries (tree.items(start, end))")
    print("   - Sequential iteration (ordered keys)")
    print("   - Large datasets (10k+ items)")
    print("   - Scenarios requiring sorted key access")

    # Demonstrate range queries
    print("\n10. Range queries (B+ Tree specialty)")

    # Add some data for range demo
    for i in range(1, 21):
        tree[i] = f"item_{i}"

    print("    All items from 5 to 15:")
    for key, value in tree.range(5, 16):  # 16 is exclusive
        print(f"      {key}: {value}")

    print("\n    All items from 10 onwards:")
    count = 0
    for key, value in tree.range(10, None):
        print(f"      {key}: {value}")
        count += 1
        if count >= 5:  # Limit output
            print("      ...")
            break

    print(f"\n=== Basic usage complete! ===")
    print(f"Final tree has {len(tree)} items")


if __name__ == "__main__":
    main()
