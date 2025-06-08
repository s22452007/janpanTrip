from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Attraction, Trip, UserProfile, Region, AttractionType, Itinerary, Favorite
from datetime import datetime, date, time
from datetime import timedelta
import json
from django.views.decorators.http import require_http_methods, require_POST


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
    # 獲取景點資料（移除評分相關）
    attractions = Attraction.objects.all()[:8]  # 顯示前8個景點
    
    ## 獲取用戶行程並計算景點數量
    user_trips = Trip.objects.filter(user=request.user).order_by('-start_date')[:3]  # 顯示前3個行程，按時間排序

    ## 獲取用戶行程並計算景點數量
    user_trips_me = Trip.objects.filter(user=request.user).order_by('-start_date')  # 顯示，按時間排序

    ## 為每個行程添加景點數量（使用新的 Itinerary 模型）
    for trip in user_trips_me:
        trip.total_attractions = Itinerary.objects.filter(trip=trip).count()
    
    # 獲取用戶的最近收藏景點（前5個）
    user_favorites = Favorite.objects.filter(user=request.user).select_related(
        'attraction', 
        'attraction__region', 
        'attraction__attraction_type'
    ).order_by('-created_at')[:5]
    
    # 新增：獲取地區和景點類型用於搜尋下拉選單
    regions = Region.objects.all().order_by('name')
    attraction_types = AttractionType.objects.all().order_by('name')
    
    ##
    context = {
        'attractions': attractions,
        'user_trips': user_trips,
        'user_trips_me': user_trips_me,
        'user_favorites': user_favorites,  # 新增收藏資料
        'regions': regions,
        'attraction_types': attraction_types,
    }
    return render(request, 'travel/home.html', context)

@login_required
@csrf_exempt # <-- 確保有這個
def profile_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')

        name_parts = full_name.split(' ', 1)
        request.user.first_name = name_parts[0]
        request.user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        request.user.email = email

        # 使用 try-except 塊來捕獲保存時可能發生的錯誤
        try:
            request.user.save() # 保存 Django User 模型的更改

            user_profile.phone = phone
            if 'avatar' in request.FILES:
                user_profile.avatar = request.FILES['avatar']

            user_profile.save() # 保存 UserProfile 模型的更改

            # messages.success(request, '個人資料已成功更新！') # 這行可以保留，但對於 AJAX 響應，前端會直接使用 JSON 消息
            return JsonResponse({'success': True, 'message': '個人資料已成功更新！'}) # <--- 就是這一行！

        except Exception as e:
            # 如果保存過程中發生錯誤，返回 JSON 錯誤響應
            print(f"Error saving profile: {e}") # 打印到終端機以供調試
            return JsonResponse({'success': False, 'message': f'更新失敗：{str(e)}'}, status=400)

    else: # GET 請求時的處理
        # 重定向到首頁
        return redirect('travel:home')

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
                    'start_date': datetime(2024, 12, 1, 9, 0),  # 更新欄位名
                    'end_date': datetime(2024, 12, 7, 18, 0),   # 更新欄位名
                }
            )
            
            # 計算建議時間
            existing_attractions = Itinerary.objects.filter(
                trip=current_trip,
                date=current_trip.start_date.date()  # 使用新欄位名
            ).order_by('visit_time')
            
            if existing_attractions.exists():
                last_attraction = existing_attractions.last()
                if last_attraction.visit_time:
                    last_time = datetime.combine(current_trip.start_date.date(), last_attraction.visit_time)
                    suggested_time = (last_time + timedelta(hours=2)).time()
                else:
                    suggested_time = time(9, 0)
            else:
                suggested_time = time(9, 0)
            
            # 確保時間不超過當天結束時間
            if suggested_time > time(21, 0):
                suggested_time = time(9, 0)
            
            # 直接添加到 Itinerary（不再需要中間表）
            Itinerary.objects.create(
                trip=current_trip,
                date=current_trip.start_date.date(),
                attraction=attraction,
                visit_time=suggested_time,
                duration_minutes=120
            )
            
            return JsonResponse({'success': True, 'message': '景點已加入行程'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '無效的請求'})

