from django.contrib import admin
from .models import UserProfile, Region, AttractionType, Attraction, Trip, Itinerary, ItineraryAttraction, FavoriteAttraction

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'email', 'phone', 'permission']
    list_filter = ['permission']
    search_fields = ['user__username', 'user__email', 'email', 'phone']

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
    list_display = ['name', 'region', 'attraction_type', 'rating']
    list_filter = ['region', 'attraction_type', 'rating']
    search_fields = ['name', 'address']

# ItineraryAttraction 的內聯管理
class ItineraryAttractionInline(admin.TabularInline):
    model = ItineraryAttraction
    extra = 1
    fields = ['attraction', 'notes']

@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ['itinerary_name', 'trip', 'date', 'start_time', 'end_time']
    list_filter = ['date', 'trip__user']
    search_fields = ['itinerary_name', 'trip__trip_name']
    inlines = [ItineraryAttractionInline]

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['trip_name', 'user', 'start_time', 'end_time']
    list_filter = ['start_time', 'user']
    search_fields = ['trip_name', 'user__username']
    
    fieldsets = (
        ('基本資訊', {
            'fields': ('user', 'trip_name', 'description')
        }),
        ('時間設定', {
            'fields': ('start_time', 'end_time')
        }),
    )

@admin.register(ItineraryAttraction)
class ItineraryAttractionAdmin(admin.ModelAdmin):
    list_display = ['itinerary', 'attraction', 'notes']
    list_filter = ['itinerary__trip__user', 'attraction__region']
    search_fields = ['itinerary__itinerary_name', 'attraction__name']

@admin.register(FavoriteAttraction)
class FavoriteAttractionAdmin(admin.ModelAdmin):
    list_display = ['user', 'attraction']
    list_filter = ['attraction__region', 'attraction__attraction_type']
    search_fields = ['user__username', 'attraction__name']