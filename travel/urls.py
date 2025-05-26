from django.urls import path
from . import views

app_name = 'travel'

urlpatterns = [
    # 認證相關
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # 主要頁面
    path('', views.home_view, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('my-trips/', views.my_trips_view, name='my_trips'),
    path('settings/', views.settings_view, name='settings'),
    
    # API 端點
    path('add-to-plan/<int:attraction_id>/', views.add_to_plan_view, name='add_to_plan'),
    path('search-attractions/', views.search_attractions_view, name='search_attractions'),
    path('get-user-trips/', views.get_user_trips_view, name='get_user_trips'),
    path('trip/edit/<int:trip_id>/', views.edit_trip_view, name='edit_trip'),
    path('trip/delete/<int:trip_id>/', views.delete_trip_view, name='delete_trip'),
]