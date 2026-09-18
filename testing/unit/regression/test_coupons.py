"""
REG-AREA-02 · Coupon & VIP privilege regression tests.

Covers the three coupon layers described in the README:
1. Auto-rotating seasonal coupon (date-of-month logic: days 1–10 / 11–20 / 21–31)
2. Exit-intent secret coupon
3. Default auto-applied "Today's VIP" coupon
Plus admin control: update all settings, generate/revoke VIP codes.

Test case IDs: TC-CPN-001 … TC-CPN-018
"""
from datetime import date
from unittest import mock

from core.views.common import get_active_coupon
from features.coupon_ops.coupon_service import calculate_active_coupon

from .base import RegressionTestCase


def fake_date(day):
    """Return a patch-friendly fake for the ``date`` symbol in a module.

    Uses October (31 days) so day 31 is valid.
    """
    class FakeDate(date):
        @classmethod
        def today(cls):
            return date(2026, 10, day)
    return FakeDate


class AutoRotationCouponTests(RegressionTestCase):
    """TC-CPN-001..005 — date-based auto coupon rotation."""

    def _expect(self, day, code, discount):
        self.ensure_settings(coupon_active=True, coupon_auto_by_date=True)
        with mock.patch('core.views.common.date', fake_date(day)):
            coupon = get_active_coupon(self.refresh_settings())
        self.assertEqual(coupon['code'], code)
        self.assertEqual(coupon['discount'], discount)
        return coupon

    def test_tc_cpn_001_days_1_to_10(self):
        """TC-CPN-001: days 1–10 serve GLAMOUR30 (30%)."""
        self._expect(1, 'GLAMOUR30', 30)
        self._expect(10, 'GLAMOUR30', 30)

    def test_tc_cpn_002_days_11_to_20(self):
        """TC-CPN-002: days 11–20 serve GLAM50 (50%)."""
        self._expect(11, 'GLAM50', 50)
        self._expect(20, 'GLAM50', 50)

    def test_tc_cpn_003_days_21_to_31(self):
        """TC-CPN-003: days 21–31 serve ANSHITA10 (10%)."""
        self._expect(21, 'ANSHITA10', 10)
        self._expect(31, 'ANSHITA10', 10)

    def test_tc_cpn_004_manual_coupon_when_auto_off(self):
        """TC-CPN-004: auto-rotation off → admin-configured coupon is served."""
        self.ensure_settings(coupon_active=True, coupon_auto_by_date=False,
                             coupon_code='CUSTOM25', coupon_discount_percent=25,
                             coupon_label='Custom Season Offer')
        coupon = get_active_coupon(self.refresh_settings())
        self.assertEqual(coupon, {'code': 'CUSTOM25', 'discount': 25, 'label': 'Custom Season Offer'})

    def test_tc_cpn_005_coupons_disabled(self):
        """TC-CPN-005: coupon_active=False → no coupon anywhere."""
        self.ensure_settings(coupon_active=False)
        self.assertIsNone(get_active_coupon(self.refresh_settings()))
        self.assertIsNone(calculate_active_coupon(self.refresh_settings()))

    def test_tc_cpn_006_service_layer_matches_view_layer(self):
        """TC-CPN-006: coupon_ops.calculate_active_coupon mirrors views.common."""
        self.ensure_settings(coupon_active=True, coupon_auto_by_date=True)
        for day in (5, 15, 25):
            with mock.patch('features.coupon_ops.coupon_service.date', fake_date(day)), \
                 mock.patch('core.views.common.date', fake_date(day)):
                s = self.refresh_settings()
                self.assertEqual(calculate_active_coupon(s), get_active_coupon(s))


class CouponApiTests(RegressionTestCase):
    """TC-CPN-007..010 — public GET /api/coupon/."""

    def test_tc_cpn_007_full_payload(self):
        """TC-CPN-007: public API returns seasonal + default + exit coupons."""
        self.ensure_settings(coupon_auto_by_date=False, coupon_code='WEDDING20',
                             coupon_discount_percent=20)
        data = self.json_response(self.client.get('/api/coupon/'))
        self.assertTrue(data['ok'])
        self.assertEqual(data['coupon']['code'], 'WEDDING20')
        self.assertEqual(data['coupon']['discount'], 20)
        self.assertEqual(data['default_coupon']['code'], 'TODAYVIP')
        self.assertEqual(data['default_coupon']['discount'], 15)
        self.assertEqual(data['exit_coupon']['code'], 'SECRET10')
        self.assertTrue(data['exit_coupon']['active'])

    def test_tc_cpn_008_disabled_layers_omitted(self):
        """TC-CPN-008: disabled layers come back as None."""
        self.ensure_settings(coupon_active=False, exit_coupon_active=False,
                             default_auto_coupon_active=False)
        data = self.json_response(self.client.get('/api/coupon/'))
        self.assertIsNone(data['coupon'])
        self.assertIsNone(data['exit_coupon'])
        self.assertIsNone(data['default_coupon'])

    def test_tc_cpn_009_auto_rotation_visible_through_api(self):
        """TC-CPN-009: date rotation logic reachable via HTTP API."""
        self.ensure_settings(coupon_auto_by_date=True)
        with mock.patch('features.coupon_ops.coupon_service.date', fake_date(12)):
            data = self.json_response(self.client.get('/api/coupon/'))
        self.assertEqual(data['coupon']['code'], 'GLAM50')

    def test_tc_cpn_010_cors_header_on_public_api(self):
        """TC-CPN-010: coupon API carries CORS allow-all header."""
        resp = self.client.get('/api/coupon/')
        self.assertEqual(resp.headers.get('Access-Control-Allow-Origin'), '*')


