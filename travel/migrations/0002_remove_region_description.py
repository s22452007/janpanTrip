# Generated by Django 5.2.1 on 2025-05-28 18:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='region',
            name='description',
        ),
    ]
