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
from ..html.table import TBTable
from ._funcs import f_form_valid, f_test_func, f_get_context_data, f_post, f_get, f_standard_context, f_search
from cover.utils import DEFPATH, paginate
from cover import data


DP = DEFPATH('apps/accounting/_shared')
PAGE_TITLE = "Trial Balance"


class TBListView(UserPassesTestMixin, generic.ListView):
    model = COA
    table = TBTable
    table_fields = ('number', 'name', 'normal', 'is_cashflow', 'header', 'debit', 'credit', 'balance', 'is_active')
    table_header = ('Code', 'Account Name', 'NB', 'CF', 'Header', 'Debit', 'Credit', 'Balance', 'Active')
    allowed_groups = ('accounting_viewer',)
    context_object_name = 'objects'
    table_object_name = 'table_obj'
    side_menu_group = 'reports'
    template_name = DP / 'regular/list.html'
    htmx_template = DP / 'list.html'
    page_title = PAGE_TITLE
    test_func = f_test_func
    get = f_get
    get_context_data = f_get_context_data

    @classmethod
    def get_table_filters(cls):
        return {
            'header': sorted(set(map(lambda i: i.header.name, cls.model.objects.all()))),
            'normal': cls.model._normal_balance,
            'is_cashflow': [("true", "Yes"), ("false", "No")],
            'is_active': [("true", "Yes"), ("false", "No")]
        }

    def filter_context_data(self, **kwargs):
        context = {}
        context["search_url"] = reverse_lazy("accounting:report_tb_search")
        context["model_name"] = 'tb'    # model_name should be lowercase
        context[type(self).context_object_name] = type(self).model.trialbalance.all()
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
def tb_search(request):
    model = COA
    table = COATable
    querymanager = 'trialbalance'
    table_fields = ('number', 'name', 'normal', 'is_cashflow', 'header', 'debit', 'credit', 'balance', 'is_active')
    header_text = ('Code', 'Account Name', 'NB', 'CF', 'Header', 'Debit', 'Credit', 'Balance', 'Active')
    table_filters = TBListView.get_table_filters()
    template_name = DP/"list.html"

    search_key = request.POST.get('search_key') or ""

    if not search_key.isnumeric():
        filter_q = Q(name__icontains=search_key)
    else:
        filter_q = Q(number__contains=search_key)


    response = f_search(request, model=model, filter_q=filter_q, table=table, table_filters=table_filters, 
                        table_fields=table_fields, header_text=header_text, template_name=template_name, querymanager=querymanager)
    return response