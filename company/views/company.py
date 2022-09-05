from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.http.response import HttpResponseNotAllowed
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin 
from django.urls.base import reverse_lazy, reverse
from django.contrib.auth.models import User, Group
from django.db.models import Q
from ..models import Company
from ..myforms.company import CompanyCreateForm
from cover.utils import htmx_refresh, htmx_redirect, DEFPATH, save_url_query, not_implemented_yet
from cover import data
from ._funcs import f_test_func
import json


DP = DEFPATH('apps/company/')


class MyCompany(UserPassesTestMixin, generic.DetailView):
    model = Company
    template_name = DP / 'my_company.html'
    test_func = f_test_func
    context_object_name = 'object'

    def get_object(self):
        comp = Company.objects.filter(author=self.request.user)
        if comp.exists(): return comp.first()
        return self.request.user.profile.company

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["alert"] = {'id': 'alert_id', 'msg':'this is an alert message'}
        return context


class CompanyCreateView(UserPassesTestMixin, generic.CreateView):
    model = Company
    form_class = CompanyCreateForm
    template_name = DP / 'create.html'
    allowed_group = 'company_admin'
    success_url = reverse_lazy("company:my_company")
    test_func = f_test_func

    def get(self, request, *args, **kwargs):
        if comp:=self.request.user.profile.company:
            err_msg = f"You already have a company {comp}. Only one company allowed for each users."
            return redirect('cover:error403', msg=err_msg)
        else:
            return super(type(self), self).get(request, *args, **kwargs)

    def form_valid(self, form):
        obj_instance = form.save(commit=False)
        obj_instance.edited_by = self.request.user
        obj_instance.save()
        return redirect(type(self).success_url)


class CompanyUpdateView(UserPassesTestMixin, generic.UpdateView):
    model = Company
    form_class = CompanyCreateForm
    template_name = DP / 'update.html'
    allowed_group = 'company_admin'
    success_url = reverse_lazy("company:my_company") 
    test_func = f_test_func

    def get(self, request, *args, **kwargs):
        my_comp = self.request.user.profile.company
        view_obj = self.get_object() 
        # view_obj is gathered from generic.UpdateView() is not comes from database
        # that's why 'my_comp is view_obj' will always return False
        # so instead of using 'is', use '==' sign to check equallity.
        if my_comp != view_obj:
            err_msg = f"Your company is {my_comp}, but you are trying to access {view_obj} which is not yours."
            return redirect("cover:error403", msg=err_msg)
        elif request.user.profile.comp_level < 4:
            err_msg = f"""Your are a {request.user.profile.get_comp_level_display()} at {request.user.profile.company}, 
                       and did not have permission to modify company informations"""
            return redirect("cover:error403", msg=err_msg)
        else:
            return super(type(self), self).get(request, *args, **kwargs)


class CompanyListView(UserPassesTestMixin, generic.ListView):
    model = Company
    context_object_name = 'objects'
    template_name = DP / 'list.html'
    test_func = f_test_func

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_url'] = reverse_lazy('company:company_search')
        return ctx


class EmployeeListView(UserPassesTestMixin, generic.ListView):
    model = User
    context_object_name = 'objects'
    template_name = DP / 'emp_list.html'
    test_func = f_test_func

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["objects"] = ctx["objects"].filter(profile__company=self.request.user.profile.company)
        return ctx
    
    def get(self, request, *args, **kwargs):
        if self.request.htmx: 
            type(self).template_name = DP/'_partials/emp_list.html'
        else:
            type(self).template_name = DP/'emp_list.html'
        return super(type(self), self).get(request, *args, **kwargs)


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
def apply(request, slug):
    user = request.user
    # validation
    if comp:=user.profile.company:
        if user.profile.comp_stat:
            err_msg = f"You already registered as employee at {comp}"
            if not request.htmx: return redirect('cover:error403', msg=err_msg)
        else:
            # cancel apply
            request.user.profile.company = None
            request.user.profile.save()
        return render(request, template_name=DP/'_partials/list.html', context={'objects':Company.objects.all()})
    appto = Company.objects.filter(slug=slug) 
    if not appto.exists():
        err_msg = f"No company with key {company} found..!"
        if not request.htmx: return redirect('cover:error403', msg=err_msg)
        return render(request, template_name=DP/'_partials/list.html', context={'objects':Company.objects.all()})
    else:
        # execute apply
        request.user.profile.company = appto.first()
        request.user.profile.comp_level = 1     # reset company level to 1
        request.user.profile.save()
    if not request.htmx: return redirect("company:company_list")
    return render(request, template_name=DP/'_partials/list.html', context={'objects':Company.objects.all()})


