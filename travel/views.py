from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Attraction, Trip, UserProfile, Region, AttractionType
import json

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'歡迎回來，{user.username}！')
            return redirect('travel:home')
        else:
            messages.error(request, '用戶名或密碼錯誤')
    
    return render(request, 'registration/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        # 基本驗證
        if password1 != password2:
            messages.error(request, '密碼不匹配')
            return render(request, 'registration/register.html')
        
        if len(password1) < 8:
            messages.error(request, '密碼長度至少需要8個字符')
            return render(request, 'registration/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, '用戶名已存在')
            return render(request, 'registration/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, '電子郵件已被使用')
            return render(request, 'registration/register.html')
        
        # 創建用戶
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            
            # 創建用戶資料
            UserProfile.objects.create(user=user)
            
            messages.success(request, f'帳號 {username} 已成功創建！')
            login(request, user)
            return redirect('travel:home')
        except Exception as e:
            messages.error(request, f'註冊失敗：{str(e)}')
    
    return render(request, 'registration/register.html')

def logout_view(request):
    logout(request)
    messages.info(request, '您已成功登出')
    return redirect('travel:login')

@login_required
def home_view(request):
    # 獲取景點資料
    attractions = Attraction.objects.all()[:8]  # 顯示前8個景點
    user_trips = Trip.objects.filter(user=request.user)[:3]  # 顯示前3個行程
    
    context = {
        'attractions': attractions,
        'user_trips': user_trips,
    }
    return render(request, 'travel/home.html', context)

@login_required
def profile_view(request):
    if request.method == 'POST':
        # 處理個人資料更新
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        # 處理用戶偏好設置
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.phone = request.POST.get('phone', '')
        profile.travel_type = request.POST.get('travel_type', '')
        profile.budget_range = request.POST.get('budget_range', '')
        
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        
        profile.save()
        messages.success(request, '個人資料已更新')
        
    return render(request, 'travel/profile.html')

@login_required
def add_to_plan_view(request, attraction_id):
    if request.method == 'POST':
        try:
            attraction = get_object_or_404(Attraction, id=attraction_id)
            
            # 檢查用戶是否有進行中的行程，如果沒有就創建一個
            current_trip, created = Trip.objects.get_or_create(
                user=request.user,
                title="我的日本行程",
                defaults={
                    'description': '自動創建的行程',
                    'start_date': '2024-12-01',
                    'end_date': '2024-12-07',
                }
            )
            
            # 檢查景點是否已經在行程中
            if current_trip.attractions.filter(id=attraction_id).exists():
                return JsonResponse({'success': False, 'message': '景點已在行程中'})
            
            # 添加景點到行程
            current_trip.attractions.add(attraction)
            
            return JsonResponse({'success': True, 'message': '景點已加入行程'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '無效的請求'})

def search_attractions_view(request):
    search_query = request.GET.get('search', '')
    region = request.GET.get('region', '')
    attraction_type = request.GET.get('type', '')
    rating = request.GET.get('rating', '')
    
    # 建立查詢
    attractions = Attraction.objects.all()
    
    if search_query:
        attractions = attractions.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    if region and region != '地區 ▼':
        attractions = attractions.filter(region__name=region)
    
    if attraction_type and attraction_type != '類型 ▼':
        attractions = attractions.filter(attraction_type__name=attraction_type)
    
    if rating and rating != '評分 ▼':
        if rating == '5星':
            attractions = attractions.filter(rating=5)
        elif rating == '4星以上':
            attractions = attractions.filter(rating__gte=4)
        elif rating == '3星以上':
            attractions = attractions.filter(rating__gte=3)
    
    attractions_data = [
        {
            'id': attr.id,
            'name': attr.name,
            'location': f"{attr.region.name}・{attr.address}",
            'rating': float(attr.rating),
            'rating_stars': attr.rating_stars,
            'image': attr.image.url if attr.image else '/static/images/default-attraction.jpg'
        }
        for attr in attractions[:20]  # 限制返回20個結果
    ]
    
    return JsonResponse({'success': True, 'attractions': attractions_data})

@login_required
def get_user_trips_view(request):
    trips = Trip.objects.filter(user=request.user)
    trips_data = [
        {
            'id': trip.id,
            'title': trip.title,
            'start_date': trip.start_date.strftime('%Y-%m-%d'),
            'end_date': trip.end_date.strftime('%Y-%m-%d'),
            'attraction_count': trip.attractions.count(),
        }
        for trip in trips
    ]
    
    return JsonResponse({'success': True, 'trips': trips_data})

@login_required
def my_trips_view(request):
    trips = Trip.objects.filter(user=request.user)
    return render(request, 'travel/my_trips.html', {'trips': trips})

@login_required
def settings_view(request):
    return render(request, 'travel/settings.html')

@login_required
def edit_trip_view(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    # 這裡可以添加編輯行程的邏輯
    return render(request, 'travel/edit_trip.html', {'trip': trip})

@login_required
def delete_trip_view(request, trip_id):
    if request.method == 'DELETE':
        try:
            trip = get_object_or_404(Trip, id=trip_id, user=request.user)
            trip.delete()
            return JsonResponse({'success': True, 'message': '行程已刪除'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '無效的請求'})