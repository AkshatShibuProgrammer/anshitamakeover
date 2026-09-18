"""
REG-AREA-09 · Artist management CRUD regression tests.

Covers GET/POST/DELETE /api/admin/artist/ — roster management with slug
uniqueness, ordering, activation toggles and photo uploads.

Test case IDs: TC-ART-001 … TC-ART-010
"""
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from core.models import Artist

from .base import RegressionTestCase


def make_png_upload(name='test_artist.png'):
    """Build a tiny valid PNG upload in memory."""
    buf = BytesIO()
    Image.new('RGB', (8, 8), color=(212, 175, 55)).save(buf, format='PNG')
    return SimpleUploadedFile(name, buf.getvalue(), content_type='image/png')


class ArtistListTests(RegressionTestCase):
    seed_dataset = True

    def test_tc_art_001_list_requires_login(self):
        """TC-ART-001: anonymous roster request is redirected."""
        self.assert_redirect_to_login(self.client.get('/api/admin/artist/'), '/api/admin/artist/')

    def test_tc_art_002_list_payload(self):
        """TC-ART-002: listing includes inactive artists for admin control."""
        self.login_admin()
        data = self.json_response(self.client.get('/api/admin/artist/'))
        names = [a['name'] for a in data['artists']]
        self.assertIn('Anshita', names)
        self.assertIn('Shristee', names)  # inactive but visible to admin
        shristee = next(a for a in data['artists'] if a['name'] == 'Shristee')
        self.assertFalse(shristee['is_active'])


class ArtistCreateTests(RegressionTestCase):

    def test_tc_art_003_create_with_slug(self):
        """TC-ART-003: create derives a unique slug from the name."""
        self.login_admin()
        resp = self.client.post('/api/admin/artist/', {
            'name': 'Ritu Kapoor', 'specialities': 'hair,beauty',
            'bio': 'Veteran hair artist.', 'order': '3', 'is_active': '1',
        })
        data = self.assert_ok(resp)
        artist = Artist.objects.get(id=data['artist']['id'])
        self.assertEqual(artist.slug, 'ritu-kapoor')
        self.assertEqual(artist.specialities, 'hair,beauty')

    def test_tc_art_004_slug_collision_suffix(self):
        """TC-ART-004: duplicate names get -1, -2 slug suffixes."""
        self.login_admin()
        self.client.post('/api/admin/artist/', {'name': 'Meera Joshi'})
        resp = self.client.post('/api/admin/artist/', {'name': 'Meera Joshi'})
        data = self.assert_ok(resp)
        slugs = set(Artist.objects.values_list('slug', flat=True))
        self.assertIn('meera-joshi', slugs)
        self.assertIn('meera-joshi-1', slugs)

    def test_tc_art_005_name_required(self):
        """TC-ART-005: empty name rejected with clear error."""
        self.login_admin()
        resp = self.client.post('/api/admin/artist/', {'name': '   '})
        data = self.json_response(resp)
        self.assertFalse(data['ok'])

    def test_tc_art_006_photo_upload(self):
        """TC-ART-006: PNG photo upload is stored and URL returned."""
        self.login_admin()
        resp = self.client.post('/api/admin/artist/', {
            'name': 'Photogenic Artist', 'photo': make_png_upload(),
        })
        data = self.assert_ok(resp)
        self.assertTrue(data['artist']['photo_url'].endswith('.png'))

    def test_tc_art_007_invalid_order_defaults_zero(self):
        """TC-ART-007: non-numeric order falls back to 0."""
        self.login_admin()
        resp = self.client.post('/api/admin/artist/', {'name': 'Order Test', 'order': 'abc'})
        self.assert_ok(resp)
        self.assertEqual(Artist.objects.get(name='Order Test').order, 0)


class ArtistUpdateDeleteTests(RegressionTestCase):
    seed_dataset = True

    def test_tc_art_008_update_fields(self):
        """TC-ART-008: POST with id updates name/bio/order without new slug."""
        self.login_admin()
        artist = Artist.objects.get(slug='tejal-sinha')
        resp = self.client.post('/api/admin/artist/', {
            'id': artist.id, 'name': 'Tejal Sinha', 'bio': 'Updated bio.',
            'specialities': 'hair', 'order': '9', 'is_active': '0',
        })
        data = self.assert_ok(resp)
        artist.refresh_from_db()
        self.assertEqual(artist.bio, 'Updated bio.')
        self.assertEqual(artist.order, 9)
        self.assertFalse(artist.is_active)

    def test_tc_art_009_update_missing_artist(self):
        """TC-ART-009: editing a missing id returns ok=False."""
        self.login_admin()
        resp = self.client.post('/api/admin/artist/', {'id': 999999, 'name': 'Ghost'})
        data = self.json_response(resp)
        self.assertFalse(data['ok'])

    def test_tc_art_010_delete_form_and_json(self):
        """TC-ART-010: delete via form action and via JSON DELETE."""
        self.login_admin()
        shristee = Artist.objects.get(slug='shristee')
        resp = self.client.post('/api/admin/artist/', {'action': 'delete', 'id': shristee.id})
        self.assert_ok(resp)
        self.assertFalse(Artist.objects.filter(id=shristee.id).exists())

        tejal = Artist.objects.get(slug='tejal-sinha')
        resp = self.client.delete('/api/admin/artist/',
                                  data='{"id": %d}' % tejal.id, content_type='application/json')
        self.assert_ok(resp)
        self.assertFalse(Artist.objects.filter(id=tejal.id).exists())