def search_attractions_view(request):
    search_query = request.GET.get('search', '')
    region = request.GET.get('region', '')
    attraction_type = request.GET.get('type', '')
    # 移除評分篩選
    
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
            # 移除評分相關欄位
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
            'trip_name': trip.trip_name,
            'start_time': trip.start_date.strftime('%Y-%m-%d'),  # 更新欄位名
            'end_time': trip.end_date.strftime('%Y-%m-%d'),      # 更新欄位名
            'attraction_count': Itinerary.objects.filter(trip=trip).count(),  # 使用新的計算方式
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
    
    # 獲取所有景點
    available_attractions = Attraction.objects.all()[:20]
    
    # 獲取地區和景點類型用於篩選
    regions = Region.objects.all()
    attraction_types = AttractionType.objects.all()
    
    # 計算統計資料
    total_attractions = Itinerary.objects.filter(trip=trip).count()
    trip_days = list(range(1, trip.duration_days + 1))
    
    # 整理每天的行程資料
    day_itineraries = {}
    for day in trip_days:
        target_date = trip.start_date.date() + timedelta(days=day-1)
        day_attractions = Itinerary.objects.filter(
            trip=trip, 
            date=target_date
        ).order_by('visit_time', 'id')
        
        # 為每個景點計算離開時間
        for item in day_attractions:
            if item.visit_time and item.duration_minutes:
                visit_datetime = datetime.combine(target_date, item.visit_time)
                departure_datetime = visit_datetime + timedelta(minutes=item.duration_minutes)
                item.departure_time = departure_datetime.time()
            else:
                item.departure_time = None
        
        day_itineraries[day] = day_attractions
    
    context = {
        'trip': trip,
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
            # 使用新的 Itinerary 模型
            itinerary_item = get_object_or_404(
                Itinerary, 
                id=attraction_id,
                trip__user=request.user
            )
            attraction_name = itinerary_item.attraction.name
            itinerary_item.delete()
            
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
            favorite, created = Favorite.objects.get_or_create(
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
                Favorite,
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
def favorites_view(request):
    """收藏頁面視圖"""
    # 獲取用戶的所有收藏，並包含相關的景點資料
    favorites = Favorite.objects.filter(user=request.user).select_related(
        'attraction', 
        'attraction__region', 
        'attraction__attraction_type'
    )
    
    # 調試輸出 - 這會出現在終端中
    print(f"=== 收藏頁面調試 ===")
    print(f"當前用戶: {request.user.username}")
    print(f"用戶 ID: {request.user.id}")
    print(f"查詢到的收藏數量: {favorites.count()}")
    
    # 列出所有收藏的景點
    for i, fav in enumerate(favorites, 1):
        print(f"收藏 {i}: {fav.attraction.name} (景點ID: {fav.attraction.id}, 收藏時間: {fav.created_at})")
    
    print(f"傳遞給模板的收藏數量: {len(list(favorites))}")
    print(f"================")
    
    context = {
        'favorites': favorites,
    }
    return render(request, 'travel/favorites.html', context)

def card_view(request):
    return render(request, 'travel/card.html')

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
                start_date=start_datetime,  # 使用新欄位名
                end_date=end_datetime       # 使用新欄位名
            )
            
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
                # 移除評分相關欄位
                'image': attr.image.url if attr.image else default_images.get(
                    attr.attraction_type.name, 
                    'https://images.unsplash.com/photo-1480796927426-f609979314bd?w=300&h=180&fit=crop'
                )
            })
        
        return JsonResponse({'success': True, 'attractions': attractions_data})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
