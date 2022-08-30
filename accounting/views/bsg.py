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
from ..forms import BSGUpdateForm, BSGCreateForm
from ._funcs import f_form_valid, f_test_func, f_get_context_data, f_post, f_get, f_standard_context, f_search
from cover.utils import DEFPATH, paginate
from cover import data


DP = DEFPATH('apps/accounting/_shared')
PAGE_TITLE = "Business Segment"


class BSGCreateView(UserPassesTestMixin, generic.CreateView):
    model = BSG
    page_title = PAGE_TITLE
    template_name = DP / 'create.html'
    form_class = BSGCreateForm
    success_url = reverse_lazy(f"accounting:{model.__name__.lower()}_list")
    allowed_group = 'accounting_admin'
    form_valid = f_form_valid
    get_context_data = f_get_context_data
    post = f_post
    get = f_get
    test_func = f_test_func


class BSGUpdateView(UserPassesTestMixin, generic.UpdateView):
    model = BSG
    page_title = PAGE_TITLE
    template_name = DP / 'update.html'
    form_class = BSGUpdateForm
    success_url = reverse_lazy(f"accounting:{model.__name__.lower()}_list") 
    allowed_group = 'accounting_admin'
    form_valid = f_form_valid
    get_context_data = f_get_context_data
    post = f_post
    test_func = f_test_func


class BSGListView(UserPassesTestMixin, generic.ListView):
    model = BSG
    table = BSGTable
    table_fields = ('number', 'name', 'group', 'is_active')
    table_header = ('Code', 'Business', 'Type', 'Active')
    context_object_name = 'objects'
    table_object_name = 'table_obj'
    template_name = DP / 'regular/list.html'
    htmx_template = DP / 'list.html'
    page_title = PAGE_TITLE
    test_func = f_test_func
    get = f_get
    get_context_data = f_get_context_data
    table_filters = {
        'is_active': [("true", "Yes"), ("false", "No")]
    }

    def filter_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context = {type(self).context_object_name:type(self).model.inactives.all()}
        if len(self.request.GET) > 0:
            for k, v in self.request.GET.items():
                if k == "group":
                    context[type(self).context_object_name] = context[type(self).context_object_name].filter(**{k:v.lower()})
                elif k == "is_active":
                    x = True if v == "true" else False
                    context[type(self).context_object_name] = context[type(self).context_object_name].filter(**{k:x})
        return context


@login_required
def search(request):
    model = BSG
    table = BSGTable
    table_fields = ('number', 'name', 'group', 'is_active')
    table_filters = {
        'is_active': [("true", "Yes"), ("false", "No")]
    }
    header_text = ('Code', 'Business', 'Type', 'Active')
    template_name = DP/"list.html"

    search_key = request.POST.get('search_key') or ""

    if not search_key.isnumeric():
        filter_q = Q(name__contains=search_key)
    else:
        filter_q = Q(number__contains=search_key)


    response = f_search(request, model=model, filter_q=filter_q, table=table, table_filters=table_filters, 
                        table_fields=table_fields, header_text=header_text, template_name=template_name)
    return response
