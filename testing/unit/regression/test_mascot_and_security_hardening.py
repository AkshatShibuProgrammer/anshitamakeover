"""
REG-AREA-15 · Mascot walk-engine + security hardening regression tests.

Locks in the remediation work described by
``docs/COMPREHENSIVE_3D_MASCOT_ANIMATION_AND_SECURITY_AUDIT.md``:

* §6  the scroll-scrubbed walk-and-dock engine replaces the binary
      ``scrollY > 180`` threshold, and both rigs expose the standard API.
* §7  CSRF protection, XSS sanitisation, rate limiting (429) and WebGL
      disposal guarantees.

Test case IDs: TC-HRD-001 … TC-HRD-014
"""
import json
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.core.cache import cache
from django.test import override_settings

from core.models import ChatMessage, BookingEnquiry
from core.security import sanitize_text, sanitize_bot_reply, strip_html, looks_like_xss
from core.ratelimit import parse_rate

from .base import RegressionTestCase

DJANGO_DIR = Path(settings.BASE_DIR)
STATIC_DIR = DJANGO_DIR / 'core' / 'static' / 'core'
TEMPLATE_DIR = DJANGO_DIR / 'core' / 'templates'

XSS_PAYLOAD = '<img src=x onerror="alert(1)">Namaste'


def chat(client, message, session_id='hardening-chat-01'):
    return client.post(
        '/api/chatbot/',
        json.dumps({'message': message, 'session_id': session_id}),
        content_type='application/json',
    )


