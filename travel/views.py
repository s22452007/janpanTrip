from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Attraction, Trip, UserProfile, Region, AttractionType, Itinerary, ItineraryAttraction, FavoriteAttraction
from datetime import datetime, date, time
from datetime import timedelta
import json
from django.views.decorators.http import require_http_methods
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
    
    # 獲取用戶行程並計算景點數量
    user_trips = Trip.objects.filter(user=request.user)[:5]  # 顯示前5個行程
    
    # 為每個行程添加景點數量
    for trip in user_trips:
        trip.total_attractions = sum(
            itinerary.attractions.count() 
            for itinerary in trip.itinerary_set.all()
        )
    
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
        profile.email = request.POST.get('email', '')  # 更新 UserProfile 的 email
        
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
                trip_name="我的日本行程",
                defaults={
                    'description': '自動創建的行程',
                    'start_time': datetime(2024, 12, 1, 9, 0),
                    'end_time': datetime(2024, 12, 7, 18, 0),
                }
            )
            
            if created:
                # 如果創建了新行程，也創建對應的每日行程
                trip_date = current_trip.start_time.date()
                itinerary = Itinerary.objects.create(
                    trip=current_trip,
                    itinerary_name=f"{current_trip.trip_name} - 第1天",
                    date=trip_date,
                    start_time=time(9, 0),
                    end_time=time(18, 0)
                )
            else:
                # 使用現有行程的第一個 itinerary，如果沒有就創建
                itinerary = current_trip.itinerary_set.first()
                if not itinerary:
                    itinerary = Itinerary.objects.create(
                        trip=current_trip,
                        itinerary_name=f"{current_trip.trip_name} - 第1天",
                        date=current_trip.start_time.date(),
                        start_time=time(9, 0),
                        end_time=time(18, 0)
                    )
            
            # 移除重複檢查，直接添加景點到行程
            
            # 計算建議時間
            existing_attractions = ItineraryAttraction.objects.filter(
                itinerary=itinerary
            ).order_by('visit_time')
            
            if existing_attractions.exists():
                last_attraction = existing_attractions.last()
                if last_attraction.visit_time:
                    last_time = datetime.combine(itinerary.date, last_attraction.visit_time)
                    suggested_time = (last_time + timedelta(hours=2)).time()
                else:
                    suggested_time = time(9, 0)
            else:
                suggested_time = time(9, 0)
            
            # 確保時間不超過當天結束時間
            if suggested_time > time(21, 0):
                suggested_time = time(9, 0)
            
            # 添加景點到行程
            ItineraryAttraction.objects.create(
                itinerary=itinerary,
                attraction=attraction,
                visit_time=suggested_time,
                notes=f'添加於 {datetime.now().strftime("%Y-%m-%d %H:%M")}'
            )
            
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
    
    # 預設圖片映射
    default_images = {
        '寺廟神社': 'https://images.unsplash.com/photo-1545569341-9eb8b30979d9?w=300&h=180&fit=crop',
        '現代景點': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=300&h=180&fit=crop',
        '自然風光': 'https://images.unsplash.com/photo-1522383225653-ed111181a951?w=300&h=180&fit=crop',
        '美食': 'https://images.unsplash.com/photo-1551218808-94e220e084d2?w=300&h=180&fit=crop',
        '購物娛樂': 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=300&h=180&fit=crop'
    }
    
    attractions_data = [
        {
            'id': attr.id,
            'name': attr.name,
            'location': f"{attr.region.name}・{attr.address}",
            'rating': float(attr.rating),
            'rating_stars': attr.rating_stars,
            'type': attr.attraction_type.name,
            'image': attr.image.url if attr.image else default_images.get(
                attr.attraction_type.name, 
                'https://images.unsplash.com/photo-1480796927426-f609979314bd?w=300&h=180&fit=crop'
            )
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
            'trip_name': trip.trip_name,  # 使用新的欄位名稱
            'start_time': trip.start_time.strftime('%Y-%m-%d'),
            'end_time': trip.end_time.strftime('%Y-%m-%d'),
            'attraction_count': sum(itinerary.attractions.count() for itinerary in trip.itinerary_set.all()),
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
    itineraries = Itinerary.objects.filter(trip=trip).order_by('date', 'start_time')
    
    # 獲取所有景點（不再排除已添加的）
    available_attractions = Attraction.objects.all()[:20]  # 限制數量
    
    # 獲取地區和景點類型用於篩選
    regions = Region.objects.all()
    attraction_types = AttractionType.objects.all()
    
    # 計算統計資料 - 改為計算實際的 ItineraryAttraction 數量
    total_attractions = ItineraryAttraction.objects.filter(itinerary__trip=trip).count()
    trip_days = list(range(1, trip.duration_days + 1))
    
    # 整理每天的行程資料，並按照 visit_time 排序
    day_itineraries = {}
    for day in trip_days:
        target_date = trip.start_time.date() + timedelta(days=day-1)
        itinerary = Itinerary.objects.filter(trip=trip, date=target_date).first()
        if itinerary:
            # 重要：為 itinerary 添加按時間排序的景點列表
            itinerary.sorted_attractions = itinerary.itineraryattraction_set.all().order_by(
                'visit_time', 'id'  # 先按 visit_time 排序，如果時間相同則按 id 排序
            )
        day_itineraries[day] = itinerary
    
    context = {
        'trip': trip,
        'itineraries': itineraries,
        'available_attractions': available_attractions,
        'regions': regions,
        'attraction_types': attraction_types,
        'total_attractions': total_attractions,
        'trip_days': trip_days,
        'day_itineraries': day_itineraries,
    }
    return render(request, 'travel/edit_trip.html', context)

@login_required
def delete_trip_view(request, trip_id):
    if request.method == 'DELETE':
        try:
            trip = get_object_or_404(Trip, id=trip_id, user=request.user)
            trip_name = trip.trip_name  # 使用新的欄位名稱
            trip.delete()
            return JsonResponse({
                'success': True, 
                'message': f'行程「{trip_name}」已刪除'
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': f'刪除失敗：{str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': '無效的請求'})

@login_required 
def remove_from_trip_view(request, attraction_id):
    """從行程中移除景點"""
    if request.method == 'DELETE':
        try:
            itinerary_attraction = get_object_or_404(
                ItineraryAttraction, 
                id=attraction_id,
                itinerary__trip__user=request.user
            )
            attraction_name = itinerary_attraction.attraction.name
            itinerary_attraction.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'已從行程中移除「{attraction_name}」'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'移除失敗：{str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': '無效的請求'})

# 新增：收藏景點相關功能
@login_required
def add_to_favorites_view(request, attraction_id):
    """添加景點到收藏"""
    if request.method == 'POST':
        try:
            attraction = get_object_or_404(Attraction, id=attraction_id)
            favorite, created = FavoriteAttraction.objects.get_or_create(
                user=request.user,
                attraction=attraction
            )
            
            if created:
                return JsonResponse({
                    'success': True,
                    'message': f'已收藏「{attraction.name}」',
                    'action': 'added'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': '景點已在收藏中',
                    'action': 'exists'
                })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '無效的請求'})

@login_required
def remove_from_favorites_view(request, attraction_id):
    """從收藏中移除景點"""
    if request.method == 'DELETE':
        try:
            attraction = get_object_or_404(Attraction, id=attraction_id)
            favorite = get_object_or_404(
                FavoriteAttraction,
                user=request.user,
                attraction=attraction
            )
            favorite.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'已從收藏中移除「{attraction.name}」'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'移除失敗：{str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': '無效的請求'})

