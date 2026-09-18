"""
REG-AREA-05 · Pricing, booking-offer rules, travel & AI-negotiation guardrails.

Covers POST /api/admin/price/ — the single endpoint behind the admin panel's
price manager: service prices, course fees, photography packages, booking
privilege rules (free sides / combo / bundle), outstation travel settings and
AI negotiation floor/max-discount guardrails.

Test case IDs: TC-PRC-001 … TC-PRC-019
"""
from core.models import ServicePrice, MakeupPackage, AcademyCourse, EventPackage

from .base import RegressionTestCase


class AdminPriceAuthTests(RegressionTestCase):

    def test_tc_prc_001_requires_login(self):
        """TC-PRC-001: anonymous price update is redirected to login."""
        resp = self.json_post('/api/admin/price/', {'service': 'makeup_hd', 'price': 40000})
        self.assert_redirect_to_login(resp, '/api/admin/price/')

    def test_tc_prc_002_non_staff_rejected(self):
        """TC-PRC-002: logged-in non-staff user cannot touch pricing."""
        self.make_client_user()
        self.client.login(username='client_user', password='Client@2026')
        resp = self.json_post('/api/admin/price/', {'service': 'makeup_hd', 'price': 40000})
        self.assert_redirect_to_login(resp, '/api/admin/price/')


class ServicePriceUpdateTests(RegressionTestCase):

    def test_tc_prc_003_update_existing_service(self):
        """TC-PRC-003: admin updates an existing service price."""
        self.login_admin()
        ServicePrice.objects.create(service='makeup_hd', price=35000)
        data = self.assert_ok(self.json_post('/api/admin/price/', {
            'service': 'makeup_hd', 'price': 40000,
        }))
        self.assertTrue(data['ok'])
        self.assertEqual(float(ServicePrice.objects.get(service='makeup_hd').price), 40000.0)

    def test_tc_prc_004_create_new_service(self):
        """TC-PRC-004: unknown service key is auto-created."""
        self.login_admin()
        self.assert_ok(self.json_post('/api/admin/price/', {
            'service': 'beauty_facial', 'price': 2999,
        }))
        sp = ServicePrice.objects.get(service='beauty_facial')
        self.assertEqual(float(sp.price), 2999.0)

    def test_tc_prc_005_on_request_flag(self):
        """TC-PRC-005: is_on_request flag can be toggled."""
        self.login_admin()
        self.assert_ok(self.json_post('/api/admin/price/', {
            'service': 'tejal_makeup', 'price': 0, 'is_on_request': True,
        }))
        self.assertTrue(ServicePrice.objects.get(service='tejal_makeup').is_on_request)


class CourseAndEventPriceTests(RegressionTestCase):
    seed_dataset = True

    def test_tc_prc_006_course_fee_update(self):
        """TC-PRC-006: academy course fee updated via price endpoint."""
        self.login_admin()
        course = AcademyCourse.objects.get(slug='professional-makeup-artist-program')
        self.assert_ok(self.json_post('/api/admin/price/', {
            'type': 'course', 'course_id': course.id, 'price': 32500,
        }))
        course.refresh_from_db()
        self.assertEqual(float(course.course_fee), 32500.0)

    def test_tc_prc_007_photography_premium_update(self):
        """TC-PRC-007: premium photography price updates with lakh label."""
        self.login_admin()
        self.assert_ok(self.json_post('/api/admin/price/', {
            'type': 'event', 'service': 'photo_premium', 'price': 150000,
        }))
        pkg = EventPackage.objects.get(package_type='photography_premium')
        self.assertEqual(float(pkg.price), 150000.0)
        self.assertEqual(pkg.price_label, '₹1.5 Lakh')

    def test_tc_prc_008_photography_standard_update(self):
        """TC-PRC-008: standard photography price updates with comma label."""
        self.login_admin()
        self.assert_ok(self.json_post('/api/admin/price/', {
            'service': 'photo_standard', 'price': 95000,
        }))
        pkg = EventPackage.objects.get(package_type='photography_standard')
        self.assertEqual(float(pkg.price), 95000.0)
        self.assertEqual(pkg.price_label, '₹95,000')


