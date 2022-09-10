from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage, EmptyPage
from django.urls import reverse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect


# urls
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


# mixins
class HtmxRedirectorMixin:
    """
        Redirect view to use htmx_template instead of template_name if request comes from htmx

        OPTIONAL INFERIOR/CHILD CLASS ATTRIBUTES:
        >> htmx_only -> if child class implement this and has value of 1/True then non htmx request will return 403 error,
                        otherwise non htmx request will return with original 'template_name'
        >> htmx_redirector_msg:str -> Error message to be display on 403 page error

        REQUIRED INFERIOR/CHILD CLASS ATTRIBUTES (child class should implement this!):
        >> htmx_template:str -> htmx template to be use if request is htmx
    """
    def dispatch(self, request, *args, **kwargs):
        if self.template_name is None: self.template_name = type(self).htmx_template
        if self.request.htmx:
            self.template_name = type(self).htmx_template
        else:
            if hasattr(type(self), 'htmx_only') and type(self).htmx_only:
                if hasattr(type(self), 'htmx_redirector_msg'): err_msg = type(self).htmx_redirector_msg
                else: err_msg = "This page should be requested from htmx!"
                return redirect("cover:error403", msg=err_msg)
        return super().dispatch(request, *args, **kwargs)

    # def get(self, request, *args, **kwargs):
    #     if self.request.htmx:
    #         self.template_name = type(self).htmx_template
    #     else:
    #         if hasattr(type(self), 'htmx_only') and type(self).htmx_only:
    #             if hasattr(type(self), 'htmx_redirector_msg'):
    #                 err_msg = type(self).htmx_redirector_msg
    #             else:
    #                 err_msg = "This page should be requested from htmx!"
    #             return redirect("cover:error403", msg=err_msg)
    #     return super().get(request, *args, **kwargs)
    
    # def post(self, *args, **kwargs):
    #     if self.template_name is None: self.template_name = type(self).htmx_template
    #     return super().post(*args, **kwargs)


class AllowedGroupsMixin:
    """ 
        Checks if current logged user groups contains all groups defined in 'allowed_groups' field
        If current logged user have all the permission then user passed, otherwise return error 403
        This mixin do a verification .

        OPTIONAL INFERIOR/CHILD CLASS ATTRIBUTES:
        >> groups_permission_error:dict -> {'title':'Error Title', 'head':'Error Head', 'msg','Error Message'}

        REQUIRED INFERIOR/CHILD CLASS ATTRIBUTES (child class should implement this!):
        >> allowed_groups:tuple|list|set -> iterator contains groups to be allowed
    """

    def dispatch(self, request, *args, **kwargs):
        for group in type(self).allowed_groups:
            if ingroup:= self.request.user.groups.filter(name=group).exists(): break
        if not ingroup:
            htmx_err = {"title":"Forbidden", "head":"Forbidden", "msg":"You dont have permission to access or modify data."}
            if hasattr(type(self), 'groups_permission_error'): htmx_err = type(self).groups_permission_error
            if self.request.htmx:
                if "modal" in self.request.htmx_target.lower():
                    return render(self.request, template_name="errors/htmx_modal_err.html", context=htmx_err)
                else:
                    return htmx_redirect(HttpResponse(status=403), reverse('cover:error403', kwargs={'msg':htmx_err["msg"]}))
            return redirect('cover:error403', msg=htmx_err['msg'])
        return super().dispatch(request, *args, **kwargs)
        # return super().get(request, *args, **kwargs)

    # def get(self, request, *args, **kwargs):
        for group in type(self).allowed_groups:
            if ingroup:= self.request.user.groups.filter(name=group).exists(): break
        if not ingroup:
            htmx_err = {"title":"Forbidden", "head":"Forbidden", "msg":"You dont have permission to access or modify data."}
            if hasattr(type(self), 'groups_permission_error'): htmx_err = type(self).groups_permission_error
            if self.request.htmx:
                if "modal" in self.request.htmx_target.lower():
                    return render(self.request, template_name="errors/htmx_modal_err.html", context=htmx_err)
                else:
                    return htmx_redirect(HttpResponse(status=403), reverse('cover:error403', kwargs={'msg':htmx_err["msg"]}))
            return redirect('cover:error403', msg=htmx_err['msg'])
        return super().get(request, *args, **kwargs)
    
    # def post(self, *args, **kwargs): 
        for group in type(self).allowed_groups:
            if ingroup:= self.request.user.groups.filter(name=group).exists(): break
        if not ingroup:
            htmx_err = {"title":"Forbidden", "head":"Forbidden", "msg":"You dont have permission to access or modify data."}
            if hasattr(type(self), 'groups_permission_error'): htmx_err = type(self).groups_permission_error
            if self.request.htmx:
                if "modal" in self.request.htmx_target.lower():
                    return render(self.request, template_name="errors/htmx_modal_err.html", context=htmx_err)
                else:
                    return htmx_redirect(HttpResponse(status=403), reverse('cover:error403', kwargs={'msg':htmx_err["msg"]}))
            return redirect('cover:error403', msg=htmx_err['msg'])
        return super().post(*args, **kwargs)