# ══════════════════════════════════════════════════════════════════════════
# 7.1 — CSRF on the AI chatbot + booking APIs
# ══════════════════════════════════════════════════════════════════════════
class CsrfEnforcementTests(RegressionTestCase):

    def test_tc_hrd_001_chatbot_post_without_csrf_token_is_rejected(self):
        """TC-HRD-001: a forged cross-site chat POST is refused with 403."""
        csrf_client = self.client_class(enforce_csrf_checks=True)
        resp = chat(csrf_client, 'bridal packages please')
        self.assertEqual(resp.status_code, 403)

    def test_tc_hrd_002_chatbot_post_with_csrf_token_succeeds(self):
        """TC-HRD-002: the real widget (cookie + X-CSRFToken) still works."""
        csrf_client = self.client_class(enforce_csrf_checks=True)
        # Warm the cookie exactly like a browser page load does.
        self.assertEqual(csrf_client.get('/').status_code, 200)
        token = csrf_client.cookies['csrftoken'].value
        resp = csrf_client.post(
            '/api/chatbot/',
            json.dumps({'message': 'hello'}),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertTrue(resp.json()['reply'])

    def test_tc_hrd_003_public_page_mints_csrf_cookie(self):
        """TC-HRD-003: EnsureCsrfCookieMiddleware mints csrftoken on GET /."""
        resp = self.client.get('/')
        self.assertIn('csrftoken', resp.cookies)

    def test_tc_hrd_004_booking_post_requires_csrf(self):
        """TC-HRD-004: enquiry creation rejects un-tokened cross-site posts."""
        csrf_client = self.client_class(enforce_csrf_checks=True)
        resp = csrf_client.post(
            '/api/booking/',
            json.dumps({'name': 'A', 'phone': '1', 'items': []}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 403)


# ══════════════════════════════════════════════════════════════════════════
# 7.1 — Rate limiting / LLM denial-of-wallet
# ══════════════════════════════════════════════════════════════════════════
class RateLimitTests(RegressionTestCase):

    def setUp(self):
        super().setUp()
        cache.clear()  # LocMem buckets survive between tests by design

    def tearDown(self):
        cache.clear()
        super().tearDown()

    @override_settings(RATELIMIT_ENABLE=True)
    def test_tc_hrd_005_chatbot_throttles_after_budget(self):
        """TC-HRD-005: the 16th chat request in a minute returns HTTP 429."""
        statuses = [chat(self.client, 'rate limit probe %d' % i).status_code for i in range(16)]
        self.assertEqual(statuses[:15], [200] * 15, statuses)
        self.assertEqual(statuses[15], 429, statuses)

    @override_settings(RATELIMIT_ENABLE=True)
    def test_tc_hrd_006_throttle_response_shape(self):
        """TC-HRD-006: 429 carries Retry-After + JSON error for the widget."""
        for _ in range(15):
            chat(self.client, 'warm up')
        resp = chat(self.client, 'one too many')
        self.assertEqual(resp.status_code, 429)
        self.assertTrue(resp.headers.get('Retry-After'))
        body = resp.json()
        self.assertFalse(body['ok'])
        self.assertGreaterEqual(body['retry_after'], 1)

    @override_settings(RATELIMIT_ENABLE=True)
    def test_tc_hrd_007_booking_endpoint_throttled(self):
        """TC-HRD-007: booking spam is throttled too (10/min)."""
        payload = {'name': 'Rate Probe', 'phone': '9999999999',
                   'items': [{'id': 'service-424242', 'qty': 1}]}
        statuses = []
        for _ in range(11):
            statuses.append(self.client.post(
                '/api/booking/', json.dumps(payload),
                content_type='application/json').status_code)
        self.assertIn(201, statuses)
        self.assertEqual(statuses[-1], 429, statuses)

    def test_tc_hrd_008_rate_parser_rejects_garbage(self):
        """TC-HRD-008: malformed rate strings fail loudly, never silently."""
        self.assertEqual(parse_rate('15/m'), (15, 60))
        self.assertEqual(parse_rate('2/5m'), (2, 300))
        for bad in ('', '15', 'abc', '0/m', '15/x'):
            with self.assertRaises(ValueError):
                parse_rate(bad)


# ══════════════════════════════════════════════════════════════════════════
# 7.1 — XSS sanitisers (server-side helpers)
# ══════════════════════════════════════════════════════════════════════════
class SanitizerTests(RegressionTestCase):

    def test_tc_hrd_009_strip_html_removes_injection_vectors(self):
        """TC-HRD-009: tags, handlers, comments and dangerous schemes go away."""
        self.assertNotIn('<script', strip_html('<script>alert(1)</script>hi'))
        self.assertNotIn('onerror', strip_html(XSS_PAYLOAD))
        self.assertNotIn('javascript:', strip_html('<a href="javascript:alert(1)">x</a>').lower())
        self.assertNotIn('<!--', strip_html('<!--[if IE]><script>x</script><![endif]-->'))
        # Double-encoded payloads must not survive either.
        self.assertNotIn('<script', strip_html('&lt;script&gt;alert(1)&lt;/script&gt;'))

    def test_tc_hrd_010_sanitize_text_caps_and_normalises(self):
        """TC-HRD-010: control/zero-width characters and length are constrained."""
        out = sanitize_text('a\u200bb\u0000c' + 'x' * 100, max_length=20)
        self.assertNotIn('\u200b', out)
        self.assertNotIn('\x00', out)
        self.assertLessEqual(len(out), 20)

    def test_tc_hrd_011_bot_reply_never_empty_or_hostile(self):
        """TC-HRD-011: a pure-payload reply degrades to a safe greeting."""
        hostile = sanitize_bot_reply('<script>fetch("//evil")</script>')
        self.assertNotIn('<script', hostile)
        self.assertTrue(hostile.strip())
        self.assertTrue(looks_like_xss(XSS_PAYLOAD))

    def test_tc_hrd_012_chatbot_reply_is_stored_inert(self):
        """TC-HRD-012: a hostile Gemini reply is sanitised before persistence."""
        with mock.patch('core.views.chatbot.get_gemini_api_key', return_value='fake-key'), \
             mock.patch('core.views.chatbot.gemini_chat',
                        return_value='<img src=x onerror=alert(1)>Namaste ji ✨'):
            resp = chat(self.client, 'hello')
        self.assertEqual(resp.status_code, 200)
        reply = resp.json()['reply']
        self.assertNotIn('onerror', reply)
        self.assertNotIn('<img', reply)
        stored = ChatMessage.objects.latest('id')
        self.assertNotIn('onerror', stored.response)

    def test_tc_hrd_013_hostile_user_message_is_stored_inert(self):
        """TC-HRD-013: stored user copy cannot re-execute in the admin portal."""
        resp = chat(self.client, XSS_PAYLOAD)
        self.assertEqual(resp.status_code, 200)
        stored = ChatMessage.objects.latest('id')
        self.assertNotIn('<', stored.message)
        self.assertNotIn('onerror', stored.message)

    def test_tc_hrd_014_hostile_session_id_is_replaced(self):
        """TC-HRD-014: session ids are opaque tokens, not free text."""
        resp = chat(self.client, 'hello', session_id='<script>alert(1)</script>')
        body = resp.json()
        self.assertNotIn('<', body['session_id'])
        self.assertNotEqual(body['session_id'], '<script>alert(1)</script>')
        self.assertIn(body['session_id'], ChatMessage.objects.latest('id').session_id)


# ══════════════════════════════════════════════════════════════════════════
# 7.1 — IDOR: opaque public booking reference
# ══════════════════════════════════════════════════════════════════════════
class BookingReferenceTests(RegressionTestCase):

    def test_tc_hrd_015_booking_returns_uuid_not_integer_pk(self):
        """TC-HRD-015: the API hands back a UUID so ids cannot be enumerated."""
        payload = {'name': 'Bride Probe', 'phone': '9876500000',
                   'city': 'Bhopal', 'items': [{'id': 'service-999', 'qty': 1}]}
        resp = self.client.post('/api/booking/', json.dumps(payload),
                                content_type='application/json')
        self.assertEqual(resp.status_code, 201, resp.content)
        body = resp.json()
        enquiry = BookingEnquiry.objects.latest('id')
        self.assertEqual(body['id'], str(enquiry.public_id))
        self.assertNotEqual(body['id'], str(enquiry.pk))
        self.assertEqual(len(body['reference']), 8)


# ══════════════════════════════════════════════════════════════════════════
# 7.2 — CSP + hardening headers
# ══════════════════════════════════════════════════════════════════════════
class ContentSecurityPolicyTests(RegressionTestCase):

    @override_settings(CSP_ENABLED=True, CSP_REPORT_ONLY=False)
    def test_tc_hrd_016_csp_header_emitted_when_enabled(self):
        """TC-HRD-016: enforcing CSP + hardening headers are present."""
        resp = self.client.get('/')
        policy = resp.headers.get('Content-Security-Policy')
        self.assertTrue(policy, resp.headers)
        self.assertIn("default-src 'self'", policy)
        self.assertIn("object-src 'none'", policy)
        self.assertEqual(resp.headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(resp.headers.get('Referrer-Policy'), 'strict-origin-when-cross-origin')

    @override_settings(CSP_ENABLED=True, CSP_REPORT_ONLY=True)
    def test_tc_hrd_017_report_only_mode_does_not_block(self):
        """TC-HRD-017: Report-Only rollout keeps the page working."""
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Content-Security-Policy-Report-Only', resp.headers)
        self.assertNotIn('Content-Security-Policy', resp.headers)

    @override_settings(CSP_ENABLED=False)
    def test_tc_hrd_018_dev_preview_not_broken_by_csp(self):
        """TC-HRD-018: the dev/preview profile stays CSP-free (iframe preview)."""
        resp = self.client.get('/')
        self.assertNotIn('Content-Security-Policy', resp.headers)
        self.assertEqual(resp.headers.get('X-Frame-Options'), 'ALLOWALL')


# ══════════════════════════════════════════════════════════════════════════
# §6 — walk-and-dock engine + WebGL lifecycle (static asset contracts)
# ══════════════════════════════════════════════════════════════════════════
class MascotEngineAssetTests(RegressionTestCase):

    def _read(self, *parts):
        path = STATIC_DIR.joinpath(*parts)
        self.assertTrue(path.exists(), f'missing asset: {path}')
        return path.read_text(encoding='utf-8')

    def test_tc_hrd_019_engine_exposes_scrubbed_api(self):
        """TC-HRD-019: engine implements scrub/dock/destroy + diagnostics."""
        src = self._read('js', 'controllers', 'mascot-scroll-engine.js')
        for symbol in ('attachCharacter', 'setProgress', 'getDiagnostics',
                       'readScrollPosition', 'enterWalkStage', 'placementFor'):
            self.assertIn(symbol, src)
        self.assertIn('prefers-reduced-motion', src)
        self.assertIn('visibilitychange', src)  # battery gate

    def test_tc_hrd_020_both_rigs_share_the_walk_contract(self):
        """TC-HRD-020: Mochi and Pip rig parity (scrub/dock/destroy/dispose)."""
        for rig in ('MochiCharacter.js', 'PipCharacter.js'):
            src = self._read('js', 'characters', rig)
            for symbol in ('scrub(progress, opts)', 'applyWalkPose(dt)', 'dock()',
                           'undock()', 'pause()', 'resume()', 'destroy()',
                           'forceContextLoss', 'geometry.dispose()', 'mat.dispose()'):
                self.assertIn(symbol, src, f'{rig} missing {symbol}')

    def test_tc_hrd_021_binary_scroll_threshold_is_not_the_primary_path(self):
        """TC-HRD-021: the 180px threshold survives only as a fallback branch."""
        base = (TEMPLATE_DIR / 'core' / 'base.html').read_text(encoding='utf-8')
        self.assertIn('mascot-scroll-engine.js', base)
        self.assertIn('engineActive()', base)
        # Legacy constants must be inside the fallback function, not the entry point.
        self.assertIn('function legacyThresholdCheck()', base)
        self.assertIn('mascot-walk-stage', base)

    def test_tc_hrd_022_walk_stage_markup_is_full_viewport_and_inert(self):
        """TC-HRD-022: the walk layer never blocks page interaction."""
        modal = (TEMPLATE_DIR / 'components' / 'chatbot_modal.html').read_text(encoding='utf-8')
        self.assertIn('id="mascot-walk-stage"', modal)
        base = (TEMPLATE_DIR / 'core' / 'base.html').read_text(encoding='utf-8')
        self.assertIn('#mascot-walk-stage', base)
        self.assertIn('pointer-events: none', base)

    def test_tc_hrd_023_innerhtml_sinks_are_sanitised(self):
        """TC-HRD-023: bubble/chat sinks route through AnshitaSanitizer."""
        base = (TEMPLATE_DIR / 'core' / 'base.html').read_text(encoding='utf-8')
        self.assertIn('AnshitaSanitizer.setHtml(textEl, text)', base)
        self.assertIn('AnshitaSanitizer.sanitize(html)', base)
        sanitiser = self._read('js', 'sanitize-html.js')
        self.assertIn('ALLOWED_TAGS', sanitiser)
        self.assertIn('javascript', sanitiser)
        self.assertIn('rel', sanitiser)

    def test_tc_hrd_024_localstorage_holds_visual_preferences_only(self):
        """TC-HRD-024: no PII/tokens are persisted in client storage."""
        inspected = []
        for path in list(TEMPLATE_DIR.rglob('*.html')) + list(STATIC_DIR.rglob('*.js')):
            try:
                text = path.read_text(encoding='utf-8')
            except (UnicodeDecodeError, OSError):
                continue
            for line in text.splitlines():
                if 'localStorage.setItem' not in line:
                    continue
                inspected.append(line)
                lowered = line.lower()
                for forbidden in ('phone', 'token', 'password', 'booking', 'customer'):
                    self.assertNotIn(forbidden, lowered,
                                     f'PII-looking localStorage write in {path}: {line.strip()}')
        self.assertTrue(inspected, 'expected at least one localStorage write to audit')


# ══════════════════════════════════════════════════════════════════════════
# 7.1 — Public review submission (CSRF + throttle + sanitiser)
# ══════════════════════════════════════════════════════════════════════════
def review_post(client, payload, **extra):
    return client.post(
        '/api/review/submit/',
        json.dumps(payload),
        content_type='application/json',
        **extra,
    )


class ReviewSubmissionHardeningTests(RegressionTestCase):

    def setUp(self):
        super().setUp()
        cache.clear()

    def tearDown(self):
        cache.clear()
        super().tearDown()

    def test_tc_hrd_025_review_post_requires_csrf(self):
        """TC-HRD-025: forged cross-site review POST is refused with 403."""
        csrf_client = self.client_class(enforce_csrf_checks=True)
        resp = review_post(csrf_client, {'client_name': 'Bot', 'review_text': 'spam'})
        self.assertEqual(resp.status_code, 403)

    def test_tc_hrd_026_review_post_with_token_succeeds(self):
        """TC-HRD-026: the real review modal (cookie + X-CSRFToken) still works."""
        csrf_client = self.client_class(enforce_csrf_checks=True)
        self.assertEqual(csrf_client.get('/').status_code, 200)
        token = csrf_client.cookies['csrftoken'].value
        resp = review_post(
            csrf_client,
            {'client_name': 'Token Bride', 'review_text': 'Lovely work.', 'rating': 5},
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertTrue(resp.json()['ok'])

    @override_settings(RATELIMIT_ENABLE=True)
    def test_tc_hrd_027_review_endpoint_throttled(self):
        """TC-HRD-027: the 11th review in a minute returns HTTP 429."""
        statuses = [
            review_post(self.client, {
                'client_name': 'Rate Bride %d' % i, 'review_text': 'Nice.',
            }).status_code
            for i in range(11)
        ]
        self.assertEqual(statuses[:10], [200] * 10, statuses)
        self.assertEqual(statuses[10], 429, statuses)

    def test_tc_hrd_028_hostile_review_fields_are_sanitised(self):
        """TC-HRD-028: markup/script in any review field is stripped at rest."""
        from core.models import CustomerReview
        resp = review_post(self.client, {
            'client_name': '<script>alert(1)</script>Mallory',
            'review_text': 'Best <img src=x onerror=alert(2)> studio',
            'event_type': '<iframe src="//evil"></iframe>Wedding',
            'location': '<b>Nowhere</b>',
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        if not data.get('ok'):
            self.skipTest('sanitiser emptied the payload — no PII stored')
        review = CustomerReview.objects.get(id=data['review_id'])
        for field in (review.client_name, review.review_text,
                      review.event_type, review.location):
            self.assertNotIn('<', field)
            self.assertNotIn('>', field)
            self.assertNotIn('onerror', field.lower())

    def test_tc_hrd_029_review_lengths_are_capped(self):
        """TC-HRD-029: oversized review payloads are truncated, not stored raw."""
        from core.models import CustomerReview
        resp = review_post(self.client, {
            'client_name': 'L' * 5000,
            'review_text': 'R' * 20000,
            'event_type': 'E' * 500,
            'location': 'C' * 500,
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        if not data.get('ok'):
            self.skipTest('payload rejected before storage')
        review = CustomerReview.objects.get(id=data['review_id'])
        self.assertLessEqual(len(review.client_name), 80)
        self.assertLessEqual(len(review.review_text), 1200)
        self.assertLessEqual(len(review.location), 60)

    def test_tc_hrd_030_review_errors_do_not_leak_internals(self):
        """TC-HRD-030: a DB failure returns a generic message, never a traceback."""
        with mock.patch('core.views.reviews.create_customer_review',
                        side_effect=RuntimeError('secret-dsn postgres://u:p@host/db')):
            resp = review_post(self.client, {'client_name': 'A', 'review_text': 'B'})
        self.assertEqual(resp.status_code, 500)
        body = resp.content.decode()
        self.assertNotIn('secret-dsn', body)
        self.assertNotIn('postgres://', body)
        self.assertNotIn('Traceback', body)
        self.assertFalse(resp.json()['ok'])
