"""
REG-AREA-06 · Event & partner add-on package CRUD regression tests.

Covers GET/POST/DELETE /api/admin/event-package/ — vendor cost vs client
quote, commission / margin / ROI maths returned on every write.

Test case IDs: TC-EVT-001 … TC-EVT-009
"""
from core.models import EventPackage

from .base import RegressionTestCase


class EventPackageListTests(RegressionTestCase):
    seed_dataset = True

    def test_tc_evt_001_list_requires_login(self):
        """TC-EVT-001: anonymous list request is redirected."""
        self.assert_redirect_to_login(self.client.get('/api/admin/event-package/'),
                                      '/api/admin/event-package/')

    def test_tc_evt_002_list_contains_computed_fields(self):
        """TC-EVT-002: listing includes commission/margin/ROI for every package."""
        self.login_admin()
        data = self.json_response(self.client.get('/api/admin/event-package/'))
        self.assertIn('packages', data)
        premium = next(p for p in data['packages'] if p['package_type'] == 'photography_premium')
        self.assertEqual(premium['commission'], 30000.0)   # 120000 - 90000
        self.assertEqual(premium['margin_pct'], 25.0)
        self.assertEqual(premium['roi_pct'], 33.3)
        self.assertEqual(premium['category_display'], '📸 Photography & Cinematography')


class EventPackageCreateTests(RegressionTestCase):

    def test_tc_evt_003_create_full_package(self):
        """TC-EVT-003: create returns computed margin and persists all fields."""
        self.login_admin()
        data = self.assert_ok(self.json_post('/api/admin/event-package/', {
            'name': 'Bespoke Royal Photography & Stage Decor', 'category': 'photography',
            'package_type': 'custom', 'description': 'Curated partner addon',
            'features': 'Cinematic 4K Wedding Film\n2 Candid Photographers',
            'vendor_cost': '50000', 'price': '68000', 'is_active': True, 'is_featured': True,
        }))
        self.assertEqual(data['commission'], 18000.0)
        self.assertAlmostEqual(data['margin_pct'], 26.5, places=1)
        self.assertAlmostEqual(data['roi_pct'], 36.0, places=1)
        pkg = EventPackage.objects.get(id=data['id'])
        self.assertEqual(pkg.name, 'Bespoke Royal Photography & Stage Decor')
        self.assertEqual(pkg.price_label, '₹68,000')
        self.assertEqual(pkg.created_by.username, 'regadmin')

    def test_tc_evt_004_create_on_request_package(self):
        """TC-EVT-004: empty price creates an On-Request package."""
        self.login_admin()
        data = self.assert_ok(self.json_post('/api/admin/event-package/', {
            'name': 'Mystery Decor', 'category': 'decor', 'vendor_cost': '', 'price': '',
        }))
        pkg = EventPackage.objects.get(id=data['id'])
        self.assertIsNone(pkg.price)
        self.assertEqual(pkg.price_label, 'On Request')

    def test_tc_evt_005_update_existing(self):
        """TC-EVT-005: POST with id updates the existing row."""
        self.login_admin()
        pkg = EventPackage.objects.create(name='Old Name', category='dj', package_type='custom',
                                          vendor_cost=10000, price=20000)
        data = self.assert_ok(self.json_post('/api/admin/event-package/', {
            'id': pkg.id, 'name': 'New DJ Bundle', 'category': 'dj',
            'package_type': 'custom', 'vendor_cost': '12000', 'price': '30000',
        }))
        self.assertEqual(data['id'], pkg.id)
        self.assertEqual(EventPackage.objects.count(), 1)
        pkg.refresh_from_db()
        self.assertEqual(pkg.name, 'New DJ Bundle')
        self.assertEqual(data['commission'], 18000.0)

    def test_tc_evt_006_update_missing_id_404ish(self):
        """TC-EVT-006: updating a non-existent id returns ok=False."""
        self.login_admin()
        data = self.json_response(self.json_post('/api/admin/event-package/', {
            'id': 999999, 'name': 'Ghost',
        }))
        self.assertFalse(data['ok'])


class EventPackageDeleteTests(RegressionTestCase):

    def test_tc_evt_007_delete(self):
        """TC-EVT-007: DELETE removes the package."""
        self.login_admin()
        pkg = EventPackage.objects.create(name='Temp', category='dj', package_type='custom')
        resp = self.client.delete('/api/admin/event-package/',
                                  data='{"id": %d}' % pkg.id, content_type='application/json')
        self.assert_ok(resp)
        self.assertFalse(EventPackage.objects.filter(id=pkg.id).exists())

    def test_tc_evt_008_commission_guard_on_loss_pricing(self):
        """TC-EVT-008: quoting below vendor cost reports zero commission."""
        self.login_admin()
        data = self.assert_ok(self.json_post('/api/admin/event-package/', {
            'name': 'Loss Leader', 'category': 'custom', 'vendor_cost': '50000', 'price': '40000',
        }))
        self.assertEqual(data['commission'], 0.0)

    def test_tc_evt_009_form_encoded_body_documented_defect(self):
        """TC-EVT-009 (KNOWN DEFECT KD-001): endpoint is JSON-only.

        A form-encoded POST hits ``json.loads(request.body)`` and raises a 500.
        The admin portal always sends JSON, so production is unaffected; this
        test locks the current behaviour. If the endpoint is hardened to
        tolerate form bodies, update this test to expect 200.
        """
        admin = self.make_admin()
        self.client.login(username='regadmin', password='RegTest@2026')
        tolerant_client = self.client_class(raise_request_exception=False)
        tolerant_client.force_login(admin)
        resp = tolerant_client.post('/api/admin/event-package/', {'name': 'FormPkg'})
        self.assertEqual(resp.status_code, 500)
