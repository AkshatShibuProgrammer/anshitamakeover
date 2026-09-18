"""
REG-AREA-11 · Media management & lookbook regression tests.

Covers:
* /api/admin/media/       — photos, Instagram auto-embed, YouTube auto-embed,
                            delete & toggle
* /api/admin/lookgroup/   — person/client folder CRUD with auto-naming
* /api/admin/lookgroup/media/ — media inside a look group with auto-cover

Network calls (Instagram/YouTube oEmbed) are mocked so the suite is
deterministic and offline-safe.

Test case IDs: TC-MED-001 … TC-MED-020
"""
import io
import json
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from core.models import MediaItem, LookGroup, LookMediaItem, GalleryImage

from .base import RegressionTestCase


def png_bytes(color=(200, 30, 90)):
    buf = io.BytesIO()
    Image.new('RGB', (12, 12), color=color).save(buf, format='PNG')
    return buf.getvalue()


def fake_urlopen_factory(metadata):
    """Return a urlopen stand-in whose read() yields ``metadata`` JSON."""
    payload = json.dumps(metadata).encode()

    class FakeResponse(io.BytesIO):
        def __init__(self):
            super().__init__(payload)

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def fake_urlopen(req, timeout=None):
        return FakeResponse()

    return fake_urlopen


def no_network():
    """Decorator factory: force oEmbed fetches to fail (offline determinism).

    Wraps mock.patch in a context manager so no mock argument is injected
    into the test signature.
    """
    def decorator(func):
        import functools

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            with mock.patch('urllib.request.urlopen', side_effect=OSError('offline')):
                return func(self, *args, **kwargs)
        return wrapper
    return decorator


class MediaListTests(RegressionTestCase):
    seed_dataset = True

    def test_tc_med_001_list_requires_login(self):
        """TC-MED-001: anonymous listing is redirected."""
        self.assert_redirect_to_login(self.client.get('/api/admin/media/'), '/api/admin/media/')

    def test_tc_med_002_list_payload(self):
        """TC-MED-002: listing exposes thumbs, embed codes and flags."""
        self.login_admin()
        data = self.json_response(self.client.get('/api/admin/media/'))
        titles = [m['title'] for m in data['media']]
        self.assertIn('Shubho Drishti — Bengali Bridal Reel', titles)
        reel = next(m for m in data['media'] if m['media_type'] == 'instagram')
        self.assertEqual(reel['embed_code'], 'Dap4JkvKL1E')
        yt = next(m for m in data['media'] if m['media_type'] == 'youtube')
        self.assertEqual(yt['thumb'], 'https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg')