class BookingOfferRuleTests(RegressionTestCase):
    seed_dataset = True

    def test_tc_prc_009_update_all_offer_rules(self):
        """TC-PRC-009: free sides, subsidized rate, combo %, bundle all saved."""
        self.login_admin()
        data = self.assert_ok(self.json_post('/api/admin/price/', {
            'type': 'booking_offer', 'free_sides': 3, 'discounted_side_price': 3000,
            'combo_discount_percent': 20, 'bundle_price': 55000, 'active': True,
        }))
        self.assertEqual(data['free_sides'], 3)
        self.assertEqual(data['discounted_side_price'], 3000.0)
        self.assertEqual(data['combo_discount_percent'], 20)
        self.assertEqual(data['bundle_price'], 55000.0)
        s = self.refresh_settings()
        self.assertEqual(s.offer_bridal_free_sides, 3)

    def test_tc_prc_010_free_sides_clamped_0_to_5(self):
        """TC-PRC-010: free-sides value is clamped into [0, 5]."""
        self.login_admin()
        self.assert_ok(self.json_post('/api/admin/price/', {'type': 'booking_offer', 'free_sides': 99}))
        self.assertEqual(self.refresh_settings().offer_bridal_free_sides, 5)
        self.assert_ok(self.json_post('/api/admin/price/', {'type': 'booking_offer', 'free_sides': -2}))
        self.assertEqual(self.refresh_settings().offer_bridal_free_sides, 0)

    def test_tc_prc_011_combo_discount_clamped_0_to_30(self):
        """TC-PRC-011: combo discount clamped into [0, 30]."""
        self.login_admin()
        self.assert_ok(self.json_post('/api/admin/price/', {'type': 'booking_offer', 'combo_discount_percent': 80}))
        self.assertEqual(self.refresh_settings().offer_combo_discount_percent, 30)

    def test_tc_prc_012_bundle_price_syncs_grand_royal_package(self):
        """TC-PRC-012: bundle price update syncs the Grand Royal Heritage package row."""
        self.login_admin()
        self.assert_ok(self.json_post('/api/admin/price/', {'type': 'booking_offer', 'bundle_price': 61000}))
        pkg = MakeupPackage.objects.get(name__icontains='Grand Royal Heritage')
        self.assertEqual(float(pkg.price), 61000.0)
        self.assertEqual(pkg.price_label, '₹61,000')

    def test_tc_prc_013_offer_rules_can_be_deactivated(self):
        """TC-PRC-013: offer rules can be switched off entirely."""
        self.login_admin()
        self.assert_ok(self.json_post('/api/admin/price/', {'type': 'booking_offer', 'active': False}))
        self.assertFalse(self.refresh_settings().offer_rules_active)


class TravelSettingsTests(RegressionTestCase):

    def test_tc_prc_014_update_travel_settings(self):
        """TC-PRC-014: outstation travel estimator settings persist."""
        self.login_admin()
        self.assert_ok(self.json_post('/api/admin/price/', {
            'type': 'travel', 'travel_widget_active': True, 'travel_same_zone_km': 120,
            'travel_near_fee_min': 9000, 'travel_near_fee_max': 16000,
            'travel_far_fee_min': 22000, 'travel_far_fee_max': 45000,
            'travel_near_label': 'Near Cities', 'travel_far_label': 'Destination India',
            'travel_custom_note': 'Travel + stay included for 50k+ packages.',
        }))
        s = self.refresh_settings()
        self.assertEqual(s.travel_same_zone_km, 120)
        self.assertEqual(s.travel_near_fee_min, 9000)
        self.assertEqual(s.travel_far_fee_max, 45000)
        self.assertEqual(s.travel_custom_note, 'Travel + stay included for 50k+ packages.')


