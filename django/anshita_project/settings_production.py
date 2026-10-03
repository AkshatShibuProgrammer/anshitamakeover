"""
Production settings for Anshita Makeover on Oracle Cloud / Production Infrastructure.
Extends base settings with strict HTTPS, HSTS, secure cookies, and environment-driven secrets.
"""
import os
from .settings import *

DEBUG = False

# Production secret key from environment or fallback to existing
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'anshita-makeover-secret-key-2026-bhopal-mp-prod-hardening-7879223442')

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

# Security & SSL configuration
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True').lower() == 'true'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# HTTP Strict Transport Security (HSTS) - 1 year
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', 31536000))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# X-Frame-Options: Strict DENY for production clickjacking protection
X_FRAME_OPTIONS = 'DENY'

# Reverse proxy SSL header (standard for Nginx / Cloudflare)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# WhatsApp business contact
WHATSAPP_NUMBER = os.environ.get('WHATSAPP_NUMBER', '917879223442')
