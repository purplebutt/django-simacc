from datetime import date
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
from ._funcs import f_form_valid, f_test_func, f_get_list_context_data, f_get_context_data, f_standard_context, f_search
from cover.utils import DEFPATH, paginate, HtmxRedirectorMixin, AllowedGroupsMixin
from cover.decorators import htmx_only, have_company_and_approved
from cover import data


DP = DEFPATH('apps/accounting/_shared')
PAGE_TITLE = "Trial Balance"


class TBListView(UserPassesTestMixin, AllowedGroupsMixin, HtmxRedirectorMixin, generic.ListView):
    model = COA
    table = TBTable
    table_fields = ('number', 'name', 'normal', 'is_cashflow', 'header', 'previous', 'debit', 'credit', 'balance')
    table_header = ('Code', 'Account Name', 'NB', 'CF', 'Header', 'Previous', 'Debit', 'Credit', 'Balance')
    allowed_groups = ('accounting_viewer',)
    context_object_name = 'objects'
    table_object_name = 'table_obj'
    side_menu_group = 'reports'
    template_name = DP / 'no_htmx/list.html'
    htmx_template = DP / 'list.html'
    page_title = PAGE_TITLE
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
        context = {}
        context["search_url"] = reverse_lazy("accounting:report_tb_search")
        context["model_name"] = 'tb'    # model_name should be lowercase
        start_date = self.request.GET.get('period_from')
        end_date = self.request.GET.get('period_to')
        if start_date and end_date:
            context[type(self).context_object_name] = \
                type(self).model.get_tb_at(date.fromisoformat(start_date), date.fromisoformat(end_date)).all()
            context["reporting_period"] = (start_date, end_date)    # add reporting period to context, so it can be consume on view template
        else:
            # different fields between original fields and report fields
            field_diff = ('previous',)
            header_diff = ('Previous',)
            # using filter to remove non report fields from type(self).table_fields and type(self).table_header
            self.table_fields = tuple(filter(lambda i: i not in field_diff, type(self).table_fields))
            self.table_header = tuple(filter(lambda i: i not in header_diff, type(self).table_header))
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
@have_company_and_approved
@htmx_only()
def tb_search(request):
    model = COA
    table = TBTable
    page_title = PAGE_TITLE
    template_name = DP/"list_search.html"
    querymanager = 'trialbalance'
    table_fields = ('number', 'name', 'normal', 'is_cashflow', 'header', 'debit', 'credit', 'balance', 'is_active')
    header_text = ('Code', 'Account Name', 'NB', 'CF', 'Header', 'Debit', 'Credit', 'Balance', 'Active')
    table_filters = TBListView.get_table_filters()

    search_key = request.GET.get('search_key') or ""

    if not search_key.isnumeric(): filter_q = Q(name__icontains=search_key)
    else: filter_q = Q(number__contains=search_key)

    response = f_search(request, model=model, filter_q=filter_q, table=table, table_filters=table_filters, table_fields=table_fields, 
        header_text=header_text, template_name=template_name, page_title=page_title, querymanager=querymanager)
    return response
