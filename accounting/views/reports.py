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
from ..models import COA, COH, JRE, CCF
from ..controllers.reports import generate_ledger, generate_cfledger
from ..html.table import TBTable, GNLTable, CFLTable
from ._funcs import f_form_valid, f_test_func, f_get_list_context_data, f_get_context_data, f_standard_context, f_search
from cover.utils import DEFPATH, paginate, HtmxRedirectorMixin, AllowedGroupsMixin
from cover.decorators import htmx_only, have_company_and_approved
from cover import data


DP = DEFPATH('apps/accounting/_shared')


class CFLListView(UserPassesTestMixin, AllowedGroupsMixin, HtmxRedirectorMixin, generic.ListView):
    model = JRE
    table = CFLTable
    table_fields = ('date', 'batch', 'ref', 'description', 'debit', 'credit', 'balance')
    table_header = ('Date', 'Batch', 'Ref', 'Description', 'Debit', 'Credit', 'Balance')
    allowed_groups = ('accounting_viewer',)
    context_object_name = 'objects'
    table_object_name = 'table_obj'
    side_menu_group = 'reports'
    template_name = DP / 'no_htmx/list.html'
    htmx_template = DP / 'list.html'
    page_title = "Cash Flow Ledger"
    test_func = f_test_func
    get_context_data = f_get_list_context_data

    def filter_context_data(self, **kwargs):
        context = {}
        context["search_url"] = reverse_lazy("accounting:report_cfl_search")
        context["model_name"] = 'cfl'    # model_name should be lowercase
        # allows the view template to render javascript for calculating and render cumulative balance
        # for more info, see the javascript attached at apps/accounting/_shared/list.html
        context["cumulative_balance"] = True    
        start_date = self.request.GET.get('period_from')
        end_date = self.request.GET.get('period_to')
        acc_num_and_name = self.request.GET.get('account')
        # cash_flow = self.request.GET.get('cash_flow')
        if start_date and end_date:
            if not acc_num_and_name: account = CCF()     # create an empty account
            else: 
                account = CCF.objects.get(number=acc_num_and_name.split("|")[0])
                context["account"] = acc_num_and_name
            qs, bb = generate_cfledger(account, date.fromisoformat(start_date), date.fromisoformat(end_date))
            context["num_rows"] = qs.count()
            context[type(self).context_object_name] = qs.all()
            context["beginning_balance"] = bb
            context["reporting_period"] = (start_date, end_date)    # add reporting period to context, so it can be consume on view template
        else:
            # different fields between original fields and report fields
            # field_diff = ('previous',)
            # header_diff = ('Previous',)
            # # using filter to remove non report fields from type(self).table_fields and type(self).table_header
            # self.table_fields = tuple(filter(lambda i: i not in field_diff, type(self).table_fields))
            # self.table_header = tuple(filter(lambda i: i not in header_diff, type(self).table_header))
            account = CCF() # create a new empty account
            context[type(self).context_object_name] = generate_cfledger(account)[0]
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
def cfl_search(request):
    kwargs = {}
    kwargs['model'] = JRE
    kwargs['table'] = CFLTable
    kwargs['page_title'] = "Cash Flow Ledger"
    kwargs['template_name'] = DP/"list_search.html"
    kwargs['table_fields'] = CFLListView.table_fields
    kwargs['header_text'] = CFLListView.table_header 
    # kwargs['table_filters'] = CFLListView.get_table_filters()
    kwargs['side_menu_group'] = "reports"  # mark this search as report search
    kwargs['cumulative_balance'] = True

    search_key = request.GET.get('search_key') or ""
    start_date = request.GET.get('period_from')
    end_date = request.GET.get('period_to')
    account = request.GET.get('account')

    if start_date and end_date:
        # set queryset
        if not account: account = CCF()     # create an empty account
        else: account = CCF.objects.get(number=account.split('|')[0])
        qs, bb = generate_cfledger(account, date.fromisoformat(start_date), date.fromisoformat(end_date))
        kwargs['querymanager'] = qs.all()
        kwargs['beginning_balance'] = bb
        kwargs["reporting_period"] = (start_date, end_date)    # add reporting period to context, so it can be consume on view template
        # set table fields and table header text
    else:
        field_diff = ('previous',)
        header_diff = ('Previous',)
        # using filter to remove non report fields from type(self).table_fields and type(self).table_header
        kwargs['table_fields'] = tuple(filter(lambda i: i not in field_diff, kwargs['table_fields']))
        kwargs['header_text'] = tuple(filter(lambda i: i not in header_diff, kwargs['header_text']))

    if not search_key.isnumeric(): 
        kwargs['filter_q'] = Q(ref__icontains=search_key)|Q(description__icontains=search_key)

    response = f_search(request, **kwargs)
    return response