@login_required
def get_user_favorites_view(request):
    """獲取用戶收藏的景點"""
    favorites = FavoriteAttraction.objects.filter(user=request.user).select_related('attraction')
    favorites_data = [
        {
            'id': fav.attraction.id,
            'name': fav.attraction.name,
            'location': f"{fav.attraction.region.name}・{fav.attraction.address}",
            'rating': float(fav.attraction.rating),
            'rating_stars': fav.attraction.rating_stars,
            'image': fav.attraction.image.url if fav.attraction.image else '/static/images/default-attraction.jpg'
        }
        for fav in favorites
    ]
    
    return JsonResponse({'success': True, 'favorites': favorites_data})

def card_view(request):
    return render(request, 'travel/card.html')

# 在 travel/views.py 中添加這個新的 view 函數：

@login_required
def create_trip_view(request):
    if request.method == 'POST':
        try:
            trip_name = request.POST.get('trip_name')
            description = request.POST.get('description', '')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            start_time_str = request.POST.get('start_time', '09:00')
            end_time_str = request.POST.get('end_time', '18:00')
            
            # 驗證必填欄位
            if not trip_name or not start_date or not end_date:
                messages.error(request, '請填寫所有必填欄位')
                return render(request, 'travel/create_trip.html')
            
            # 組合日期和時間
            from datetime import datetime, date, time
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            start_time_obj = datetime.strptime(start_time_str, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time_str, '%H:%M').time()
            
            # 組合完整的 datetime
            start_datetime = datetime.combine(start_date_obj, start_time_obj)
            end_datetime = datetime.combine(end_date_obj, end_time_obj)
            
            # 驗證日期邏輯
            if end_datetime <= start_datetime:
                messages.error(request, '結束日期必須晚於開始日期')
                return render(request, 'travel/create_trip.html')
            
            # 創建行程
            trip = Trip.objects.create(
                user=request.user,
                trip_name=trip_name,
                description=description,
                start_time=start_datetime,
                end_time=end_datetime
            )
            
            # 為每一天創建 Itinerary
            current_date = start_date_obj
            day_count = 1
            
            while current_date <= end_date_obj:
                Itinerary.objects.create(
                    trip=trip,
                    itinerary_name=f"{trip_name} - 第{day_count}天",
                    date=current_date,
                    start_time=start_time_obj,
                    end_time=end_time_obj
                )
                current_date = current_date + timedelta(days=1)
                day_count += 1
            
            messages.success(request, f'行程「{trip_name}」建立成功！')
            return redirect('travel:edit_trip', trip_id=trip.id)
            
        except Exception as e:
            messages.error(request, f'建立行程失敗：{str(e)}')
            return render(request, 'travel/create_trip.html')
    
    return render(request, 'travel/create_trip.html')

