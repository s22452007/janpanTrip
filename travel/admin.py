from django.contrib import admin
from .models import UserProfile, Region, AttractionType, Attraction, Trip, Itinerary, FavoriteAttraction

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'email', 'phone', 'permission', '使用者編號']
    list_filter = ['permission']
    search_fields = ['user__username', 'user__email', 'email', 'phone', '使用者編號']
    readonly_fields = ['使用者編號']  # 設為只讀，因為會自動生成

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(AttractionType)
class AttractionTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    search_fields = ['name']

@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'attraction_type']  # 移除 rating
    list_filter = ['region', 'attraction_type']  # 移除 rating
    search_fields = ['name', 'address']
    fieldsets = (
        ('基本資訊', {
            'fields': ('name', 'description', 'address')
        }),
        ('分類', {
            'fields': ('region', 'attraction_type')
        }),
        ('詳細資訊', {
            'fields': ('features', 'opening_hours', 'phone', 'website', 'image')
        }),
    )

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['trip_name', 'user', 'start_date', 'end_date']  # 更新欄位名
    list_filter = ['start_date', 'user']  # 更新欄位名
    search_fields = ['trip_name', 'user__username']
    
    fieldsets = (
        ('基本資訊', {
            'fields': ('user', 'trip_name', 'description')
        }),
        ('時間設定', {
            'fields': ('start_date', 'end_date')  # 更新欄位名
        }),
    )

@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ['trip', 'attraction', 'date', 'visit_time', 'duration_minutes']
    list_filter = ['date', 'trip__user']
    search_fields = ['trip__trip_name', 'attraction__name']
    
    fieldsets = (
        ('行程資訊', {
            'fields': ('trip', 'date')
        }),
        ('景點資訊', {
            'fields': ('attraction', 'visit_time', 'duration_minutes')
        }),
    )

@admin.register(FavoriteAttraction)
class FavoriteAttractionAdmin(admin.ModelAdmin):
    list_display = ['user', 'attraction']
    list_filter = ['attraction__region', 'attraction__attraction_type']
    search_fields = ['user__username', 'attraction__name']