class NoCompanyMixin:
    def dispatch(self, request, *args, **kwargs):
        htmx_err = {"title":"Forbidden", "head":"Forbidden"}
        if comp:=self.request.user.profile.company:
            htmx_err["msg"] = f"You already have a company ({comp}). This request can only be perform when you have no company."
            if self.request.htmx:
                if "modal" in self.request.htmx_target.lower():
                    return render(self.request, template_name="errors/htmx_modal_err.html", context=htmx_err)
                else:
                    return htmx_redirect(HttpResponse(status=403), reverse('cover:error403', kwargs={'msg':htmx_err["msg"]}))
            return redirect('cover:error403', msg=htmx_err["msg"])
        return super().dispatch(request, *args, **kwargs)


class HaveCompanyMixin:
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.profile.company:
            return super().dispatch(request, *args, **kwargs)
        else:
            htmx_err = {"title":"Forbidden", "head":"Forbidden"}
            htmx_err["msg"] = f"You dont have company yet. This request can only be perform if you have a company."
            if self.request.htmx:
                if "modal" in self.request.htmx_target.lower():
                    return render(self.request, template_name="errors/htmx_modal_err.html", context=htmx_err)
                else:
                    return htmx_redirect(HttpResponse(status=403), reverse('cover:error403', kwargs={'msg':htmx_err["msg"]}))
        return redirect('cover:error403', msg=htmx_err["msg"])


class HaveAndMyCompanyMixin:
    """
        Return error if current logged user have no company or have company but trying to access other company
    """
    def dispatch(self, request, *args, **kwargs):
        my_comp = self.request.user.profile.company
        view_obj = self.get_object() 
        # view_obj is gathered from generic.UpdateView() is not comes from database
        # that's why 'my_comp is view_obj' will always return False
        # so instead of using 'is', use '==' sign to check equallity.
        htmx_err = {"title":"Forbidden", "head":"Forbidden"}
        htmx_err["msg"] = f"You dont have company yet. This request can only be perform if you have a company."
        if self.request.user.profile.company:
            if my_comp != view_obj: 
                htmx_err["msg"] = f"Your company is {my_comp}, but you are trying to access {view_obj} which is not yours."
            else: return super().dispatch(request, *args, **kwargs)
        if self.request.htmx:
            if "modal" in self.request.htmx_target.lower():
                return render(self.request, template_name="errors/htmx_modal_err.html", context=htmx_err)
            else:
                return htmx_redirect(HttpResponse(status=403), reverse('cover:error403', kwargs={'msg':htmx_err["msg"]}))
        return redirect('cover:error403', msg=htmx_err["msg"])


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


# others
def paginate(page, querySet:object, paginateBy:int=5):
    paginator = Paginator(querySet, paginateBy)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger or InvalidPage:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj

class DEFPATH():
    def __init__(self, base:str): self.base = base
    def __truediv__(self, other:str): return self.base + "/" + other 

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