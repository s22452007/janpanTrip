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
    path('card/', views.card_view, name='card'),
    
    # 景點相關
    path('attraction/<int:attraction_id>/', views.attraction_detail, name='attraction_detail'),
    
    # 收藏功能 - 新增這些路由
    path('favorites/', views.favorites_view, name='favorites'),
    path('toggle-favorite/<int:attraction_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('add-to-favorites/<int:attraction_id>/', views.add_to_favorites_view, name='add_to_favorites'),
    path('remove-from-favorites/<int:attraction_id>/', views.remove_from_favorites_view, name='remove_from_favorites'),
    #path('get-user-favorites/', views.get_user_favorites_view, name='get_user_favorites'),
    
    # 行程管理 API
    path('add-to-plan/<int:attraction_id>/', views.add_to_plan_view, name='add_to_plan'),
    path('search-attractions/', views.search_attractions_view, name='search_attractions'),
    path('get-user-trips/', views.get_user_trips_view, name='get_user_trips'),
    path('trip/create/', views.create_trip_view, name='create_trip'),
    path('trip/view/<int:trip_id>/', views.view_trip, name='view_trip'),
    path('trip/share/<int:trip_id>/', views.share_trip_view, name='share_trip'),
    path('trip/edit/<int:trip_id>/', views.edit_trip_view, name='edit_trip'),
    path('trip/delete/<int:trip_id>/', views.delete_trip_view, name='delete_trip'),
    path('get-trip-dates/<int:trip_id>/', views.get_trip_dates, name='get_trip_dates'),
    path('add-attraction-to-trip/', views.add_attraction_to_trip, name='add_attraction_to_trip'),
    
    # 公開行程查看（無需登入）
    path('public/trip/<int:trip_id>/', views.public_trip_view, name='public_trip'),
    path('remove-from-trip/<int:attraction_id>/', views.remove_from_trip_view, name='remove_from_trip'),
    
    # 編輯行程相關 API
    path('search-available-attractions/', views.search_available_attractions_view, name='search_available_attractions'),
    path('add-to-itinerary/', views.add_to_itinerary_view, name='add_to_itinerary'),
    path('change-attraction-day/', views.change_attraction_day_view, name='change_attraction_day'),
    path('update-attraction-duration/', views.update_attraction_duration_view, name='update_attraction_duration'),
    
    # 收藏功能相關路由
    path('toggle-favorite/<int:attraction_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('get-favorite-status/', views.get_favorite_status, name='get_favorite_status'),
    path('favorites/', views.favorites_view, name='favorites'),
    
]