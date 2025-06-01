from django import template
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """從字典中獲取指定鍵的值"""
    return dictionary.get(key)

@register.filter
def add_minutes(time_obj, minutes):
    """給時間對象添加分鐘數"""
    if not time_obj or not minutes:
        return time_obj
    
    # 將時間轉換為 datetime 對象進行計算
    today = datetime.today().date()
    dt = datetime.combine(today, time_obj)
    new_dt = dt + timedelta(minutes=minutes)
    return new_dt.time()