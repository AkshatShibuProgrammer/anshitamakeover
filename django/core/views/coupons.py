import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from features.coupon_ops.coupon_service import (
    fetch_active_and_exit_coupons,
    update_or_generate_coupon
)

def get_coupon_api(request):
    """Orchestrator endpoint delegating to coupon_ops service"""
    result = fetch_active_and_exit_coupons()
    return JsonResponse(result)

@login_required
def admin_coupon_update(request):
    """Orchestrator endpoint delegating to coupon_ops service"""
    if request.method == 'POST':
        action = request.POST.get('action') or ''
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                action = data.get('action', action)
            except Exception:
                data = {}
        else:
            data = request.POST
        
        result = update_or_generate_coupon(data, action)
        return JsonResponse(result)
    return JsonResponse({'ok': False})
