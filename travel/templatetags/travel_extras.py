from django import template
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """從字典中獲取指定鍵的值"""
    return dictionary.get(key)

@register.filter
def add_minutes(time_obj, minutes):
    """為時間對象添加分鐘"""
    if time_obj:
        datetime_obj = datetime.combine(datetime.today(), time_obj)
        new_datetime = datetime_obj + timedelta(minutes=minutes)
        return new_datetime.time()
    return None