"""
REG-AREA-07 · Makeup package CRUD regression tests.

Covers GET/POST/DELETE /api/admin/service/ — create, edit, delete and listing
of bridal suites / packages, including 'On Request' pricing and the JSON and
form-encoded payloads the admin portal may send.

Test case IDs: TC-PKG-001 … TC-PKG-011
"""
from core.models import MakeupPackage

from .base import RegressionTestCase


class PackageListTests(RegressionTestCase):
    seed_dataset = True

    def test_tc_pkg_001_list_requires_login(self):
        """TC-PKG-001: anonymous list request is redirected."""
        self.assert_redirect_to_login(self.client.get('/api/admin/service/'), '/api/admin/service/')

    def test_tc_pkg_002_list_returns_all_packages(self):
        """TC-PKG-002: GET returns every package (active and inactive) for admin."""
        self.login_admin()
        data = self.json_response(self.client.get('/api/admin/service/'))
        self.assertEqual(len(data['packages']), MakeupPackage.objects.count())


class PackageCreateTests(RegressionTestCase):

    def test_tc_pkg_003_create_json(self):
        """TC-PKG-003: JSON create with price computes label automatically."""
        self.login_admin()
        data = self.assert_ok(self.json_post('/api/admin/service/', {
            'name': 'Haldi Sunshine Glam', 'package_type': 'party',
            'tagline': 'Golden hour haldi glow', 'price': '8500',
            'features': 'Dewy yellow tones\nFlower jewellery setting', 'is_featured': '1',
        }))
        pkg = MakeupPackage.objects.get(id=data['package']['id'])
        self.assertEqual(pkg.name, 'Haldi Sunshine Glam')
        self.assertEqual(pkg.price_label, '₹8,500')
        self.assertEqual(data['package']['price'], 8500.0)
        self.assertTrue(pkg.is_featured)

    def test_tc_pkg_004_create_form_encoded(self):
        """TC-PKG-004: form-encoded create also works (multipart admin forms)."""
        self.login_admin()
        resp = self.client.post('/api/admin/service/', {
            'name': 'Mehendi Green Muse', 'package_type': 'engagement', 'price': '7000',
            'features': 'Fresh florals',
        })
        data = self.assert_ok(resp)
        self.assertTrue(MakeupPackage.objects.filter(name='Mehendi Green Muse').exists())

    def test_tc_pkg_005_create_on_request(self):
        """TC-PKG-005: blank price yields NULL price + 'On Request' label."""
        self.login_admin()
        data = self.assert_ok(self.json_post('/api/admin/service/', {
            'name': 'Celebrity Custom Suite', 'package_type': 'custom', 'price': '',
            'features': 'Bespoke',
        }))
        pkg = MakeupPackage.objects.get(id=data['package']['id'])
        self.assertIsNone(pkg.price)
        self.assertEqual(pkg.price_label, 'On Request')

    def test_tc_pkg_006_create_requires_name(self):
        """TC-PKG-006: missing name is rejected with a clear error."""
        self.login_admin()
        data = self.json_response(self.json_post('/api/admin/service/', {'price': '5000'}))
        self.assertFalse(data['ok'])
        self.assertIn('name', data['error'].lower())


class PackageUpdateTests(RegressionTestCase):

    def test_tc_pkg_007_update_price_and_features(self):
        """TC-PKG-007: POST with id updates name, price, features."""
        self.login_admin()
        pkg = MakeupPackage.objects.create(name='Old Suite', package_type='bridal',
                                           price=10000, features='old')
        data = self.assert_ok(self.json_post('/api/admin/service/', {
            'id': pkg.id, 'name': 'Renamed Suite', 'package_type': 'bridal',
            'price': '20000', 'features': 'new line one\nnew line two',
        }))
        pkg.refresh_from_db()
        self.assertEqual(pkg.name, 'Renamed Suite')
        self.assertEqual(float(pkg.price), 20000.0)
        self.assertEqual(pkg.price_label, '₹20,000')
        self.assertEqual(pkg.get_features_list(), ['new line one', 'new line two'])

    def test_tc_pkg_008_update_missing_package(self):
        """TC-PKG-008: editing a deleted package returns ok=False."""
        self.login_admin()
        data = self.json_response(self.json_post('/api/admin/service/', {
            'id': 999999, 'name': 'Ghost Suite', 'price': '1000',
        }))
        self.assertFalse(data['ok'])

    def test_tc_pkg_009_deactivate_flag(self):
        """TC-PKG-009: is_active '0' hides package from public site."""
        self.login_admin()
        pkg = MakeupPackage.objects.create(name='Seasonal Suite', package_type='bridal',
                                           price=10000, features='x')
        self.assert_ok(self.json_post('/api/admin/service/', {
            'id': pkg.id, 'name': 'Seasonal Suite', 'is_active': '0',
        }))
        pkg.refresh_from_db()
        self.assertFalse(pkg.is_active)


class PackageDeleteTests(RegressionTestCase):

    def test_tc_pkg_010_delete_via_post_action(self):
        """TC-PKG-010: action=delete in POST body removes package."""
        self.login_admin()
        pkg = MakeupPackage.objects.create(name='Doomed Suite', package_type='bridal',
                                           price=1, features='x')
        self.assert_ok(self.json_post('/api/admin/service/', {'action': 'delete', 'id': pkg.id}))
        self.assertFalse(MakeupPackage.objects.filter(id=pkg.id).exists())

    def test_tc_pkg_011_delete_via_http_delete(self):
        """TC-PKG-011: HTTP DELETE removes package."""
        self.login_admin()
        pkg = MakeupPackage.objects.create(name='Doomed Twice', package_type='bridal',
                                           price=1, features='x')
        resp = self.client.delete('/api/admin/service/',
                                  data='{"id": %d}' % pkg.id, content_type='application/json')
        self.assert_ok(resp)
        self.assertFalse(MakeupPackage.objects.filter(id=pkg.id).exists())
