from django.shortcuts import render, redirect
from django.http import JsonResponse
from features.auth_ops.auth_service import (
    authenticate_admin_user,
    logout_admin_user,
    compile_admin_portal_data
)

def admin_login(request):
    """Orchestrator endpoint delegating authentication to auth_ops service"""
    is_ajax = (
        request.headers.get('x-requested-with') == 'XMLHttpRequest' or
        request.headers.get('accept', '').startswith('application/json') or
        request.POST.get('ajax') == '1'
    )
    if request.user.is_authenticated and request.user.is_staff:
        if is_ajax:
            return JsonResponse({'ok': True, 'redirect': '/admin-portal/'})
        return redirect(request.GET.get('next', '/admin-portal/'))

    error = ''
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        result = authenticate_admin_user(request, username, password)
        if result.get('success'):
            next_url = request.GET.get('next') or '/admin-portal/'
            if is_ajax:
                return JsonResponse({'ok': True, 'redirect': next_url})
            return redirect(next_url)
        else:
            error = result.get('error')
            if is_ajax:
                return JsonResponse({'ok': False, 'error': error}, status=401)
    return render(request, 'core/admin_login.html', {'error': error})

def admin_logout_view(request):
    """Orchestrator endpoint delegating session termination to auth_ops service"""
    logout_admin_user(request)
    return redirect('/')

def admin_portal(request):
    """Orchestrator endpoint delegating dashboard data compilation to auth_ops service"""
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/admin-login/?next=/admin-portal/')
    context = compile_admin_portal_data(request.user)
    return render(request, 'core/admin_portal.html', context)
