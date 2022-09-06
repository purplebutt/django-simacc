from django.urls import path
from .views import company as comp_view

app_name='company'

urlpatterns = [
    #! company
    path("my_company/", comp_view.MyCompany.as_view(), name="my_company"),
    path("add/", comp_view.CompanyCreateView.as_view(), name="company_add"),
    path("detail/<slug:slug>/", comp_view.CompanyUpdateView.as_view(), name="company_detail"),
    path("update/<slug:slug>/", comp_view.CompanyUpdateView.as_view(), name="company_update"),
    path("list/", comp_view.CompanyListView.as_view(), name="company_list"),
    path("employees/", comp_view.EmployeeListView.as_view(), name="company_emp_list"),
    path("employees/remove/<slug:slug>/", comp_view.empRemove, name="company_emp_remove"),
    path("employees/approve/<slug:slug>/", comp_view.empApprove, name="company_emp_approve"),
    path("employees/edit_group/<slug:slug>/", comp_view.empGroups, name="company_emp_groups"),
    path("apply/<slug:slug>/", comp_view.apply, name="company_apply"),
    path("search/", comp_view.search, name="company_search"),

    #! config
    path("config/add", comp_view.ConfigCreateView.as_view(), name="config_add"),
]