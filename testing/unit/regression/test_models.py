"""
REG-AREA-01 · Model & business-logic regression tests.

Validates computed properties, defaults, ordering and helpers on every model
in ``core.models`` — the business rules that pricing, commissions, GST and
display formatting depend on.

Test case IDs: TC-MOD-001 … TC-MOD-024
"""
from decimal import Decimal

from core.models import (
    SiteSettings, Artist, AcademyCourse, CourseModule, MakeupPackage,
    GalleryImage, MediaItem, ServicePrice, EventPackage, ChatMessage,
    CustomerReview, StudioService, LookGroup, LookMediaItem,
)

from .base import RegressionTestCase


class SiteSettingsModelTests(RegressionTestCase):
    """TC-MOD-001..003 — SiteSettings singleton defaults."""

    def test_tc_mod_001_defaults(self):
        """TC-MOD-001: singleton carries canonical WhatsApp/coupon defaults."""
        s = self.refresh_settings()
        self.assertEqual(s.whatsapp_number, '917879223442')
        self.assertEqual(s.coupon_code, 'GLAMOUR30')
        self.assertEqual(s.coupon_discount_percent, 30)
        self.assertEqual(s.exit_coupon_code, 'SECRET10')
        self.assertEqual(s.default_auto_coupon_code, 'TODAYVIP')
        self.assertTrue(s.ai_negotiation_enabled)

    def test_tc_mod_002_str(self):
        """TC-MOD-002: human readable __str__."""
        self.assertEqual(str(self.refresh_settings()), 'Site Settings')

    def test_tc_mod_003_get_or_create_singleton(self):
        """TC-MOD-003: get_or_create(id=1) never duplicates the row."""
        from core.views.common import get_site_settings
        a = get_site_settings()
        b = get_site_settings()
        self.assertEqual(a.pk, b.pk)
        self.assertEqual(SiteSettings.objects.count(), 1)


class ArtistModelTests(RegressionTestCase):

    def test_tc_mod_004_specialities_split(self):
        """TC-MOD-004: comma-separated specialities parsed to clean list."""
        a = Artist.objects.create(name='Anshita', slug='anshita', specialities=' makeup , hair,draping ')
        self.assertEqual(a.get_specialities_list(), ['makeup', 'hair', 'draping'])

    def test_tc_mod_005_ordering(self):
        """TC-MOD-005: artists ordered by (order, name)."""
        Artist.objects.create(name='Zara', slug='zara', order=1)
        Artist.objects.create(name='Anshita', slug='anshita', order=0)
        Artist.objects.create(name='Meera', slug='meera', order=1)
        names = [a.name for a in Artist.objects.all()]
        self.assertEqual(names, ['Anshita', 'Meera', 'Zara'])


class AcademyCourseModelTests(RegressionTestCase):

    def _course(self, fee=30000, gst=18):
        return AcademyCourse.objects.create(
            name='Professional Makeup Artist Program', slug='pmu-program',
            course_fee=fee, gst_percent=gst,
        )

    def test_tc_mod_006_gst_amount(self):
        """TC-MOD-006: GST amount = fee * gst% (rounded)."""
        self.assertEqual(self._course(30000, 18).gst_amount, 5400)

    def test_tc_mod_007_total_payable(self):
        """TC-MOD-007: total payable = fee + GST."""
        self.assertEqual(self._course(30000, 18).total_payable, 35400.0)

    def test_tc_mod_008_module_str_and_order(self):
        """TC-MOD-008: modules ordered by order and str includes course name."""
        c = self._course()
        m2 = CourseModule.objects.create(course=c, order=2, title='Bridal Training')
        m1 = CourseModule.objects.create(course=c, order=1, title='Foundations')
        mods = list(c.modules.all())
        self.assertEqual([m.id for m in mods], [m1.id, m2.id])
        self.assertIn('Professional Makeup Artist Program', str(m1))


class MakeupPackageModelTests(RegressionTestCase):

    def test_tc_mod_009_features_list(self):
        """TC-MOD-009: multi-line features parsed, blank lines dropped."""
        p = MakeupPackage.objects.create(
            name='HD Suite', package_type='bridal', price=35000,
            features='HD Base\n\nCut-crease eyes\n  \nDupatta draping\n',
        )
        self.assertEqual(p.get_features_list(), ['HD Base', 'Cut-crease eyes', 'Dupatta draping'])

    def test_tc_mod_010_on_request_package(self):
        """TC-MOD-010: price may be NULL ('On Request' packages)."""
        p = MakeupPackage.objects.create(name='Bespoke', package_type='custom',
                                         price=None, price_label='On Request', features='x')
        self.assertIsNone(p.price)
        self.assertEqual(p.price_label, 'On Request')

    def test_tc_mod_011_negotiation_guardrail_defaults(self):
        """TC-MOD-011: AI negotiation guardrail defaults."""
        p = MakeupPackage.objects.create(name='X', package_type='bridal', price=10000, features='x')
        self.assertTrue(p.allow_ai_negotiation)
        self.assertEqual(p.max_discount_percent, 15)
        self.assertIsNone(p.min_negotiated_price)


class ServicePriceModelTests(RegressionTestCase):

    def test_tc_mod_012_display_price_normal(self):
        """TC-MOD-012: formatted Indian-grouping price."""
        sp = ServicePrice.objects.create(service='makeup_hd', price=35000)
        self.assertEqual(sp.display_price(), '₹35,000')

    def test_tc_mod_013_display_price_on_request(self):
        """TC-MOD-013: is_on_request wins over numeric price."""
        sp = ServicePrice.objects.create(service='tejal_makeup', price=0, is_on_request=True)
        self.assertEqual(sp.display_price(), 'On Request')

    def test_tc_mod_014_display_price_label_override(self):
        """TC-MOD-014: custom label overrides numeric formatting."""
        sp = ServicePrice.objects.create(service='hair_bridal', price=3500, price_label='Starting 3,500')
        self.assertEqual(sp.display_price(), 'Starting 3,500')


