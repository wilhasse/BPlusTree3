"""
Fuzz test failure reproduction
Seed: 517372
Capacity: 3
Failed at operation: 0
"""

from bplus_tree import BPlusTreeMap
from collections import OrderedDict

def reproduce_failure():
    tree = BPlusTreeMap(capacity=3)
    reference = OrderedDict()

    # Verify final consistency
    assert len(tree) == len(reference), "Length mismatch"
    for key, value in reference.items():
        assert tree[key] == value, f"Value mismatch for {key}"
    print("Reproduction completed successfully")

if __name__ == "__main__":
    reproduce_failure()
