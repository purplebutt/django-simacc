from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.db.models import Q, F
from django.urls.base import reverse_lazy
from ..models import COA, COH
from ..html.table import COATable
from ..myforms.coa import COACreateForm, COAUpdateForm
from ._funcs import f_form_valid, f_test_func, f_get_list_context_data, f_get_context_data, f_standard_context, f_search
from cover.utils import DEFPATH, paginate, htmx_redirect, HtmxRedirectorMixin, AllowedGroupsMixin
from cover.decorators import htmx_only, have_company_and_approved
from cover import data


DP = DEFPATH('apps/accounting/_shared')
PAGE_TITLE = "Chart Of Account"


class COACreateView(UserPassesTestMixin, AllowedGroupsMixin, HtmxRedirectorMixin, generic.CreateView):
    model = COA
    page_title = PAGE_TITLE
    htmx_template = DP / 'create.html'
    htmx_only = True
    form_class = COACreateForm
    success_url = reverse_lazy("accounting:coa_list")
    allowed_groups = ('accounting_staff',)
    form_valid = f_form_valid
    get_context_data = f_get_context_data
    test_func = f_test_func
    # post = f_post
    # get = f_get


class COADetailView(UserPassesTestMixin, AllowedGroupsMixin, HtmxRedirectorMixin, generic.DetailView):
    model = COA
    page_title = PAGE_TITLE
    htmx_template = DP / 'detail.html'
    htmx_only = True
    allowed_groups = ('accounting_viewer','accounting_staff')
    test_func = f_test_func


class COAUpdateView(UserPassesTestMixin, AllowedGroupsMixin, HtmxRedirectorMixin, generic.UpdateView):
    model = COA
    page_title = PAGE_TITLE
    htmx_template = DP / 'update.html'
    htmx_only = True
    form_class = COAUpdateForm
    success_url = reverse_lazy("accounting:coa_list") 
    allowed_groups = ('accounting_staff',)
    form_valid = f_form_valid
    get_context_data = f_get_context_data
    test_func = f_test_func


class COAListView(UserPassesTestMixin, AllowedGroupsMixin, HtmxRedirectorMixin, generic.ListView):
    model = COA
    table = COATable
    table_fields = ('number', 'name', 'normal', 'is_cashflow', 'header', 'is_active')
    table_header = ('Code', 'Account Name', 'NB', 'CF', 'Header', 'Active')
    context_object_name = 'objects'
    table_object_name = 'table_obj'
    side_menu_group = 'master'
    page_title = PAGE_TITLE
    allowed_groups = ('accounting_viewer','accounting_staff')
    template_name = DP / 'no_htmx/list.html'
    htmx_template = DP / 'list.html'
    test_func = f_test_func
    get_context_data = f_get_list_context_data

    @classmethod
    def get_table_filters(cls):
        return {
            'header': sorted(set(map(lambda i: i.header.name, cls.model.objects.all()))),
            'normal': cls.model._normal_balance,
            'is_cashflow': [("true", "Yes"), ("false", "No")],
            'is_active': [("true", "Yes"), ("false", "No")]
        }

    def filter_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if len(self.request.GET) > 0:
            for k, v in self.request.GET.items():
                if k == "header":
                    header_id = COH.objects.get(name__iexact=v)
                    context[type(self).context_object_name] = context[type(self).context_object_name].filter(**{k:header_id})
                elif k == "normal":
                    context[type(self).context_object_name] = context[type(self).context_object_name].filter(**{k:v[:1].lower()})
                elif k == "is_active" or k == "is_cashflow":
                    x = True if v == "true" else False
                    context[type(self).context_object_name] = context[type(self).context_object_name].filter(**{k:x})
        return context


@login_required
@have_company_and_approved
@htmx_only()
def search(request):
    model = COA
    table = COATable
    page_title = PAGE_TITLE
    template_name = DP/"list_search.html"
    table_fields = ('number', 'name', 'normal', 'is_cashflow', 'header', 'is_active')
    header_text = ('Code', 'Account Name', 'NB', 'CF', 'Header', 'Active')
    table_filters = COAListView.get_table_filters()

    search_key = request.GET.get('search_key') or ""

    if not search_key.isnumeric(): filter_q = Q(name__icontains=search_key)
    else: filter_q = Q(number__contains=search_key)

    response = f_search(request, model=model, filter_q=filter_q, table=table, table_filters=table_filters, 
                        table_fields=table_fields, header_text=header_text, template_name=template_name, page_title=page_title)
    return response
