from django.shortcuts import reverse, redirect
from django.http import HttpResponse
from cover.utils import htmx_redirect



def require_groups(*args, **kwargs):
    """
        Checks if current logged in user in groups, if not then return error page
        required keyword args:
            groups:tuple(str) > tuple contains groups to be evaluate
        optional keyword args:
            error_msg:str > optional error message to be display on error page
    """
    def inner_func(func):
        # validate args and kwargs
        gr = args[0] if len(args) > 0 else kwargs.setdefault("groups", None)
        error_msg = kwargs.setdefault("error_msg", None)
        def core_func(*args, **kwargs):
            if gr:
                request, *_ = args
                if error_msg is None: err_msg = f"Only user in groups {gr} are allowed to access this page." 
                else: err_msg = error_msg
                for g in gr:
                    if exist:=request.user.groups.filter(name=g).exists(): 
                        if not exist: break 
                if not exist:
                    # checks if request from htmx, return error page if it's not
                    if request.htmx: return htmx_redirect(HttpResponse(status=403), reverse("cover:error403", kwargs={'msg':err_msg}))
                    return redirect("cover:error403", msg=err_msg) 
            return func(*args, **kwargs)
        return core_func
    return inner_func


def have_company(func, *args, **kwargs):
    def inner_func(*args, **kwargs):
        request, *_ = args
        user_profile = request.user.profile
        err_msg = "Unknown error"
        if not user_profile.company:
            err_msg = 'You currently not registered to any company. This request required you to have a company.'
            if request.htmx: return htmx_redirect(HttpResponse(status=403), reverse("cover:error403", kwargs={'msg':err_msg}))
            return redirect("cover:error403", msg=err_msg) 
        return func(*args, **kwargs)
    return inner_func


def have_company_and_approved(func, *args, **kwargs):
    def inner_func(*args, **kwargs):
        request, *_ = args
        user_profile = request.user.profile
        err_msg = "Unknown error"
        if user_profile.company:
            if user_profile.comp_stat: return func(*args, **kwargs)
            err_msg = f'{user_profile.company.name.title()} admin is not approved you yet as their employees.'
        else:
            err_msg = 'You currently not registered to any company. This request required you to have a company.'
        if request.htmx: return htmx_redirect(HttpResponse(status=403), reverse("cover:error403", kwargs={'msg':err_msg}))
        return redirect("cover:error403", msg=err_msg) 
    return inner_func


def htmx_only_bak(func, *args, **kwargs):
    def inner_func(*args, **kwargs):
        request, *_ = args
        if not request.htmx:
            err_msg = 'Can only be requested from htmx.'
            return redirect("cover:error403", msg=err_msg)
        return func(*args, **kwargs)
    return inner_func


def htmx_only(*args, **kwargs):
    """
        Checks if request come from htmx, if it's not then return 403 error page
        This function decorator accept keyword argument
        valid keyword args:
            error_msg:str > set custom error message to be display on error page.
    """
    def inner_func(func):
        # validate args and kwargs
        err_msg = args[0] if len(args) > 0 else kwargs.setdefault("error_msg", "Can only be requested with htmx.")
        def core_func(*args, **kwargs):
            # checks if request from htmx, return error page if it's not
            request, *_ = args
            if not request.htmx: return redirect("cover:error403", msg=err_msg)
            return func(*args, **kwargs)
        return core_func
    return inner_func


def post_only(func, *args, **kwargs):
    def inner_func(*args, **kwargs):
        request, *_ = args      # unpacked first item from args (args is a tuple) and ignore or put others items on '_'
        if request.method != 'POST':
            err_msg='Only POST method allowed for this request.'
            if request.htmx: return htmx_redirect(HttpResponse(status=403), reverse("cover:error403", kwargs={'msg':err_msg}))
            return redirect("cover:error403", msg=err_msg)
        return func(*args, **kwargs)
    return inner_func


def get_only(func, *args, **kwargs):
    def inner_func(*args, **kwargs):
        request, *_ = args      # unpacked first item from args (args is a tuple) and ignore or put others items on '_'
        if request.method != 'GET':
            err_msg='Only GET method allowed for this request.'
            if request.htmx: return htmx_redirect(HttpResponse(status=403), reverse("cover:error403", kwargs={'msg':err_msg}))
            return redirect("cover:error403", msg=err_msg)
        return func(*args, **kwargs)
    return inner_func
