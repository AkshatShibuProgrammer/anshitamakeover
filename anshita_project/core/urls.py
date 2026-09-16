from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('academy/', views.academy, name='academy'),
    path('set-language/', views.set_language, name='set_language'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-portal/', views.admin_portal, name='admin_portal'),
    path('admin-logout/', views.admin_logout_view, name='admin_logout'),
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
    path('api/coupon/', views.get_coupon_api, name='coupon_api'),
    path('api/admin/coupon/', views.admin_coupon_update, name='admin_coupon'),
    path('api/admin/price/', views.admin_price_update, name='admin_price'),
    path('api/admin/event-package/', views.admin_event_package, name='admin_event_package'),
    path('api/admin/artist/', views.admin_artist_manage, name='admin_artist'),
    path('api/admin/service/', views.admin_service_manage, name='admin_service'),
    path('api/review/submit/', views.submit_review, name='submit_review'),
    path('api/admin/review/', views.admin_review_manage, name='admin_review'),
    path('api/admin/media/', views.admin_media_manage, name='admin_media'),
    path('api/admin/studio-service/', views.admin_studio_service_manage, name='admin_studio_service'),
    path('api/admin/lookgroup/', views.admin_lookgroup_manage, name='admin_lookgroup'),
    path('api/admin/lookgroup/media/', views.admin_lookmedia_manage, name='admin_lookmedia'),
    path('sinha-logos/', views.sinha_logo_studio, name='sinha_logo_studio'),
]

