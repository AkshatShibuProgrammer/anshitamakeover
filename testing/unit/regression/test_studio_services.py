"""
REG-AREA-08 · Studio service CRUD regression tests.

Covers GET/POST /api/admin/studio-service/ — signature service disciplines
with pricing, discount price, bundle note, features inclusions, image and
look-group linkage.

Test case IDs: TC-SSV-001 … TC-SSV-009
"""
from core.models import StudioService

from .base import RegressionTestCase


class StudioServiceListTests(RegressionTestCase):
    seed_dataset = True

    def test_tc_ssv_001_list_requires_login(self):
        """TC-SSV-001: anonymous list is redirected."""
        self.assert_redirect_to_login(self.client.get('/api/admin/studio-service/'),
                                      '/api/admin/studio-service/')

    def test_tc_ssv_002_list_payload_shape(self):
        """TC-SSV-002: listing serialises every management field."""
        self.login_admin()
        data = self.json_response(self.client.get('/api/admin/studio-service/'))
        svc = next(s for s in data['services'] if s['category'] == 'bridal')
        for key in ['id', 'title', 'discipline', 'category', 'price', 'discount_price',
                    'bundle_note', 'description', 'features', 'features_list',
                    'display_image', 'look_group_id', 'order', 'is_active']:
            self.assertIn(key, svc, f'studio service payload missing {key}')
        self.assertEqual(svc['features_list'], ['TEMPTU airbrush base', 'Cut-crease artistry', 'Dupatta draping'])


class StudioServiceCreateTests(RegressionTestCase):

    def test_tc_ssv_003_create_full_service(self):
        """TC-SSV-003: create persists all fields including features."""
        self.login_admin()
        resp = self.client.post('/api/admin/studio-service/', {
            'title': 'Sangeet Sparkle Service',
            'discipline': 'SIGNATURE DISCIPLINE 05 · SANGEET NIGHT',
            'category': 'sangeet', 'price': '12000', 'discount_price': '9999',
            'bundle_note': 'Save 20% with full wedding package',
            'description': 'Glitter glam for sangeet nights.',
            'features': 'Shimmer glam\nHair waves\nTouch-up kit',
            'image_url': '/static/core/images/anshita_front.jpg',
            'look_group_id': 'sangeet_group', 'order': '5', 'is_active': '1',
        })
        data = self.assert_ok(resp)
        svc = StudioService.objects.get(id=data['service']['id'])
        self.assertEqual(float(svc.price), 12000.0)
        self.assertEqual(float(svc.discount_price), 9999.0)
        self.assertEqual(svc.get_features_list(), ['Shimmer glam', 'Hair waves', 'Touch-up kit'])
        self.assertEqual(svc.look_group_id, 'sangeet_group')

    def test_tc_ssv_004_auto_discipline(self):
        """TC-SSV-004: missing discipline gets an auto-generated tag."""
        self.login_admin()
        resp = self.client.post('/api/admin/studio-service/', {
            'title': 'No Discipline Service', 'price': '5000', 'description': 'd',
        })
        data = self.assert_ok(resp)
        self.assertIn('SIGNATURE DISCIPLINE', data['service']['discipline'])

    def test_tc_ssv_005_title_required(self):
        """TC-SSV-005: missing title is rejected."""
        self.login_admin()
        resp = self.client.post('/api/admin/studio-service/', {'price': '5000'})
        data = self.json_response(resp)
        self.assertFalse(data['ok'])
        self.assertIn('title', data['error'].lower())

    def test_tc_ssv_006_invalid_numeric_input_tolerated(self):
        """TC-SSV-006: non-numeric price/order degrade gracefully to 0."""
        self.login_admin()
        resp = self.client.post('/api/admin/studio-service/', {
            'title': 'Garbage Numbers', 'price': 'abc', 'discount_price': 'xyz',
            'order': 'not-a-number', 'description': 'd',
        })
        data = self.assert_ok(resp)
        self.assertEqual(data['service']['price'], 0.0)
        self.assertIsNone(data['service']['discount_price'])
        self.assertEqual(data['service']['order'], 0)


class StudioServiceUpdateDeleteTests(RegressionTestCase):
    seed_dataset = True

    def test_tc_ssv_007_update_existing(self):
        """TC-SSV-007: POST with id updates the service in place."""
        self.login_admin()
        svc = StudioService.objects.get(title='Nail Couture Atelier')
        resp = self.client.post('/api/admin/studio-service/', {
            'id': svc.id, 'title': 'Nail Couture Atelier V2', 'category': 'nails',
            'price': '6500', 'description': 'updated', 'features': 'Gel\nArt',
        })
        data = self.assert_ok(resp)
        self.assertEqual(data['service']['title'], 'Nail Couture Atelier V2')
        self.assertEqual(StudioService.objects.filter(title__startswith='Nail Couture').count(), 1)

    def test_tc_ssv_008_delete_form_and_json(self):
        """TC-SSV-008: delete works via form action and JSON body."""
        self.login_admin()
        svc_a = StudioService.objects.get(title='Retired Haldi Service')
        resp = self.client.post('/api/admin/studio-service/', {'action': 'delete', 'id': svc_a.id})
        self.assert_ok(resp)
        self.assertFalse(StudioService.objects.filter(id=svc_a.id).exists())

        svc_b = StudioService.objects.get(title='Nail Couture Atelier')
        resp = self.json_post('/api/admin/studio-service/', {'action': 'delete', 'id': svc_b.id})
        self.assert_ok(resp)
        self.assertFalse(StudioService.objects.filter(id=svc_b.id).exists())

    def test_tc_ssv_009_update_missing_service(self):
        """TC-SSV-009: editing a non-existent id returns ok=False."""
        self.login_admin()
        resp = self.client.post('/api/admin/studio-service/', {
            'id': 999999, 'title': 'Ghost', 'price': '100',
        })
        data = self.json_response(resp)
        self.assertFalse(data['ok'])
