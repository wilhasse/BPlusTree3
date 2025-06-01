"""
Pytest configuration for building the C extension in-place before tests.
"""
import sys
import subprocess
from pathlib import Path

# Ensure the C extension built in this directory is importable
sys.path.insert(0, str(Path(__file__).parent))

def pytest_sessionstart(session):
    """Build the C extension in-place using the current Python interpreter."""
    here = Path(__file__).parent
    cmd = [sys.executable, 'setup.py', 'build_ext', '--inplace']
    subprocess.check_call(cmd, cwd=str(here))