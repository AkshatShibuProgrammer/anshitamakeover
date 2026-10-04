"""
Anshita Makeover — custom middleware.

``CORSMiddleware``
    Dev/preview convenience layer: the e2b live preview embeds the site in an
    iframe on a different origin, so the development profile opts into
    ``Access-Control-Allow-Origin: *`` and ``X-Frame-Options: ALLOWALL``.
    **Production must never inherit those values** — the audit (Section 7)
    flagged that an unconditional ``ALLOWALL`` silently defeated
    ``X_FRAME_OPTIONS = 'DENY'`` in ``settings_production.py``.

``ContentSecurityPolicyMiddleware``
    Emits the strict CSP from the audit's Section 7.2 baseline, plus the
    standard hardening headers (nosniff / referrer / permissions). Enabled via
    ``CSP_ENABLED`` (on by default whenever ``DEBUG`` is False).
"""

from __future__ import annotations

from django.conf import settings

# ── Defaults mirror settings_production.py / audit §7.2 ────────────────────
DEFAULT_CSP = {
    'default-src': ("'self'",),
    'script-src': ("'self'", 'https://cdnjs.cloudflare.com', 'https://cdn.jsdelivr.net'),
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


class EnsureCsrfCookieMiddleware:
    """Mint the ``csrftoken`` cookie on public HTML pages.

    The concierge / cart widgets POST JSON with an ``X-CSRFToken`` header
    (audit §7.1), but public pages never rendered ``{% csrf_token %}`` — so
    without this middleware the cookie would be missing and every chat POST
    would be rejected with 403. Ordering note: it must sit *before*
    ``CsrfViewMiddleware`` so the request flag is set while the response is
    still being assembled.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in ('GET', 'HEAD'):
            path = request.path_info or '/'
            static_url = getattr(settings, 'STATIC_URL', '/static/') or '/static/'
            media_url = getattr(settings, 'MEDIA_URL', '/media/') or '/media/'
            if not (path.startswith(static_url) or path.startswith(media_url)):
                from django.middleware.csrf import get_token
                get_token(request)
        return self.get_response(request)


def _csp_value(directives) -> str:
    parts = []
    for directive, sources in directives.items():
        if sources:
            parts.append(f"{directive} {' '.join(sources)}")
        else:
            parts.append(directive)
    return '; '.join(parts)


class CORSMiddleware:
    """Dev-friendly CORS/iframe headers; strict in production."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        allow_all = getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', settings.DEBUG)

        if allow_all:
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken, Accept'
        else:
            origin = request.META.get('HTTP_ORIGIN')
            allowed = list(getattr(settings, 'CORS_ALLOWED_ORIGINS', []) or [])
            if origin and origin in allowed:
                response['Access-Control-Allow-Origin'] = origin
                response['Vary'] = 'Origin'
                response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
                response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken, Accept'

        # The preview iframe needs ALLOWALL; production keeps DENY from settings.
        if allow_all:
            response['X-Frame-Options'] = 'ALLOWALL'
        else:
            response['X-Frame-Options'] = getattr(settings, 'X_FRAME_OPTIONS', 'DENY')
        return response


class ContentSecurityPolicyMiddleware:
    """Adds CSP + hardening headers when ``CSP_ENABLED`` is truthy."""

    def __init__(self, get_response):
        self.get_response = get_response

    def _enabled(self):
        return bool(getattr(settings, 'CSP_ENABLED', not settings.DEBUG))

    def __call__(self, request):
        response = self.get_response(request)
        if not self._enabled():
            return response

        directives = getattr(settings, 'CSP_DIRECTIVES', None) or DEFAULT_CSP
        policy = _csp_value(directives)
        report_only = bool(getattr(settings, 'CSP_REPORT_ONLY', False))
        header = 'Content-Security-Policy-Report-Only' if report_only else 'Content-Security-Policy'
        # Never clobber a policy a view/proxy already set.
        if header not in response:
            response[header] = policy

        response.setdefault('X-Content-Type-Options', 'nosniff')
        response.setdefault('Referrer-Policy',
                            getattr(settings, 'SECURE_REFERRER_POLICY',
                                    'strict-origin-when-cross-origin'))
        response.setdefault('Permissions-Policy',
                            'camera=(), microphone=(self), geolocation=(), payment=()')
        response.setdefault('Cross-Origin-Opener-Policy',
                            getattr(settings, 'SECURE_CROSS_ORIGIN_OPENER_POLICY', 'same-origin') or
                            'same-origin')
        return response
