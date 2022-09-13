from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.db.models import Q, F, Count
from django.urls.base import reverse_lazy
from ..models import JRE, JRB, COA, BSG, CCF
from ..html.table import JRETable
from ..myforms.jre import JRECreateSingleForm, JRECreateForm, JREUpdateForm
from ._funcs import f_form_valid, f_test_func, f_get_list_context_data, f_get_context_data, f_standard_context, f_search
from cover.utils import DEFPATH, paginate, AllowedGroupsMixin, ProtectClosedPeriodMixin, HtmxRedirectorMixin, AllowedTodayMixin, not_implemented_yet
from cover.decorators import htmx_only, have_company_and_approved, require_groups, protect_closed_period
from cover import data


DP = DEFPATH('apps/accounting/_shared')
PAGE_TITLE = "Journal Entry"


class JRECreateView(UserPassesTestMixin, AllowedGroupsMixin, AllowedTodayMixin, HtmxRedirectorMixin, generic.CreateView):
    model = JRE
    page_title = PAGE_TITLE
    htmx_template = DP / 'create.html'
    htmx_only = True
    errmsg_allowed_today = dict(title="Error", head="Invalid date", msg="Can not add journals entry with date > today.")
    form_class = JRECreateForm
    success_url = reverse_lazy(f"accounting:{model.__name__.lower()}_list")
    allowed_groups = ('accounting_staff',)
    form_valid = f_form_valid
    get_context_data = f_get_context_data
    test_func = f_test_func


class JRECreateSingle(UserPassesTestMixin, AllowedGroupsMixin, HtmxRedirectorMixin, generic.CreateView):
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


class JREDetailView(UserPassesTestMixin, AllowedGroupsMixin, HtmxRedirectorMixin, generic.DetailView):
    model = JRE
    page_title = PAGE_TITLE
    template_name = DP / 'detail.html'
    htmx_template = DP / 'detail.html'
    allowed_groups = ('accounting_viewer',)
    get_context_data = f_get_context_data
    test_func = f_test_func


class JREUpdateView(UserPassesTestMixin, AllowedGroupsMixin, ProtectClosedPeriodMixin, HtmxRedirectorMixin, generic.UpdateView):
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


class JREListView(UserPassesTestMixin, AllowedGroupsMixin, HtmxRedirectorMixin, generic.ListView):
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
        coa = COA.objects.annotate(entries=(Count('journal'))).filter(entries__gt=0)
        seg = BSG.objects.annotate(entries=(Count('journal'))).filter(entries__gt=0)
        ccf = CCF.objects.annotate(entries=(Count('journal'))).filter(entries__gt=0)
        return {
            'group': cls.model._type,
            'account': sorted(set(map(lambda i: i.name, coa))),
            'segment': sorted(set(map(lambda i: i.name, seg))),
            'cashflow': sorted(set(map(lambda i: i.name, ccf))),
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
@have_company_and_approved
@require_groups(groups=("accounting_staff",), error_msg="You are not allowed to perform journal deletion")
@protect_closed_period(klass=JRE, field="date")
def jre_delete(request, slug, *args, **kwargs):
    target_entry = kwargs["target_entry"]
    pair_entry = get_object_or_404(JRE, pair=target_entry)

    ctx = {}
    ctx['object'] = target_entry
    ctx['pair'] = pair_entry
    ctx['delete_url'] = target_entry.get_delete_url()
    ctx['more_info'] = True     # makes template shows more info

    if request.method == "GET":
        ctx['question'] = f"Are you sure to delete both {target_entry.slug} and {pair_entry.slug} journal?"
        return render(request, template_name=DP/'delete_confirm.html', context=ctx)
    else:
        pair_entry.delete()
        target_entry.delete()
        return redirect("accounting:jre_list")


@login_required
@have_company_and_approved
@htmx_only()
def search(request):
    model = JRE
    table = JRETable
    page_title = PAGE_TITLE
    template_name = DP/"list_search.html"
    table_fields = ('date', 'number', 'batch', 'ref', 'description', 'amount', 'group', 'account', 'segment', 'cashflow')
    header_text = ('Date', 'number', 'Batch', 'REF', 'Description', 'Amount', 'Type', 'Account', 'B.Sgmt', 'Cash Flow')
    table_filters = JREListView.get_table_filters()

    search_key = request.GET.get('search_key') or ""
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
