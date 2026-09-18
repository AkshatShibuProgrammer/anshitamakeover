"""
REG-AREA-03 · Public pages, translations & discount-engine regression tests.

Covers: homepage render + context, offer-price computation, academy page,
language switching (cookie + JSON), translation fallbacks, Sinha logo studio.

Test case IDs: TC-PUB-001 … TC-PUB-020
"""
from unittest import mock

from core.translations import get_translation, TRANSLATIONS

from .base import RegressionTestCase


class HomePageTests(RegressionTestCase):
    seed_dataset = True

    def test_tc_pub_001_home_renders(self):
        """TC-PUB-001: homepage renders 200 with brand content."""
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Anshita')

    def test_tc_pub_002_home_context_keys(self):
        """TC-PUB-002: homepage context carries every showcase the template needs."""
        resp = self.client.get('/')
        ctx = resp.context
        for key in ['site', 'coupon', 'default_coupon', 'exit_coupon', 'artists',
                    'gallery', 'packages_bridal', 'packages_other', 'studio_services',
                    'event_packages', 'reviews', 'media_reels', 'look_groups',
                    'whatsapp', 't', 'current_lang']:
            self.assertIn(key, ctx, f'context missing {key}')

    def test_tc_pub_003_inactive_records_filtered(self):
        """TC-PUB-003: inactive packages/artists/reviews never reach the template."""
        ctx = self.client.get('/').context
        pkg_names = [p.name for p in ctx['packages_bridal']] + [p.name for p in ctx['packages_other']]
        self.assertNotIn('Legacy Trial Package', pkg_names)
        self.assertNotIn('Retired Trial Reel', [m.title for m in ctx['media_reels']])
        artist_names = [a.name for a in ctx['artists']]
        self.assertIn('Anshita', artist_names)
        self.assertNotIn('Shristee', artist_names)  # is_active=False
        review_names = [r.client_name for r in ctx['reviews']]
        self.assertNotIn('Hidden Reviewer', review_names)

    def test_tc_pub_004_gallery_group_cover_filter(self):
        """TC-PUB-004: only group-cover gallery images appear on the main grid."""
        ctx = self.client.get('/').context
        captions = [g.caption for g in ctx['gallery']]
        self.assertIn('Royal Bengali Bride — Front', captions)
        self.assertNotIn('Royal Bengali Bride — Side', captions)   # not a cover
        self.assertNotIn('Hidden Gallery Shot', captions)          # inactive

    def test_tc_pub_005_offer_price_computation(self):
        """TC-PUB-005: package offer price = base * (100-discount)/100."""
        self.ensure_settings(coupon_auto_by_date=False, coupon_active=True,
                             coupon_discount_percent=20)
        ctx = self.client.get('/').context
        hd = next(p for p in ctx['packages_bridal'] if p.name == 'Imperial Royal HD Bridal Suite')
        self.assertTrue(hd.has_offer)
        self.assertEqual(hd.offer_price, 28000)          # 35000 * 0.80
        self.assertEqual(hd.saving, 7000.0)
        self.assertEqual(hd.discount_percent, 20)

    def test_tc_pub_006_no_offer_when_coupon_disabled(self):
        """TC-PUB-006: with no active coupon, offer price equals base price."""
        self.ensure_settings(coupon_active=False)
        ctx = self.client.get('/').context
        hd = next(p for p in ctx['packages_bridal'] if p.name == 'Imperial Royal HD Bridal Suite')
        self.assertFalse(hd.has_offer)
        self.assertEqual(hd.offer_price, 35000)
        self.assertEqual(hd.saving, 0)

    def test_tc_pub_007_null_price_package_survives(self):
        """TC-PUB-007: 'On Request' package (NULL price) renders without crash."""
        ctx = self.client.get('/').context
        bespoke = next(p for p in ctx['packages_other'] if p.name == 'Bespoke Custom Couture')
        self.assertIsNone(bespoke.price)
        self.assertFalse(hasattr(bespoke, 'offer_price') and bespoke.offer_price)

    def test_tc_pub_008_studio_service_offer_computation(self):
        """TC-PUB-008: studio services get the same coupon-driven offer math."""
        self.ensure_settings(coupon_auto_by_date=False, coupon_active=True,
                             coupon_discount_percent=10)
        ctx = self.client.get('/').context
        svc = next(s for s in ctx['studio_services'] if s.category == 'bridal')
        self.assertTrue(svc.has_offer)
        self.assertEqual(svc.offer_price, 31500)  # 35000 * 0.90
        retired = [s.title for s in ctx['studio_services']]
        self.assertNotIn('Retired Haldi Service', retired)

    def test_tc_pub_009_reviews_capped_at_eight(self):
        """TC-PUB-009: homepage shows at most 8 reviews."""
        ctx = self.client.get('/').context
        self.assertLessEqual(len(ctx['reviews']), 8)

    def test_tc_pub_010_media_reels_capped_at_six(self):
        """TC-PUB-010: reels carousel shows only featured media, max 6."""
        ctx = self.client.get('/').context
        self.assertLessEqual(len(ctx['media_reels']), 6)
        for m in ctx['media_reels']:
            self.assertTrue(m.is_featured)

    def test_tc_pub_011_lang_query_sets_cookie(self):
        """TC-PUB-011: ?lang=hindi sets the lang cookie for a year."""
        resp = self.client.get('/?lang=hindi')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.cookies['lang'].value, 'hindi')

    def test_tc_pub_012_lang_cookie_respected(self):
        """TC-PUB-012: stored lang cookie drives translation selection."""
        self.client.cookies['lang'] = 'hindi'
        ctx = self.client.get('/').context
        self.assertEqual(ctx['current_lang'], 'hindi')
        self.assertEqual(ctx['t']['code'], TRANSLATIONS['hindi']['code'])