def add_to_itinerary_view(request):
    """添加景點到行程"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            trip_id = data.get('trip_id')
            attraction_id = data.get('attraction_id')
            day = int(data.get('day', 1))
            
            trip = get_object_or_404(Trip, id=trip_id, user=request.user)
            attraction = get_object_or_404(Attraction, id=attraction_id)
            
            # 計算目標日期
            target_date = trip.start_date.date() + timedelta(days=day-1)  # 使用新欄位名
            
            # 計算建議的參觀時間
            existing_attractions = Itinerary.objects.filter(
                trip=trip,
                date=target_date
            ).order_by('visit_time')
            
            if existing_attractions.exists():
                last_attraction = existing_attractions.last()
                if last_attraction.visit_time:
                    last_time = datetime.combine(target_date, last_attraction.visit_time)
                    suggested_time = (last_time + timedelta(hours=2)).time()
                else:
                    suggested_time = time(9, 0)
            else:
                suggested_time = time(9, 0)
            
            # 確保時間不超過當天結束時間
            if suggested_time > time(21, 0):
                suggested_time = time(9, 0)
            
            # 直接創建 Itinerary 項目
            Itinerary.objects.create(
                trip=trip,
                date=target_date,
                attraction=attraction,
                visit_time=suggested_time,
                duration_minutes=120
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
            itinerary_id = data.get('itinerary_attraction_id')  # 實際上是 itinerary_id
            new_day = int(data.get('new_day'))
            
            # 修正：直接使用 Itinerary 模型
            itinerary_item = get_object_or_404(
                Itinerary, 
                id=itinerary_id,
                trip__user=request.user
            )
            
            trip = itinerary_item.trip
            target_date = trip.start_date.date() + timedelta(days=new_day-1)
            
            # 更新日期
            itinerary_item.date = target_date
            itinerary_item.save()
            
            return JsonResponse({'success': True, 'message': f'景點已移至第{new_day}天'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '無效的請求'})

@login_required
def update_attraction_time_view(request):
    """更新景點時間"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            itinerary_id = data.get('itinerary_attraction_id')
            new_time = data.get('new_time')
            
            print(f"=== 更新時間調試 ===")
            print(f"itinerary_id: {itinerary_id}")
            print(f"new_time: {new_time}")
            
            itinerary_item = get_object_or_404(
                Itinerary, 
                id=itinerary_id,
                trip__user=request.user
            )
            
            print(f"找到行程項目: {itinerary_item.attraction.name}")
            print(f"原始時間: {itinerary_item.visit_time}")
            
            # 將時間字符串轉換為 time 對象
            time_obj = datetime.strptime(new_time, '%H:%M').time()
            
            # 更新 visit_time 欄位
            itinerary_item.visit_time = time_obj
            itinerary_item.save()
            
            print(f"更新後時間: {itinerary_item.visit_time}")
            print(f"==================")
            
            return JsonResponse({
                'success': True, 
                'message': f'時間已更新為 {new_time}'
            })
            
        except Exception as e:
            print(f"更新時間錯誤: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '無效的請求'})

def attraction_detail(request, attraction_id):
    """景點詳情頁面"""
    attraction = get_object_or_404(Attraction, id=attraction_id)
    
    ## 獲取用戶的行程列表
    user_trips= []
    if request.user.is_authenticated:
        user_trips= Trip.objects.filter(user=request.user, end_date__gte=datetime.now())
    
    ## 獲取用戶的行程列表
    user_trips_me = []
    if request.user.is_authenticated:
        user_trips_me = Trip.objects.filter(user=request.user, end_date__gte=datetime.now())
    
    ##
    context = {
        'attraction': attraction,
        'user_trips': user_trips,
        'user_trips_me': user_trips_me,
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
        current_date = trip.start_date.date()
        end_date = trip.end_date.date()
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
        print(f"get_trip_dates 錯誤: {str(e)}")
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
        
        print(f"收到請求 - attraction_id: {attraction_id}, trip_id: {trip_id}, selected_date: {selected_date}")
        
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
        if not (trip.start_date.date() <= selected_date <= trip.end_date.date()):
            return JsonResponse({
                'success': False,
                'message': '選擇的日期不在行程範圍內'
            })
        
        # 計算建議時間
        existing_attractions = Itinerary.objects.filter(
            trip=trip,
            date=selected_date
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
        
        # 檢查景點是否已經在當天行程中
        existing_today = Itinerary.objects.filter(
            trip=trip,
            date=selected_date,
            attraction=attraction
        ).exists()
        
        # 檢查景點是否已經在其他日期的行程中
        existing_other_days = Itinerary.objects.filter(
            trip=trip,
            attraction=attraction
        ).exclude(date=selected_date).exists()
        
        # 決定訊息內容
        if existing_today:
            message = f'「{attraction.name}」已在{selected_date.strftime("%m/%d")}的行程中，已更新時間！'
            # 更新現有記錄的時間
            Itinerary.objects.filter(
                trip=trip,
                date=selected_date,
                attraction=attraction
            ).update(visit_time=suggested_time)
        else:
            # 創建新的記錄
            Itinerary.objects.create(
                trip=trip,
                date=selected_date,
                attraction=attraction,
                visit_time=suggested_time,
                duration_minutes=120
            )
            
            if existing_other_days:
                message = f'「{attraction.name}」已在此行程的其他日期中，現在也加入到{selected_date.strftime("%m/%d")}！'
            else:
                message = f'已成功將「{attraction.name}」加入到{selected_date.strftime("%m/%d")}的行程中！'
        
        print(f"成功處理請求 - {message}")
        
        return JsonResponse({
            'success': True,
            'message': message,
            'trip_id': trip_id
        })
        
    except json.JSONDecodeError:
        print("JSON 解析錯誤")
        return JsonResponse({
            'success': False,
            'message': '無效的請求格式'
        })
    except Exception as e:
        print(f"add_attraction_to_trip 錯誤: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'加入行程失敗：{str(e)}'
        })

@login_required
def view_trip(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    
    # 計算統計資料
    total_attractions = Itinerary.objects.filter(trip=trip).count()
    trip_days = list(range(1, trip.duration_days + 1))
    
    # 整理每天的行程資料
    day_itineraries = {}
    for day in trip_days:
        target_date = trip.start_date.date() + timedelta(days=day-1)
        # 直接獲取該天的所有景點安排，已經按時間排序
        day_attractions = Itinerary.objects.filter(
            trip=trip, 
            date=target_date
        ).order_by('visit_time', 'id')
        day_itineraries[day] = day_attractions
    
    context = {
        'trip': trip,
        'total_attractions': total_attractions,
        'trip_days': trip_days,
        'day_itineraries': day_itineraries,
    }
    return render(request, 'travel/view_trip.html', context)

@login_required
def share_trip_view(request, trip_id):
    """生成行程分享資訊"""
    if request.method == 'GET':
        try:
            trip = get_object_or_404(Trip, id=trip_id, user=request.user)
            
            # 計算行程統計
            total_attractions = Itinerary.objects.filter(trip=trip).count()
            
            share_data = {
                'trip_id': trip.id,
                'trip_name': trip.trip_name,
                'description': trip.description,
                'start_date': trip.start_date.strftime('%Y/%m/%d'),
                'end_date': trip.end_date.strftime('%Y/%m/%d'),
                'duration_days': trip.duration_days,
                'total_attractions': total_attractions,
                'share_url': request.build_absolute_uri(f'/public/trip/{trip.id}/'),
                'share_text': f'快來看看我的日本旅遊行程：{trip.trip_name} ({trip.start_date.strftime("%Y/%m/%d")} - {trip.end_date.strftime("%Y/%m/%d")})',
            }
            
            return JsonResponse({'success': True, 'data': share_data})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '無效的請求'})

def public_trip_view(request, trip_id):
    """公開行程查看（無需登入）"""
    try:
        trip = get_object_or_404(Trip, id=trip_id)
        
        # 計算統計資料
        total_attractions = Itinerary.objects.filter(trip=trip).count()
        trip_days = list(range(1, trip.duration_days + 1))
        
        # 整理每天的行程資料，並按照 visit_time 排序
        day_itineraries = {}
        for day in trip_days:
            target_date = trip.start_date.date() + timedelta(days=day-1)
            day_attractions = Itinerary.objects.filter(
                trip=trip, 
                date=target_date
            ).order_by('visit_time', 'id')
            day_itineraries[day] = day_attractions
        
        print(f"公開行程查看 - trip_id: {trip_id}, 總景點數: {total_attractions}")
        
        context = {
            'trip': trip,
            'total_attractions': total_attractions,
            'trip_days': trip_days,
            'day_itineraries': day_itineraries,
            'is_public_view': True,
            'trip_owner': trip.user,
        }
        return render(request, 'travel/public_trip.html', context)
        
    except Exception as e:
        print(f"public_trip_view 錯誤: {str(e)}")
        return render(request, 'travel/trip_not_found.html', {
            'error_message': '找不到指定的行程，可能已被刪除或設為私人。'
        })

@require_POST
@login_required
def toggle_favorite(request, attraction_id):
    try:
        attraction = get_object_or_404(Attraction, id=attraction_id)
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            attraction=attraction
        )
        
        if not created:
            # 如果已存在就刪除（取消收藏）
            favorite.delete()
            is_favorited = False
        else:
            # 如果不存在就是新增收藏
            is_favorited = True
            
        return JsonResponse({
            'success': True,
            'is_favorited': is_favorited
        })
    except Attraction.DoesNotExist:
        return JsonResponse({'success': False, 'error': '景點不存在'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def update_attraction_duration_view(request):
    """更新景點參觀時間（分鐘數）"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            itinerary_id = data.get('itinerary_attraction_id')
            new_duration = data.get('new_duration')
            
            # 驗證參數
            if not itinerary_id or not new_duration:
                return JsonResponse({
                    'success': False, 
                    'message': '缺少必要參數'
                })
            
            # 驗證參觀時間範圍
            duration = int(new_duration)
            if duration < 1 or duration > 1440:
                return JsonResponse({
                    'success': False, 
                    'message': '參觀時間必須在 1-1440 分鐘之間'
                })
            
            itinerary_item = get_object_or_404(
                Itinerary, 
                id=itinerary_id,
                trip__user=request.user
            )
            
            # 更新 duration_minutes 欄位
            itinerary_item.duration_minutes = duration
            itinerary_item.save()
            
            return JsonResponse({
                'success': True, 
                'message': f'參觀時間已更新為 {duration} 分鐘'
            })
            
        except ValueError:
            return JsonResponse({
                'success': False, 
                'message': '無效的時間格式'
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': f'更新失敗：{str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': '無效的請求'})

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

@login_required
@require_POST
def get_favorite_status(request):
    """獲取多個景點的收藏狀態"""
    try:
        data = json.loads(request.body)
        attraction_ids = data.get('attraction_ids', [])
        
        if not attraction_ids:
            return JsonResponse({
                'success': False,
                'error': '沒有提供景點ID'
            })
        
        # 使用你現有的 Favorite 模型
        user_favorites = Favorite.objects.filter(
            user=request.user,
            attraction_id__in=attraction_ids
        ).values_list('attraction_id', flat=True)
        
        # 建立返回的數據結構
        favorites = {}
        for attraction_id in attraction_ids:
            favorites[attraction_id] = attraction_id in user_favorites
        
        return JsonResponse({
            'success': True,
            'favorites': favorites
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '無效的JSON數據'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

# 同時更新 search_attractions_view 函數，使其在搜尋結果中包含收藏狀態
def search_attractions_view(request):
    search_query = request.GET.get('search', '')
    region = request.GET.get('region', '')
    attraction_type = request.GET.get('type', '')
    
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
    
    # 預設圖片映射
    default_images = {
        '寺廟神社': 'https://images.unsplash.com/photo-1545569341-9eb8b30979d9?w=300&h=180&fit=crop',
        '現代景點': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=300&h=180&fit=crop',
        '自然風光': 'https://images.unsplash.com/photo-1522383225653-ed111181a951?w=300&h=180&fit=crop',
        '美食': 'https://images.unsplash.com/photo-1551218808-94e220e084d2?w=300&h=180&fit=crop',
        '購物娛樂': 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=300&h=180&fit=crop'
    }
    
    # 如果用戶已登入，獲取收藏狀態
    user_favorites = set()
    if request.user.is_authenticated:
        user_favorites = set(
            Favorite.objects.filter(
                user=request.user,
                attraction__in=attractions
            ).values_list('attraction_id', flat=True)
        )
    
    attractions_data = []
    for attr in attractions[:20]:  # 限制返回20個結果
        attractions_data.append({
            'id': attr.id,
            'name': attr.name,
            'location': f"{attr.region.name}・{attr.address}",
            'type': attr.attraction_type.name,
            'image': attr.image.url if attr.image else default_images.get(
                attr.attraction_type.name, 
                'https://images.unsplash.com/photo-1480796927426-f609979314bd?w=300&h=180&fit=crop'
            ),
            'is_favorited': attr.id in user_favorites  # 添加收藏狀態
        })
    
    return JsonResponse({'success': True, 'attractions': attractions_data})

# 同時更新 home_view，在初始加載時也包含收藏狀態
@login_required
def home_view(request):
    # 獲取景點資料
    attractions = Attraction.objects.all()[:8]  # 顯示前8個景點
    
    # 獲取用戶行程並計算景點數量
    user_trips= Trip.objects.filter(user=request.user)[:3]  # 顯示前3個行程

    ## 獲取用戶行程並計算景點數量
    user_trips_me = Trip.objects.filter(user=request.user)  # 顯示前個行程
    
    ## 為每個行程添加景點數量
    for trip in user_trips:
        trip.total_attractions = Itinerary.objects.filter(trip=trip).count()
    
    ## 為每個行程添加景點數量
    for trip in user_trips_me:
        trip.total_attractions = Itinerary.objects.filter(trip=trip).count()
    
    # 獲取地區和景點類型用於搜尋下拉選單
    regions = Region.objects.all().order_by('name')
    attraction_types = AttractionType.objects.all().order_by('name')
    
    # 獲取用戶收藏的景點ID集合
    user_favorites = set()
    if request.user.is_authenticated:
        user_favorites = set(
            Favorite.objects.filter(user=request.user)
            .values_list('attraction_id', flat=True)
        )
    
    # 為每個景點添加收藏狀態
    for attraction in attractions:
        attraction.is_favorited = attraction.id in user_favorites

    ##
    context = {
        'attractions': attractions,
        'user_trips': user_trips,
        'user_trips_me': user_trips_me,
        'regions': regions,
        'attraction_types': attraction_types,
        'user_favorites': user_favorites,
    }
    return render(request, 'travel/home.html', context)

@login_required
def update_departure_time_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            itinerary_id = data.get('itinerary_attraction_id')
            departure_time = data.get('departure_time')
            
            return JsonResponse({
                'success': True, 
                'message': f'離開時間已更新為 {departure_time}'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '無效的請求'})

@login_required
def update_trip_dates_view(request):
    """更新旅程日期"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            trip_id = data.get('trip_id')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            
            trip = get_object_or_404(Trip, id=trip_id, user=request.user)
            
            # 轉換日期格式
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # 驗證日期邏輯
            if end_date_obj < start_date_obj:
                return JsonResponse({
                    'success': False,
                    'message': '回程日期不能早於出發日期'
                })
            
            # 檢查是否天數有變化
            old_duration = trip.duration_days
            
            # 更新日期（保持原有的時間）
            trip.start_date = datetime.combine(start_date_obj, trip.start_date.time())
            trip.end_date = datetime.combine(end_date_obj, trip.end_date.time())
            trip.save()
            
            new_duration = trip.duration_days
            duration_changed = old_duration != new_duration
            
            # 如果天數有變化，需要調整行程
            if duration_changed:
                # 清理超出新日期範圍的行程項目
                for day in range(new_duration + 1, old_duration + 1):
                    target_date = trip.start_date.date() + timedelta(days=day-1)
                    Itinerary.objects.filter(trip=trip, date=target_date).delete()
            
            return JsonResponse({
                'success': True,
                'message': '日期已更新',
                'duration_changed': duration_changed,
                'new_duration': new_duration
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'更新失敗：{str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': '無效的請求'})