from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.db.models import Q, F
from django.urls.base import reverse_lazy
from ..models import JRE, JRB, COA, BSG, CCF
from ..html.table import JRETable
# from ..forms import JREUpdateForm, JRECreateForm
from ..myforms.jre import JRECreateSingleForm, JRECreateForm, JREUpdateForm
from ._funcs import f_form_valid, f_test_func, f_get_context_data, f_post, f_get, f_standard_context, f_search
from cover.utils import DEFPATH, paginate
from cover import data


DP = DEFPATH('apps/accounting/_shared')
PAGE_TITLE = "Journal Entry"


class JRECreateView(UserPassesTestMixin, generic.CreateView):
    model = JRE
    page_title = PAGE_TITLE
    template_name = DP / 'create.html'
    form_class = JRECreateForm
    success_url = reverse_lazy(f"accounting:{model.__name__.lower()}_list")
    allowed_groups = ('accounting_staff',)
    form_valid = f_form_valid
    get_context_data = f_get_context_data
    post = f_post
    get = f_get
    test_func = f_test_func


class JRECreateSingle(UserPassesTestMixin, generic.CreateView):
    model = JRE
    page_title = PAGE_TITLE
    template_name = DP / 'create_single.html'
    form_class = JRECreateSingleForm
    success_url = reverse_lazy(f"accounting:{model.__name__.lower()}_list")
    allowed_groups = ('accounting_staff',)
    form_valid = f_form_valid
    get_context_data = f_get_context_data
    post = f_post
    get = f_get
    test_func = f_test_func


class JREUpdateView(UserPassesTestMixin, generic.UpdateView):
    model = JRE
    page_title = PAGE_TITLE
    template_name = DP / 'update.html'
    form_class = JREUpdateForm
    success_url = reverse_lazy(f"accounting:{model.__name__.lower()}_list") 
    allowed_groups = ('accounting_staff',)
    form_valid = f_form_valid
    get_context_data = f_get_context_data
    post = f_post
    test_func = f_test_func


class JREListView(UserPassesTestMixin, generic.ListView):
    model = JRE
    table = JRETable
    table_fields = ('date', 'number', 'batch', 'ref', 'description', 'amount', 'group', 'account', 'segment', 'cashflow')
    table_header = ('Date', 'number', 'Batch', 'REF', 'Description', 'Amount', 'Type', 'Account', 'B.Sgmt', 'Cash Flow')
    allowed_groups = ('accounting_viewer',)
    context_object_name = 'objects'
    table_object_name = 'table_obj'
    side_menu_group = 'transactions'
    template_name = DP / 'regular/list.html'
    htmx_template = DP / 'list.html'
    page_title = PAGE_TITLE
    test_func = f_test_func
    get = f_get
    get_context_data = f_get_context_data

    @classmethod
    def get_table_filters(cls):
        return {
            'group': cls.model._type,
            'account': sorted(set(map(lambda i: i.name, COA.actives.all()))),
            'segment': sorted(set(map(lambda i: i.name, BSG.actives.all()))),
            'cashflow': sorted(set(map(lambda i: i.name, CCF.actives.all()))),
            'is_active': [("true", "Yes"), ("false", "No")]
        }

    def filter_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if len(self.request.GET) > 0:
            for k, v in self.request.GET.items():
                if k == "group":
                    context[type(self).context_object_name] = context[type(self).context_object_name].filter(**{k:v[:1].lower()})
                elif k == "account":
                    obj_id = COA.actives.get(name__iexact=v)
                    context[type(self).context_object_name] = context[type(self).context_object_name].filter(**{k:obj_id})
                elif k == "segment":
                    obj_id = BSG.actives.get(name__iexact=v)
                    context[type(self).context_object_name] = context[type(self).context_object_name].filter(**{k:obj_id})
                elif k == "cashflow":
                    obj_id = CCF.actives.get(name__iexact=v)
                    context[type(self).context_object_name] = context[type(self).context_object_name].filter(**{k:obj_id})
                elif k == "is_active":
                    x = True if v == "true" else False
                    context[type(self).context_object_name] = context[type(self).context_object_name].filter(**{k:x})
        return context


@login_required
def search(request):
    model = JRE
    table = JRETable
    template_name = DP/"list.html"
    table_fields = ('date', 'number', 'batch', 'ref', 'description', 'amount', 'group', 'account', 'segment', 'cashflow')
    header_text = ('Date', 'number', 'Batch', 'REF', 'Description', 'Amount', 'Type', 'Account', 'B.Sgmt', 'Cash Flow')
    table_filters = JREListView.get_table_filters()

    search_key = request.POST.get('search_key') or ""
    batch = JRB.objects.filter(number__contains=search_key)
    filter_q = Q()
    if batch.exists(): filter_q = Q(batch=batch.first())

    if search_key[:1].isnumeric():
        filter_q = filter_q|Q(number__contains=search_key)|Q(date__contains=search_key)|Q(amount__contains=search_key)
    else:
        filter_q = filter_q|Q(ref__icontains=search_key)|Q(description__icontains=search_key)

    response = f_search(request, model=model, filter_q=filter_q, table=table, table_filters=table_filters, 
                        table_fields=table_fields, header_text=header_text, template_name=template_name)
    return response
