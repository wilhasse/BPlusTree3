import os
import pytest

def test_no_unsafe_compile_flags():
    if os.environ.get('BPLUSTREE_C_FAST_MATH'):
        pytest.fail('BPLUSTREE_C_FAST_MATH is set; unsafe compile flag used')
    if os.environ.get('BPLUSTREE_C_MARCH_NATIVE'):
        pytest.fail('BPLUSTREE_C_MARCH_NATIVE is set; unsafe compile flag used')