class AdminCouponUpdateTests(RegressionTestCase):
    """TC-CPN-011..015 — POST /api/admin/coupon/."""

    def test_tc_cpn_011_requires_login(self):
        """TC-CPN-011: anonymous admin coupon update is rejected."""
        resp = self.json_post('/api/admin/coupon/', {'coupon_code': 'X'})
        self.assert_redirect_to_login(resp, '/api/admin/coupon/')

    def test_tc_cpn_012_update_seasonal_coupon(self):
        """TC-CPN-012: admin can change seasonal coupon settings."""
        self.login_admin()
        data = self.assert_ok(self.json_post('/api/admin/coupon/', {
            'coupon_active': '1', 'coupon_auto_by_date': '0',
            'coupon_code': 'diwali50', 'coupon_discount_percent': '50',
            'coupon_label': 'Diwali Dhamaka',
        }))
        self.assertEqual(data['coupon_code'], 'diwali50')
        s = self.refresh_settings()
        self.assertEqual(s.coupon_code, 'diwali50')
        self.assertEqual(s.coupon_discount_percent, 50)
        self.assertFalse(s.coupon_auto_by_date)

    def test_tc_cpn_013_update_exit_and_default_coupons(self):
        """TC-CPN-013: exit-intent and default auto coupons are admin editable."""
        self.login_admin()
        self.assert_ok(self.json_post('/api/admin/coupon/', {
            'exit_coupon_active': '1', 'exit_coupon_code': 'comeback15',
            'exit_coupon_discount_percent': '15', 'exit_coupon_label': 'Comeback treat',
            'default_auto_coupon_active': '1', 'default_auto_coupon_code': 'todayvip20',
            'default_auto_coupon_discount': '20', 'default_auto_coupon_type': 'percent',
            'default_auto_coupon_badge': 'New badge text',
        }))
        s = self.refresh_settings()
        self.assertEqual(s.exit_coupon_code, 'COMEBACK15')
        self.assertEqual(s.exit_coupon_discount_percent, 15)
        self.assertEqual(s.default_auto_coupon_code, 'TODAYVIP20')
        self.assertEqual(s.default_auto_coupon_discount, 20)
        self.assertEqual(s.default_auto_coupon_badge, 'New badge text')

    def test_tc_cpn_014_generate_vip_code(self):
        """TC-CPN-014: VIP code generation persists to settings JSON list."""
        self.login_admin()
        data = self.assert_ok(self.json_post('/api/admin/coupon/', {
            'action': 'generate_vip', 'code': 'vipqueen', 'discount': 25,
            'discount_type': 'percent', 'client_name': 'Royal Bride',
            'notes': 'Concierge privilege',
        }))
        self.assertEqual(data['vip']['code'], 'VIPQUEEN')
        self.assertEqual(data['vip']['discount'], 25)
        self.assertEqual(data['vip']['client_name'], 'Royal Bride')
        self.assertEqual(len(data['vip_list']), 1)
        import json
        stored = json.loads(self.refresh_settings().vip_generated_codes)
        self.assertEqual(stored[0]['code'], 'VIPQUEEN')

    def test_tc_cpn_015_generate_vip_auto_code(self):
        """TC-CPN-015: omitting code auto-generates VIP-XXX-XX format."""
        self.login_admin()
        data = self.assert_ok(self.json_post('/api/admin/coupon/', {'action': 'generate_vip'}))
        self.assertTrue(data['vip']['code'].startswith('VIP-'))

    def test_tc_cpn_016_delete_vip_code(self):
        """TC-CPN-016: VIP revocation removes code from stored list."""
        self.login_admin()
        self.json_post('/api/admin/coupon/', {'action': 'generate_vip', 'code': 'REVOKE1'})
        self.json_post('/api/admin/coupon/', {'action': 'generate_vip', 'code': 'KEEP1'})
        data = self.assert_ok(self.json_post('/api/admin/coupon/',
                                             {'action': 'delete_vip', 'code': 'REVOKE1'}))
        codes = [v['code'] for v in data['vip_list']]
        self.assertNotIn('REVOKE1', codes)
        self.assertIn('KEEP1', codes)

    def test_tc_cpn_017_get_not_allowed(self):
        """TC-CPN-017: GET on admin coupon endpoint answers ok=False."""
        self.login_admin()
        data = self.json_response(self.client.get('/api/admin/coupon/'))
        self.assertFalse(data['ok'])

    def test_tc_cpn_018_boolean_coercion(self):
        """TC-CPN-018: boolean flags accept '1'/'true'/'on' and reject others."""
        self.login_admin()
        self.assert_ok(self.json_post('/api/admin/coupon/', {'coupon_active': 'true'}))
        self.assertTrue(self.refresh_settings().coupon_active)
        self.assert_ok(self.json_post('/api/admin/coupon/', {'coupon_active': '0'}))
        self.assertFalse(self.refresh_settings().coupon_active)
        self.assert_ok(self.json_post('/api/admin/coupon/', {'coupon_active': 'on'}))
        self.assertTrue(self.refresh_settings().coupon_active)
