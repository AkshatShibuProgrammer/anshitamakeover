from pathlib import Path
import os
import sys

BASE_DIR = Path(__file__).resolve().parent.parent


def _env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def _detect_test_run():
    """True while Django/pytest suites are importing settings.

    Rate limiting uses the cache, and a cache survives between test methods —
    without this switch the 15/min concierge throttle would 429 the regression
    suite itself. Dedicated tests override the setting back on.
    """
    if _env_bool('DJANGO_TESTING', False):
        return True
    argv = ' '.join(sys.argv).lower()
    return 'test' in argv or 'pytest' in argv


TESTING = _detect_test_run()

# ── Secrets & debug (audit §7.1: never commit production secrets) ──────────
# The development fallback is *only* active when DJANGO_DEBUG is on and is
# visibly labelled as insecure; settings_production.py refuses to boot without
# a real DJANGO_SECRET_KEY in the environment.
DEBUG = _env_bool('DJANGO_DEBUG', True)
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY') or (
    'dev-only-insecure-anshita-makeover-secret-key' if DEBUG else '')
if not SECRET_KEY:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured(
        'DJANGO_SECRET_KEY must be set when DJANGO_DEBUG is false.')

ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h.strip()] or (
    ['*'] if DEBUG else ['anshitamakeover.com', 'www.anshitamakeover.com'])

# Preview iframe embedding is a *development* affordance only. Production
# derives X-Frame-Options from settings_production.py (DENY).
X_FRAME_OPTIONS = 'ALLOWALL' if DEBUG else 'DENY'
CORS_ALLOW_ALL_ORIGINS = DEBUG
SECURE_CROSS_ORIGIN_OPENER_POLICY = None if DEBUG else 'same-origin'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
CSRF_TRUSTED_ORIGINS = ['https://*.e2b.app', 'http://localhost:3001', 'http://127.0.0.1:3001']

# ── Rate limiting (LLM denial-of-wallet guard, audit §7.1) ─────────────────
RATELIMIT_ENABLE = _env_bool('RATELIMIT_ENABLE', not TESTING)
USE_X_FORWARDED_FOR = _env_bool('USE_X_FORWARDED_FOR', False)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'anshita-makeover-ratelimit',
        'TIMEOUT': 300,
    }
}

# ── Content Security Policy ────────────────────────────────────────────────
# Off for the dev preview (the e2b iframe + inline preview shims), enforced
# from settings_production.py. See docs/QUALITY_GATE_VERIFICATION.md.
CSP_ENABLED = _env_bool('CSP_ENABLED', False)
CSP_REPORT_ONLY = _env_bool('CSP_REPORT_ONLY', True)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'core.middleware.CORSMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # Must sit above CsrfViewMiddleware so the minted token is picked up by
    # its process_response (public pages POST JSON with X-CSRFToken).
    'core.middleware.EnsureCsrfCookieMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # CSP + hardening headers (enabled via CSP_ENABLED in production).
    'core.middleware.ContentSecurityPolicyMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'anshita_project.urls'

# Login target for @login_required — the studio uses its own branded login
# page, not Django's default /accounts/login/ (which does not exist).
LOGIN_URL = '/admin-login/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'anshita_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

AUTHENTICATION_BACKENDS = [
    'core.backends.CaseInsensitiveEmailOrUsernameBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'core' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# Fixture discovery for the regression suite (testing/testdata/fixtures/)
FIXTURE_DIRS = [BASE_DIR.parent / 'testing' / 'testdata' / 'fixtures']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Gemini API Key file
GEMINI_API_KEY_FILE = BASE_DIR / 'gemini_api_key.txt'

# WhatsApp Number
WHATSAPP_NUMBER = '917879223442'

# Email (for password reset - configure with your email)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# For production, use:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your@gmail.com'
# EMAIL_HOST_PASSWORD = 'your-app-password'
