"""
Shared pytest fixtures for the API contract suite (testing/api) and the
Playwright E2E suite (testing/e2e).

``live_base_url`` boots a real ``manage.py runserver`` against a scratch
database seeded with the canonical regression dataset, so both suites
exercise the genuine HTTP stack (middleware, CORS, CSRF, templates).

Run via the master program (``python testing/run_all.py``) or directly::

    python -m pytest testing/api -v            # API contract suite
    python -m pytest testing/e2e -v            # Playwright E2E (needs browsers)

Ports default per-suite via AUTOMATION_PORT (set by the master program).
"""
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
DJANGO_DIR = REPO_ROOT / 'django'
VENV_PY = Path(os.environ.get('AUTOMATION_PYTHON', sys.executable))
HOST = '127.0.0.1'
PORT = int(os.environ.get('AUTOMATION_PORT', '8111'))
BASE_URL = f'http://{HOST}:{PORT}'

ADMIN_USERNAME = 'regadmin'
ADMIN_PASSWORD = 'RegTest@2026'


def _port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.4)
        return s.connect_ex((HOST, port)) == 0


def _ensure_seeded_db():
    """Create + seed the scratch db if it doesn't exist yet."""
    db_path = DJANGO_DIR / 'db.sqlite3'
    env = dict(os.environ)
    if not db_path.exists():
        subprocess.run([str(VENV_PY), 'manage.py', 'migrate', '--no-input'],
                       cwd=DJANGO_DIR, check=True, env=env,
                       capture_output=True)
        subprocess.run([str(VENV_PY), 'manage.py', 'seed_test_data'],
                       cwd=DJANGO_DIR, check=True, env=env,
                       capture_output=True)


@pytest.fixture(scope='session')
def live_base_url():
    """Session-scoped running Django server with the regression dataset."""
    _ensure_seeded_db()
    proc = subprocess.Popen(
        [str(VENV_PY), 'manage.py', 'runserver', f'{HOST}:{PORT}', '--noreload',
         '--insecure'],
        cwd=DJANGO_DIR,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    deadline = time.time() + 30
    ready = False
    while time.time() < deadline:
        if proc.poll() is not None:
            out = proc.stdout.read().decode() if proc.stdout else ''
            raise RuntimeError(f'runserver died during startup:\n{out[-2000:]}')
        if _port_open(PORT):
            try:
                r = requests.get(f'{BASE_URL}/api/coupon/', timeout=2)
                if r.status_code == 200:
                    ready = True
                    break
            except requests.RequestException:
                pass
        time.sleep(0.3)
    if not ready:
        proc.terminate()
        raise RuntimeError('Live server did not become ready within 30s')

    yield BASE_URL

    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


class CsrfSession(requests.Session):
    """requests.Session that mimics the browser's CSRF behaviour.

    Django's CsrfViewMiddleware demands the csrftoken cookie value on every
    mutating request; this session warms the cookie via a GET and then stamps
    ``X-CSRFToken`` + ``Referer`` onto all POST/PUT/DELETE calls, exactly like
    the site's own fetch() wrappers do.
    """

    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url.rstrip('/')
        # warm-up requests so Django sets the csrftoken cookie; the admin
        # login page is public and renders a CSRF-protected form, guaranteeing
        # the cookie is minted regardless of template-level token usage.
        r = super().get(f'{self.base_url}/', timeout=15)
        r.raise_for_status()
        if not self.cookies.get('csrftoken'):
            r = super().get(f'{self.base_url}/admin-login/', timeout=15)
            r.raise_for_status()
        assert self.cookies.get('csrftoken'), 'csrftoken cookie never minted'

    def request(self, method, url, **kwargs):
        method_up = method.upper()
        if method_up in ('POST', 'PUT', 'PATCH', 'DELETE'):
            headers = kwargs.setdefault('headers', {})
            csrf = self.cookies.get('csrftoken')
            if csrf:
                headers.setdefault('X-CSRFToken', csrf)
                headers.setdefault('Referer', self.base_url + '/')
            kwargs.setdefault('timeout', 20)
        return super().request(method, url, **kwargs)


class AdminSession(CsrfSession):
    """CSRF-aware session logged into the admin portal."""

    def __init__(self, base_url, username=ADMIN_USERNAME, password=ADMIN_PASSWORD):
        super().__init__(base_url)
        # Fetch the login page (re-warms csrftoken) then authenticate.
        self.get(f'{self.base_url}/admin-login/', timeout=10)
        resp = self.post(
            f'{self.base_url}/admin-login/',
            data={'username': username, 'password': password},
            allow_redirects=False, timeout=10,
        )
        assert resp.status_code == 302 and '/admin-portal/' in resp.headers.get('Location', ''), \
            f'Admin login failed: {resp.status_code} {resp.headers.get("Location")}'

    def api_post(self, path, payload):
        """JSON POST to an admin API."""
        import json
        return self.post(f'{self.base_url}{path}', data=json.dumps(payload),
                         headers={'Content-Type': 'application/json'})

    def api_delete(self, path, payload):
        import json
        return self.request('DELETE', f'{self.base_url}{path}', data=json.dumps(payload),
                            headers={'Content-Type': 'application/json'})


@pytest.fixture(scope='session')
def admin_session(live_base_url):
    return AdminSession(live_base_url)


@pytest.fixture(scope='session')
def anon_session(live_base_url):
    """Anonymous CSRF-aware session (mirrors a visitor's browser)."""
    return CsrfSession(live_base_url)