@login_required
def search_available_attractions_view(request):
    """搜索所有景點（用於編輯行程頁面）"""
    search_query = request.GET.get('search', '').strip()
    region = request.GET.get('region', '').strip()
    attraction_type = request.GET.get('type', '').strip()
    trip_id = request.GET.get('trip_id', '')
    
    try:
        # 建立查詢 - 不再排除已添加的景點
        attractions = Attraction.objects.all()
        
        if search_query:
            attractions = attractions.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(address__icontains=search_query)
            )
        
        if region:
            attractions = attractions.filter(region__name=region)
        
        if attraction_type:
            attractions = attractions.filter(attraction_type__name=attraction_type)
        
        # 預設圖片映射
        default_images = {
            '寺廟神社': 'https://images.unsplash.com/photo-1545569341-9eb8b30979d9?w=300&h=180&fit=crop',
            '現代景點': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=300&h=180&fit=crop',
            '自然風光': 'https://images.unsplash.com/photo-1522383225653-ed111181a951?w=300&h=180&fit=crop',
            '美食': 'https://images.unsplash.com/photo-1551218808-94e220e084d2?w=300&h=180&fit=crop',
            '購物娛樂': 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=300&h=180&fit=crop'
        }
        
        attractions_data = []
        for attr in attractions[:20]:  # 限制返回20個結果
            attractions_data.append({
                'id': attr.id,
                'name': attr.name,
                'location': f"{attr.region.name}・{attr.address}",
                'rating': float(attr.rating),
                'rating_stars': attr.rating_stars,
                'image': attr.image.url if attr.image else default_images.get(
                    attr.attraction_type.name, 
                    'https://images.unsplash.com/photo-1480796927426-f609979314bd?w=300&h=180&fit=crop'
                )
            })
        
        return JsonResponse({'success': True, 'attractions': attractions_data})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@login_required
