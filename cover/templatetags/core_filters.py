from django import template
from django.urls import reverse
from django.contrib.auth.models import Group


register = template.Library()


@register.filter
def is_gt(value, arg): return value > arg

@register.filter
def is_lt(value, arg): return value < arg

@register.filter
def is_eq(value:str|int, arg:str|int): 
    return str(value) == str(arg)

@register.filter
def is_na(value): return value == None

@register.filter
def getval(data, criteria:str|int):
    return data.get(criteria)

@register.filter
def iftrue(condition, value:str|int=None):
    """
    return condition if condition is true, otherwise return value
    """
    return condition if bool(condition) else value

@register.filter
def concat(value:str, other:str):
    return value + other

@register.filter
def getval(obj, index:int=0):
    if isinstance(obj, dict):
        return obj.popitem()[1]
    elif isinstance(obj, tuple):
        return obj[index]
    else:
        return obj

@register.filter
def getvalbyfield(obj, field:str):
    return getattr(obj, field)

@register.filter
def toset(iterable):
    return set(iterable)

@register.filter
def to_media_url(url):
    return '/media/' + str(url)

@register.filter
def get_file_name(value):
    return str(value).split("/")[-1:].pop()