import gc
import weakref

from bplustree_c import BPlusTree

def test_gc_collects_self_referencing_tree():
    """Self-referencing BPlusTree instances should be collected by the GC."""
    tree = BPlusTree()
    # Create a cycle: tree contains itself as a value
    tree[0] = tree
    ref = weakref.ref(tree)
    # Remove local reference and trigger GC
    del tree
    gc.collect()

    assert ref() is None, "Self-referencing BPlusTree should be freed after gc.collect()"