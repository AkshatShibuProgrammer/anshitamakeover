"""
REG-AREA-12 · Public chatbot (AI Concierge) regression tests.

The chatbot must work in two modes:
1. **Fallback mode** (no Gemini key / Gemini failure) — deterministic intent
   engine with smart negotiation, tested fully here.
2. **Gemini mode** — live DB prompt injection with negotiation guardrails,
   tested with a mocked HTTP layer (no real network calls).

Every exchange must be persisted to ChatMessage.

Test case IDs: TC-CHT-001 … TC-CHT-018
"""
import json
from pathlib import Path
from unittest import mock

from django.conf import settings

from core.models import ChatMessage

from .base import RegressionTestCase

GEMINI_KEY_FILE = Path(settings.BASE_DIR) / 'gemini_api_key.txt'


def chat(client, message, session_id='regression-chat-01'):
    resp = client.post('/api/chatbot/', json.dumps({'message': message, 'session_id': session_id}),
                       content_type='application/json')
    assert resp.status_code == 200, resp.content
    return resp.json()


class ChatbotApiContractTests(RegressionTestCase):

    def test_tc_cht_001_requires_post(self):
        """TC-CHT-001: GET on chatbot API returns 405."""
        self.assertEqual(self.client.get('/api/chatbot/').status_code, 405)

    def test_tc_cht_002_empty_message_greeting(self):
        """TC-CHT-002: empty message returns a greeting and is not persisted."""
        data = chat(self.client, '')
        self.assertIn('reply', data)
        self.assertTrue(data['reply'])
        self.assertEqual(ChatMessage.objects.count(), 0)

    def test_tc_cht_003_session_id_round_trip(self):
        """TC-CHT-003: supplied session id echoes back and is stored."""
        data = chat(self.client, 'hello there', session_id='sess-xyz')
        self.assertEqual(data['session_id'], 'sess-xyz')
        self.assertEqual(ChatMessage.objects.get().session_id, 'sess-xyz')

    def test_tc_cht_004_malformed_json_never_500(self):
        """TC-CHT-004: malformed body returns graceful WhatsApp fallback reply."""
        resp = self.client.post('/api/chatbot/', data='{{{bad', content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('reply', resp.json())

    def test_tc_cht_005_history_persisted(self):
        """TC-CHT-005: question and answer both land in ChatMessage."""
        chat(self.client, 'What are your bridal packages?')
        msg = ChatMessage.objects.get()
        self.assertEqual(msg.message, 'What are your bridal packages?')
        self.assertTrue(msg.response)


class FallbackIntentTests(RegressionTestCase):
    """Intent routing of the deterministic fallback engine."""

    def test_tc_cht_006_greeting_intent(self):
        """TC-CHT-006: greetings produce the warm welcome message."""
        reply = chat(self.client, 'Hello!')['reply']
        self.assertIn('Namaste', reply)
        self.assertIn('TODAYVIP', reply)  # today's auto coupon surfaced

    def test_tc_cht_007_bridal_intent(self):
        """TC-CHT-007: bridal intent surfaces suites + booking privileges."""
        # NB: the word 'wedding' also trips the negotiation keyword list, so a
        # pure bridal-intent probe must avoid it (documented keyword overlap).
        reply = chat(self.client, 'tell me about your bridal makeup packages')['reply']
        self.assertIn('Bridal Suites', reply)
        self.assertIn('FREE', reply)          # free side makeups privilege
        self.assertIn('WhatsApp', reply)      # WhatsApp hand-off

    def test_tc_cht_008_pricing_intent(self):
        """TC-CHT-008: pricing intent returns the pricing table."""
        reply = chat(self.client, 'What is the price of HD makeup?')['reply']
        self.assertIn('Pricing Guide', reply)
        self.assertIn('Airbrush', reply)

    def test_tc_cht_009_coupon_intent(self):
        """TC-CHT-009: coupon queries return active offers."""
        reply = chat(self.client, 'Do you have any coupon code?')['reply']
        self.assertIn('TODAYVIP', reply)

    def test_tc_cht_010_location_intent(self):
        """TC-CHT-010: location queries mention the studio base."""
        reply = chat(self.client, 'Where is your studio located?')['reply']
        self.assertIn('Madhya Pradesh', reply)

    def test_tc_cht_011_unknown_intent_default(self):
        """TC-CHT-011: unmatched messages get the WhatsApp fallback."""
        reply = chat(self.client, 'quantum entanglement of zebra stripes')['reply']
        self.assertIn('WhatsApp', reply)


class FallbackNegotiationTests(RegressionTestCase):
    """Smart AI negotiation flow (floor price enforcement)."""

    def test_tc_cht_012_budget_above_floor_accepted(self):
        """TC-CHT-012: budget >= floor is granted as privilege rate."""
        reply = chat(self.client, 'my budget is 30000, can you manage?')['reply']
        self.assertIn('Privilege Approved', reply)
        self.assertIn('₹30,000', reply)
        self.assertIn('TODAYVIP', reply)
        self.assertIn('wa.me', reply)

    def test_tc_cht_013_budget_k_notation(self):
        """TC-CHT-013: '30k' notation parses to ₹30,000 budget."""
        reply = chat(self.client, 'my budget is 30k only')['reply']
        self.assertIn('₹30,000', reply)

    def test_tc_cht_014_budget_below_floor_defended(self):
        """TC-CHT-014: budget below floor never undercuts the floor price."""
        reply = chat(self.client, 'I can only pay 20000')['reply']
        self.assertIn('₹26,250', reply)      # 75% floor of ₹35,000
        self.assertNotIn('Privilege Approved', reply)

    def test_tc_cht_015_airbrush_suite_selected_for_high_budget(self):
        """TC-CHT-015: budget above airbrush floor targets the airbrush suite."""
        reply = chat(self.client, 'budget 40000 for the best you have')['reply']
        self.assertIn('Airbrush', reply)

    def test_tc_cht_016_generic_negotiation_prompt(self):
        """TC-CHT-016: discount question without budget invites negotiation."""
        reply = chat(self.client, 'can I get a discount please?')['reply']
        self.assertIn('Negotiation', reply)
        self.assertIn('Wedding Date', reply)

    def test_tc_cht_017_negotiation_disabled(self):
        """TC-CHT-017: with negotiation disabled, discount query hits coupon intent."""
        self.ensure_settings(ai_negotiation_enabled=False)
        reply = chat(self.client, 'can I get a discount please?')['reply']
        self.assertNotIn('Negotiation', reply)


class GeminiModeTests(RegressionTestCase):
    """Gemini-backed concierge (network mocked)."""

    def setUp(self):
        super().setUp()
        GEMINI_KEY_FILE.write_text('test-gemini-key-0001\n')
        self.addCleanup(GEMINI_KEY_FILE.unlink, missing_ok=True)

    def _mock_gemini(self, reply_text, status=200):
        fake = mock.MagicMock()
        fake.status_code = status
        fake.json.return_value = {
            'candidates': [{'content': {'parts': [{'text': reply_text}]}}],
        }
        fake.text = reply_text
        return mock.patch('requests.post', return_value=fake)

    def test_tc_cht_018_gemini_reply_passthrough_and_prompt_injection(self):
        """TC-CHT-018: live-DB pricing is injected into the Gemini system prompt."""
        from core.models import MakeupPackage
        MakeupPackage.objects.create(name='Prompt Injection Probe Suite', package_type='bridal',
                                     price=35000, features='Probe feature')
        captured = {}

        def capture_post(url, json=None, timeout=None):
            captured['url'] = url
            captured['payload'] = json
            fake = mock.MagicMock()
            fake.status_code = 200
            fake.json.return_value = {'candidates': [{'content': {'parts': [{'text': 'Gemini says hello ✨'}]}}]}
            return fake

        with mock.patch('requests.post', side_effect=capture_post):
            data = chat(self.client, 'what packages do you have?')
        self.assertEqual(data['reply'], 'Gemini says hello ✨')
        system_prompt = captured['payload']['systemInstruction']['parts'][0]['text']
        self.assertIn('Prompt Injection Probe Suite', system_prompt)   # live DB pricing
        self.assertIn('ABSOLUTE MINIMUM NEGOTIATED FLOOR', system_prompt)
        self.assertIn('TODAYVIP', system_prompt)

    def test_tc_cht_019_gemini_error_falls_back(self):
        """TC-CHT-019: Gemini HTTP failure degrades to the fallback engine."""
        fake = mock.MagicMock()
        fake.status_code = 500
        fake.text = 'server exploded'
        with mock.patch('requests.post', return_value=fake):
            data = chat(self.client, 'bridal packages please')
        self.assertIn('Bridal Suites', data['reply'])  # fallback content

    def test_tc_cht_020_gemini_exception_falls_back(self):
        """TC-CHT-020: network exception also degrades gracefully."""
        with mock.patch('requests.post', side_effect=ConnectionError('offline')):
            data = chat(self.client, 'hello')
        self.assertIn('Namaste', data['reply'])

class ConversationContextTests(RegressionTestCase):
    """The concierge must carry conversation memory and respect style/token rules."""

    def setUp(self):
        super().setUp()
        GEMINI_KEY_FILE.write_text('test-gemini-key-0001\n')
        self.addCleanup(GEMINI_KEY_FILE.unlink, missing_ok=True)

    def _capture_posts(self):
        captured = []

        def capture_post(url, json=None, timeout=None):
            captured.append({'url': url, 'payload': json, 'timeout': timeout})
            fake = mock.MagicMock()
            fake.status_code = 200
            fake.json.return_value = {'candidates': [{'content': {'parts': [{'text': 'ok ✨'}]}}]}
            return fake

        return mock.patch('requests.post', side_effect=capture_post), captured

    def test_tc_cht_021_history_sent_to_gemini(self):
        """TC-CHT-021: earlier turns of the same session are re-sent as context."""
        patcher, captured = self._capture_posts()
        with patcher:
            chat(self.client, 'what is the bridal price?', session_id='ctx-01')
            chat(self.client, 'aur usme kya kya milega?', session_id='ctx-01')
        contents = captured[-1]['payload']['contents']
        # turn 1 user + model, turn 2 user
        self.assertEqual(len(contents), 3)
        self.assertEqual(contents[0]['role'], 'user')
        self.assertEqual(contents[0]['parts'][0]['text'], 'what is the bridal price?')
        self.assertEqual(contents[1]['role'], 'model')
        self.assertEqual(contents[2]['parts'][0]['text'], 'aur usme kya kya milega?')

    def test_tc_cht_022_sessions_are_isolated(self):
        """TC-CHT-022: a different session id starts with a clean context."""
        patcher, captured = self._capture_posts()
        with patcher:
            chat(self.client, 'first question', session_id='ctx-A')
            chat(self.client, 'another question', session_id='ctx-B')
        self.assertEqual(len(captured[-1]['payload']['contents']), 1)

    def test_tc_cht_023_history_window_capped(self):
        """TC-CHT-023: only the last N exchanges are re-sent (token budget)."""
        from core.views.chatbot import GEMINI_HISTORY_TURNS
        patcher, captured = self._capture_posts()
        with patcher:
            for i in range(GEMINI_HISTORY_TURNS + 4):
                chat(self.client, f'message number {i}', session_id='ctx-cap')
        contents = captured[-1]['payload']['contents']
        self.assertLessEqual(len(contents), GEMINI_HISTORY_TURNS * 2 + 1)

    def test_tc_cht_024_token_guardrails(self):
        """TC-CHT-024: thinking tokens disabled, output capped, no-table style rule."""
        patcher, captured = self._capture_posts()
        with patcher:
            chat(self.client, 'hello', session_id='ctx-tok')
        payload = captured[-1]['payload']
        gen = payload['generationConfig']
        self.assertEqual(gen['thinkingConfig']['thinkingBudget'], 0)
        self.assertLessEqual(gen['maxOutputTokens'], 640)
        prompt = payload['systemInstruction']['parts'][0]['text']
        self.assertIn('no markdown tables', prompt.lower())
        self.assertNotIn('| Service / Package |', prompt)  # bulky pricing table removed


class FallbackStyleTests(RegressionTestCase):
    """Fallback replies must be plain-text bullets — no pipes, no html."""

    def test_tc_cht_025_no_tables_in_any_intent(self):
        """TC-CHT-025: no intent renders a markdown table or <br> anymore."""
        probes = [
            'tell me about your bridal packages',
            'What is the price of HD makeup?',
            'can I get a discount please?',
            'Do you have any coupon code?',
        ]
        for probe in probes:
            reply = chat(self.client, probe)['reply']
            self.assertNotIn('|', reply, f'table pipes leaked for: {probe}')
            self.assertNotIn('<br>', reply.lower(), f'html leaked for: {probe}')
            self.assertIn('✦', reply, f'bullets missing for: {probe}')

class HeadroomCompressionTests(RegressionTestCase):
    """Headroom (headroomlabs-ai/headroom) compresses chat history before Gemini.

    A stub headroom module is injected so these tests run whether or not the
    optional ``headroom-ai`` package is installed.
    """

    def setUp(self):
        super().setUp()
        GEMINI_KEY_FILE.write_text('test-gemini-key-0001\n')
        self.addCleanup(GEMINI_KEY_FILE.unlink, missing_ok=True)
        ChatMessage.objects.create(
            session_id='hr-01', message='a very long earlier question about everything',
            response='a very long earlier answer with lots of detail ' * 10)

    def _capture_post(self):
        captured = []

        def capture_post(url, json=None, timeout=None):
            captured.append(json)
            fake = mock.MagicMock()
            fake.status_code = 200
            fake.json.return_value = {'candidates': [{'content': {'parts': [{'text': 'ok'}]}}]}
            return fake

        return mock.patch('requests.post', side_effect=capture_post), captured

    def _stub_headroom(self, compress_fn):
        import sys, types
        fake_mod = types.ModuleType('headroom')
        fake_mod.compress = compress_fn
        return mock.patch.dict(sys.modules, {'headroom': fake_mod})

    def test_tc_cht_026_compressed_history_reaches_gemini(self):
        """TC-CHT-026: Headroom output (smaller history) is what Gemini receives."""
        from types import SimpleNamespace

        def fake_compress(messages, model=None, **kw):
            self.assertEqual(messages[0]['role'], 'user')
            self.assertEqual(messages[1]['role'], 'assistant')
            return SimpleNamespace(messages=[
                {'role': 'user', 'content': 'earlier Q (compressed)'},
                {'role': 'assistant', 'content': 'earlier A (compressed)'},
            ])

        patcher, captured = self._capture_post()
        with self._stub_headroom(fake_compress), patcher:
            chat(self.client, 'follow-up question', session_id='hr-01')
        contents = captured[-1]['contents']
        self.assertEqual(contents[0]['parts'][0]['text'], 'earlier Q (compressed)')
        self.assertEqual(contents[1]['role'], 'model')
        self.assertEqual(contents[1]['parts'][0]['text'], 'earlier A (compressed)')
        self.assertEqual(contents[-1]['parts'][0]['text'], 'follow-up question')

    def test_tc_cht_027_headroom_failure_degrades_to_raw_history(self):
        """TC-CHT-027: if Headroom blows up, raw history is used — never a crash."""
        def broken_compress(messages, model=None, **kw):
            raise RuntimeError('compressor exploded')

        patcher, captured = self._capture_post()
        with self._stub_headroom(broken_compress), patcher:
            data = chat(self.client, 'still chatting', session_id='hr-01')
        self.assertEqual(data['reply'], 'ok')
        contents = captured[-1]['contents']
        self.assertEqual(contents[0]['parts'][0]['text'],
                         'a very long earlier question about everything')
