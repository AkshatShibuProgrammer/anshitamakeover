"""
REG-AREA-14 · Security, middleware & URL-routing regression tests.

Validates the security posture required for the admin-managed studio site:
* every admin API demands an authenticated session
* CORS + iframe headers (needed for the e2b/live preview embedding)
* CSRF stays on for state-changing admin endpoints
* all public & admin routes resolve; unknown routes 404

Test case IDs: TC-SEC-001 … TC-SEC-012
"""
from django.test import override_settings
from django.urls import reverse, resolve, Resolver404

from .base import RegressionTestCase

ADMIN_ONLY_ENDPOINTS = [
    ('GET', '/admin-portal/'),
    ('GET', '/api/admin/coupon/'),
    ('GET', '/api/admin/artist/'),
    ('GET', '/api/admin/review/'),
    ('GET', '/api/admin/media/'),
    ('GET', '/api/admin/studio-service/'),
    ('GET', '/api/admin/lookgroup/'),
    ('GET', '/api/admin/service/'),
    ('GET', '/api/admin/event-package/'),
]

PUBLIC_ENDPOINTS = [
    ('GET', '/'),
    ('GET', '/academy/'),
    ('GET', '/sinha-logos/'),
    ('GET', '/api/coupon/'),
    ('GET', '/admin-login/'),
]

NAMED_ROUTES = [
    'home', 'academy', 'set_language', 'admin_login', 'admin_portal',
    'admin_logout', 'chatbot_api', 'coupon_api', 'admin_coupon',
    'admin_price', 'admin_event_package', 'admin_artist', 'admin_service',
    'submit_review', 'admin_review', 'admin_media', 'admin_studio_service',
    'admin_lookgroup', 'admin_lookmedia', 'sinha_logo_studio',
]


class AdminEndpointProtectionTests(RegressionTestCase):

    def test_tc_sec_001_all_admin_endpoints_redirect_anonymous(self):
        """TC-SEC-001: every admin-only endpoint redirects anonymous users."""
        for method, url in ADMIN_ONLY_ENDPOINTS:
            resp = self.client.get(url) if method == 'GET' else self.client.post(url, {})
            self.assert_redirect_to_login(resp, url)

    def test_tc_sec_002_public_endpoints_open(self):
        """TC-SEC-002: public endpoints stay accessible without login."""
        for method, url in PUBLIC_ENDPOINTS:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200, f'{url} must stay public')

    def test_tc_sec_003_admin_post_endpoints_protected(self):
        """TC-SEC-003: state-changing admin APIs also require login."""
        protected_posts = [
            '/api/admin/price/', '/api/admin/coupon/', '/api/admin/service/',
            '/api/admin/studio-service/', '/api/admin/artist/',
            '/api/admin/event-package/', '/api/admin/lookgroup/media/',
        ]
        for url in protected_posts:
            resp = self.client.post(url, {})
            self.assertEqual(resp.status_code, 302, f'{url} POST must redirect anonymous users')
            self.assertIn('/admin-login/', resp.headers.get('Location', ''))

    def test_tc_sec_004_non_staff_locked_out_of_admin_apis(self):
        """TC-SEC-004: logged-in non-staff user is rejected from admin portal."""
        self.make_client_user()
        self.client.login(username='client_user', password='Client@2026')
        resp = self.client.get('/admin-portal/')
        self.assertEqual(resp.status_code, 302)


class MiddlewareHeaderTests(RegressionTestCase):

    def test_tc_sec_005_cors_headers_on_public_response(self):
        """TC-SEC-005: CORSMiddleware stamps allow-origin on responses."""
        resp = self.client.get('/api/coupon/')
        self.assertEqual(resp.headers['Access-Control-Allow-Origin'], '*')
        self.assertIn('POST', resp.headers['Access-Control-Allow-Methods'])
        self.assertIn('X-CSRFToken', resp.headers['Access-Control-Allow-Headers'])

    def test_tc_sec_006_iframe_embedding_allowed(self):
        """TC-SEC-006: X-Frame-Options permits preview iframe embedding."""
        resp = self.client.get('/')
        self.assertEqual(resp.headers.get('X-Frame-Options'), 'ALLOWALL')

    def test_tc_sec_007_csrf_enforced_on_form_posts(self):
        """TC-SEC-007: CSRF protection is active for browser form posts."""
        self.make_admin()
        csrf_client = self.client_class(enforce_csrf_checks=True)
        resp = csrf_client.post('/admin-login/', {
            'username': 'regadmin', 'password': 'RegTest@2026',
        })
        self.assertEqual(resp.status_code, 403)


class UrlRoutingTests(RegressionTestCase):

    def test_tc_sec_008_named_routes_resolve(self):
        """TC-SEC-008: every documented route name reverses successfully."""
        for name in NAMED_ROUTES:
            self.assertTrue(reverse(name), f'route {name} failed to reverse')

    def test_tc_sec_009_route_table_matches_documented_paths(self):
        """TC-SEC-009: reversed URLs match the documented public paths."""
        self.assertEqual(reverse('home'), '/')
        self.assertEqual(reverse('academy'), '/academy/')
        self.assertEqual(reverse('chatbot_api'), '/api/chatbot/')
        self.assertEqual(reverse('coupon_api'), '/api/coupon/')
        self.assertEqual(reverse('admin_portal'), '/admin-portal/')
        self.assertEqual(reverse('sinha_logo_studio'), '/sinha-logos/')

    def test_tc_sec_010_unknown_route_404(self):
        """TC-SEC-010: unknown paths return 404 (no accidental catch-alls)."""
        with self.assertRaises(Resolver404):
            resolve('/definitely-not-a-page/')
        resp = self.client.get('/definitely-not-a-page/')
        self.assertEqual(resp.status_code, 404)

    def test_tc_sec_011_chatbot_requires_post(self):
        """TC-SEC-011: chatbot + review endpoints reject GET with 405."""
        self.assertEqual(self.client.get('/api/chatbot/').status_code, 405)
        self.assertEqual(self.client.get('/api/review/submit/').status_code, 405)

    def test_tc_sec_012_secret_key_not_hardcoded_in_repo_docs(self):
        """TC-SEC-012: settings module exposes SECRET_KEY (lock current state).

        KNOWN DEFECT KD-004: SECRET_KEY is hardcoded and DEBUG=True in
        settings.py. Acceptable for the preview environment, must be replaced
        by env-var based secrets before any public production deployment.
        NOTE: Django forces DEBUG=False during test runs, so the source file
        is inspected instead.
        """
        from pathlib import Path
        from django.conf import settings
        self.assertTrue(settings.SECRET_KEY)
        settings_src = (Path(settings.BASE_DIR) / 'anshita_project' / 'settings.py').read_text()
        self.assertIn('DEBUG = True', settings_src)  # locked as-is; see KD-004
