from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """從字典中取得指定鍵的值"""
    if dictionary and key in dictionary:
        return dictionary[key]
    return None