from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class UserProfile(models.Model):
    PERMISSION_CHOICES = [
        ('user', '使用者'),
        ('admin', '管理員'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='使用者')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='頭像')
    email = models.EmailField(max_length=254, blank=True, verbose_name='電子郵件')
    phone = models.CharField(max_length=20, blank=True, verbose_name='電話')
    permission = models.CharField(max_length=20, choices=PERMISSION_CHOICES, default='user', verbose_name='權限')
    
    class Meta:
        verbose_name = '使用者資料'
        verbose_name_plural = '使用者資料'
    
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
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='地區')
    attraction_type = models.ForeignKey(AttractionType, on_delete=models.CASCADE, verbose_name='景點類型')
    address = models.CharField(max_length=300, verbose_name='地址')
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0,
        verbose_name='評分'
    )
    image = models.ImageField(upload_to='attractions/', blank=True, null=True, verbose_name='圖片')
    website = models.URLField(blank=True, verbose_name='官方網站')
    phone = models.CharField(max_length=20, blank=True, verbose_name='電話')
    opening_hours = models.TextField(blank=True, verbose_name='營業時間')
    features = models.TextField(blank=True, verbose_name='特色')
    
    class Meta:
        ordering = ['-rating', 'name']
        verbose_name = '景點'
        verbose_name_plural = '景點'
    
    def __str__(self):
        return self.name
    
    @property
    def rating_stars(self):
        return '★' * int(self.rating) + '☆' * (5 - int(self.rating))

class Trip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='使用者')
    trip_name = models.CharField(max_length=200, verbose_name='旅程名稱')
    description = models.TextField(blank=True, verbose_name='描述')
    start_time = models.DateTimeField(verbose_name='開始時間')
    end_time = models.DateTimeField(verbose_name='結束時間')
    
    class Meta:
        ordering = ['-start_time']
        verbose_name = '旅程'
        verbose_name_plural = '旅程'
    
    def __str__(self):
        return f"{self.user.username} - {self.trip_name}"
    
    @property
    def duration_days(self):
        return (self.end_time.date() - self.start_time.date()).days + 1

class Itinerary(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, verbose_name='旅程')
    itinerary_name = models.CharField(max_length=200, verbose_name='行程名稱')
    date = models.DateField(verbose_name='日期')
    attractions = models.ManyToManyField(Attraction, through='ItineraryAttraction', verbose_name='景點')
    start_time = models.TimeField(verbose_name='開始時間')
    end_time = models.TimeField(verbose_name='結束時間')
    
    class Meta:
        ordering = ['date', 'start_time']
        verbose_name = '行程'
        verbose_name_plural = '行程'
    
    def __str__(self):
        return f"{self.trip.trip_name} - {self.itinerary_name} ({self.date})"

class ItineraryAttraction(models.Model):
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, verbose_name='行程')
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE, verbose_name='景點')
    notes = models.TextField(blank=True, verbose_name='備註')
    visit_time = models.TimeField(null=True, blank=True, verbose_name='參觀時間')
    duration_minutes = models.PositiveIntegerField(default=120, verbose_name='預計停留時間(分鐘)')
    
    class Meta:
        verbose_name = '行程景點'
        verbose_name_plural = '行程景點'
    
    def __str__(self):
        time_str = f" ({self.visit_time.strftime('%H:%M')})" if self.visit_time else ""
        return f"{self.itinerary.itinerary_name} - {self.attraction.name}{time_str}"

class FavoriteAttraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='使用者')
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE, verbose_name='景點')
    
    class Meta:
        unique_together = ['user', 'attraction']
        verbose_name = '收藏景點'
        verbose_name_plural = '收藏景點'
    
    def __str__(self):
        return f"{self.user.username} 收藏 {self.attraction.name}"