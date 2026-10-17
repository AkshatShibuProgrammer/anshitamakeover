"""
Anshita Makeover — dependency-free rate limiting (denial-of-wallet protection).

Section 7 of ``docs/COMPREHENSIVE_3D_MASCOT_ANIMATION_AND_SECURITY_AUDIT.md``
requires that the public 24/7 AI Concierge endpoint (and the other anonymous
POST endpoints that touch the database) are throttled so automated scripts
cannot drain the LLM token budget or flood the enquiry table.

The implementation is intentionally small, auditable and dependency free
(``django-ratelimit`` is not a project requirement, so the production image
never has to grow for this). It uses Django's cache framework, which is a
process-local LocMemCache in this project — good enough for the single
Gunicorn worker deployment, and swappable for Redis/Memcached without code
changes by overriding ``CACHES`` in production.

Public API
----------
``@rate_limit(key='ip', rate='15/m', block=True)`` — decorator for views.
``is_rate_limited(request, scope, rate)`` — low-level helper returning
``(limited, retry_after_seconds)``.
"""

from __future__ import annotations

import hashlib
import re
import time
from functools import wraps

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse

__all__ = ['rate_limit', 'is_rate_limited', 'client_ip', 'parse_rate', 'RateLimitExceeded']

# e.g. '15/m', '30/h', '5/s', '100/d', '10/2m'
_RATE_RE = re.compile(r'^\s*(\d+)\s*/\s*(\d*)\s*([smhd])\s*$', re.I)
_UNIT_SECONDS = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}

# Never let a single attacker blow up the cache key space.
_MAX_KEY_LEN = 200


class RateLimitExceeded(Exception):
    """Raised internally when ``block`` semantics are requested as an exception."""

    def __init__(self, retry_after, limit, window):
        super().__init__(f'Rate limit exceeded ({limit}/{window}s)')
        self.retry_after = retry_after


def parse_rate(rate: str):
    """Return ``(limit, window_seconds)`` for a rate string like ``'15/m'``."""
    match = _RATE_RE.match(str(rate or ''))
    if not match:
        raise ValueError(f'Invalid rate string: {rate!r} (expected e.g. "15/m")')
    limit = int(match.group(1))
    multiplier = int(match.group(2) or 1)
    window = multiplier * _UNIT_SECONDS[match.group(3).lower()]
    if limit <= 0:
        raise ValueError(f'Invalid rate limit: {rate!r}')
    return limit, window


def client_ip(request) -> str:
    """Best-effort client IP, honouring the reverse proxy when trusted.

    ``settings.USE_X_FORWARDED_FOR`` (off by default) must only be enabled
    behind a proxy that overwrites ``X-Forwarded-For`` — otherwise a client
    could spoof the header to dodge the throttle.
    """
    if getattr(settings, 'USE_X_FORWARDED_FOR', False):
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if forwarded:
            return forwarded.split(',')[0].strip()
    return (request.META.get('REMOTE_ADDR') or '0.0.0.0').strip() or '0.0.0.0'


def _cache_key(scope: str, identifier: str) -> str:
    digest = hashlib.sha256(f'{identifier}'.encode('utf-8')).hexdigest()[:24]
    scope = re.sub(r'[^A-Za-z0-9_.:-]', '', str(scope))[:_MAX_KEY_LEN]
    return f'rl:{scope}:{digest}'


def is_rate_limited(request, scope: str, rate: str, identifier: str | None = None):
    """Fixed-window counter in the Django cache.

    Returns ``(limited: bool, retry_after: int, limit: int, window: int)``.
    """
    limit, window = parse_rate(rate)
    if not getattr(settings, 'RATELIMIT_ENABLE', True):
        return False, 0, limit, window

    ident = identifier if identifier is not None else client_ip(request)
    cache_key = _cache_key(scope, ident)
    now = time.time()
    state = cache.get(cache_key)
    if not state or state[0] <= now:
        state = (now + window, 1)
        cache.set(cache_key, state, timeout=window)
        return False, 0, limit, window

    resets_at, count = state
    if count >= limit:
        retry_after = max(1, int(resets_at - now) + 1)
        return True, retry_after, limit, window

    # Increment without extending the window (fixed-window semantics).
    remaining = max(0.0, resets_at - now)
    cache.set(cache_key, (resets_at, count + 1), timeout=max(1, int(remaining) + 1))
    return False, 0, limit, window


def _too_many_requests_response(request, retry_after, limit, window):
    """429 in the caller's native shape (JSON for APIs, HTML for pages)."""
    message = ('Too many requests — please slow down and try again shortly. '
               'अत्यधिक अनुरोध — कृपया थोड़ी देर बाद प्रयास करें।')
    wants_json = (
        request.path.startswith('/api/')
        or 'application/json' in request.META.get('HTTP_ACCEPT', '')
        or request.META.get('CONTENT_TYPE', '').startswith('application/json')
        or request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    )
    if wants_json:
        response = JsonResponse({'ok': False, 'error': message, 'retry_after': retry_after},
                                status=429)
    else:
        from django.http import HttpResponse
        response = HttpResponse(message, status=429, content_type='text/plain; charset=utf-8')
    response['Retry-After'] = str(retry_after)
    response['X-RateLimit-Limit'] = str(limit)
    response['X-RateLimit-Window'] = f'{window}s'
    return response


def rate_limit(key: str = 'ip', rate: str = '15/m', block: bool = True,
               scope: str | None = None, methods=('POST', 'PUT', 'PATCH', 'DELETE')):
    """Throttle a view.

    ``key``    — ``'ip'`` (default) or ``'session'``.
    ``rate``   — e.g. ``'15/m'``, ``'120/h'``.
    ``block``  — when True (default) an over-limit caller receives HTTP 429.
                 When False the request is still allowed, but the view can read
                 ``request.rate_limited`` / ``request.rate_limit_retry_after``.
    ``scope``  — cache namespace; defaults to the module + function name so two
                 endpoints never share a bucket.
    """
    comparable_methods = tuple(m.upper() for m in (methods or ()))

    def decorator(view_func):
        resolved_scope = scope or f'{view_func.__module__}.{view_func.__name__}'

        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if comparable_methods and request.method.upper() not in comparable_methods:
                return view_func(request, *args, **kwargs)

            if key == 'session':
                if not request.session.session_key:
                    request.session.save()
                identifier = request.session.session_key
            else:
                identifier = client_ip(request)

            limited, retry_after, limit, window = is_rate_limited(
                request, resolved_scope, rate, identifier=identifier)

            request.rate_limited = limited
            request.rate_limit_retry_after = retry_after
            request.rate_limit_info = {'limit': limit, 'window': window, 'rate': rate}

            if limited and block:
                return _too_many_requests_response(request, retry_after, limit, window)
            return view_func(request, *args, **kwargs)

        _wrapped.rate_limit = {'key': key, 'rate': rate, 'scope': resolved_scope}
        return _wrapped

    return decorator
