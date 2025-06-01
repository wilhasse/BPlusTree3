import sys
import shutil
import importlib
from pathlib import Path

import pytest

def test_extension_import_error_triggers_python_fallback(tmp_path, monkeypatch):
    # Copy the package to a temporary directory to avoid tampering with original files
    pkg_src = Path(__file__).parent.parent
    pkg_copy = tmp_path / "bplustree"
    shutil.copytree(pkg_src, pkg_copy)

    # Remove compiled extension files to force ImportError for bplustree_c
    for f in pkg_copy.glob("bplustree_c*.so"):
        f.unlink()

    # Prepend the temp directory so imports use the copied package
    monkeypatch.syspath_prepend(str(tmp_path))
    # Remove original package path to prevent importing the compiled extension
    orig_pkg = str(pkg_src)
    if orig_pkg in sys.path:
        sys.path.remove(orig_pkg)

    # Ensure fresh import without leftover modules
    for mod in ("bplustree", "bplustree_c"):
        sys.modules.pop(mod, None)
    importlib.invalidate_caches()

    # Import package and verify fallback to pure Python implementation
    import bplustree

    assert bplustree.get_implementation() == "Pure Python"