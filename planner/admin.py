from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, TravelPlan, Location, Schedule

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('id', 'username', 'email', 'phone')
    search_fields = ('username', 'email', 'phone')
    
    fieldsets = (
        (None, {'fields': ('username', 'password', 'email', 'phone')}),
        ('權限', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

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
