from django.db import models
from django.core.validators import RegexValidator, MinValueValidator

class UserProfile(models.Model):
    name = models.CharField(max_length=50)
    phone = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r'^\d{10}$', message='手機號碼需為 10 碼數字')]
    )
    email = models.EmailField()
    photo = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.name

class TravelPlan(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()  # 格式可在表單輸入時設定 yyyy/mm/dd
    end_date = models.DateField()
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.user.name})"

class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    area = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=3, decimal_places=1, validators=[
        MinValueValidator(0.0)
    ])
    image = models.ImageField(upload_to='locations/', blank=True, null=True)
    clickRate = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    def increase_click(self):
        self.clickRate += 1
        self.save()

class Schedule(models.Model):
    travel_plan = models.ForeignKey(TravelPlan, on_delete=models.CASCADE)
    date = models.DateField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.travel_plan.name} - {self.date} - {self.location.address}"