def add_to_itinerary_view(request):
    """添加景點到行程（允許重複）"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            trip_id = data.get('trip_id')
            attraction_id = data.get('attraction_id')
            day = int(data.get('day', 1))
            
            trip = get_object_or_404(Trip, id=trip_id, user=request.user)
            attraction = get_object_or_404(Attraction, id=attraction_id)
            
            # 計算目標日期
            target_date = trip.start_time.date() + timedelta(days=day-1)
            
            # 獲取或創建對應日期的 Itinerary
            itinerary, created = Itinerary.objects.get_or_create(
                trip=trip,
                date=target_date,
                defaults={
                    'itinerary_name': f"{trip.trip_name} - 第{day}天",
                    'start_time': time(9, 0),
                    'end_time': time(18, 0)
                }
            )
            
            # 移除重複檢查，允許同一景點多次添加
            
            # 計算建議的參觀時間（基於該天已有的景點）
            existing_attractions = ItineraryAttraction.objects.filter(
                itinerary=itinerary
            ).order_by('visit_time')
            
            if existing_attractions.exists():
                # 找到最後一個景點的時間，加上2小時作為新景點的開始時間
                last_attraction = existing_attractions.last()
                if last_attraction.visit_time:
                    last_time = datetime.combine(target_date, last_attraction.visit_time)
                    suggested_time = (last_time + timedelta(hours=2)).time()
                else:
                    suggested_time = time(9, 0)
            else:
                suggested_time = time(9, 0)
            
            # 確保時間不超過當天結束時間
            if suggested_time > time(21, 0):  # 如果超過晚上9點，重置為早上9點
                suggested_time = time(9, 0)
            
            # 添加景點到行程，設定建議時間
            itinerary_attraction = ItineraryAttraction.objects.create(
                itinerary=itinerary,
                attraction=attraction,
                visit_time=suggested_time,
                notes=f'添加於 {datetime.now().strftime("%Y-%m-%d %H:%M")}'
            )
            
            return JsonResponse({
                'success': True, 
                'message': f'景點「{attraction.name}」已加入第{day}天行程，建議參觀時間：{suggested_time.strftime("%H:%M")}'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '無效的請求'})

@login_required
def change_attraction_day_view(request):
    """更改景點的天數（允許重複）"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            itinerary_attraction_id = data.get('itinerary_attraction_id')
            new_day = int(data.get('new_day'))
            
            itinerary_attraction = get_object_or_404(
                ItineraryAttraction, 
                id=itinerary_attraction_id,
                itinerary__trip__user=request.user
            )
            
            trip = itinerary_attraction.itinerary.trip
            target_date = trip.start_time.date() + timedelta(days=new_day-1)
            
            # 獲取或創建新的 Itinerary
            new_itinerary, created = Itinerary.objects.get_or_create(
                trip=trip,
                date=target_date,
                defaults={
                    'itinerary_name': f"{trip.trip_name} - 第{new_day}天",
                    'start_time': time(9, 0),
                    'end_time': time(18, 0)
                }
            )
            
            # 移除重複檢查，直接更新景點的 itinerary
            itinerary_attraction.itinerary = new_itinerary
            itinerary_attraction.save()
            
            return JsonResponse({'success': True, 'message': f'景點已移至第{new_day}天'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '無效的請求'})

