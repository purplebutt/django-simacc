from django import template
from django.urls import reverse
from accounting.models import *


register = template.Library()


@register.inclusion_tag("utc_diff.html")
def utc_diff(class_: str=None):
    return {'class_': class_}

@register.inclusion_tag("utc_diff_title.html")
def utc_diff_title(target:str="input[type='datetime']", class_: str=None):
    return {'target':target, 'class_':class_}

@register.inclusion_tag('profile_pic.html')
def profile_pic(user, width: int = 32, height: int = 32, tooltip: str = None):
    tooltip = "" if tooltip is None else tooltip
    return {'user': user, 'width': width, 'height': height, 'tooltip': tooltip}

@register.inclusion_tag('brand.html')
def brand(is_link: bool=True, size: int=50, class_:"str"="", link_to="/"):
    return {'height': size, 'class_':class_, 'is_link': is_link, 'link_to': link_to}

@register.inclusion_tag('logo.html')
def logo(is_link: bool=True, size: int=30, class_:"str"="", link_to="/"):
    return {'height': size, 'class_':class_, 'is_link': is_link, 'link_to': link_to}

@register.inclusion_tag('scroll_up.html')
def scroll_up(target:str = "hero", class_:str ="scroll-up"):
    return {'target': target, 'class_': class_}

@register.inclusion_tag('notification.html')
def notification(messages, class_: str="container fixed-bottom mb-2"):
    return {'messages':messages, 'class_': class_}

@register.inclusion_tag('paginator.html')
def paginator(page:object, request:object, outerClass: str=None, innerClass: str="pagination mb-0"):
    return {
        'page': page,
        'request': request,
        'outer_class': outerClass,
        'inner_class': innerClass
    }

@register.inclusion_tag('htmx_paginator.html')
def htmx_paginator(swapTarget:str, page:object, request:object, ignore_url_queries:str="", outer_class: str=None, inner_class: str="pagination pagination-sm mb-0"):
    """
        ignore_url_queries -> string with comma separated url key to be ignore. ex -> "id,page,color"
        outer_class  -> defined bootstrap css class on outer element
        inner_class  -> defined bootstrap css class on inner element

        ex:
            {% htmx_paginator 'div#paginator' 'page_obj' request ('sortby', 'sort_mode') 'text-warning' %}
    """
    return {
        'swap_target': swapTarget,
        'page': page,
        'request': request,
        'outer_class': outer_class,
        'inner_class': inner_class,
        'ignore_url_queries': ignore_url_queries
    }

@register.inclusion_tag('form_float.html')
def form_float(forms, space=2, show_file_label:bool=False):
    is_multi = isinstance(forms, list)
    return {
        'forms': forms, 
        'space': space, 
        'is_multi': is_multi, 
        'show_file_label': show_file_label
    }

@register.inclusion_tag('form_float.html')
def form_float_cbleft(forms, space=2, show_file_label:bool=False):
    is_multi = isinstance(forms, list)
    return {
        'forms': forms, 
        'space': space, 
        'is_multi': is_multi, 
        'show_file_label': show_file_label,
        'checkbox_left': True
    }

@register.inclusion_tag('form_float.html')
def form_float_pswrd(forms, space=2, textarea_height="120", show_pswrdbtn:bool=True, show_file_label:bool=False):
    textarea_height = "height: " + textarea_height + "px"
    is_multi = isinstance(forms, list)
    return {
        'forms': forms, 
        'space': space, 
        'is_multi': is_multi, 
        'show_pswrdbtn': show_pswrdbtn,
        'textarea_height': textarea_height,
        'show_file_label': show_file_label
    }

@register.inclusion_tag('form_float.html')
def form_float_filelabel(forms, space=2, textarea_height="120", show_file_label:bool=True):
    textarea_height = "height: " + textarea_height + "px"
    is_multi = isinstance(forms, list)
    return {
        'forms': forms, 
        'space': space, 
        'is_multi': is_multi, 
        'textarea_height': textarea_height,
        'show_file_label': show_file_label
    }


@register.inclusion_tag("page_title.html")
def page_title(title:str="title"):
    return {'title': title}


##! simple tags
def _querydict_to_dict(query_dict, query:str, ignore_queries:tuple):
    d = {}
    for k, v in query_dict.items():
        if k not in ignore_queries:
            d[k] = v
    key, val = query.split('=')
    d[key] = val
    if val == '_none': 
        d.pop(key)
    return d

def _url_query_builder(query_dict:dict, query:str, ignore_queries:tuple=()):
    d = _querydict_to_dict(query_dict, query, ignore_queries)
    result = "?"
    first = ""
    for k, v in d.items():
        result += first + k + "=" + v
        first = "&"
    return result if result != "?" else ""

@register.simple_tag
def url_queryAdd(request, query_key:str, query_val:str, ignore_queries:str=""):
    query = query_key + "=" + str(query_val)
    ignore_q = tuple(ignore_queries.replace(" ", "").split(","))
    return request.path + _url_query_builder(request.GET, query, ignore_q)

@register.simple_tag
def url_query(request, query:str='q=_none'):
    return request.path + _url_query_builder(request.GET, query)

@register.simple_tag
def url_queryGrab(url, request, query_key:str="q", query_val:str="_none"):
    query = query_key + "=" + str(query_val)
    return url + _url_query_builder(request.GET, query)

@register.simple_tag
def url_queryParse(url:str, request, query_key:str="q", query_val:str="_none"):
    query = query_key + "=" + str(query_val)
    return reverse(url) + _url_query_builder(request.GET, query)

@register.simple_tag
def url_parseDict(url_name:str, query:dict):
    """
    Combine url with dictionary, value on dictionary will be added as url query
    Ex:  
        url = url_parseDict("user_list", {"id":1, "gender":"female"})
        url will be "/user/list/?id=1&gender=female"
    """
    q = "?"
    for k, v in query.items():
        q += f"{k}={v}&"
    q = q[:-1]  # remove last char (&)
    return reverse(url_name) + q

@register.simple_tag
def url_fresp(request, **kwargs):
    q = "?"

    for k, v in request.GET.items():
        if k not in kwargs: q += f"{k}={v}&"
    for k, v in kwargs.items(): 
        q += f"{k}={v}&"
    q = q[:-1]  # remove last char (&)
    return request.path + q

@register.simple_tag
def get_qsfield(queryset, **kwargs):
    target = kwargs.get("target") or ""
    value = kwargs.get("value") or ""
    x = list(queryset.values_list("id", target))
    n = tuple(filter(lambda i: i[0]==value, x))
    if len(n) <= 0:
        n = tuple(filter(lambda i: i[1]==value, x))
        if len(n) <= 0: return ""
        return n[0][1]
    else:
        return n[0][1]

@register.simple_tag
def getval_frstr(model_name:str, key:int|str, field:str=None):
    if field == None or field == "": field = "name"
    try:
        model = eval(model_name)
        return getattr(model.actives.get(pk=int(key)), field)
    except:
        return key

@register.simple_tag
def iftf(condition, iftrue:str='true', iffalse:str='false'):
    return iftrue if bool(condition) else iffalse

