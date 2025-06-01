"""
Pytest configuration for building the C extension in-place before tests.
"""
import sys
import subprocess
from pathlib import Path

def pytest_sessionstart(session):
    """Build the C extension in-place using the current Python interpreter."""
    here = Path(__file__).parent
    cmd = [sys.executable, 'setup.py', 'build_ext', '--inplace']
    subprocess.check_call(cmd, cwd=str(here))