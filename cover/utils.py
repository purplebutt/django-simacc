from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage, EmptyPage
from django.urls import reverse
from django.http.response import HttpResponse
from django.shortcuts import redirect


def paginate(page, querySet:object, paginateBy:int=5):
    paginator = Paginator(querySet, paginateBy)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger or InvalidPage:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj


def url_query_parse(url:str, keys:tuple=None, **kwargs):
    base = url if url.startswith('/') else reverse(url)
    if len(kwargs) > 0: base+="?"
    start = ""
    if keys is None:
        for k, v in kwargs.items():
            base += start + k + "=" + v
            start = "&"
    else:
        for k, v in kwargs.items():
            if k in keys: 
                base += start + k + "=" + v
                start = "&"
    return base

def _extract_url_query(url:str, ignore_query:tuple=(), **new_query):
    if "?" in url:
        query = {}
        q = url.split("?")[1].split("&")
        for i in q:
            k = i.split("=")[0]
            if k not in new_query and k not in ignore_query:
                v = i.split("=")[1]
                query[k]=v
        for k, v in new_query.items():
            query[k] = v
        return query
    else:
        return new_query

def url_query_add(url:str, **kwargs):
    base = url if url.startswith('/') else reverse(url)
    base = base.split("?")[0] if "?" in base else base
    query = _extract_url_query(url, **kwargs)
    start = "?"
    for k, v in query.items():
        base += start + k + "=" + v
        start = "&"
    return base

# htmx response header
def htmx_redirect(response, to:str):
    """ 
    cause htmx to do a client-side redirect to a new location
    """
    response.headers['HX-Redirect'] = to
    return response

def htmx_refresh(response):
    """ 
    cause the client side to do a a full refresh of the page
    """
    response.headers['HX-Refresh'] = "true"
    return response

def htmx_retarget(response, new_target:str):
    """ 
    change the target html element
    new_target should be a CSS selector
    example "body.div#target" > target div element inside body element with id='target'
    """
    response.headers['HX-Retarget'] = new_target
    return response

def htmx_trigger(response, target_event:str):
    """ 
    causes htmx to trigger other event on client side
    """
    response.headers['HX-Trigger'] = target_event
    return response

def htmx_trigger_af_settle(response, target_event:str):
    """ 
    causes htmx to trigger other event on client side after settling
    """
    response.headers['HX-Trigger-After-Settle'] = target_event
    return response

def htmx_trigger_af_swap(response, target_event:str):
    """ 
    causes htmx to trigger other event on client side after swapping
    """
    response.headers['HX-Trigger-After-Swap'] = target_event
    return response

class DEFPATH():
    def __init__(self, base:str):
        self.base = base
    def __truediv__(self, other:str):
        return self.base + "/" + other 

def auto_number_generator(incrementor:int=1)->int:
    from datetime import datetime
    d = datetime.now().strftime("%y%m%d") + "{:0>4}".format(incrementor)
    return int(d)

def save_url_query(url_query:str):
    #   url contains "/" character, but this character
    #   will cause an error when use as argument on url path 
    #   so we can convert "/" to other character and revert it back later
    if "/" in url_query:
        return url_query.replace("/", "%~%")
    else:
        return url_query.replace("%~%", "/")

def not_implemented_yet(request, reason:str="this feature is not implemented yet"):
    if request.htmx:
        return htmx_redirect(HttpResponse(status=403), reverse("cover:error403", kwargs={'msg':reason.title()}))
    return redirect("cover:error403", msg=reason.title())