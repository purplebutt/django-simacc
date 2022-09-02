from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.urls.base import reverse_lazy
from ..models import Company
from cover.utils import htmx_refresh, DEFPATH
from cover import data


DP = DEFPATH('apps/company/')


class MyCompany(UserPassesTestMixin, generic.DetailView):
    model = Company
    template_name = DP / 'my_company.html'

    def test_func(self):
        return self.request.user.is_authenticated


class CompanyCreateView(UserPassesTestMixin, generic.CreateView):
    model = Company
    template_name = DP / 'create.html'
    # form_class = CompanyCreateForm
    allowed_group = 'company_admin'

class CompanyUpdateView(UserPassesTestMixin, generic.UpdateView):
    model = Company
    template_name = DP / 'update.html'
    # form_class = CompanyUpdateForm
    # success_url = reverse_lazy("accounting:comp_list") 
    allowed_group = 'company_admin'

class CompanyListView(generic.ListView):
    model = Company
    context_object_name = 'objects'
    template_name = DP / 'list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["report"] = data.sidebar("report")
        context["master"] = data.sidebar("master")
        context["trans"] = data.sidebar("trans")
        return context


class CompEmpList(generic.ListView):
    model = User
    context_object_name = 'objects'
    template_name = DP / 'employees/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["objects"] = User.objects.filter(profile__company=self.request.user.profile.company)
        context["company"] = self.request.user.profile.company
        return context


@login_required
def search(request):
    pass

@login_required
def empList(request):
    pass