import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from .common import admin_required
from ..ratelimit import rate_limit
from features.review_ops.review_service import (
    create_customer_review,
    handle_admin_review_action
)

import logging

logger = logging.getLogger(__name__)


# ── API: public review submission ──────────────────────────────────────
# Security posture (audit §7.1), mirroring the chatbot contract:
#   * CSRF protected  — browsers must send X-CSRFToken (the review modal does).
#   * Rate limited    — 10 submissions/minute/IP stops review-table spam.
#   * Sanitised       — the service layer strips markup from every field.
#   * No error leakage — failures return a generic message, details are logged.
# The JSON envelope stays stable (HTTP 200 + {ok: false, error}) because the
# public review modal branches on `data.ok`; only genuine server faults use 5xx.
@csrf_protect
@require_POST
@rate_limit(key='ip', rate='10/m', block=True, scope='submit_review')
def submit_review(request):
    """Orchestrator endpoint for public review submissions."""
    try:
        data = json.loads(request.body or b'{}')
    except (ValueError, TypeError):
        return JsonResponse({'ok': False, 'error': 'Invalid request payload.'})

    if not isinstance(data, dict):
        return JsonResponse({'ok': False, 'error': 'Invalid request payload.'})

    try:
        result = create_customer_review(data)
    except Exception:
        # Never reflect internals (stack traces, DB errors) to a public client.
        logger.exception('submit_review failed')
        return JsonResponse(
            {'ok': False, 'error': 'We could not save your review right now. Please try again.'},
            status=500,
        )

    return JsonResponse(result)


@admin_required
def admin_review_manage(request):
    """Orchestrator endpoint for admin review moderation."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except Exception:
            data = {}
        if not isinstance(data, dict):
            data = {}
        result = handle_admin_review_action(data)
        return JsonResponse(result)

    result = handle_admin_review_action({})
    return JsonResponse(result)
