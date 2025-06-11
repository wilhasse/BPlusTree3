#!/usr/bin/env python3
"""
Range query examples for BPlusTree.

This example demonstrates the B+ Tree's powerful range query capabilities,
which are one of its key advantages over standard dictionaries and many
other data structures.
"""

import sys
import os
import random
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bplustree import BPlusTreeMap


def demo_basic_range_queries():
    """Demonstrate basic range query functionality."""
    print("=== Basic Range Queries ===\n")

    tree = BPlusTreeMap(capacity=8)

    # Add some test data
    data = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }
    tree.update(data)

    print("Full dataset:")
    for key, value in tree.items():
        print(f"  {key}: {value}")

    print("\n1. Range queries with start and end")
    print("   Months 3-6 (Spring/Early Summer):")
    for key, value in tree.range(3, 7):  # End is exclusive
        print(f"     {key}: {value}")

    print("\n2. Open-ended ranges")
    print("   From month 9 onwards (Fall/Winter):")
    for key, value in tree.range(9, None):
        print(f"     {key}: {value}")

    print("\n   Up to month 3 (Winter/Early Spring):")
    for key, value in tree.range(None, 4):  # End is exclusive
        print(f"     {key}: {value}")

    print("\n3. Single month 'range':")
    for key, value in tree.range(6, 7):  # Just June
        print(f"     {key}: {value}")


def demo_practical_use_cases():
    """Show practical real-world use cases for range queries."""
    print("\n=== Practical Use Cases ===\n")

    # Scenario 1: Time-series data
    print("1. Time-series data (last 7 days)")
    tree = BPlusTreeMap(capacity=16)

    # Simulate daily metrics
    base_date = datetime.now()
    for i in range(30):  # 30 days of data
        date_key = int((base_date - timedelta(days=i)).timestamp())
        tree[date_key] = {
            "date": (base_date - timedelta(days=i)).strftime("%Y-%m-%d"),
            "users": random.randint(100, 1000),
            "revenue": random.randint(1000, 10000),
        }

    # Get last 7 days (most recent timestamps)
    cutoff = int((base_date - timedelta(days=7)).timestamp())
    print("   Last 7 days of metrics:")
    count = 0
    for timestamp, metrics in tree.range(cutoff, None):
        print(
            f"     {metrics['date']}: {metrics['users']} users, ${metrics['revenue']} revenue"
        )
        count += 1
        if count >= 7:
            break

    # Scenario 2: Score ranges
    print("\n2. Student grade analysis")
    grades_tree = BPlusTreeMap(capacity=8)

    students = [
        ("Alice", 95),
        ("Bob", 67),
        ("Charlie", 89),
        ("Diana", 76),
        ("Eve", 93),
        ("Frank", 54),
        ("Grace", 88),
        ("Henry", 72),
        ("Iris", 91),
        ("Jack", 63),
        ("Kate", 85),
        ("Leo", 79),
    ]

    for name, score in students:
        grades_tree[score] = name

    print("   A grades (90-100):")
    for score, name in grades_tree.range(90, 101):
        print(f"     {name}: {score}")

    print("   B grades (80-89):")
    for score, name in grades_tree.range(80, 90):
        print(f"     {name}: {score}")

    print("   At-risk students (below 70):")
    for score, name in grades_tree.range(None, 70):
        print(f"     {name}: {score}")


def demo_pagination_pattern():
    """Demonstrate pagination using range queries."""
    print("\n=== Pagination Pattern ===\n")

    tree = BPlusTreeMap(capacity=16)

    # Create a dataset of products
    products = []
    for i in range(100):
        product_id = i + 1
        tree[product_id] = {
            "name": f"Product {product_id:03d}",
            "price": random.randint(10, 500),
            "category": random.choice(["Electronics", "Books", "Clothing", "Home"]),
        }

    print("Simulating paginated API responses:")

    def get_page(start_id, page_size):
        """Get a page of products starting from start_id."""
        results = []
        count = 0
        for product_id, product in tree.range(start_id, None):
            results.append((product_id, product))
            count += 1
            if count >= page_size:
                break
        return results

    # Simulate pagination
    page_size = 10
    current_id = 1
    page_num = 1

    while current_id <= 100 and page_num <= 3:  # Show first 3 pages
        page_data = get_page(current_id, page_size)
        print(f"\n   Page {page_num} (starting from ID {current_id}):")

        for product_id, product in page_data:
            print(f"     {product_id}: {product['name']} - ${product['price']}")

        if page_data:
            current_id = page_data[-1][0] + 1  # Next page starts after last item
        page_num += 1

    print(
        f"   ... (showing only first 3 pages of ~{len(tree) // page_size} total pages)"
    )


def demo_performance_comparison():
    """Show performance advantages of range queries."""
    print("\n=== Performance Advantages ===\n")

    tree = BPlusTreeMap(capacity=32)

    # Create larger dataset
    print("Setting up performance test with 10,000 items...")
    for i in range(10000):
        tree[i] = f"item_{i:05d}"

    import time

    # Test 1: Get range of 100 items from middle
    start_time = time.time()
    range_items = list(tree.range(5000, 5100))
    range_time = time.time() - start_time

    print(f"   Range query (100 items): {range_time:.6f} seconds")
    print(f"   Retrieved {len(range_items)} items efficiently")

    # Test 2: Compare with dictionary approach (simulated)
    dict_data = {i: f"item_{i:05d}" for i in range(10000)}

    start_time = time.time()
    dict_range = [(k, v) for k, v in dict_data.items() if 5000 <= k < 5100]
    dict_time = time.time() - start_time

    print(f"   Dictionary scan (100 items): {dict_time:.6f} seconds")
    print(f"   B+ Tree is {dict_time/range_time:.1f}x faster for this range query!")

    # Test 3: Early termination advantage
    print("\n   Early termination test (find first 5 items > 7500):")

    start_time = time.time()
    tree_early = []
    for key, value in tree.range(7500, None):
        tree_early.append((key, value))
        if len(tree_early) >= 5:
            break
    tree_early_time = time.time() - start_time

    start_time = time.time()
    dict_early = []
    for k, v in sorted(dict_data.items()):
        if k >= 7500:
            dict_early.append((k, v))
            if len(dict_early) >= 5:
                break
    dict_early_time = time.time() - start_time

    print(f"     B+ Tree: {tree_early_time:.6f} seconds")
    print(f"     Dict scan: {dict_early_time:.6f} seconds")
    print(f"     B+ Tree is {dict_early_time/tree_early_time:.1f}x faster!")


def main():
    """Run all range query demonstrations."""
    print("🌳 B+ Tree Range Query Examples 🌳\n")

    demo_basic_range_queries()
    demo_practical_use_cases()
    demo_pagination_pattern()
    demo_performance_comparison()

    print("\n=== Summary ===")
    print("Range queries are ideal for:")
    print("• Database-style LIMIT queries")
    print("• Time-series data analysis")
    print("• Pagination in web APIs")
    print("• Score/grade analysis")
    print("• Any scenario requiring ordered subset access")
    print("\nB+ Trees excel when you need fast, ordered access to ranges of data!")


if __name__ == "__main__":
    main()
