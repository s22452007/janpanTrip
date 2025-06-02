from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class UserProfile(models.Model):
    PERMISSION_CHOICES = [
        ('user', '使用者'),
        ('admin', '管理員'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='使用者')
    使用者編號 = models.CharField(max_length=50, unique=True, verbose_name='使用者編號', blank=True)  # 新增欄位
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='頭像')
    email = models.EmailField(max_length=254, blank=True, verbose_name='電子郵件')
    phone = models.CharField(max_length=20, blank=True, verbose_name='電話')
    permission = models.CharField(max_length=20, choices=PERMISSION_CHOICES, default='user', verbose_name='權限')
    
    class Meta:
        verbose_name = '使用者資料'
        verbose_name_plural = '使用者資料'
    
    def save(self, *args, **kwargs):
        # 如果使用者編號為空，自動生成
        if not self.使用者編號:
            self.使用者編號 = f"USER{self.user.id:06d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} ({self.get_permission_display()})"

class Region(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='地區名稱')
    
    class Meta:
        verbose_name = '地區'
        verbose_name_plural = '地區'
    
    def __str__(self):
        return self.name

class AttractionType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='類型名稱')
    icon = models.CharField(max_length=50, blank=True, verbose_name='圖標')
    
    class Meta:
        verbose_name = '景點類型'
        verbose_name_plural = '景點類型'
    
    def __str__(self):
        return self.name

class Attraction(models.Model):
    name = models.CharField(max_length=200, verbose_name='景點名稱')
    description = models.TextField(verbose_name='描述')
    address = models.CharField(max_length=300, verbose_name='地址')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='地區')
    attraction_type = models.ForeignKey(AttractionType, on_delete=models.CASCADE, verbose_name='景點類型')
    features = models.TextField(blank=True, verbose_name='特色')
    opening_hours = models.TextField(blank=True, verbose_name='營業時間')
    phone = models.CharField(max_length=20, blank=True, verbose_name='電話')
    website = models.URLField(blank=True, verbose_name='官方網站')
    image = models.ImageField(upload_to='attractions/', blank=True, null=True, verbose_name='圖片')
    
    class Meta:
        ordering = ['name']  # 移除按評分排序
        verbose_name = '景點'
        verbose_name_plural = '景點'
    
    def __str__(self):
        return self.name
    
    # 移除 rating_stars 屬性，因為沒有評分欄位了

class Trip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='使用者')
    trip_name = models.CharField(max_length=200, verbose_name='旅程名稱')  # 保持英文欄位名
    description = models.TextField(blank=True, verbose_name='旅程描述')
    start_date = models.DateTimeField(verbose_name='開始日期')  # 改為 start_date
    end_date = models.DateTimeField(verbose_name='結束日期')    # 改為 end_date
    
    class Meta:
        ordering = ['-start_date']  # 更新排序欄位
        verbose_name = '旅程'
        verbose_name_plural = '旅程'
    
    def __str__(self):
        return f"{self.user.username} - {self.trip_name}"
    
    @property
    def duration_days(self):
        return (self.end_date.date() - self.start_date.date()).days + 1
    
    # 為了向後相容，保留舊的屬性名稱
    @property
    def start_time(self):
        return self.start_date
    
    @property
    def end_time(self):
        return self.end_date

class Itinerary(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, verbose_name='旅程')
    date = models.DateField(verbose_name='日期')
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE, verbose_name='景點')  # 直接關聯景點
    visit_time = models.TimeField(null=True, blank=True, verbose_name='參觀時間')
    duration_minutes = models.PositiveIntegerField(default=120, verbose_name='預計停留時間(分鐘)')
    
    class Meta:
        ordering = ['date', 'visit_time']
        verbose_name = '行程'
        verbose_name_plural = '行程'
        # 可以允許同一個景點在同一天多次出現，所以不設定 unique_together
    
    def __str__(self):
        time_str = f" ({self.visit_time.strftime('%H:%M')})" if self.visit_time else ""
        return f"{self.trip.trip_name} - {self.attraction.name} ({self.date}){time_str}"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'attraction')  # 防止重複收藏
    
    def __str__(self):
        return f"{self.user.username} - {self.attraction.name}"
    
# 在你的 models.py 中，Favorite 模型已經正確，但需要確保 verbose_name
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'attraction')  # 防止重複收藏
        verbose_name = '收藏景點'
        verbose_name_plural = '收藏景點'
    
    def __str__(self):
        return f"{self.user.username} - {self.attraction.name}"
