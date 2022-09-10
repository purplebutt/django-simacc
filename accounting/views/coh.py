from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.urls.base import reverse_lazy
from django.db.models import Q, F
from ..models import COH
from ..myforms.coh import COHCreateForm, COHUpdateForm
from ..html.table import COHTable
from ._funcs import f_form_valid, f_test_func, f_get_list_context_data, f_get_context_data, f_post, f_get, f_standard_context, f_search
from cover.utils import htmx_refresh, DEFPATH, paginate, HtmxRedirectorMixin, AllowedGroupsMixin
from cover import data


DP = DEFPATH('apps/accounting/_shared')
PAGE_TITLE = "Account Header"


class COHCreateView(AllowedGroupsMixin, HtmxRedirectorMixin, UserPassesTestMixin, generic.CreateView):
    model = COH
    page_title = PAGE_TITLE
    htmx_template = DP / 'create.html'
    htmx_only = True 
    # htmx_redirector_msg = f'Bad Request - Can not create new COH this way!'
    form_class = COHCreateForm
    success_url = reverse_lazy("accounting:coh_list")
    allowed_groups = ('accounting_staff',)
    form_valid = f_form_valid
    get_context_data = f_get_context_data
    test_func = f_test_func
    # post = f_post
    # get = f_get


class COHDetailView(AllowedGroupsMixin, HtmxRedirectorMixin, UserPassesTestMixin, generic.DetailView):
    model = COH
    page_title = PAGE_TITLE
    htmx_template = DP / 'detail.html'
    htmx_only = True
    allowed_groups = ('accounting_viewer',)
    get_context_data = f_get_context_data
    test_func = f_test_func


class COHUpdateView(AllowedGroupsMixin, HtmxRedirectorMixin, UserPassesTestMixin, generic.UpdateView):
    model = COH
    page_title = PAGE_TITLE
    htmx_template = DP / 'update.html'
    htmx_only = True
    form_class = COHUpdateForm
    success_url = reverse_lazy("accounting:coh_list") 
    allowed_groups = ('accounting_staff',)
    form_valid = f_form_valid
    get_context_data = f_get_context_data
    test_func = f_test_func
    # post = f_post


class COHListView(AllowedGroupsMixin, HtmxRedirectorMixin, UserPassesTestMixin, generic.ListView):
    model = COH
    table = COHTable
    table_fields = ('number', 'name', 'report', 'group')
    table_header = ('Code', 'Header Name', 'Report', 'Account Group')
    allowed_groups = ('accounting_viewer',)
    context_object_name = 'objects'
    table_object_name = 'table_obj'
    side_menu_group = 'master'
    template_name = DP / 'no_htmx/list.html'
    htmx_template = DP / 'list.html'
    page_title = PAGE_TITLE
    test_func = f_test_func
    get_context_data = f_get_list_context_data
    # get_context_data = f_get_context_data
    # get = f_get

    @classmethod
    def get_table_filters(cls):
        return {
            'group': COH._account_group,
            'report': COH._reports
        }

    def filter_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if len(self.request.GET) > 0:
            for k, v in self.request.GET.items():
                if k == "group" or k == "report":
                    context[type(self).context_object_name] = context[type(self).context_object_name].filter(**{k:v})
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

    model = COH
    table = COHTable
    page_title = PAGE_TITLE
    table_fields = ('number', 'name', 'report', 'group')
    header_text = ('Code', 'Header Name', 'Report', 'Account Group')
    table_filters = COHListView.get_table_filters()
    template_name = DP/"list_search.html"

    search_key = request.GET.get('search_key') or ""
    if search_key.isnumeric():
        filter_q = Q(number__contains=search_key)
    else:
        filter_q = Q(name__icontains=search_key)

    response = f_search(request, model=model, filter_q=filter_q, table=table, table_filters=table_filters, 
                        table_fields=table_fields, header_text=header_text, template_name=template_name, page_title=page_title)
    return response
