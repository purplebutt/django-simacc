from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage, EmptyPage
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.timezone import datetime, timedelta


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
def _show_mixin_err(self, htmx_err:dict):
    if self.request.htmx:
        if "modal" in self.request.htmx_target.lower():
            return render(self.request, template_name="errors/htmx_modal_err.html", context=htmx_err)
        else:
            return htmx_redirect(HttpResponse(status=403), reverse('cover:error403', kwargs={'msg':htmx_err["msg"]}))
    return redirect('cover:error403', msg=htmx_err['msg'])


class AllowedTodayMixin:
    """
        Allow only data with date <= today, today will be calculated at server time (utc-0) with offset to user.company.config.time_zone
        this mixin will read date fields on the object. If object didn't have date fields or the date fields is not contains date/datetime data format
        then this mixin will fail and return error. Only use this mixin if you have date field on your model that using date/datetime format

        OPTIONAL SUBCLASS ATTRIBUTES:
        >> errmsg_allowed_today:dict -> {'title':'Error Title', 'head':'Error Head', 'msg','Error Message'}
    """

    def post(self, request, *args, **kwargs):
        obj_date = self.request.POST.get("date")
        if len(obj_date) > 0:
            user = self.request.user
            tz = user.profile.company.config.setdefault("time_zone", [0])[0]
            obj_date = datetime.fromisoformat(obj_date).date()
            today = timezone.now() + timedelta(hours=int(tz))   # convert server datetime to client datetime
            today = today.date()
            if obj_date > today: 
                form = self.form_class(self.request.POST)
                # super().form_invalid() didn't create the self.object instance
                # and required self.object instance to work properly
                self.object = type(self).model()
                form.add_error('date', f"Requires value < {today}")
                return super().form_invalid(form, *args, **kwargs)
        return super().post(request, *args, **kwargs)

    # def dispatch(self, request, *args, **kwargs):
    #     if self.request.method == "POST":
    #         obj_date = self.request.POST.get("date")
    #         if len(obj_date) > 0:
    #             user = self.request.user
    #             tz = user.profile.company.config.setdefault("time_zone", [0])[0]
    #             obj_date = datetime.fromisoformat(obj_date).date()
    #             today = timezone.now() + timedelta(hours=int(tz))   # convert server datetime to client datetime
    #             today = today.date()
    #             if obj_date > today: 
    #                 htmx_err = {"title":"Forbidden", "head":"Forbidden", "msg":"Invalid date, date should <= today."}
    #                 if hasattr(type(self), "errmsg_allowed_today"): htmx_err = type(self).errmsg_allowed_today
    #                 return _show_mixin_err(self, htmx_err)
    #     return super().dispatch(request, *args, **kwargs)


class AllowedOpenPeriodMixin:
    """
        Allow only data with date on open accounting period, otherwise return error

        OPTIONAL SUBCLASS ATTRIBUTES:
        >> errmsg_allowed_open_period:dict -> {'title':'Error Title', 'head':'Error Head', 'msg','Error Message'}
    """
    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if self.request.method == "POST":
            op_start = user.profile.company.get_current_period_start()
            op_end = user.profile.company.get_current_period_end()
            obj_date = self.request.POST.get("date")
            obj_date = obj_date.date() if isinstance(obj_date, "datetime") else obj_date
            if not (obj_date >= op_start and obj_date <= op_end): 
                htmx_err = {"title":"Forbidden", "head":"Forbidden", "msg":"Invalid date. Date should on current open accounting period."}
                if hasattr(type(self), "errmsg_allowed_open_period"): htmx_err = type(self).errmsg_allowed_open_period
                return _show_mixin_err(self, htmx_err)
        return super().dispatch(request, *args, **kwargs)


class ProtectClosedPeriodMixin:
    """
        Protect data of being deleted or modify when data.date (or data.created if data doesn't have date attribute)
        is <= closed period (closed period is read from user.profile.company.get_closed_period())

        REQUIRED SUBCLASS ATTRIBUTES (child/subclass should implement this):
        >> model > model to be used (model should have 'date' or 'created' attribute)

        OPTIONAL SUBCLASS ATTRIBUTES:
        >> errmsg_protect_closed:dict -> {'title':'Error Title', 'head':'Error Head', 'msg','Error Message'}
    """
    def dispatch(self, request, *args, **kwargs):
        if 'slug' in kwargs: obj = type(self).model.objects.get(slug=kwargs.get('slug'))
        elif 'pk' in kwargs: obj = type(self).model.objects.get(pk=kwargs.get('pk'))
        else: obj = type(self).model.objects.get(id=kwargs.get('id'))

        if hasattr(obj, "date"): obj_date = obj.date
        else: obj_date = obj.created.date()

        closed_period = self.request.user.profile.company.get_closed_period().date()

        if obj_date <= closed_period:
            # Data already on closed period
            htmx_err = {"title":"Forbidden", "head":"Forbidden", "msg":"Accounting period already closed. Can not modify this record."}
            if hasattr(type(self), "errmsg_protect_closed_period"): htmx_err = type(self).errmsg_protect_closed_period
            return _show_mixin_err(self, htmx_err)
        return super().dispatch(request, *args, **kwargs)


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

        REQUIRED INFERIOR/CHILD CLASS ATTRIBUTES (child class should implement this!):
        >> allowed_groups:tuple|list|set -> iterator contains groups to be allowed

        OPTIONAL INFERIOR/CHILD CLASS ATTRIBUTES:
        >> errmsg_allowed_groups:dict -> {'title':'Error Title', 'head':'Error Head', 'msg':'Error Message'}
    """
    def dispatch(self, request, *args, **kwargs):
        for group in type(self).allowed_groups:
            if ingroup:= self.request.user.groups.filter(name=group).exists(): break
        if not ingroup:
            htmx_err = {"title":"Forbidden", "head":"Forbidden", "msg":"You dont have permission to access or modify data."}
            if hasattr(type(self), 'errmsg_allowed_groups'): htmx_err = type(self).errmsg_allowed_groups
            return _show_mixin_err(self, htmx_err)
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
    """
        Return error if current logged user already have company

        OPTIONAL INFERIOR/CHILD CLASS ATTRIBUTES:
        >> errmsg_no_company:dict -> {'title':'Error Title', 'head':'Error Head', 'msg':'Error Message'}
    """
    def dispatch(self, request, *args, **kwargs):
        htmx_err = {"title":"Forbidden", "head":"Forbidden"}
        if comp:=self.request.user.profile.company:
            htmx_err = {"title":"Forbidden", "head":"Forbidden", "msg":"You already have a company, this request require you to have no company."}
            if hasattr(type(self), 'errmsg_no_company'): htmx_err = type(self).errmsg_no_company
            return _show_mixin_err(self, htmx_err)
        return super().dispatch(request, *args, **kwargs)


class HaveCompanyMixin:
    """
        Return error page if current logged user doesn't have company

        OPTIONAL INFERIOR/CHILD CLASS ATTRIBUTES:
        >> errmsg_no_company:dict -> {'title':'Error Title', 'head':'Error Head', 'msg':'Error Message'}
    """
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.profile.company:
            htmx_err = {"title":"Forbidden", "head":"Forbidden", "msg":"You dont have company yet, this request require you to have a company."}
            if hasattr(type(self), 'errmsg_have_company'): htmx_err = type(self).errmsg_have_company
            return _show_mixin_err(self, htmx_err)
        return super().dispatch(request, *args, **kwargs)


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
        return _show_mixin_err(self, htmx_err)


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
