"""
Anshita Makeover — server-side output sanitisation & security utilities.

Companion module to ``core.ratelimit``. Section 7 of the security audit
requires that no dynamic content reaches the browser unsanitised:

* stored/reflected XSS — AI concierge replies, review text and enquiry notes
  are all attacker-influenced strings;
* defence in depth — even though the browser renderer escapes text, the
  payload that lands in the database (and therefore in the admin portal, in
  e-mails, and in any future API consumer) must already be inert.

The sanitiser below is deliberately allow-list free: for chatbot copy we strip
*all* markup and keep the plain text. Luxury concierge replies are plain text
(``\\n`` separated); the front-end re-introduces formatting from escaped text.
"""

from __future__ import annotations

import html
import re
import unicodedata

__all__ = [
    'strip_html', 'sanitize_text', 'sanitize_bot_reply', 'escape_html',
    'looks_like_xss', 'MAX_CHAT_MESSAGE_CHARS', 'MAX_BOT_REPLY_CHARS',
]

MAX_CHAT_MESSAGE_CHARS = 1200
MAX_BOT_REPLY_CHARS = 4000

# Anything that could open/close a tag, an HTML comment, or a CDATA block.
_TAG_RE = re.compile(r'<\s*/?\s*[a-zA-Z!][^<>]*>?', re.S)
_COMMENT_RE = re.compile(r'<!--.*?-->', re.S)
_CDATA_RE = re.compile(r'<!\[CDATA\[.*?\]\]>', re.S)
_DOCTYPE_RE = re.compile(r'<!DOCTYPE[^>]*>', re.I)

# Inline event handlers and script-ish URL schemes that survive tag stripping
# when text is later re-rendered by a naive markdown renderer.
_EVENT_ATTR_RE = re.compile(r'\bon[a-z]{3,}\s*=\s*("[^"]*"|\'[^\']*\'|[^\s>]+)', re.I)
_DANGEROUS_SCHEME_RE = re.compile(r'(?:javascript|vbscript|data)\s*:', re.I)
_NULL_AND_CONTROL_RE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')
_ZERO_WIDTH_RE = re.compile(r'[\u200b-\u200f\u202a-\u202e\u2060\ufeff]')


def looks_like_xss(value: str) -> bool:
    """Heuristic used by tests/telemetry to flag hostile payloads."""
    if not value:
        return False
    sample = str(value)
    return bool(
        _TAG_RE.search(sample)
        or _EVENT_ATTR_RE.search(sample)
        or _DANGEROUS_SCHEME_RE.search(sample)
    )


def strip_html(value: str) -> str:
    """Remove every tag/comment/doctype from ``value`` (never raises)."""
    if value is None:
        return ''
    text = str(value)
    text = _COMMENT_RE.sub(' ', text)
    text = _CDATA_RE.sub(' ', text)
    text = _DOCTYPE_RE.sub(' ', text)
    text = _TAG_RE.sub(' ', text)
    text = _EVENT_ATTR_RE.sub(' ', text)
    text = _DANGEROUS_SCHEME_RE.sub(' ', text)
    # Decode then re-strip: catches double-encoded payloads such as
    # ``&lt;script&gt;`` which a markdown renderer might decode and re-inject.
    decoded = html.unescape(text)
    if decoded != text:
        decoded = _TAG_RE.sub(' ', decoded)
        decoded = _EVENT_ATTR_RE.sub(' ', decoded)
        decoded = _DANGEROUS_SCHEME_RE.sub(' ', decoded)
        text = decoded
    return text


def sanitize_text(value: str, max_length: int = 0, *, keep_newlines: bool = True) -> str:
    """Strip markup + control characters and normalise whitespace.

    Unicode is NFC-normalised so homoglyph/zero-width tricks cannot be used to
    smuggle payloads past downstream filters.
    """
    if value is None:
        return ''
    text = strip_html(value)
    text = _NULL_AND_CONTROL_RE.sub('', text)
    text = _ZERO_WIDTH_RE.sub('', text)
    text = unicodedata.normalize('NFC', text)
    if keep_newlines:
        text = re.sub(r'[ \t\f\v]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
    else:
        text = re.sub(r'\s+', ' ', text)
    text = text.replace('<', '').replace('>', '').strip()
    if max_length and len(text) > max_length:
        text = text[:max_length].rstrip()
    return text


def sanitize_bot_reply(value: str, max_length: int = MAX_BOT_REPLY_CHARS) -> str:
    """Sanitiser applied to every AI concierge reply before it is stored or
    returned to the browser (Gemini output is *untrusted input*)."""
    text = sanitize_text(value, max_length=max_length, keep_newlines=True)
    # A reply that has been reduced to a stub (pure markup payload) still gets
    # a safe, useful answer rather than an empty bubble.
    if not text:
        return 'Namaste from Anshita Makeover ✨ How may I help you today?'
    return text


def escape_html(value: str) -> str:
    """Convenience wrapper used by templates/tests."""
    return html.escape('' if value is None else str(value), quote=True)
