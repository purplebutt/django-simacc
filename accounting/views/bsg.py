from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.db.models import Q, F
from django.urls.base import reverse_lazy
from ..models import BSG
from ..html.table import BSGTable
from ..myforms.bsg import BSGUpdateForm, BSGCreateForm
from ._funcs import f_form_valid, f_test_func, f_get_list_context_data, f_get_context_data, f_post, f_get, f_standard_context, f_search
from cover.utils import DEFPATH, paginate, HtmxRedirectorMixin, AllowedGroupsMixin
from cover import data


DP = DEFPATH('apps/accounting/_shared')
PAGE_TITLE = "Business Segment"


class BSGCreateView(AllowedGroupsMixin, HtmxRedirectorMixin, UserPassesTestMixin, generic.CreateView):
    model = BSG
    page_title = PAGE_TITLE
    # template_name = DP / 'create.html'
    htmx_template = DP / 'create.html'
    htmx_only = True
    groups_permission_error = {'title':'error 403, Forbidden', 'head':'Forbidden', 'msg':'Required accounting_staff permission to add new Business Segment.'}
    htmx_redirector_msg = "This page should be requested by htmx!"
    form_class = BSGCreateForm
    success_url = reverse_lazy(f"accounting:{model.__name__.lower()}_list")
    allowed_groups = ('accounting_staff',)
    form_valid = f_form_valid
    get_context_data = f_get_context_data
    test_func = f_test_func
    # post = f_post
    # get = f_get


class BSGDetailView(AllowedGroupsMixin, HtmxRedirectorMixin, UserPassesTestMixin, generic.DetailView):
    model = BSG
    page_title = PAGE_TITLE
    htmx_template = DP / 'detail.html'
    htmx_only = True
    allowed_groups = ('accounting_viewer',)
    get_context_data = f_get_context_data
    test_func = f_test_func
    # post = f_post


class BSGUpdateView(AllowedGroupsMixin, HtmxRedirectorMixin, UserPassesTestMixin, generic.UpdateView):
    model = BSG
    page_title = PAGE_TITLE
    htmx_template = DP / 'update.html'
    htmx_only = True
    form_class = BSGUpdateForm
    success_url = reverse_lazy(f"accounting:{model.__name__.lower()}_list") 
    allowed_groups = ('accounting_staff',)
    form_valid = f_form_valid
    get_context_data = f_get_context_data
    test_func = f_test_func
    # post = f_post


class BSGListView(AllowedGroupsMixin, HtmxRedirectorMixin, UserPassesTestMixin, generic.ListView):
    model = BSG
    table = BSGTable
    table_fields = ('number', 'name', 'group', 'is_active')
    table_header = ('Code', 'Business', 'Type', 'Active')
    template_name = DP / 'no_htmx/list.html'
    htmx_template = DP / 'list.html'
    allowed_groups = ('accounting_viewer',)
    context_object_name = 'objects'
    table_object_name = 'table_obj'
    side_menu_group = 'master'
    page_title = PAGE_TITLE
    test_func = f_test_func
    get_context_data = f_get_list_context_data
    # get_context_data = f_get_context_data
    # get = f_get

    @classmethod
    def get_table_filters(cls):
        return { 
            'is_active': [("true", "Yes"), ("false", "No")],
            'group': sorted(set(map(lambda i: i[0], BSG.actives.values_list('group'))))
        }

    def filter_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if len(self.request.GET) > 0:
            for k, v in self.request.GET.items():
                if k == "group":
                    context[type(self).context_object_name] = context[type(self).context_object_name].filter(**{k:v.upper()})
                elif k == "is_active":
                    x = True if v == "true" else False
                    context[type(self).context_object_name] = context[type(self).context_object_name].filter(**{k:x})
        return context


@login_required
def search(request):
    # checks user permission
    # return Response Error 403 if user dont have permission
    if not f_test_func(request):
        if request.htmx:
            err_msg = f"You are not authorized to view or modify data."
            return htmx_redirect(HttpResponse(403), reverse_lazy("cover:error403", kwargs={'msg':err_msg}))
        return redirect("cover:error403", msg=err_msg)

    model = BSG
    table = BSGTable
    page_title = PAGE_TITLE
    table_fields = ('number', 'name', 'group', 'is_active')
    header_text = ('Code', 'Business', 'Type', 'Active')
    table_filters = BSGListView.get_table_filters()
    template_name = DP/"list_search.html"

    search_key = request.GET.get('search_key') or ""

    if not search_key.isnumeric():
        filter_q = Q(name__icontains=search_key)
    else:
        filter_q = Q(number__contains=search_key)


    response = f_search(request, model=model, filter_q=filter_q, table=table, table_filters=table_filters, 
                        table_fields=table_fields, header_text=header_text, template_name=template_name, page_title=page_title)
    return response
