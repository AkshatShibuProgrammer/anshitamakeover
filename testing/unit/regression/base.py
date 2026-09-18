"""
Shared base class and helpers for the regression suite.

All regression tests derive from :class:`RegressionTestCase`, which gives:

* ``make_admin() / login_admin()``   – staff superuser session helpers
* ``make_client_user()``              – non-staff user for negative auth tests
* ``json_post()``                     – JSON-body POST helper
* ``ensure_settings()``               – deterministic SiteSettings singleton

Run the whole suite with::

    python testing/unit/run.py -v 2          (via master: --suite unit)
"""
import json

from django.contrib.auth.models import User
from django.test import TestCase

from core.models import SiteSettings

from testdata.factories import (
    ADMIN_USERNAME, ADMIN_PASSWORD,
    CLIENT_USERNAME, CLIENT_PASSWORD,
    build_admin_user, build_client_user, build_site_settings,
)


class RegressionTestCase(TestCase):
    """Base class for all Anshita Makeover regression tests."""

    #: tests that need the whole canonical dataset can set this to True
    seed_dataset = False

    def setUp(self):
        super().setUp()
        if self.seed_dataset:
            from testdata.factories import build_full_dataset
            build_full_dataset()
        else:
            # Most suites only need a deterministic SiteSettings row.
            build_site_settings()

    # ── auth helpers ────────────────────────────────────────────────────
    def make_admin(self, username=ADMIN_USERNAME, password=ADMIN_PASSWORD):
        return build_admin_user(username=username, password=password)

    def login_admin(self, username=ADMIN_USERNAME, password=ADMIN_PASSWORD):
        self.make_admin(username=username, password=password)
        self.assertTrue(
            self.client.login(username=username, password=password),
            'Admin login helper must succeed',
        )

    def make_client_user(self, username=CLIENT_USERNAME, password=CLIENT_PASSWORD):
        return build_client_user(username=username, password=password)

    # ── request helpers ─────────────────────────────────────────────────
    def json_post(self, url, payload, **extra):
        return self.client.post(
            url, data=json.dumps(payload), content_type='application/json', **extra
        )

    def json_response(self, response):
        self.assertEqual(response.status_code, 200, f'{response.request["PATH_INFO"]} -> {response.status_code}')
        return response.json()

    def assert_ok(self, response):
        """Shortcut: endpoint answered 200 with ok=True."""
        data = self.json_response(response)
        self.assertTrue(data.get('ok'), f'Expected ok=True, got {data}')
        return data

    # ── settings helpers ────────────────────────────────────────────────
    def ensure_settings(self, **overrides):
        return build_site_settings(**overrides)

    def refresh_settings(self):
        return SiteSettings.objects.get(id=1)

    # ── assertion helpers ───────────────────────────────────────────────
    def assert_redirect_to_login(self, response, url=''):
        """Admin-only endpoint must bounce anonymous users to /admin-login/."""
        self.assertEqual(response.status_code, 302, f'{url} should redirect anonymous users')
        self.assertIn('/admin-login/', response.headers.get('Location', ''),
                      f'{url} should redirect to admin login')
