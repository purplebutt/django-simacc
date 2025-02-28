from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.db.models import Q, F
from django.db.models.deletion import RestrictedError
from django.urls.base import reverse_lazy
from ..models import JRB
from ..html.table import JRBTable
from ..myforms.jrb import JRBCreateForm, JRBUpdateForm
from ._funcs import f_form_valid, f_test_func, f_get_list_context_data, f_get_context_data, f_standard_context, f_search
from cover.utils import DEFPATH, paginate, AllowedGroupsMixin, HtmxRedirectorMixin, htmx_redirect
from cover.decorators import htmx_only, have_company_and_approved, require_groups, htmx_only
from cover import data


DP = DEFPATH('apps/accounting/_shared')
PAGE_TITLE = "Journal Batch"


class JRBCreateView(UserPassesTestMixin, AllowedGroupsMixin, HtmxRedirectorMixin, generic.CreateView):
    model = JRB
    page_title = PAGE_TITLE
    htmx_template = DP / 'create.html'
    htmx_only = True
    form_class = JRBCreateForm
    success_url = reverse_lazy(f"accounting:{model.__name__.lower()}_list")
    allowed_groups = ('accounting_staff',)
    form_valid = f_form_valid
    get_context_data = f_get_context_data
    test_func = f_test_func


class JRBDetailView(UserPassesTestMixin, AllowedGroupsMixin, HtmxRedirectorMixin, generic.DetailView):
    model = JRB
    page_title = PAGE_TITLE
    htmx_template = DP / 'detail.html'
    htmx_only = True
    allowed_groups = ('accounting_viewer',)
    get_context_data = f_get_context_data
    test_func = f_test_func


class JRBUpdateView(UserPassesTestMixin, AllowedGroupsMixin, HtmxRedirectorMixin, generic.UpdateView):
    model = JRB
    page_title = PAGE_TITLE
    htmx_template = DP / 'update.html'
    htmx_only = True
    form_class = JRBUpdateForm
    success_url = reverse_lazy(f"accounting:{model.__name__.lower()}_list") 
    allowed_groups = ('accounting_staff',)
    form_valid = f_form_valid
    get_context_data = f_get_context_data
    test_func = f_test_func


class JRBListView(UserPassesTestMixin, AllowedGroupsMixin, HtmxRedirectorMixin, generic.ListView):
    model = JRB
    table = JRBTable
    table_fields = ('created', 'number', 'description', 'group', 'is_active', 'balance', 'entries')
    table_header = ('Date', 'Batch Code', 'Description', 'Type', 'Active', 'Balance', 'Entries')
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
            'is_active': [("true", "Yes"), ("false", "No")],
            'group': sorted(set(map(lambda i: i[0], JRB.actives.values_list('group'))))
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
@have_company_and_approved
@require_groups(groups=("accounting_staff",), error_msg="You are not allowed to perform batch deletion")
@htmx_only()
def jrb_delete(request, slug, *args, **kwargs):
    target_entry = get_object_or_404(JRB, slug=slug)

    ctx = {}
    ctx['object'] = target_entry
    ctx['delete_url'] = target_entry.get_delete_url()

    if request.method == "GET":
        ctx['question'] = f"Are you sure to delete {target_entry.slug} batch?"
        return render(request, template_name=DP/'delete_confirm.html', context=ctx)
    else:
        try:
            target_entry.delete()
        except RestrictedError as err:
            err_msg = "Can not delete Journal Batch due to relationship restriction with Journal Entry"
            return htmx_redirect(HttpResponse(status=403), reverse_lazy("cover:error403", kwargs={'msg':err_msg}))
        return redirect("accounting:jrb_list")


@login_required
@have_company_and_approved
@htmx_only()
def search(request):
    model = JRB
    table = JRBTable
    page_title = PAGE_TITLE
    template_name = DP/"list_search.html"
    table_fields = ('created', 'number', 'description', 'group', 'is_active')
    header_text = ('Date', 'Batch Code', 'Description', 'Type', 'Active')
    table_filters = JRBListView.get_table_filters()

    search_key = request.GET.get('search_key') or ""

    if search_key.isnumeric(): filter_q = Q(created__contains=search_key)
    else: filter_q = Q(description__icontains=search_key)|Q(number__icontains=search_key)

    response = f_search(request, model=model, filter_q=filter_q, table=table, table_filters=table_filters, 
                        table_fields=table_fields, header_text=header_text, template_name=template_name, page_title=page_title)
    return response
