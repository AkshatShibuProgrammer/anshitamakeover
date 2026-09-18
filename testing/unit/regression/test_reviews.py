"""
REG-AREA-10 · Customer review submission & moderation regression tests.

Covers POST /api/review/submit/ (public) and GET/POST /api/admin/review/
(admin moderation: list, toggle, delete).

Test case IDs: TC-REV-001 … TC-REV-012
"""
from core.models import CustomerReview

from .base import RegressionTestCase


class PublicReviewSubmitTests(RegressionTestCase):

    def test_tc_rev_001_submit_full_review(self):
        """TC-REV-001: valid submission creates an active verified review."""
        data = self.assert_ok(self.json_post('/api/review/submit/', {
            'client_name': 'Tanvi Deshmukh', 'event_type': 'Royal Bride',
            'location': 'Bhopal', 'rating': 5,
            'review_text': 'Absolutely royal experience. The airbrush base is magic!',
            'wedding_date': 'Nov 2026',
        }))
        self.assertIn('submitted', data['message'].lower())
        review = CustomerReview.objects.get(id=data['review_id'])
        self.assertEqual(review.client_name, 'Tanvi Deshmukh')
        self.assertTrue(review.is_verified)
        self.assertTrue(review.is_active)
        self.assertEqual(review.rating, 5)

    def test_tc_rev_002_submit_minimal_defaults(self):
        """TC-REV-002: minimal payload gets sensible defaults."""
        data = self.assert_ok(self.json_post('/api/review/submit/', {
            'client_name': 'Minimal Bride', 'review_text': 'Great service.',
        }))
        review = CustomerReview.objects.get(id=data['review_id'])
        self.assertEqual(review.event_type, 'Bridal Makeover')
        self.assertEqual(review.location, 'India')
        self.assertEqual(review.rating, 5)

    def test_tc_rev_003_name_required(self):
        """TC-REV-003: missing name is rejected."""
        data = self.json_response(self.json_post('/api/review/submit/', {
            'review_text': 'No name supplied.',
        }))
        self.assertFalse(data['ok'])
        self.assertIn('required', data['error'].lower())

    def test_tc_rev_004_text_required(self):
        """TC-REV-004: missing review text is rejected."""
        data = self.json_response(self.json_post('/api/review/submit/', {
            'client_name': 'Empty Text',
        }))
        self.assertFalse(data['ok'])

    def test_tc_rev_005_rating_clamped_1_to_5(self):
        """TC-REV-005: out-of-range ratings clamp into [1, 5]."""
        data = self.assert_ok(self.json_post('/api/review/submit/', {
            'client_name': 'Over Rater', 'review_text': 'Wow', 'rating': 99,
        }))
        self.assertEqual(CustomerReview.objects.get(id=data['review_id']).rating, 5)
        data = self.assert_ok(self.json_post('/api/review/submit/', {
            'client_name': 'Zero Rater', 'review_text': 'Meh', 'rating': -3,
        }))
        self.assertEqual(CustomerReview.objects.get(id=data['review_id']).rating, 1)

    def test_tc_rev_006_get_not_allowed(self):
        """TC-REV-006: GET on submit endpoint returns 405."""
        resp = self.client.get('/api/review/submit/')
        self.assertEqual(resp.status_code, 405)

    def test_tc_rev_007_invalid_json_handled(self):
        """TC-REV-007: malformed JSON body returns ok=False (no 500)."""
        resp = self.client.post('/api/review/submit/', data='not-json{',
                                content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.json()['ok'])


class AdminReviewModerationTests(RegressionTestCase):
    seed_dataset = True

    def test_tc_rev_008_list_requires_login(self):
        """TC-REV-008: anonymous moderation request is redirected."""
        self.assert_redirect_to_login(self.client.get('/api/admin/review/'), '/api/admin/review/')

    def test_tc_rev_009_list_all_reviews(self):
        """TC-REV-009: admin sees every review including hidden ones."""
        self.login_admin()
        data = self.json_response(self.client.get('/api/admin/review/'))
        self.assertEqual(len(data['reviews']), CustomerReview.objects.count())
        names = [r['client_name'] for r in data['reviews']]
        self.assertIn('Hidden Reviewer', names)

    def test_tc_rev_010_toggle_active(self):
        """TC-REV-010: toggle_active flips visibility both ways."""
        self.login_admin()
        review = CustomerReview.objects.get(client_name='Priya Sharma')
        data = self.assert_ok(self.json_post('/api/admin/review/', {
            'action': 'toggle_active', 'id': review.id,
        }))
        self.assertFalse(data['is_active'])
        review.refresh_from_db()
        self.assertFalse(review.is_active)
        data = self.assert_ok(self.json_post('/api/admin/review/', {
            'action': 'toggle_active', 'id': review.id,
        }))
        self.assertTrue(data['is_active'])

    def test_tc_rev_011_delete_review(self):
        """TC-REV-011: delete removes the review permanently."""
        self.login_admin()
        review = CustomerReview.objects.get(client_name='Hidden Reviewer')
        self.assert_ok(self.json_post('/api/admin/review/', {
            'action': 'delete', 'id': review.id,
        }))
        self.assertFalse(CustomerReview.objects.filter(id=review.id).exists())

    def test_tc_rev_012_toggle_missing_review(self):
        """TC-REV-012: toggling a missing review returns no is_active key."""
        self.login_admin()
        data = self.json_response(self.json_post('/api/admin/review/', {
            'action': 'toggle_active', 'id': 999999,
        }))
        self.assertNotIn('is_active', data)