class GNLListView(UserPassesTestMixin, AllowedGroupsMixin, HtmxRedirectorMixin, generic.ListView):
    model = JRE
    table = GNLTable
    table_fields = ('date', 'batch', 'ref', 'description', 'pair_account', 'debit', 'credit', 'balance')
    table_header = ('Date', 'Batch', 'Ref', 'Description', 'Pair Account', 'Debit', 'Credit', 'Balance')
    allowed_groups = ('accounting_viewer',)
    context_object_name = 'objects'
    table_object_name = 'table_obj'
    side_menu_group = 'reports'
    template_name = DP / 'no_htmx/list.html'
    htmx_template = DP / 'list.html'
    page_title = "General Ledger"
    test_func = f_test_func
    get_context_data = f_get_list_context_data

    def filter_context_data(self, **kwargs):
        context = {}
        context["search_url"] = reverse_lazy("accounting:report_gnl_search")
        context["model_name"] = 'gnl'    # model_name should be lowercase
        # allows the view template to render javascript for calculating and render cumulative balance
        # for more info, see the javascript attached at apps/accounting/_shared/list.html
        context["cumulative_balance"] = True    
        start_date = self.request.GET.get('period_from')
        end_date = self.request.GET.get('period_to')
        acc_num_and_name = self.request.GET.get('account')
        if start_date and end_date:
            if not acc_num_and_name: account = COA()     # create an empty account
            else: 
                account = COA.objects.get(number=acc_num_and_name.split("|")[0])
                context["account"] = acc_num_and_name
            qs, bb = generate_ledger(account, date.fromisoformat(start_date), date.fromisoformat(end_date))
            context["num_rows"] = qs.count()
            context[type(self).context_object_name] = qs.all()
            context["beginning_balance"] = bb
            context["reporting_period"] = (start_date, end_date)    # add reporting period to context, so it can be consume on view template
        else:
            # different fields between original fields and report fields
            # field_diff = ('previous',)
            # header_diff = ('Previous',)
            # # using filter to remove non report fields from type(self).table_fields and type(self).table_header
            # self.table_fields = tuple(filter(lambda i: i not in field_diff, type(self).table_fields))
            # self.table_header = tuple(filter(lambda i: i not in header_diff, type(self).table_header))
            acc = COA() # create a new empty coa
            context[type(self).context_object_name] = generate_ledger(acc)[0]
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
def gnl_search(request):
    kwargs = {}
    kwargs['model'] = JRE
    kwargs['table'] = GNLTable
    kwargs['page_title'] = "General Ledger"
    kwargs['template_name'] = DP/"list_search.html"
    kwargs['table_fields'] = GNLListView.table_fields 
    kwargs['header_text'] = GNLListView.table_header 
    # kwargs['table_filters'] = GNLListView.get_table_filters()
    kwargs['side_menu_group'] = "reports"  # mark this search as report search
    kwargs['cumulative_balance'] = True

    search_key = request.GET.get('search_key') or ""
    start_date = request.GET.get('period_from')
    end_date = request.GET.get('period_to')
    account = request.GET.get('account')

    if start_date and end_date:
        # set queryset
        if not account: account = COA()     # create an empty account
        else: account = COA.objects.get(number=account.split('|')[0])
        qs, bb = generate_ledger(account, date.fromisoformat(start_date), date.fromisoformat(end_date))
        kwargs['querymanager'] = qs.all()
        kwargs['beginning_balance'] = bb
        kwargs["reporting_period"] = (start_date, end_date)    # add reporting period to context, so it can be consume on view template
        # set table fields and table header text
    else:
        field_diff = ('previous',)
        header_diff = ('Previous',)
        # using filter to remove non report fields from type(self).table_fields and type(self).table_header
        kwargs['table_fields'] = tuple(filter(lambda i: i not in field_diff, kwargs['table_fields']))
        kwargs['header_text'] = tuple(filter(lambda i: i not in header_diff, kwargs['header_text']))

    if not search_key.isnumeric(): 
        kwargs['filter_q'] = Q(ref__icontains=search_key)|Q(description__icontains=search_key)

    response = f_search(request, **kwargs)
    return response


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
    page_title = "Trial Balance"
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
    kwargs = {}
    kwargs['model'] = COA
    kwargs['table'] = TBTable
    kwargs['page_title'] = "Trial Balance"
    kwargs['template_name'] = DP/"list_search.html"
    kwargs['querymanager'] = 'trialbalance'
    # kwargs['table_fields'] = ('number', 'name', 'normal', 'is_cashflow', 'header', 'debit', 'credit', 'balance', 'is_active')
    # kwargs['table_header'] = ('Code', 'Account Name', 'NB', 'CF', 'Header', 'Debit', 'Credit', 'Balance', 'Active')
    kwargs['table_fields'] = TBListView.table_fields 
    kwargs['header_text'] = TBListView.table_header 
    kwargs['table_filters'] = TBListView.get_table_filters()
    kwargs['side_menu_group'] = "reports"  # mark this search as report search

    search_key = request.GET.get('search_key') or ""
    start_date = request.GET.get('period_from')
    end_date = request.GET.get('period_to')

    if start_date and end_date:
        # set queryset
        kwargs['querymanager'] = kwargs['model'].get_tb_at(date.fromisoformat(start_date), date.fromisoformat(end_date)).all()
        kwargs["reporting_period"] = (start_date, end_date)    # add reporting period to context, so it can be consume on view template
        # set table fields and table header text
    else:
        field_diff = ('previous',)
        header_diff = ('Previous',)
        # using filter to remove non report fields from type(self).table_fields and type(self).table_header
        kwargs['table_fields'] = tuple(filter(lambda i: i not in field_diff, kwargs['table_fields']))
        kwargs['header_text'] = tuple(filter(lambda i: i not in header_diff, kwargs['header_text']))

    if not search_key.isnumeric(): kwargs['filter_q'] = Q(name__icontains=search_key)
    else: kwargs['filter_q'] = Q(number__contains=search_key)

    # response = f_search(request, model=model, filter_q=filter_q, table=table, table_filters=table_filters, table_fields=table_fields, 
    #     header_text=header_text, template_name=template_name, page_title=page_title, querymanager=querymanager)
    response = f_search(request, **kwargs)
    return response
