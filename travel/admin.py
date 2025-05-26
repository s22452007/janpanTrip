from django.contrib import admin
from .models import UserProfile, Region, AttractionType, Attraction, Trip, TripAttraction, FavoriteTrip

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'travel_type', 'budget_range', 'created_at']
    list_filter = ['travel_type', 'budget_range', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_en']
    search_fields = ['name', 'name_en']

@admin.register(AttractionType)
class AttractionTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    search_fields = ['name']

@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'attraction_type', 'rating', 'created_at']
    list_filter = ['region', 'attraction_type', 'rating', 'created_at']
    search_fields = ['name', 'name_en', 'address']
    readonly_fields = ['created_at', 'updated_at']

# TripAttraction 的內聯管理
class TripAttractionInline(admin.TabularInline):
    model = TripAttraction
    extra = 1
    fields = ['attraction', 'day_number', 'order', 'visit_time', 'notes']

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'start_date', 'end_date', 'is_public', 'created_at']
    list_filter = ['is_public', 'start_date', 'created_at']
    search_fields = ['title', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [TripAttractionInline]  # 使用內聯而不是 filter_horizontal
    
    fieldsets = (
        ('基本資訊', {
            'fields': ('user', 'title', 'description')
        }),
        ('日期設定', {
            'fields': ('start_date', 'end_date')
        }),
        ('其他設定', {
            'fields': ('is_public',)
        }),
        ('系統資訊', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(TripAttraction)
class TripAttractionAdmin(admin.ModelAdmin):
    list_display = ['trip', 'attraction', 'day_number', 'order', 'visit_time']
    list_filter = ['day_number', 'trip__start_date']
    search_fields = ['trip__title', 'attraction__name']
    list_editable = ['day_number', 'order', 'visit_time']

@admin.register(FavoriteTrip)
class FavoriteTripAdmin(admin.ModelAdmin):
    list_display = ['user', 'trip', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'trip__title']