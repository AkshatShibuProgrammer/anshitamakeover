from django.contrib import admin
from .models import *

admin.site.site_header = "Anshita Makeover Admin"
admin.site.site_title = "Anshita Admin"
admin.site.index_title = "Welcome to Anshita Makeover Portal"

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['whatsapp_number', 'coupon_active', 'coupon_code', 'coupon_discount_percent']
    fieldsets = [
        ('Contact', {'fields': ['whatsapp_number', 'instagram_url']}),
        ('Coupon Settings', {'fields': ['coupon_active', 'coupon_auto_by_date', 'coupon_code', 'coupon_discount_percent', 'coupon_label']}),
    ]


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialities', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    prepopulated_fields = {'slug': ('name',)}


class CourseModuleInline(admin.TabularInline):
    model = CourseModule
    extra = 1


@admin.register(AcademyCourse)
class AcademyCourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'duration_label', 'course_fee', 'total_payable', 'is_active', 'is_featured']
    list_editable = ['course_fee', 'is_active', 'is_featured']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [CourseModuleInline]


@admin.register(MakeupPackage)
class MakeupPackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'package_type', 'price', 'is_featured', 'is_active', 'order']
    list_editable = ['price', 'is_featured', 'is_active', 'order']


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['caption', 'category', 'artist', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    list_filter = ['category', 'artist']


@admin.register(ServicePrice)
class ServicePriceAdmin(admin.ModelAdmin):
    list_display = ['service', 'price', 'price_label', 'is_on_request', 'is_active']
    list_editable = ['price', 'is_on_request', 'is_active']


@admin.register(EventPackage)
class EventPackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'package_type', 'display_price', 'is_featured', 'is_active', 'order']
    list_editable = ['is_featured', 'is_active', 'order']

    fieldsets = [
        ('Basic Info', {'fields': ['name', 'package_type', 'description', 'is_active', 'is_featured', 'order']}),
        ('Pricing', {'fields': ['price', 'price_label']}),
        ('Features', {'fields': ['features'], 'description': 'Enter one feature per line'}),
    ]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'created_at']
    readonly_fields = ['session_id', 'message', 'response', 'created_at']


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'email']
