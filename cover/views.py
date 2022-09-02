from django.http import HttpResponse
from django.shortcuts import render, redirect
from . import data as dt


def get_homepage_content(context:dict={}):
    context['hero'] = dt.hero()
    context['about'] = dt.about()
    context['stats'] = dt.stat_card(4)
    context['services'] = dt.service_card(6)
    context['features'] = dt.feature_card(6)
    context['blogs'] = dt.blog_card(12)
    return context

def homepage(request):
    ctx = get_homepage_content()
    return render(request, template_name="apps/cover/index.html", context=ctx)

def login_required(request):
    next_url = request.GET['next']
    if request.user.is_authenticated and next_url:
        return redirect(next_url) 
    msg = f"You have to login to be able to access '{next_url}'"
    ctx = {}
    ctx['page_title'] = 'Login required'
    ctx['require_login'] = True
    ctx['alert_message'] = msg
    ctx = get_homepage_content(ctx)
    return render(request, template_name="apps/cover/index.html", context=ctx)

def htmx_modal_error(request):
    queries = request.GET.get('err_info') or {'title':'Error', 'head':'An error has occured!', 'msg':'Unknown error'}
    ctx = {}
    ctx["error"] = queries
    return render(request, template_name="errors/htmx_modal_err.html", context=ctx)

def error_forbidden(request):
    return render(request, template_name="errors/403.html")