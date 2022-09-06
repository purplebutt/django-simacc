from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.db.models import Q, F
from django.urls.base import reverse_lazy
from ..models import JRB
from ..html.table import JRBTable
# from ..forms import JRBUpdateForm, JRBCreateForm
from ..myforms.jrb import JRBCreateForm, JRBUpdateForm
from ._funcs import f_form_valid, f_test_func, f_get_context_data, f_post, f_get, f_standard_context, f_search
from cover.utils import DEFPATH, paginate
from cover import data


DP = DEFPATH('apps/accounting/_shared')
PAGE_TITLE = "Journal Batch"


class JRBCreateView(UserPassesTestMixin, generic.CreateView):
    model = JRB
    page_title = PAGE_TITLE
    template_name = DP / 'create.html'
    form_class = JRBCreateForm
    success_url = reverse_lazy(f"accounting:{model.__name__.lower()}_list")
    allowed_groups = ('accounting_staff',)
    form_valid = f_form_valid
    get_context_data = f_get_context_data
    post = f_post
    get = f_get
    test_func = f_test_func


class JRBUpdateView(UserPassesTestMixin, generic.UpdateView):
    model = JRB
    page_title = PAGE_TITLE
    template_name = DP / 'update.html'
    form_class = JRBUpdateForm
    success_url = reverse_lazy(f"accounting:{model.__name__.lower()}_list") 
    allowed_groups = ('accounting_staff',)
    form_valid = f_form_valid
    get_context_data = f_get_context_data
    post = f_post
    test_func = f_test_func


class JRBListView(UserPassesTestMixin, generic.ListView):
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
    get = f_get
    get_context_data = f_get_context_data

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
def search(request):
    # checks user permission
    # return Response Error 403 if user dont have permission
    if not f_test_func(request):
        if request.htmx:
            err_msg = f"You are not authorized to view or modify data."
            return htmx_redirect(HttpResponse(403), reverse_lazy("cover:error403", kwargs={'msg':err_msg}))
        return redirect("cover:error403", msg=err_msg)

    model = JRB
    table = JRBTable
    page_title = PAGE_TITLE
    table_fields = ('created', 'number', 'description', 'group', 'is_active')
    header_text = ('Date', 'Batch Code', 'Description', 'Type', 'Active')
    table_filters = JRBListView.get_table_filters()
    template_name = DP/"list_search.html"

    search_key = request.POST.get('search_key') or ""

    if search_key.isnumeric():
        filter_q = Q(created__contains=search_key)
    else:
        filter_q = Q(description__icontains=search_key)|Q(number__icontains=search_key)

    response = f_search(request, model=model, filter_q=filter_q, table=table, table_filters=table_filters, 
                        table_fields=table_fields, header_text=header_text, template_name=template_name, page_title=page_title)
    return response