class EventPackageModelTests(RegressionTestCase):

    def _pkg(self, price, vendor_cost, **kw):
        kw.setdefault('name', 'Test Event Package')
        kw.setdefault('category', 'photography')
        kw.setdefault('package_type', 'custom')
        return EventPackage.objects.create(price=price, vendor_cost=vendor_cost, **kw)

    def test_tc_mod_015_commission(self):
        """TC-MOD-015: studio commission = client price - vendor cost."""
        p = self._pkg(Decimal('120000'), Decimal('90000'))
        self.assertEqual(p.studio_commission, 30000.0)

    def test_tc_mod_016_margin_percent(self):
        """TC-MOD-016: margin % = commission / price * 100."""
        p = self._pkg(Decimal('120000'), Decimal('90000'))
        self.assertEqual(p.margin_percent, 25.0)

    def test_tc_mod_017_roi_percent(self):
        """TC-MOD-017: ROI % = commission / vendor cost * 100."""
        p = self._pkg(Decimal('120000'), Decimal('90000'))
        self.assertEqual(p.roi_percent, 33.3)

    def test_tc_mod_018_display_price_lakh(self):
        """TC-MOD-018: prices >= 1 lakh render as '₹X Lakh'."""
        self.assertEqual(self._pkg(Decimal('500000'), 0, name='A').display_price(), '₹5 Lakh')
        self.assertEqual(self._pkg(Decimal('120000'), 0, name='B').display_price(), '₹1.2 Lakh')
        self.assertEqual(self._pkg(Decimal('90000'), 0, name='C').display_price(), '₹90,000')

    def test_tc_mod_019_display_price_on_request(self):
        """TC-MOD-019: NULL price falls back to price_label."""
        p = self._pkg(None, Decimal('60000'), name='D', price_label='On Request')
        self.assertEqual(p.display_price(), 'On Request')

    def test_tc_mod_020_commission_never_negative(self):
        """TC-MOD-020: commission clamped to 0 when price < vendor cost."""
        p = self._pkg(Decimal('50000'), Decimal('60000'), name='E')
        self.assertEqual(p.studio_commission, 0.0)


class MediaDisplayTests(RegressionTestCase):

    def test_tc_mod_021_media_item_display_thumb_fallbacks(self):
        """TC-MOD-021: display_thumb priority image_file > thumb > youtube > static."""
        m = MediaItem.objects.create(title='YT', media_type='youtube', embed_code='abc12345678')
        self.assertEqual(m.display_thumb, 'https://img.youtube.com/vi/abc12345678/hqdefault.jpg')
        m2 = MediaItem.objects.create(title='T', media_type='image',
                                      thumbnail_url='https://cdn.test/x.jpg')
        self.assertEqual(m2.display_thumb, 'https://cdn.test/x.jpg')
        m3 = MediaItem.objects.create(title='F', media_type='image')
        self.assertEqual(m3.display_thumb, '/static/core/images/anshita_front.jpg')

    def test_tc_mod_022_look_media_display_thumb(self):
        """TC-MOD-022: LookMediaItem thumbnail fallback chain."""
        g = LookGroup.objects.create(name='G')
        i = LookMediaItem.objects.create(group=g, media_type='youtube', embed_code='xyz98765432')
        self.assertEqual(i.display_thumb, 'https://img.youtube.com/vi/xyz98765432/hqdefault.jpg')

    def test_tc_mod_023_lookgroup_display_cover_fallback(self):
        """TC-MOD-023: group cover falls back to first media item then static."""
        g = LookGroup.objects.create(name='NoCover')
        self.assertEqual(g.display_cover, '/static/core/images/curated/royal_crimson_bride_angle3.jpg')
        LookMediaItem.objects.create(group=g, media_type='image',
                                     thumbnail_url='/static/x.jpg', order=1)
        self.assertEqual(g.display_cover, '/static/x.jpg')
        g.cover_image_url = '/static/cover.jpg'
        self.assertEqual(g.display_cover, '/static/cover.jpg')

    def test_tc_mod_024_studio_service_display_image(self):
        """TC-MOD-024: StudioService image_url fallback and features parsing."""
        s = StudioService.objects.create(
            title='Svc', discipline='D1', price=1000, description='d', features='a\nb\n',
        )
        self.assertEqual(s.get_features_list(), ['a', 'b'])
        self.assertTrue(s.display_image.startswith('/static/core/images/'))
        s.image_url = '/static/custom.jpg'
        self.assertEqual(s.display_image, '/static/custom.jpg')


class ReviewAndChatModelTests(RegressionTestCase):

    def test_tc_mod_025_review_stars_range(self):
        """TC-MOD-025: star range generator matches rating."""
        r = CustomerReview.objects.create(client_name='X', review_text='t', rating=4)
        self.assertEqual(len(list(r.get_stars_range())), 4)
        self.assertIn('(4★)', str(r))

    def test_tc_mod_026_chat_message_str(self):
        """TC-MOD-026: chat log str includes truncated session id."""
        m = ChatMessage.objects.create(session_id='session-abcdefgh-123', message='q', response='r')
        self.assertIn('session-', str(m))

    def test_tc_mod_027_gallery_str_and_defaults(self):
        """TC-MOD-027: gallery caption str and lookbook grouping defaults."""
        g = GalleryImage.objects.create()
        self.assertTrue(str(g).startswith('Gallery Image'))
        g2 = GalleryImage.objects.create(caption='Bride X')
        self.assertEqual(str(g2), 'Bride X')
        self.assertTrue(g2.is_group_cover)
