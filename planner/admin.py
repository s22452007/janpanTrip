from django.contrib import admin
from .models import UserProfile, TravelPlan, Location, Schedule

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'email')
    search_fields = ('name', 'phone', 'email')

@admin.register(TravelPlan)
class TravelPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'start_date', 'end_date', 'user')
    list_filter = ('start_date', 'end_date')
    search_fields = ('name',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'area', 'type', 'rate', 'clickRate')  
    list_filter = ('area', 'type')
    search_fields = ('name', 'address', 'area')

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'travel_plan', 'date', 'location', 'start_time', 'end_time')
    list_filter = ('date',)
    search_fields = ('travel_plan__name', 'location__address')
