import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from features.review_ops.review_service import (
    create_customer_review,
    handle_admin_review_action
)

@require_POST
def submit_review(request):
    """Orchestrator endpoint for public review submissions"""
    try:
        data = json.loads(request.body)
        result = create_customer_review(data)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})

@login_required
def admin_review_manage(request):
    """Orchestrator endpoint for admin review moderation"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except Exception:
            data = {}
        result = handle_admin_review_action(data)
        return JsonResponse(result)

    result = handle_admin_review_action({})
    return JsonResponse(result)
