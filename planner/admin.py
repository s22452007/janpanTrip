from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, TravelPlan, Location, Schedule

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('id', 'username', 'email', 'phone')  
    search_fields = ('username', 'email', 'phone')
    
    fieldsets = (
        (None, {'fields': ('username', 'password', 'email', 'phone')}),
        ('權限', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )


@admin.register(TravelPlan)
class TravelPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'travel_name', 'start_date', 'end_date', 'user_ID') 
    list_filter = ('start_date', 'end_date')
    search_fields = ('travel_name',)


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'travel_ID', 'date', 'locations_ID', 'start_time', 'end_time')  
    list_filter = ('date',)
    search_fields = ('travel_ID__travel_name', 'locations_ID__address')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'locations_name', 'address', 'area', 'type', 'rate', 'clickRate')
    list_filter = ('area', 'type')
    search_fields = ('locations_name', 'address', 'area')  