class MediaCreateTests(RegressionTestCase):

    @no_network()
    def test_tc_med_003_instagram_shortcode_extraction(self):
        """TC-MED-003: Instagram reel URL → shortcode embed code."""
        self.login_admin()
        resp = self.client.post('/api/admin/media/', {
            'title': 'New Reel', 'media_type': 'instagram',
            'external_url': 'https://www.instagram.com/reel/Dxyz123AbCd/?utm_source=ig',
            'category': 'bridal', 'section': 'reels',
        })
        data = self.assert_ok(resp)
        item = MediaItem.objects.get(id=data['item']['id'])
        self.assertEqual(item.embed_code, 'Dxyz123AbCd')
        self.assertEqual(item.media_type, 'instagram')

    @no_network()
    def test_tc_med_004_instagram_post_url_variant(self):
        """TC-MED-004: /p/ style Instagram URLs also resolve shortcodes."""
        self.login_admin()
        resp = self.client.post('/api/admin/media/', {
            'media_type': 'instagram', 'external_url': 'https://www.instagram.com/p/DW0f_eHAecV/',
        })
        data = self.assert_ok(resp)
        self.assertEqual(data['item']['embed_code'], 'DW0f_eHAecV')
        self.assertEqual(data['item']['title'], 'Instagram Reel Showcase')  # default title

    @no_network()
    def test_tc_med_005_youtube_id_and_thumbnail(self):
        """TC-MED-005: YouTube URL → 11-char id + hqdefault thumbnail."""
        self.login_admin()
        resp = self.client.post('/api/admin/media/', {
            'title': 'Cinematic Film', 'media_type': 'youtube',
            'external_url': 'https://www.youtube.com/watch?v=aBcDeFgHiJk',
            'section': 'both',
        })
        data = self.assert_ok(resp)
        item = MediaItem.objects.get(id=data['item']['id'])
        self.assertEqual(item.embed_code, 'aBcDeFgHiJk')
        self.assertEqual(item.thumbnail_url, 'https://img.youtube.com/vi/aBcDeFgHiJk/hqdefault.jpg')

    @no_network()
    def test_tc_med_006_youtube_shorts_url(self):
        """TC-MED-006: youtu.be and shorts URLs are recognised."""
        self.login_admin()
        resp = self.client.post('/api/admin/media/', {
            'title': 'Short', 'external_url': 'https://youtu.be/12345678901',
        })
        self.assertEqual(self.assert_ok(resp)['item']['embed_code'], '12345678901')

    def test_tc_med_007_youtube_oembed_metadata(self):
        """TC-MED-007: successful oEmbed call auto-fills the title."""
        self.login_admin()
        fake = fake_urlopen_factory({'title': 'Auto Fetched Title',
                                     'thumbnail_url': 'https://cdn.test/thumb.jpg'})
        with mock.patch('urllib.request.urlopen', side_effect=fake):
            resp = self.client.post('/api/admin/media/', {
                'title': 'YouTube Video', 'media_type': 'youtube',
                'external_url': 'https://www.youtube.com/watch?v=aBcDeFgHiJk',
            })
        data = self.assert_ok(resp)
        item = MediaItem.objects.get(id=data['item']['id'])
        self.assertEqual(item.title, 'Auto Fetched Title')
        self.assertEqual(item.thumbnail_url, 'https://cdn.test/thumb.jpg')

    @no_network()
    def test_tc_med_008_image_upload_creates_gallery_copy(self):
        """TC-MED-008: uploaded image in gallery section also creates GalleryImage."""
        self.login_admin()
        upload = SimpleUploadedFile('bride.png', png_bytes(), content_type='image/png')
        resp = self.client.post('/api/admin/media/', {
            'title': 'Uploaded Bridal Look', 'media_type': 'image', 'section': 'gallery',
            'category': 'bridal', 'look_group_id': 'bengali_bride',
            'look_group_name': 'Royal Bengali Bride (4 Looks)', 'is_group_cover': '0',
            'image_file': upload,
        })
        data = self.assert_ok(resp)
        item = MediaItem.objects.get(id=data['item']['id'])
        self.assertTrue(item.image_file)
        gal = GalleryImage.objects.get(caption='Uploaded Bridal Look')
        self.assertEqual(gal.look_group_id, 'bengali_bride')
        self.assertFalse(gal.is_group_cover)

    @no_network()
    def test_tc_med_009_reels_section_no_gallery_copy(self):
        """TC-MED-009: reels-only uploads do not create GalleryImage rows."""
        self.login_admin()
        before = GalleryImage.objects.count()
        upload = SimpleUploadedFile('reel.png', png_bytes((10, 100, 10)), content_type='image/png')
        resp = self.client.post('/api/admin/media/', {
            'title': 'Reels Only Shot', 'media_type': 'image', 'section': 'reels',
            'image_file': upload,
        })
        self.assert_ok(resp)
        self.assertEqual(GalleryImage.objects.count(), before)

    @no_network()
    def test_tc_med_010_default_title_and_views(self):
        """TC-MED-010: missing title/views get branded defaults."""
        self.login_admin()
        resp = self.client.post('/api/admin/media/', {'media_type': 'image'})
        data = self.assert_ok(resp)
        item = MediaItem.objects.get(id=data['item']['id'])
        self.assertEqual(item.title, 'Bridal Portfolio Look')
        self.assertIn('views', item.views_count)


class MediaModerationTests(RegressionTestCase):
    seed_dataset = True

    def test_tc_med_011_toggle_active_form(self):
        """TC-MED-011: form toggle flips the active flag… via JSON body."""
        self.login_admin()
        item = MediaItem.objects.get(title='Retired Trial Reel')
        data = self.assert_ok(self.json_post('/api/admin/media/', {
            'action': 'toggle_active', 'id': item.id,
        }))
        self.assertTrue(data['is_active'])
        item.refresh_from_db()
        self.assertTrue(item.is_active)

    def test_tc_med_012_delete_form_and_json(self):
        """TC-MED-012: delete via form action and JSON body."""
        self.login_admin()
        item = MediaItem.objects.get(title='Retired Trial Reel')
        resp = self.client.post('/api/admin/media/', {'action': 'delete', 'id': item.id})
        self.assert_ok(resp)
        self.assertFalse(MediaItem.objects.filter(id=item.id).exists())

        item2 = MediaItem.objects.get(title='Chandan Art Detail')
        self.assert_ok(self.json_post('/api/admin/media/', {'action': 'delete', 'id': item2.id}))
        self.assertFalse(MediaItem.objects.filter(id=item2.id).exists())


