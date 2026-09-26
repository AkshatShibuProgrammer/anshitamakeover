"""Phase 7 package-builder contract and guardrail tests."""
import json

from core.models import StudioService
from .base import RegressionTestCase


class PackageBuilderTests(RegressionTestCase):
    def make_service(self, **kwargs):
        defaults = dict(title='Test Bridal Look', discipline='TEST', category='bridal',
                        price=10000, description='Test service', is_active=True, order=1)
        defaults.update(kwargs)
        return StudioService.objects.create(**defaults)

    def test_builder_page_is_public(self):
        response = self.client.get('/build-your-look/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Build Your Look')

    def test_recommends_active_services_using_database_prices(self):
        active = self.make_service(price=12345)
        self.make_service(title='Hidden', is_active=False, price=1)
        response = self.json_post('/api/package-builder/', {'categories': ['bridal']})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual([item['id'] for item in payload['items']], [active.id])
        self.assertEqual(payload['subtotal'], 12345.0)
        self.assertEqual(payload['total'], 12345.0)

    def test_budget_excludes_services_that_would_exceed_ceiling(self):
        self.make_service(price=9000, order=1)
        self.make_service(title='Second', price=3000, order=2)
        response = self.json_post('/api/package-builder/', {'budget': 10000})
        payload = response.json()
        self.assertEqual(len(payload['items']), 1)
        self.assertEqual(payload['subtotal'], 9000.0)

    def test_discount_is_clamped_server_side(self):
        self.make_service(price=10000)
        response = self.json_post('/api/package-builder/', {'max_discount': 999})
        payload = response.json()
        self.assertEqual(payload['guardrails']['max_discount_percent'], 50)
        self.assertEqual(payload['discount'], 5000)
        self.assertEqual(payload['total'], 5000.0)

    def test_invalid_json_and_method_are_safe(self):
        response = self.client.post('/api/package-builder/', data='{bad', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response = self.client.get('/api/package-builder/')
        self.assertEqual(response.status_code, 405)
