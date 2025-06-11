import gc
import pytest

try:
    from bplustree_c import BPlusTree
except ImportError as e:
    pytest.skip(f"C extension not available: {e}", allow_module_level=True)


def test_gc_collects_self_referencing_tree():
    """The BPlusTree should be trackable by GC and cycles should be collected."""
    gc.collect()
    tree = BPlusTree()
    # Create a cycle: tree contains itself as a value
    tree[0] = tree
    tree_id = id(tree)
    # Tree must participate in GC tracking
    assert any(tree is obj for obj in gc.get_objects())
    del tree
    gc.collect()

    # After GC, the self-referenced tree should be collected
    assert not any(obj_id == tree_id for obj_id in map(id, gc.get_objects()))
