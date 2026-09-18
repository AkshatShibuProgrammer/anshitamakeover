"""Shared configuration for all Anshita Makeover test programs."""
import os
from pathlib import Path

TESTING_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTING_DIR.parent
DJANGO_DIR = REPO_ROOT / 'django'

# Ports — each layer gets its own port so parallel runs never collide.
PORT_API = int(os.environ.get('TEST_PORT_API', '8121'))
PORT_E2E = int(os.environ.get('TEST_PORT_E2E', '8122'))
PORT_SHARED = int(os.environ.get('TEST_PORT_SHARED', '8123'))   # bdd/smoke/perf

# Credentials from the canonical test dataset (testing/testdata/factories.py)
ADMIN_USERNAME = 'regadmin'
ADMIN_PASSWORD = 'RegTest@2026'


CORE_REQUIREMENTS = [
    'Django>=5.0,<7.0', 'Pillow', 'requests', 'python-dotenv',
    'pytest', 'pytest-html', 'pytest-playwright', 'playwright',
    'unittest-xml-reporting', 'coverage', 'headroom-ai',
]


def _has_django(py):
    """True only for REAL Django — the project's own ``django/`` folder is an
    implicit namespace package and would fool a bare ``import django`` when
    the current directory is the repository root."""
    import subprocess
    probe = 'import django.core.management, django; print(django.get_version())'
    return subprocess.run([py, '-c', probe], capture_output=True).returncode == 0


def find_python(auto_provision=True):
    """Best available interpreter with Django installed.

    If none exists, bootstrap ``testenv/`` automatically (venv + pip install)
    so the master program works on a fresh clone.
    """
    import shutil
    import subprocess

    if os.environ.get('PYTHON'):
        return os.environ['PYTHON']

    venv_py = REPO_ROOT / 'testenv' / 'bin' / 'python'
    if venv_py.exists() and _has_django(str(venv_py)):
        return str(venv_py)

    system_py = shutil.which('python3') or 'python3'
    if _has_django(system_py):
        return system_py

    if not auto_provision:
        return system_py

    print('[master] No Python with Django found — bootstrapping testenv/ …')
    subprocess.run([system_py, '-m', 'venv', str(REPO_ROOT / 'testenv')], check=True)
    subprocess.run([str(venv_py), '-m', 'pip', 'install', '--quiet',
                    '--upgrade', 'pip'], check=True)
    subprocess.run([str(venv_py), '-m', 'pip', 'install', '--quiet',
                    *CORE_REQUIREMENTS], check=True)
    print('[master] testenv ready.')
    return str(venv_py)