class AiNegotiationGuardrailTests(RegressionTestCase):
    seed_dataset = True

    def test_tc_prc_015_update_negotiation_settings(self):
        """TC-PRC-015: global AI negotiation settings persist."""
        self.login_admin()
        data = self.assert_ok(self.json_post('/api/admin/price/', {
            'type': 'ai_negotiation', 'ai_negotiation_enabled': True,
            'ai_negotiation_min_floor_percent': 80, 'ai_max_discount_percent': 25,
            'ai_negotiation_strategy': 'high_conversion',
            'ai_negotiation_instructions': 'Never go below floor. Offer free sides first.',
        }))
        self.assertEqual(data['ai_negotiation_min_floor_percent'], 80)
        self.assertEqual(data['ai_max_discount_percent'], 25)
        self.assertEqual(data['ai_negotiation_strategy'], 'high_conversion')
        s = self.refresh_settings()
        self.assertIn('floor', s.ai_negotiation_instructions)

    def test_tc_prc_016_floor_percent_clamped_40_to_95(self):
        """TC-PRC-016: floor percent clamped into [40, 95]."""
        self.login_admin()
        self.assert_ok(self.json_post('/api/admin/price/', {
            'type': 'ai_negotiation', 'ai_negotiation_min_floor_percent': 10,
        }))
        self.assertEqual(self.refresh_settings().ai_negotiation_min_floor_percent, 40)
        self.assert_ok(self.json_post('/api/admin/price/', {
            'type': 'ai_negotiation', 'ai_negotiation_min_floor_percent': 99,
        }))
        self.assertEqual(self.refresh_settings().ai_negotiation_min_floor_percent, 95)

    def test_tc_prc_017_max_discount_clamped_5_to_50(self):
        """TC-PRC-017: AI max discount clamped into [5, 50]."""
        self.login_admin()
        self.assert_ok(self.json_post('/api/admin/price/', {
            'type': 'ai_negotiation', 'ai_max_discount_percent': 1,
        }))
        self.assertEqual(self.refresh_settings().ai_max_discount_percent, 5)
        self.assert_ok(self.json_post('/api/admin/price/', {
            'type': 'ai_negotiation', 'ai_max_discount_percent': 99,
        }))
        self.assertEqual(self.refresh_settings().ai_max_discount_percent, 50)

    def test_tc_prc_018_per_service_floor_updates(self):
        """TC-PRC-018: service_floors list updates per-service negotiation guardrails."""
        self.login_admin()
        svc = self.refresh_settings()  # ensure settings exist
        from core.models import StudioService
        target = StudioService.objects.get(title='Nail Couture Atelier')
        self.assert_ok(self.json_post('/api/admin/price/', {
            'type': 'ai_negotiation',
            'service_floors': [{
                'id': target.id, 'min_negotiated_price': '4400',
                'allow_ai_negotiation': True, 'max_discount_percent': '20',
            }],
        }))
        target.refresh_from_db()
        self.assertEqual(float(target.min_negotiated_price), 4400.0)
        self.assertTrue(target.allow_ai_negotiation)
        self.assertEqual(target.max_discount_percent, 20)

    def test_tc_prc_019_floor_clear_with_empty_string(self):
        """TC-PRC-019: empty-string floor clears the per-service override."""
        self.login_admin()
        from core.models import StudioService
        target = StudioService.objects.get(title='Imperial Bridal Couture & Airbrush')
        self.assertIsNotNone(target.min_negotiated_price)
        self.assert_ok(self.json_post('/api/admin/price/', {
            'type': 'ai_negotiation',
            'service_floors': [{'id': target.id, 'min_negotiated_price': ''}],
        }))
        target.refresh_from_db()
        self.assertIsNone(target.min_negotiated_price)