@login_required
def update_attraction_time_view(request):
    """更新景點時間並返回重新排序的資料"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            itinerary_attraction_id = data.get('itinerary_attraction_id')
            new_time = data.get('new_time')
            
            itinerary_attraction = get_object_or_404(
                ItineraryAttraction, 
                id=itinerary_attraction_id,
                itinerary__trip__user=request.user
            )
            
            # 將時間字符串轉換為 time 對象
            time_obj = datetime.strptime(new_time, '%H:%M').time()
            
            # 更新 visit_time 欄位
            itinerary_attraction.visit_time = time_obj
            itinerary_attraction.save()
            
            # 獲取同一天的所有景點，按時間重新排序
            itinerary = itinerary_attraction.itinerary
            sorted_attractions = itinerary.itineraryattraction_set.all().order_by(
                'visit_time', 'id'
            )
            
            # 構建返回的排序資料
            attractions_data = []
            for ia in sorted_attractions:
                attractions_data.append({
                    'id': ia.id,
                    'attraction_id': ia.attraction.id,
                    'name': ia.attraction.name,
                    'address': ia.attraction.address,
                    'visit_time': ia.visit_time.strftime('%H:%M') if ia.visit_time else '09:00',
                    'image_url': ia.attraction.image.url if ia.attraction.image else None,
                    'attraction_type': ia.attraction.attraction_type.name
                })
            
            return JsonResponse({
                'success': True, 
                'message': f'時間已更新為 {new_time}',
                'sorted_attractions': attractions_data,
                'itinerary_date': itinerary.date.isoformat()
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '無效的請求'})

def attraction_detail(request, attraction_id):
    """景點詳情頁面"""
    attraction = get_object_or_404(Attraction, id=attraction_id)
    
    # 獲取用戶的行程列表
    user_trips = []
    if request.user.is_authenticated:
        user_trips = Trip.objects.filter(user=request.user, end_time__gte=datetime.now())
    
    context = {
        'attraction': attraction,
        'user_trips': user_trips,
    }
    return render(request, 'travel/attraction_detail.html', context)

@login_required
@require_http_methods(["GET"])
def get_trip_dates(request, trip_id):
    """獲取指定行程的可選日期"""
    try:
        trip = get_object_or_404(Trip, id=trip_id, user=request.user)
        
        # 生成行程期間的所有日期
        dates = []
        current_date = trip.start_time.date()
        end_date = trip.end_time.date()
        day_counter = 1
        
        while current_date <= end_date:
            dates.append({
                'value': current_date.isoformat(),
                'label': f'第{day_counter}天 ({current_date.strftime("%m/%d")})'
            })
            current_date += timedelta(days=1)
            day_counter += 1
        
        return JsonResponse({
            'success': True,
            'dates': dates
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
@require_http_methods(["POST"])
def add_attraction_to_trip(request):
    """將景點加入到指定行程的指定日期（允許重複）"""
    try:
        data = json.loads(request.body)
        attraction_id = data.get('attraction_id')
        trip_id = data.get('trip_id')
        selected_date = data.get('selected_date')
        remember_choice = data.get('remember_choice', False)
        
        # 驗證資料
        if not all([attraction_id, trip_id, selected_date]):
            return JsonResponse({
                'success': False,
                'message': '缺少必要參數'
            })
        
        attraction = get_object_or_404(Attraction, id=attraction_id)
        trip = get_object_or_404(Trip, id=trip_id, user=request.user)
        
        # 轉換日期格式
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        
        # 檢查日期是否在行程範圍內
        if not (trip.start_time.date() <= selected_date <= trip.end_time.date()):
            return JsonResponse({
                'success': False,
                'message': '選擇的日期不在行程範圍內'
            })
        
        # 獲取或創建當日行程
        itinerary, created = Itinerary.objects.get_or_create(
            trip=trip,
            date=selected_date,
            defaults={
                'itinerary_name': f'{trip.trip_name} - {selected_date.strftime("%m/%d")}',
                'start_time': trip.start_time.time(),
                'end_time': trip.end_time.time(),
            }
        )
        
        # 移除重複檢查，直接添加景點到行程
        
        # 計算建議時間
        existing_attractions = ItineraryAttraction.objects.filter(
            itinerary=itinerary
        ).order_by('visit_time')
        
        if existing_attractions.exists():
            last_attraction = existing_attractions.last()
            if last_attraction.visit_time:
                last_time = datetime.combine(selected_date, last_attraction.visit_time)
                suggested_time = (last_time + timedelta(hours=2)).time()
            else:
                suggested_time = time(9, 0)
        else:
            suggested_time = time(9, 0)
        
        # 確保時間不超過當天結束時間
        if suggested_time > time(21, 0):
            suggested_time = time(9, 0)
        
        # 添加景點到行程
        ItineraryAttraction.objects.create(
            itinerary=itinerary,
            attraction=attraction,
            visit_time=suggested_time,
            notes=f'從景點詳情頁面加入 - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'已成功將「{attraction.name}」加入到{selected_date.strftime("%m/%d")}的行程中！'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '無效的請求格式'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'加入行程失敗：{str(e)}'
        })

@login_required
@require_http_methods(["POST"])
def toggle_favorite(request):
    """切換景點收藏狀態"""
    try:
        data = json.loads(request.body)
        attraction_id = data.get('attraction_id')
        
        if not attraction_id:
            return JsonResponse({
                'success': False,
                'message': '缺少景點ID'
            })
        
        attraction = get_object_or_404(Attraction, id=attraction_id)
        
        # 檢查是否已收藏
        favorite, created = FavoriteAttraction.objects.get_or_create(
            user=request.user,
            attraction=attraction
        )
        
        if created:
            # 新建收藏
            is_favorite = True
            message = '已加入收藏'
        else:
            # 取消收藏
            favorite.delete()
            is_favorite = False
            message = '已取消收藏'
        
        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite,
            'message': message
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '無效的請求格式'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })
    
import json
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

def add_attraction_to_trip(request):
    """將景點加入到指定行程的指定日期"""
    try:
        data = json.loads(request.body)
        attraction_id = data.get('attraction_id')
        trip_id = data.get('trip_id')
        selected_date = data.get('selected_date')
        remember_choice = data.get('remember_choice', False)
        
        # 驗證資料
        if not all([attraction_id, trip_id, selected_date]):
            return JsonResponse({
                'success': False,
                'message': '缺少必要參數'
            })
        
        attraction = get_object_or_404(Attraction, id=attraction_id)
        trip = get_object_or_404(Trip, id=trip_id, user=request.user)
        
        # 轉換日期格式
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        
        # 檢查日期是否在行程範圍內
        if not (trip.start_time.date() <= selected_date <= trip.end_time.date()):
            return JsonResponse({
                'success': False,
                'message': '選擇的日期不在行程範圍內'
            })
        
        # 獲取或創建當日行程
        itinerary, created = Itinerary.objects.get_or_create(
            trip=trip,
            date=selected_date,
            defaults={
                'itinerary_name': f'{trip.trip_name} - {selected_date.strftime("%m/%d")}',
                'start_time': trip.start_time.time(),
                'end_time': trip.end_time.time(),
            }
        )
        
        # 檢查景點是否已經在當天行程中
        existing_today = ItineraryAttraction.objects.filter(
            itinerary=itinerary, 
            attraction=attraction
        ).exists()
        
        # 檢查景點是否已經在其他日期的行程中
        existing_other_days = ItineraryAttraction.objects.filter(
            itinerary__trip=trip,
            attraction=attraction
        ).exclude(itinerary=itinerary).exists()
        
        # 決定訊息內容
        if existing_today:
            message = f'「{attraction.name}」已在{selected_date.strftime("%m/%d")}的行程中，已重新加入！'
        elif existing_other_days:
            message = f'「{attraction.name}」已在此行程的其他日期中，現在也加入到{selected_date.strftime("%m/%d")}！'
        else:
            message = f'已成功將「{attraction.name}」加入到{selected_date.strftime("%m/%d")}的行程中！'
        
        # 不管是否已存在，都允許加入（如果已存在就更新）
        itinerary_attraction, created = ItineraryAttraction.objects.get_or_create(
            itinerary=itinerary,
            attraction=attraction,
            defaults={
                'notes': f'從景點詳情頁面加入 - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
            }
        )
        
        # 如果已存在，更新筆記
        if not created:
            itinerary_attraction.notes = f'重新加入 - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
            itinerary_attraction.save()
        
        return JsonResponse({
            'success': True,
            'message': message,
            'trip_id': trip_id  # 加入 trip_id 供前端跳轉使用
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '無效的請求格式'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'加入行程失敗：{str(e)}'
        })