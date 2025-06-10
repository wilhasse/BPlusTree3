import bplustree_c


def test_data_alignment_default():
    """
    Verify that the root node's data array is cache-line aligned using default capacity.
    """
    assert bplustree_c._check_data_alignment()


def test_data_alignment_various_capacities():
    """
    Test alignment for a range of capacities to catch edge cases.
    """
    for cap in (4, 8, 16, 32, 64):
        assert bplustree_c._check_data_alignment(
            cap
        ), f"Alignment failed for capacity={cap}"
