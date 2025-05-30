# Generated by Django 5.2.1 on 2025-05-28 18:04

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AttractionType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='類型名稱')),
                ('icon', models.CharField(blank=True, max_length=50, verbose_name='圖標')),
            ],
            options={
                'verbose_name': '景點類型',
                'verbose_name_plural': '景點類型',
            },
        ),
        migrations.CreateModel(
            name='Itinerary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('itinerary_name', models.CharField(max_length=200, verbose_name='行程名稱')),
                ('date', models.DateField(verbose_name='日期')),
                ('start_time', models.TimeField(verbose_name='開始時間')),
                ('end_time', models.TimeField(verbose_name='結束時間')),
            ],
            options={
                'verbose_name': '行程',
                'verbose_name_plural': '行程',
                'ordering': ['date', 'start_time'],
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='地區名稱')),
                ('description', models.TextField(blank=True, verbose_name='描述')),
            ],
            options={
                'verbose_name': '地區',
                'verbose_name_plural': '地區',
            },
        ),
        migrations.CreateModel(
            name='Attraction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='景點名稱')),
                ('description', models.TextField(verbose_name='描述')),
                ('address', models.CharField(max_length=300, verbose_name='地址')),
                ('rating', models.DecimalField(decimal_places=2, default=0, max_digits=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)], verbose_name='評分')),
                ('image', models.ImageField(blank=True, null=True, upload_to='attractions/', verbose_name='圖片')),
                ('website', models.URLField(blank=True, verbose_name='官方網站')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='電話')),
                ('opening_hours', models.TextField(blank=True, verbose_name='營業時間')),
                ('features', models.TextField(blank=True, verbose_name='特色')),
                ('attraction_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='travel.attractiontype', verbose_name='景點類型')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='travel.region', verbose_name='地區')),
            ],
            options={
                'verbose_name': '景點',
                'verbose_name_plural': '景點',
                'ordering': ['-rating', 'name'],
            },
        ),
        migrations.CreateModel(
            name='ItineraryAttraction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.TextField(blank=True, verbose_name='備註')),
                ('attraction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='travel.attraction', verbose_name='景點')),
                ('itinerary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='travel.itinerary', verbose_name='行程')),
            ],
            options={
                'verbose_name': '行程景點',
                'verbose_name_plural': '行程景點',
                'unique_together': {('itinerary', 'attraction')},
            },
        ),
        migrations.AddField(
            model_name='itinerary',
            name='attractions',
            field=models.ManyToManyField(through='travel.ItineraryAttraction', to='travel.attraction', verbose_name='景點'),
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trip_name', models.CharField(max_length=200, verbose_name='旅程名稱')),
                ('description', models.TextField(blank=True, verbose_name='描述')),
                ('start_time', models.DateTimeField(verbose_name='開始時間')),
                ('end_time', models.DateTimeField(verbose_name='結束時間')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='使用者')),
            ],
            options={
                'verbose_name': '旅程',
                'verbose_name_plural': '旅程',
                'ordering': ['-start_time'],
            },
        ),
        migrations.AddField(
            model_name='itinerary',
            name='trip',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='travel.trip', verbose_name='旅程'),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/', verbose_name='頭像')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='電話')),
                ('permission', models.CharField(choices=[('user', '使用者'), ('admin', '管理員')], default='user', max_length=20, verbose_name='權限')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='使用者')),
            ],
            options={
                'verbose_name': '使用者資料',
                'verbose_name_plural': '使用者資料',
            },
        ),
        migrations.CreateModel(
            name='FavoriteAttraction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attraction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='travel.attraction', verbose_name='景點')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='使用者')),
            ],
            options={
                'verbose_name': '收藏景點',
                'verbose_name_plural': '收藏景點',
                'unique_together': {('user', 'attraction')},
            },
        ),
    ]
