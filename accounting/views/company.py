from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.urls.base import reverse_lazy
from ..models import Company
from ..forms import CompanyUpdateForm, CompanyCreateForm
from cover.utils import htmx_refresh, DEFPATH
from cover import data


DP = DEFPATH('apps/accounting/company')


class CompanyCreateView(UserPassesTestMixin, generic.CreateView):
    model = Company
    template_name = DP / 'create.html'
    form_class = CompanyCreateForm
    allowed_group = 'company_admin'

    def test_func(self):
        # ingroup = self.request.user.groups.filter(name=type(self).allowed_group).exists()
        user = self.request.user
        is_no_company = user.profile.company not in Company.objects.all()
        return user.is_authenticated and is_no_company

    def form_valid(self, form):
        company_instance = form.save(commit=True)
        self.request.user.profile.company = company_instance
        self.request.user.profile.save()    # save to database
        gr = Group.objects.get(name=type(self).allowed_group)
        self.request.user.groups.add(gr)
        self.request.user.save()
        # self.success_url = reverse_lazy("accounting:comp_update", kwargs={'slug': instance.pk})
        return super(type(self), self).form_valid(form)

class CompanyUpdateView(UserPassesTestMixin, generic.UpdateView):
    model = Company
    template_name = DP / 'update.html'
    form_class = CompanyUpdateForm
    success_url = reverse_lazy("accounting:comp_list") 
    allowed_group = 'company_admin'

    def test_func(self):
        group = self.request.user.groups
        is_employee = self.request.user.profile in self.get_object().employees.all()
        return group.filter(name=type(self).allowed_group).exists() and is_employee

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["report"] = data.sidebar("report")
        context["master"] = data.sidebar("master")
        context["trans"] = data.sidebar("trans")
        return context

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
    