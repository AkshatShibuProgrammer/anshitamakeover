import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from features.artist_ops.artist_service import (
    save_artist_record,
    delete_artist_by_id,
    list_all_artists
)

@login_required
def admin_artist_manage(request):
    """Orchestrator endpoint delegating to artist_ops service"""
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'delete':
            artist_id = request.POST.get('id')
            return JsonResponse(delete_artist_by_id(artist_id))

        result = save_artist_record(request.POST, request.FILES)
        return JsonResponse(result)

    if request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            artist_id = data.get('id')
            return JsonResponse(delete_artist_by_id(artist_id))
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)})

    # GET
    return JsonResponse(list_all_artists())