class AcademyPageTests(RegressionTestCase):
    seed_dataset = True

    def test_tc_pub_013_academy_renders(self):
        """TC-PUB-013: academy page renders with active courses only."""
        resp = self.client.get('/academy/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Professional Makeup Artist Program')
        self.assertNotContains(resp, 'Retired')

    def test_tc_pub_014_academy_offer_math(self):
        """TC-PUB-014: course offer price computed on fee + GST total."""
        self.ensure_settings(coupon_auto_by_date=False, coupon_active=True,
                             coupon_discount_percent=10)
        ctx = self.client.get('/academy/').context
        main = ctx['courses'][0]
        # total payable 35400 -> 10% off = 31860
        self.assertEqual(main.offer_price, 31860)
        self.assertEqual(main.saving, 3540)
        self.assertTrue(main.has_offer)

    def test_tc_pub_015_academy_fallback_prices(self):
        """TC-PUB-015: fallback 35,400 pricing present for templates without DB courses."""
        ctx = self.client.get('/academy/').context
        self.assertEqual(ctx['fallback_std_price'], 35400)
        self.assertEqual(len(ctx['modules_static']), 6)


class TranslationTests(RegressionTestCase):

    def test_tc_pub_016_all_languages_present(self):
        """TC-PUB-016: english, hindi, marathi, bundelkhandi dictionaries exist."""
        for lang in ['english', 'hindi', 'marathi', 'bundelkhandi']:
            self.assertIn(lang, TRANSLATIONS)
            self.assertIn('hero_title', TRANSLATIONS[lang])

    def test_tc_pub_017_unknown_language_falls_back_to_english(self):
        """TC-PUB-017: unknown/None language codes fall back to english."""
        self.assertEqual(get_translation('klingon')['locale_name'], 'English')
        self.assertEqual(get_translation(None)['locale_name'], 'English')
        self.assertEqual(get_translation('')['locale_name'], 'English')

    def test_tc_pub_018_key_parity_with_english(self):
        """TC-PUB-018: every language provides all english keys (no KeyError in templates)."""
        en_keys = set(TRANSLATIONS['english'].keys())
        for lang, table in TRANSLATIONS.items():
            missing = en_keys - set(table.keys())
            self.assertFalse(missing, f"{lang} missing keys: {missing}")


class SetLanguageTests(RegressionTestCase):

    def test_tc_pub_019_json_switch(self):
        """TC-PUB-019: JSON POST switches language and sets cookie."""
        resp = self.json_post('/set-language/', {'language': 'hinglish'})
        data = self.json_response(resp)
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['language'], 'hinglish')
        self.assertEqual(resp.cookies['lang'].value, 'hinglish')

    def test_tc_pub_020_form_and_get_switch(self):
        """TC-PUB-020: form POST and GET fallback redirect with lang cookie."""
        resp = self.client.post('/set-language/', {'lang': 'marathi'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.cookies['lang'].value, 'marathi')
        resp = self.client.get('/set-language/?lang=bundelkhandi')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.cookies['lang'].value, 'bundelkhandi')

    def test_tc_pub_021_sinha_logo_studio(self):
        """TC-PUB-021: Sinha luxury branding visualizer page renders."""
        resp = self.client.get('/sinha-logos/')
        self.assertEqual(resp.status_code, 200)
