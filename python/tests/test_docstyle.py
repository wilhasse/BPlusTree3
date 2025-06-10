import os
import sys
import subprocess

import pytest


def test_pydocstyle_conformance():
    pytest.importorskip("pydocstyle")

    pkg_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    result = subprocess.run(
        [sys.executable, "-m", "pydocstyle", pkg_dir],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert result.returncode == 0, f"pydocstyle violations:\n{result.stdout}"
