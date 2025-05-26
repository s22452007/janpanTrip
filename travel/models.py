from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class UserProfile(models.Model):
    TRAVEL_TYPE_CHOICES = [
        ('culture', '文化體驗'),
        ('nature', '自然風光'),
        ('food', '美食探索'),
        ('shopping', '購物娛樂'),
    ]
    
    BUDGET_CHOICES = [
        ('budget', '經濟型'),
        ('mid', '中等型'),
        ('luxury', '高端型'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    travel_type = models.CharField(max_length=20, choices=TRAVEL_TYPE_CHOICES, default='culture')
    budget_range = models.CharField(max_length=20, choices=BUDGET_CHOICES, default='mid')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} 的個人資料"

class Region(models.Model):
    name = models.CharField(max_length=50, unique=True)
    name_en = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class AttractionType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return self.name

class Attraction(models.Model):
    name = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    attraction_type = models.ForeignKey(AttractionType, on_delete=models.CASCADE)
    address = models.CharField(max_length=300)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0
    )
    image = models.ImageField(upload_to='attractions/', blank=True, null=True)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    opening_hours = models.TextField(blank=True)
    ticket_price = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-rating', 'name']
    
    def __str__(self):
        return self.name
    
    @property
    def rating_stars(self):
        return '★' * int(self.rating) + '☆' * (5 - int(self.rating))

class Trip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    attractions = models.ManyToManyField(Attraction, through='TripAttraction')
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days + 1

class TripAttraction(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE)
    day_number = models.PositiveIntegerField()
    order = models.PositiveIntegerField()
    visit_time = models.TimeField(blank=True, null=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['day_number', 'order']
        unique_together = ['trip', 'attraction']
    
    def __str__(self):
        return f"{self.trip.title} - Day {self.day_number}: {self.attraction.name}"

class FavoriteTrip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'trip']
    
    def __str__(self):
        return f"{self.user.username} 喜歡 {self.trip.title}"