from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r'^\d{10}$', message='手機號碼需為 10 碼數字')]
    )
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return self.username  

class TravelPlan(models.Model):
    travel_name = models.CharField("旅程名稱", max_length=100)
    start_date = models.DateField("起始日期")
    end_date = models.DateField("結束日期")
    user_ID = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="使用者編號")

    def __str__(self):
        return f"{self.travel_name} ({self.user_ID.username})"

class Schedule(models.Model):
    travel_ID = models.ForeignKey(TravelPlan, on_delete=models.CASCADE, verbose_name="旅程編號")
    date = models.DateField("日期")
    locations_ID = models.ForeignKey('Location', on_delete=models.CASCADE, verbose_name="景點編號")
    start_time = models.TimeField("起始時間")
    end_time = models.TimeField("結束時間")

    def __str__(self):
        return f"{self.travel_ID.travel_name} - {self.date} - {self.locations_ID.locations_name}"
    
class Location(models.Model):
    locations_name = models.CharField("地點", max_length=100)
    address = models.CharField("地址", max_length=255)
    area = models.CharField("地區", max_length=100)
    type = models.CharField("類型", max_length=100)
    rate = models.DecimalField("評分", max_digits=3, decimal_places=1, validators=[
        MinValueValidator(0.0)
    ])
    image = models.ImageField("圖片", upload_to='locations/', blank=True, null=True)
    clickRate = models.PositiveIntegerField("點擊率", default=0)

    def __str__(self):
        return self.locations_name

    def increase_click(self):
        self.clickRate += 1
        self.save()

