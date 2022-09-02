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
    path("employees/list", comp_view.empList, name="company_emp_list"),
    path("search/", comp_view.search, name="company_search"),
]