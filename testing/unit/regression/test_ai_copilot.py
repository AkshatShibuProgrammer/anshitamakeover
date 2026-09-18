"""
REG-AREA-13 · Admin AI Co-Pilot (natural-language website manager) regression tests.

The copilot translates admin instructions into structured DB actions via
Gemini.  The Gemini round-trip is mocked; every executable action schema is
verified end-to-end against the database:

modify_booking_offers · update_package · create_package · update_coupon ·
add_media (instagram/youtube) · update_price · create_addon_bundle · answer

NOTE: this endpoint is NOT wired into ``core/urls.py`` (see KD-003); tests
drive the view function directly.

Test case IDs: TC-AIC-001 … TC-AIC-015
"""
import json
from pathlib import Path
from unittest import mock

from django.conf import settings

from core.models import (
    MakeupPackage, MediaItem, ServicePrice, EventPackage, SiteSettings,
)
from core.views.chatbot import admin_ai_command

from .base import RegressionTestCase

GEMINI_KEY_FILE = Path(settings.BASE_DIR) / 'gemini_api_key.txt'


class AiCopilotTestCase(RegressionTestCase):
    seed_dataset = True

    def setUp(self):
        super().setUp()
        self.login_admin()
        GEMINI_KEY_FILE.write_text('test-gemini-key-copilot\n')
        self.addCleanup(GEMINI_KEY_FILE.unlink, missing_ok=True)

    def run_prompt(self, prompt, gemini_json):
        """Invoke the copilot view with Gemini mocked to return ``gemini_json``."""
        raw = gemini_json if isinstance(gemini_json, str) else json.dumps(gemini_json)
        fake = mock.MagicMock()
        fake.status_code = 200
        fake.json.return_value = {'candidates': [{'content': {'parts': [{'text': raw}]}}]}
        from django.test import RequestFactory
        req = RequestFactory().post('/admin-ai/', data=json.dumps({'prompt': prompt}),
                                    content_type='application/json')
        req.user = self.admin_user_obj
        with mock.patch('requests.post', return_value=fake):
            response = admin_ai_command(req)
        return json.loads(response.content)

    def login_admin(self, *args, **kwargs):
        super().login_admin(*args, **kwargs)
        from django.contrib.auth.models import User
        self.admin_user_obj = User.objects.get(username='regadmin')


class AiCopilotContractTests(AiCopilotTestCase):

    def test_tc_aic_001_empty_prompt_rejected(self):
        """TC-AIC-001: empty instruction returns a helpful error."""
        data = self.run_prompt('', {'action': 'answer', 'message': 'n/a'})
        self.assertFalse(data['ok'])
        self.assertIn('instruction', data['error'].lower())

    def test_tc_aic_002_missing_api_key_rejected(self):
        """TC-AIC-002: without a Gemini key the copilot refuses to run."""
        GEMINI_KEY_FILE.unlink()
        data = self.run_prompt('change coupon', {'action': 'answer', 'message': 'x'})
        self.assertFalse(data['ok'])
        self.assertIn('API key', data['error'])

    def test_tc_aic_003_markdown_fences_stripped(self):
        """TC-AIC-003: ```json fenced Gemini output still parses."""
        fenced = '```json\n' + json.dumps({'action': 'answer', 'message': 'Fenced OK'}) + '\n```'
        data = self.run_prompt('hello', fenced)
        self.assertTrue(data['ok'])
        self.assertEqual(data['message'], 'Fenced OK')

    def test_tc_aic_004_invalid_gemini_json_handled(self):
        """TC-AIC-004: unparseable Gemini output returns ok=False, not 500."""
        data = self.run_prompt('do something', 'this is not json at all')
        self.assertFalse(data['ok'])
        self.assertIn('Failed to execute', data['error'])