@login_required
def search(request):
    if request.method == "POST":
        ctx = {}
        name = request.POST.get("search_key") or ""
        f = Q(name__icontains=name)
        ctx['objects'] = Company.objects.filter(f)
        return render(request, template_name=DP/'_partials/list.html', context=ctx)
    return HttpResponse(status=204)


@login_required
def empApprove(request, slug):
    approvor = request.user
    company = approvor.profile.company
    applicant = get_object_or_404(User, profile__slug=slug)
    if approvor.profile.comp_level < 4 or company != applicant.profile.company:
        err_msg = f"You are not authorized or you have different company with {applicant}"
        if request.htmx: return htmx_redirect(HttpResponse(status=403), reverse("cover:error403", kwargs={'msg':err_msg}))
        else: return redirect("cover:error403", msg=err_msg)
    elif applicant.profile.comp_stat:
        err_msg = f"{applicant} already have an approval"
        if request.htmx: return htmx_redirect(HttpResponse(status=403), reverse("cover:error403", kwargs={'msg':err_msg}))
        else: return redirect("cover:error403", msg=err_msg)
    else:
        ctx = {}
        ctx['objects'] = User.objects.filter(profile__company=company).all()
        if request.method == "GET":
            ctx["ajax_confirm_approval"] = f"Are you sure you want to approve {applicant} application as an employee at {company}?"
            ctx["target"] = applicant
        else:
            # give approval
            applicant.profile.comp_stat = True
            applicant.profile.save()
            ctx["ajax_msg"] = f"{applicant} have been added to {company}"
            notif_msg = f"You have been approved as employee on {company}"
            add_company_notification(applicant, approvor, message=notif_msg, reason="...")
        if request.htmx: return render(request, template_name=DP/'_partials/emp_list.html', context=ctx)
        else: return render(request, template_name=DP/'list.html', context=ctx)
        

@login_required
def empRemove(request, slug):
    if request.htmx:
        approvor = request.user
        applicant = get_object_or_404(User, profile__slug=slug)
        company = approvor.profile.company
        if approvor.profile.comp_level < 4:
            # user is not a company administrator
            err_msg = f"You are not a company administrator."
            # response = redirect("cover:error403", msg=err_msg)
            return htmx_redirect(HttpResponse(status=204), reverse("cover:error403", kwargs={'msg':err_msg}))
        elif company.author == applicant:
            # company author can not be removed
            err_msg = f"{applicant} is the author of this company and can not be removed."
            # response =  redirect("cover:error403", msg=err_msg)
            return htmx_redirect(HttpResponse(status=204), reverse("cover:error403", kwargs={'msg':err_msg}))
        else:
            ctx = {}
            ctx["objects"] = User.objects.filter(profile__company=company)
            ctx["company"] = company
            # remove user from the company
            if request.method == "GET":
                ctx["ajax_confirm_removal"] = f"Are you sure to remove {applicant} from {company}?"
                ctx["target"] = applicant
            else:
                applicant.profile.company = None      # update user profile to remove company
                applicant.profile.comp_stat = False   # update user profile to set company status to false
                applicant.profile.save()  # make persistent on database
                ctx["ajax_msg"] = f"{applicant} have been removed from {company}"
                notif_msg = f"You have been removed from the company"
                add_company_notification(applicant, approvor, message=notif_msg, reason="...")
            return render(request, template_name=DP/"_partials/emp_list.html", context=ctx)
    else:
        url = save_url_query(request.get_full_path())
        return redirect("cover:error400", method=request.method, url=url, msg="Wrong way of request")


def add_company_notification(receiver, sender, **kwargs):
    pass