class LookGroupCrudTests(RegressionTestCase):
    seed_dataset = True

    def test_tc_med_013_list_groups_with_media(self):
        """TC-MED-013: group listing embeds media items and counts."""
        self.login_admin()
        data = self.json_response(self.client.get('/api/admin/lookgroup/'))
        kuhu = next(g for g in data['groups'] if g['client_name'] == 'Kuhu')
        self.assertEqual(kuhu['media_count'], 3)
        types = {m['media_type'] for m in kuhu['media_items']}
        self.assertEqual(types, {'image', 'instagram', 'youtube'})

    def test_tc_med_014_create_group_auto_name(self):
        """TC-MED-014: missing name auto-composes 'Client — Makeup Type'."""
        self.login_admin()
        resp = self.client.post('/api/admin/lookgroup/', {
            'client_name': 'Rani', 'makeup_type': 'Pastel Reception Glam',
            'category': 'reception',
        })
        data = self.assert_ok(resp)
        self.assertEqual(data['group']['name'], 'Rani — Pastel Reception Glam')

    def test_tc_med_015_update_and_delete_group(self):
        """TC-MED-015: update + delete lifecycle of a look group."""
        self.login_admin()
        grp = LookGroup.objects.get(client_name='Miss Rajak')
        resp = self.client.post('/api/admin/lookgroup/', {
            'id': grp.id, 'name': 'Miss Rajak — Updated Mauve Look',
            'client_name': 'Miss Rajak', 'makeup_type': 'Mauve Shimmer',
            'category': 'reception', 'order': '7',
        })
        self.assert_ok(resp)
        grp.refresh_from_db()
        self.assertEqual(grp.order, 7)

        resp = self.client.post('/api/admin/lookgroup/', {'action': 'delete', 'id': grp.id})
        self.assert_ok(resp)
        self.assertFalse(LookGroup.objects.filter(id=grp.id).exists())
        self.assertEqual(LookMediaItem.objects.filter(group_id=grp.id).count(), 0)  # cascade


class LookMediaTests(RegressionTestCase):
    seed_dataset = True

    @no_network()
    def test_tc_med_016_add_image_to_group(self):
        """TC-MED-016: adding an image increments group media."""
        self.login_admin()
        grp = LookGroup.objects.get(client_name='Kuhu')
        upload = SimpleUploadedFile('look.png', png_bytes((250, 200, 100)), content_type='image/png')
        resp = self.client.post('/api/admin/lookgroup/media/', {
            'group_id': grp.id, 'media_type': 'image', 'image_file': upload,
            'title': 'Kuhu Extra Look',
        })
        data = self.assert_ok(resp)
        self.assertEqual(data['item']['title'], 'Kuhu Extra Look')
        self.assertEqual(grp.media_items.count(), 4)

    @no_network()
    def test_tc_med_017_add_youtube_sets_auto_cover(self):
        """TC-MED-017: first media of a cover-less group becomes the cover."""
        self.login_admin()
        grp = LookGroup.objects.get(client_name='Miss Rajak')
        self.assertEqual(grp.cover_image_url, '')
        resp = self.client.post('/api/admin/lookgroup/media/', {
            'group_id': grp.id, 'media_type': 'youtube',
            'external_url': 'https://www.youtube.com/watch?v=zZzZzZzZzZz',
        })
        self.assert_ok(resp)
        grp.refresh_from_db()
        self.assertIn('zZzZzZzZzZz', grp.cover_image_url)

    @no_network()
    def test_tc_med_018_group_required(self):
        """TC-MED-018: adding media without a group is rejected."""
        self.login_admin()
        resp = self.client.post('/api/admin/lookgroup/media/', {'media_type': 'image'})
        data = self.json_response(resp)
        self.assertFalse(data['ok'])

    @no_network()
    def test_tc_med_019_missing_group_rejected(self):
        """TC-MED-019: unknown group id is rejected."""
        self.login_admin()
        resp = self.client.post('/api/admin/lookgroup/media/', {
            'group_id': 999999, 'media_type': 'image',
        })
        data = self.json_response(resp)
        self.assertFalse(data['ok'])

    def test_tc_med_020_delete_look_media(self):
        """TC-MED-020: look media deletion via form and JSON."""
        self.login_admin()
        item = LookMediaItem.objects.get(title='Kuhu Front Portrait')
        resp = self.client.post('/api/admin/lookgroup/media/', {'action': 'delete', 'id': item.id})
        self.assert_ok(resp)
        self.assertFalse(LookMediaItem.objects.filter(id=item.id).exists())

        item2 = LookMediaItem.objects.get(title='Rajak Side Profile')
        self.assert_ok(self.json_post('/api/admin/lookgroup/media/', {'action': 'delete', 'id': item2.id}))
        self.assertFalse(LookMediaItem.objects.filter(id=item2.id).exists())