class AiCopilotActionTests(AiCopilotTestCase):

    def test_tc_aic_005_modify_booking_offers_with_clamps(self):
        """TC-AIC-005: booking-offer action saves with guardrail clamping."""
        data = self.run_prompt('set 9 free sides and 99% combo discount', {
            'action': 'modify_booking_offers', 'free_sides': 9,
            'discounted_side_price': 9999, 'combo_discount_percent': 99,
            'bundle_price': 75000, 'active': True,
        })
        self.assertTrue(data['ok'])
        s = SiteSettings.objects.get(id=1)
        self.assertEqual(s.offer_bridal_free_sides, 5)          # clamped 0..5
        self.assertEqual(float(s.offer_next_sides_discounted_price), 4500.0)  # clamped ≤4500
        self.assertEqual(s.offer_combo_discount_percent, 25)    # clamped ≤25
        self.assertEqual(float(s.offer_grand_combo_bundle_price), 75000.0)
        pkg = MakeupPackage.objects.get(name__icontains='Grand Royal Heritage')
        self.assertEqual(float(pkg.price), 75000.0)             # bundle sync

    def test_tc_aic_006_create_package(self):
        """TC-AIC-006: create_package adds a new suite."""
        data = self.run_prompt('add haldi package', {
            'action': 'create_package', 'name': 'Haldi Sunshine Glam',
            'package_type': 'party', 'price': 8500, 'price_label': '₹8,500',
            'tagline': 'Golden hour glow', 'features': 'Dewy tones\nFloral setting',
            'is_featured': False,
        })
        self.assertTrue(data['ok'])
        pkg = MakeupPackage.objects.get(name='Haldi Sunshine Glam')
        self.assertEqual(float(pkg.price), 8500.0)

    def test_tc_aic_007_update_package_by_name_query(self):
        """TC-AIC-007: update_package resolves target by name query."""
        data = self.run_prompt('raise HD price', {
            'action': 'update_package', 'name_query': 'Imperial Royal HD',
            'price': 42000,
        })
        self.assertTrue(data['ok'])
        pkg = MakeupPackage.objects.get(name__icontains='Imperial Royal HD')
        self.assertEqual(float(pkg.price), 42000.0)
        self.assertEqual(pkg.price_label, '₹42,000')

    def test_tc_aic_008_update_package_not_found(self):
        """TC-AIC-008: unresolvable package query returns ok=False."""
        data = self.run_prompt('update ghost', {'action': 'update_package',
                                                'name_query': 'NoSuchPackage', 'price': 1})
        self.assertFalse(data['ok'])

    def test_tc_aic_009_update_coupon(self):
        """TC-AIC-009: coupon action stores code and disables auto rotation."""
        data = self.run_prompt('new coupon', {
            'action': 'update_coupon', 'coupon_code': 'summer40',
            'discount_percent': 40, 'label': 'Summer Bridal Privilege', 'active': True,
        })
        self.assertTrue(data['ok'])
        s = SiteSettings.objects.get(id=1)
        self.assertEqual(s.coupon_code, 'SUMMER40')
        self.assertEqual(s.coupon_discount_percent, 40)
        self.assertFalse(s.coupon_auto_by_date)

    def test_tc_aic_010_add_instagram_media(self):
        """TC-AIC-010: add_media instagram extracts shortcode."""
        data = self.run_prompt('embed reel', {
            'action': 'add_media', 'title': 'Shubho Drishti', 'media_type': 'instagram',
            'url': 'https://www.instagram.com/reel/Dap4JkvKL1E/', 'category': 'bridal',
            'section': 'reels',
        })
        self.assertTrue(data['ok'])
        item = MediaItem.objects.get(title='Shubho Drishti')
        self.assertEqual(item.embed_code, 'Dap4JkvKL1E')
        self.assertEqual(item.media_type, 'instagram')

    def test_tc_aic_011_add_youtube_media(self):
        """TC-AIC-011: add_media youtube extracts id and thumbnail."""
        data = self.run_prompt('embed video', {
            'action': 'add_media', 'title': 'Bridal Masterclass', 'media_type': 'youtube',
            'url': 'https://www.youtube.com/watch?v=aBcDeFgHiJk',
        })
        self.assertTrue(data['ok'])
        item = MediaItem.objects.get(title='Bridal Masterclass')
        self.assertEqual(item.embed_code, 'aBcDeFgHiJk')
        self.assertIn('hqdefault.jpg', item.thumbnail_url)

    def test_tc_aic_012_update_service_price(self):
        """TC-AIC-012: update_price persists ServicePrice change."""
        data = self.run_prompt('change hd price', {
            'action': 'update_price', 'service': 'makeup_hd', 'price': 26000,
        })
        self.assertTrue(data['ok'])
        self.assertEqual(float(ServicePrice.objects.get(service='makeup_hd').price), 26000.0)

    def test_tc_aic_013_photo_price_action_documented_defect(self):
        """TC-AIC-013 (KNOWN DEFECT KD-002): photo_* update_price is a silent no-op.

        The copilot filters ``EventPackage.package_type`` by 'photo_premium',
        but the model choice is 'photography_premium', so nothing updates even
        though the response claims success. Locked by this regression test.
        """
        before = float(EventPackage.objects.get(package_type='photography_premium').price)
        data = self.run_prompt('raise premium photo price', {
            'action': 'update_price', 'service': 'photo_premium', 'price': 199000,
        })
        self.assertTrue(data['ok'])  # claims success…
        after = float(EventPackage.objects.get(package_type='photography_premium').price)
        self.assertEqual(before, after)  # …but nothing changed

    def test_tc_aic_014_create_addon_bundle(self):
        """TC-AIC-014: create_addon_bundle stores vendor cost and computes margin."""
        data = self.run_prompt('new bundle', {
            'action': 'create_addon_bundle', 'name': 'Bespoke Royal Photography & Stage Decor',
            'category': 'photography', 'vendor_cost': 50000, 'client_quote': 68000,
            'features': 'Cinematic 4K\n2 Photographers', 'description': 'Curated addon',
        })
        self.assertTrue(data['ok'])
        pkg = EventPackage.objects.get(name='Bespoke Royal Photography & Stage Decor')
        self.assertEqual(pkg.studio_commission, 18000.0)
        self.assertEqual(pkg.created_by.username, 'regadmin')
        self.assertIn('₹18,000', data['message'])

    def test_tc_aic_015_answer_action(self):
        """TC-AIC-015: informational answers pass through untouched."""
        data = self.run_prompt('what is my margin?', {
            'action': 'answer', 'message': 'Your margin is 25%.',
        })
        self.assertTrue(data['ok'])
        self.assertEqual(data['message'], 'Your margin is 25%.')
