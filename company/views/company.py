from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.http.response import HttpResponseNotAllowed
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin 
from django.urls.base import reverse_lazy, reverse
from django.contrib.auth.models import User, Group
from django.utils.safestring import mark_safe
from django.db.models import Q
from ..models import Company
from ..myforms.company import CompanyEditForm, ConfigEditForm, UserEditGroupForm
from cover.utils import (
    not_implemented_yet, DEFPATH, save_url_query,
    htmx_refresh, htmx_redirect, 
    AllowedGroupsMixin, HaveAndMyCompanyMixin, HaveCompanyMixin, NoCompanyMixin, HtmxRedirectorMixin
)
from cover import data
from ._funcs import f_test_func


DP = DEFPATH('apps/company/')


class MyCompany(HaveCompanyMixin, HtmxRedirectorMixin, UserPassesTestMixin, generic.DetailView):
    model = Company
    template_name = DP / 'my_company.html'
    htmx_template = DP / '_partials/my_company.html'
    test_func = f_test_func
    context_object_name = 'object'

    def get_object(self): return self.request.user.profile.company


class CompanyCreateView(NoCompanyMixin, UserPassesTestMixin, generic.CreateView):
    model = Company
    form_class = CompanyEditForm
    template_name = DP / 'create.html'
    allowed_groups = ('company_admin',)
    success_url = reverse_lazy("company:my_company")
    test_func = f_test_func

    def form_valid(self, form):
        obj_instance = form.save(commit=False)
        obj_instance.edited_by = self.request.user
        obj_instance.save()
        return redirect(type(self).success_url)


class CompanyUpdateView(AllowedGroupsMixin, HaveAndMyCompanyMixin, HtmxRedirectorMixin, UserPassesTestMixin, generic.UpdateView):
    model = Company
    form_class = CompanyEditForm
    htmx_template = DP / 'update.html'
    allowed_groups = ('company_admin',)
    success_url = reverse_lazy("company:my_company") 
    test_func = f_test_func


class CompanyListView(NoCompanyMixin, UserPassesTestMixin, generic.ListView):
    model = Company
    context_object_name = 'objects'
    template_name = DP / 'list.html'
    test_func = f_test_func

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_url'] = reverse_lazy('company:company_search')
        return ctx


class EmployeeListView(HaveCompanyMixin, HtmxRedirectorMixin, UserPassesTestMixin, generic.ListView):
    model = User
    context_object_name = 'objects'
    template_name = DP / 'emp_list.html'
    htmx_template = DP / '_partials/emp_list.html'
    test_func = f_test_func

    def get_context_data(self, **kwargs):
        search_key = self.request.GET.get("search_key") or ""
        qs_criteria = Q(profile__company=self.request.user.profile.company)&(
            Q(first_name__icontains=search_key)|Q(username__icontains=search_key)|Q(last_name__icontains=search_key))
        ctx = {}
        ctx["user_is_admin"] = self.request.user.groups.filter(name='company_admin').exists()
        ctx[type(self).context_object_name] = User.objects.filter(qs_criteria)
        if self.request.htmx_target == "employeesList": self.template_name = DP/'_partials/emp_list_search.html'
        return ctx
    

class ConfigCreateView(AllowedGroupsMixin, HtmxRedirectorMixin, UserPassesTestMixin, generic.View):
    form_class = ConfigEditForm
    template_name = DP/'create.html'
    htmx_template = DP/'_partials/create.html'
    allowed_groups = ('company_admin',)
    form_class = ConfigEditForm
    test_func = f_test_func
    context_object_name = 'form'
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        company = request.user.profile.company
        ctx = {'company': company}
        config_data = {}
        if isinstance(company.config, str): 
            config_data = dict()
        else:
            c = {}
            for k, v in company.config.items():
                c[k] = v[0] if isinstance(v, list) else v
            config_data = c 

        form_instance = type(self).form_class(config_data)
        ctx[type(self).context_object_name] = form_instance
        return render(request, template_name=self.template_name, context=ctx)

    def post(self, request, *args, **kwargs):
        frm_instance = type(self).form_class(request.POST)
        if frm_instance.is_valid():
            company = request.user.profile.company
            company.save_config(dict(request.POST))
        if self.request.htmx:
            return htmx_redirect(HttpResponse(status=204), reverse('company:my_company'))
        else:
            return redirect('company:my_company')


class EmployeeEditGroup(AllowedGroupsMixin, HtmxRedirectorMixin, UserPassesTestMixin, generic.UpdateView):
    model = User
    form_class = UserEditGroupForm
    template_name = DP / 'edit_group.html'
    htmx_template = DP / 'edit_group.html'
    success_url = reverse_lazy("company:company_emp_list")
    allowed_groups = ('company_admin',)
    test_func = f_test_func

    def form_valid(self, form, *args, **kwargs):
        frm_instance = form.save(commit=True)

        if self.request.htmx:
            return htmx_refresh(HttpResponse(status=204))
        return redirect(self.success_url)


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
            ctx["target"] = applicant
            ctx["mode"] = f"approve"
            ctx["question"] = mark_safe(f"Are you sure you want to add <b>{applicant.username.title()}</b> as employee on <b>{company.name.title()}</b>?")
            return render(request, template_name=DP/"_partials/emp_list_confirm.html", context=ctx)
        else:
            # give approval
            applicant.profile.comp_stat = True
            applicant.profile.save()
            ctx["ajax_msg"] = f"{applicant.username.title()} have been added to {company.name.title()}"
            notif_msg = f"You have been approved as employee on {company.name.title()}"
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
                ctx["target"] = applicant
                ctx["mode"] = f"remove"
                ctx["question"] = mark_safe(f"Are you sure you want to remove <b>{applicant.username.title()}</b> from <b>{company.name.title()}</b>?")
                return render(request, template_name=DP/"_partials/emp_list_confirm.html", context=ctx)
            else:
                applicant.profile.company = None      # update user profile to remove company
                applicant.profile.comp_stat = False   # update user profile to set company status to false
                applicant.profile.save()  # make persistent on database
                ctx["ajax_msg"] = f"{applicant.username.title()} have been removed from {company.name.title()}"
                notif_msg = f"You have been removed from {company.name.title()}"
                add_company_notification(applicant, approvor, message=notif_msg, reason="...")
            return render(request, template_name=DP/"_partials/emp_list.html", context=ctx)
    else:
        url = save_url_query(request.get_full_path())
        return redirect("cover:error400", method=request.method, url=url, msg="Wrong way of request")


def add_company_notification(receiver, sender, **kwargs):
    pass