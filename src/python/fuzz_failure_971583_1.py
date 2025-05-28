"""
Fuzz test failure reproduction
Seed: 971583
Capacity: 3
Failed at operation: 1
"""

from bplus_tree import BPlusTreeMap
from collections import OrderedDict

def reproduce_failure():
    tree = BPlusTreeMap(capacity=3)
    reference = OrderedDict()

    # Operation 1: get
    assert tree.invariants(), "Invariants failed at step 1"

    # Operation 2: update
    tree[1648] = 'value_214529'
    reference[1648] = 'value_214529'
    assert tree.invariants(), "Invariants failed at step 2"

    # Verify final consistency
    assert len(tree) == len(reference), "Length mismatch"
    for key, value in reference.items():
        assert tree[key] == value, f"Value mismatch for {key}"
    print("Reproduction completed successfully")

if __name__ == "__main__":
    reproduce_failure()
