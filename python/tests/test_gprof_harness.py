import pytest

pytest.skip(
    "gprof profiling harness (requires custom build with -pg); see docs for setup",
    allow_module_level=True,
)

"""
Profiling harness for BPlusTree C extension using gprof.

To use:
    CFLAGS='-pg -O3 -march=native' LDFLAGS='-pg' pip install -e .
    pytest src/python/tests/test_gprof_harness.py::test_generate_gprof
"""

def test_generate_gprof(tmp_path):
    import subprocess, sys, os

    # Rebuild extension with profiling flags
    env = os.environ.copy()
    env.update({'CFLAGS': env.get('CFLAGS', '') + ' -pg -O3 -march=native',
                'LDFLAGS': env.get('LDFLAGS', '') + ' -pg'})
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-e', '.'], env=env)

    # Run a simple workload to generate gmon.out
    script = tmp_path / 'run_profile.py'
    script.write_text(
        "from bplustree import BPlusTree\n"
        "import random\n"
        "tree = BPlusTree(branching_factor=128)\n"
        "for i in range(10000): tree[i] = i\n"
        "for _ in range(100000): _ = tree[random.randint(0, 9999)]\n"
    )
    subprocess.check_call([sys.executable, str(script)], env=env)
    assert os.path.exists('gmon.out'), "gmon.out file was not generated"