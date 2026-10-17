"""
Production settings for Anshita Makeover on Oracle Cloud / Production Infrastructure.
Extends base settings with strict HTTPS, HSTS, secure cookies, CSP, and
environment-driven secrets (audit §7.2).

Boot contract
-------------
Required environment variables:
    DJANGO_SECRET_KEY   — 50+ random characters. The process refuses to start
                          without it (no committed fallback; audit §7.1 CRITICAL).
Optional:
    DJANGO_DEBUG=0                  (default)
    ALLOWED_HOSTS=host1,host2
    SECURE_SSL_REDIRECT=1
    SECURE_HSTS_SECONDS=31536000
    USE_X_FORWARDED_FOR=1           (only behind a trusted reverse proxy)
    CSP_REPORT_ONLY=1               (default; set 0 to enforce the CSP)
    WHATSAPP_NUMBER=91XXXXXXXXXX
"""
import os

from django.core.exceptions import ImproperlyConfigured

from .settings import *  # noqa: F401,F403  (base configuration)

DEBUG = False


def _env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


# ── Secret key: fail fast, never fall back to a committed value ────────────
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '').strip()
if not SECRET_KEY:
    raise ImproperlyConfigured(
        'DJANGO_SECRET_KEY is required in production. Generate one with:\n'
        "    python -c \"import secrets; print(secrets.token_urlsafe(64))\""
    )
if len(SECRET_KEY) < 32:
    raise ImproperlyConfigured('DJANGO_SECRET_KEY is too short for production (need >= 32 chars).')

ALLOWED_HOSTS = [
    'anshitamakeover.com',
    'www.anshitamakeover.com',
    'anshita.in',
    'www.anshita.in',
    'localhost',
    '127.0.0.1',
]

extra_hosts = os.environ.get('ALLOWED_HOSTS', '')
if extra_hosts:
    ALLOWED_HOSTS.extend([h.strip() for h in extra_hosts.split(',') if h.strip()])

# ── HTTPS / HSTS ───────────────────────────────────────────────────────────
SECURE_SSL_REDIRECT = _env_bool('SECURE_SSL_REDIRECT', True)
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', 31536000))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ── Cookie flags ───────────────────────────────────────────────────────────
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = True
# The token is exposed to JS through <meta name="csrf-token"> in base.html,
# so the cookie itself can stay unreadable (strict XSS hardening).
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# ── Clickjacking / sniffing / referrer ─────────────────────────────────────
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
CORS_ALLOW_ALL_ORIGINS = False

# Reverse proxy SSL header (standard for Nginx / Cloudflare)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# Only trust X-Forwarded-For when the proxy overwrites it (rate-limit keying).
USE_X_FORWARDED_FOR = _env_bool('USE_X_FORWARDED_FOR', True)

# ── Content Security Policy ────────────────────────────────────────────────
# Report-Only by default: base.html still uses inline onclick handlers, so a
# blocking rollout needs the inline-event migration first (tracked in
# docs/QUALITY_GATE_VERIFICATION.md). Set CSP_REPORT_ONLY=0 to enforce.
CSP_ENABLED = _env_bool('CSP_ENABLED', True)
CSP_REPORT_ONLY = _env_bool('CSP_REPORT_ONLY', True)
CSP_DIRECTIVES = {
    'default-src': ("'self'",),
    'script-src': ("'self'", "'unsafe-inline'", 'https://cdnjs.cloudflare.com',
                   'https://cdn.jsdelivr.net'),
    'style-src': ("'self'", "'unsafe-inline'", 'https://fonts.googleapis.com'),
    'font-src': ("'self'", 'https://fonts.gstatic.com', 'data:'),
    'img-src': ("'self'", 'data:', 'blob:', 'https://images.unsplash.com',
                'https://res.cloudinary.com', 'https://*.cdninstagram.com',
                'https://*.fbcdn.net', 'https://i.ytimg.com'),
    'media-src': ("'self'", 'blob:', 'https://*.cdninstagram.com', 'https://*.fbcdn.net'),
    'connect-src': ("'self'",),
    'frame-src': ("'self'", 'https://www.instagram.com', 'https://www.youtube.com'),
    'object-src': ("'none'",),
    'base-uri': ("'self'",),
    'form-action': ("'self'", 'https://wa.me', 'https://api.whatsapp.com'),
    'frame-ancestors': ("'none'",),
    'upgrade-insecure-requests': (),
}

# ── Rate limiting / LLM cost guard ─────────────────────────────────────────
RATELIMIT_ENABLE = _env_bool('RATELIMIT_ENABLE', True)

# WhatsApp business contact
WHATSAPP_NUMBER = os.environ.get('WHATSAPP_NUMBER', '917879223442')
