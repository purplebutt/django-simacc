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
from ._funcs import f_form_valid, f_test_func, f_get_list_context_data, f_get_context_data, f_post, f_get, f_standard_context, f_search
from cover.utils import DEFPATH, paginate, AllowedGroupsMixin, HtmxRedirectorMixin, not_implemented_yet
from cover import data


DP = DEFPATH('apps/accounting/_shared')
PAGE_TITLE = "Journal Entry"


class JRECreateView(AllowedGroupsMixin, HtmxRedirectorMixin, UserPassesTestMixin, generic.CreateView):
    model = JRE
    page_title = PAGE_TITLE
    htmx_template = DP / 'create.html'
    htmx_only = True
    form_class = JRECreateForm
    success_url = reverse_lazy(f"accounting:{model.__name__.lower()}_list")
    allowed_groups = ('accounting_staff',)
    form_valid = f_form_valid
    get_context_data = f_get_context_data
    test_func = f_test_func
    # post = f_post
    # get = f_get


class JRECreateSingle(AllowedGroupsMixin, HtmxRedirectorMixin, UserPassesTestMixin, generic.CreateView):
    model = JRE
    page_title = PAGE_TITLE
    htmx_template = DP / 'create_single.html'
    htmx_only = True
    form_class = JRECreateSingleForm
    success_url = reverse_lazy(f"accounting:{model.__name__.lower()}_list")
    allowed_groups = ('accounting_staff',)
    form_valid = f_form_valid
    get_context_data = f_get_context_data
    test_func = f_test_func


class JREDetailView(AllowedGroupsMixin, HtmxRedirectorMixin, UserPassesTestMixin, generic.DetailView):
    model = JRE
    page_title = PAGE_TITLE
    template_name = DP / 'detail.html'
    allowed_groups = ('accounting_viewer',)
    get_context_data = f_get_context_data
    test_func = f_test_func


class JREUpdateView(AllowedGroupsMixin, HtmxRedirectorMixin, UserPassesTestMixin, generic.UpdateView):
    model = JRE
    page_title = PAGE_TITLE
    htmx_template = DP / 'update.html'
    htmx_only = True
    form_class = JREUpdateForm
    success_url = reverse_lazy(f"accounting:{model.__name__.lower()}_list") 
    allowed_groups = ('accounting_staff',)
    form_valid = f_form_valid
    get_context_data = f_get_context_data
    test_func = f_test_func


class JREListView(AllowedGroupsMixin, HtmxRedirectorMixin, UserPassesTestMixin, generic.ListView):
    model = JRE
    table = JRETable
    table_fields = ('date', 'number', 'batch', 'ref', 'description', 'amount', 'group', 'account', 'segment', 'cashflow')
    table_header = ('Date', 'number', 'Batch', 'REF', 'Description', 'Amount', 'Type', 'Account', 'B.Sgmt', 'Cash Flow')
    allowed_groups = ('accounting_viewer',)
    context_object_name = 'objects'
    table_object_name = 'table_obj'
    side_menu_group = 'transactions'
    template_name = DP / 'no_htmx/list.html'
    htmx_template = DP / 'list.html'
    page_title = PAGE_TITLE
    test_func = f_test_func
    get_context_data = f_get_list_context_data

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
def jre_delete(request, slug):
    # checks user permission
    # return Response Error 403 if user dont have permission
    if not f_test_func(request):
        if request.htmx:
            err_msg = f"You are not authorized to delete data."
            return htmx_redirect(HttpResponse(403), reverse_lazy("cover:error403", kwargs={'msg':err_msg}))
        return redirect("cover:error403", msg=err_msg)

    target_entry = get_object_or_404(JRE, slug=slug)
    pair_entry = get_object_or_404(JRE, pair=target_entry)
    # check if transaction still on open accounting period
    # closed accounting period journals can not be edited or deleted
    # on_open_accounting_period(request, transaction) 

    ctx = {}
    ctx['object'] = target_entry
    ctx['pair'] = pair_entry

    if request.method == "GET":
        ctx['question'] = f"Are you sure to delete both {target_entry.slug} and {pair_entry.slug} journal?"
        return render(request, template_name=DP/'delete_confirm.html', context=ctx)
    else:
        pair_entry.delete()
        target_entry.delete()
        return redirect("accounting:jre_list")


def on_open_accounting_period(request, transaction):
    return not_implemented_yet(request)    

@login_required
def search(request):
    # checks user permission
    # return Response Error 403 if user dont have permission
    if not f_test_func(request):
        if request.htmx:
            err_msg = f"You are not authorized to view or modify data."
            return htmx_redirect(HttpResponse(403), reverse_lazy("cover:error403", kwargs={'msg':err_msg}))
        return redirect("cover:error403", msg=err_msg)

    model = JRE
    table = JRETable
    page_title = PAGE_TITLE
    template_name = DP/"list_search.html"
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
                        table_fields=table_fields, header_text=header_text, template_name=template_name, page_title=page_title)
    return response
