# Generated by Django 5.1.3 on 2025-06-02 14:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('attraction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='travel.attraction')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '收藏景點',
                'verbose_name_plural': '收藏景點',
                'unique_together': {('user', 'attraction')},
            },
        ),
        migrations.DeleteModel(
            name='FavoriteAttraction',
        ),
    ]
