"""
REG-AREA-04 · Admin authentication & authorisation regression tests.

Covers the README promise "Non-technical admin can manage everything from a
simple panel": login page, AJAX login flow, case-insensitive email/username
backend, staff-only enforcement, portal dashboard context, logout.

Test case IDs: TC-AUTH-001 … TC-AUTH-018
"""
from django.contrib.auth.models import User

from core.backends import CaseInsensitiveEmailOrUsernameBackend

from .base import RegressionTestCase


class AdminLoginTests(RegressionTestCase):

    def test_tc_auth_001_login_page_renders(self):
        """TC-AUTH-001: anonymous user gets the login page."""
        resp = self.client.get('/admin-login/')
        self.assertEqual(resp.status_code, 200)

    def test_tc_auth_002_valid_form_login(self):
        """TC-AUTH-002: valid credentials redirect to admin portal."""
        self.make_admin()
        resp = self.client.post('/admin-login/', {
            'username': 'regadmin', 'password': 'RegTest@2026',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/admin-portal/')

    def test_tc_auth_003_invalid_credentials(self):
        """TC-AUTH-003: wrong password re-renders form with error."""
        self.make_admin()
        resp = self.client.post('/admin-login/', {
            'username': 'regadmin', 'password': 'WrongPassword!',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Invalid credentials')

    def test_tc_auth_004_non_staff_rejected(self):
        """TC-AUTH-004: authenticated-but-non-staff user cannot log in via admin form."""
        self.make_client_user()
        resp = self.client.post('/admin-login/', {
            'username': 'client_user', 'password': 'Client@2026',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Invalid credentials')

    def test_tc_auth_005_ajax_login_success(self):
        """TC-AUTH-005: AJAX login returns JSON ok + redirect target."""
        self.make_admin()
        resp = self.client.post('/admin-login/', {
            'username': 'regadmin', 'password': 'RegTest@2026',
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = self.json_response(resp)
        self.assertTrue(data['ok'])
        self.assertEqual(data['redirect'], '/admin-portal/')

    def test_tc_auth_006_ajax_login_failure(self):
        """TC-AUTH-006: AJAX login failure returns 401 JSON error."""
        self.make_admin()
        resp = self.client.post('/admin-login/', {
            'username': 'regadmin', 'password': 'nope',
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(resp.status_code, 401)
        data = resp.json()
        self.assertFalse(data['ok'])
        self.assertIn('error', data)

    def test_tc_auth_007_next_param_respected(self):
        """TC-AUTH-007: ?next= is honoured after successful login."""
        self.make_admin()
        resp = self.client.post('/admin-login/?next=/academy/', {
            'username': 'regadmin', 'password': 'RegTest@2026',
        })
        self.assertEqual(resp.headers['Location'], '/academy/')

    def test_tc_auth_008_already_authenticated_redirect(self):
        """TC-AUTH-008: visiting login page while logged in goes to portal."""
        self.login_admin()
        resp = self.client.get('/admin-login/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/admin-portal/', resp.headers['Location'])


class CaseInsensitiveBackendTests(RegressionTestCase):

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username='AnshitaAdmin', email='Admin@AnshitaMakeover.test', password='Secret@123',
        )
        self.user.is_staff = True
        self.user.save()
        self.backend = CaseInsensitiveEmailOrUsernameBackend()

    def test_tc_auth_009_exact_username(self):
        """TC-AUTH-009: exact username still authenticates."""
        self.assertEqual(self.backend.authenticate(None, username='AnshitaAdmin',
                                                   password='Secret@123'), self.user)

    def test_tc_auth_010_case_insensitive_username(self):
        """TC-AUTH-010: username matching is case-insensitive."""
        self.assertEqual(self.backend.authenticate(None, username='anshitaadmin',
                                                   password='Secret@123'), self.user)

    def test_tc_auth_011_email_login(self):
        """TC-AUTH-011: email address can be used as the login identifier."""
        self.assertEqual(self.backend.authenticate(None, username='admin@anshitamakeover.test',
                                                   password='Secret@123'), self.user)

    def test_tc_auth_012_whitespace_tolerated(self):
        """TC-AUTH-012: leading/trailing whitespace stripped from identifier & password."""
        self.assertEqual(self.backend.authenticate(None, username='  AnshitaAdmin  ',
                                                   password='  Secret@123  '), self.user)

    def test_tc_auth_013_wrong_password(self):
        """TC-AUTH-013: wrong password returns None."""
        self.assertIsNone(self.backend.authenticate(None, username='AnshitaAdmin',
                                                    password='Wrong@123'))

    def test_tc_auth_014_missing_credentials(self):
        """TC-AUTH-014: missing username/password safely returns None."""
        self.assertIsNone(self.backend.authenticate(None, username='', password='x'))
        self.assertIsNone(self.backend.authenticate(None, username='AnshitaAdmin', password=''))


class AdminPortalAccessTests(RegressionTestCase):
    seed_dataset = True

    def test_tc_auth_015_anonymous_redirected(self):
        """TC-AUTH-015: anonymous portal visit redirects to login with ?next=."""
        resp = self.client.get('/admin-portal/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/admin-login/', resp.headers['Location'])
        self.assertIn('next=/admin-portal/', resp.headers['Location'])

    def test_tc_auth_016_non_staff_redirected(self):
        """TC-AUTH-016: logged-in non-staff user cannot open the portal."""
        self.make_client_user()
        self.client.login(username='client_user', password='Client@2026')
        resp = self.client.get('/admin-portal/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/admin-login/', resp.headers['Location'])

    def test_tc_auth_017_portal_renders_full_context(self):
        """TC-AUTH-017: staff user gets dashboard with every management dataset."""
        self.login_admin()
        resp = self.client.get('/admin-portal/')
        self.assertEqual(resp.status_code, 200)
        ctx = resp.context
        for key in ['site', 'coupon', 'default_coupon', 'vip_codes', 'services',
                    'look_groups', 'media_items', 'packages', 'reviews',
                    'event_packages', 'courses', 'service_prices', 'artists',
                    'whatsapp', 'travel_settings']:
            self.assertIn(key, ctx, f'admin portal context missing {key}')
        self.assertEqual(ctx['whatsapp'], '917879223442')
        self.assertTrue(ctx['travel_settings']['active'])

    def test_tc_auth_018_logout(self):
        """TC-AUTH-018: logout ends session and redirects home."""
        self.login_admin()
        resp = self.client.get('/admin-logout/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/')
        resp = self.client.get('/admin-portal/')
        self.assertEqual(resp.status_code, 302)  # logged out again
