from django.urls import path
from .views import index
from .views import utils as utl_view
from .views import coh as coh_view
from .views import coa as coa_view
from .views import ccf as ccf_view
from .views import bsg as bsg_view
from .views import jrb as jrb_view
from .views import jre as jre_view
from .views import reports as rep_view


app_name='accounting'

urlpatterns = [
    #! index
    path("", index.homepage, name="index"),

    #! utils
    path("utils/datalist/<str:model>/", utl_view.get_datalist, name="utils_datalist"),

    #! COA Header
    path("coh_add/", coh_view.COHCreateView.as_view(), name="coh_add"),
    path("coh_detail/<slug:slug>/", coh_view.COHDetailView.as_view(), name="coh_detail"),
    path("coh_update/<slug:slug>/", coh_view.COHUpdateView.as_view(), name="coh_update"),
    path("coh_list/", coh_view.COHListView.as_view(), name="coh_list"),
    path("coh_search/", coh_view.search, name="coh_search"),

    #! Chart Of Account
    path("coa_add/", coa_view.COACreateView.as_view(), name="coa_add"),
    path("coa_detail/<slug:slug>/", coa_view.COADetailView.as_view(), name="coa_detail"),
    path("coa_update/<slug:slug>/", coa_view.COAUpdateView.as_view(), name="coa_update"),
    path("coa_list/", coa_view.COAListView.as_view(), name="coa_list"),
    path("coa_search/", coa_view.search, name="coa_search"),

    #! Chart Of Cash Flow
    path("ccf_add/", ccf_view.CCFCreateView.as_view(), name="ccf_add"),
    path("ccf_detail/<slug:slug>/", ccf_view.CCFDetailView.as_view(), name="ccf_detail"),
    path("ccf_update/<slug:slug>/", ccf_view.CCFUpdateView.as_view(), name="ccf_update"),
    path("ccf_list/", ccf_view.CCFListView.as_view(), name="ccf_list"),
    path("ccf_search/", ccf_view.search, name="ccf_search"),

    #! Business Segment 
    path("bsg_add/", bsg_view.BSGCreateView.as_view(), name="bsg_add"),
    path("bsg_detail/<slug:slug>/", bsg_view.BSGDetailView.as_view(), name="bsg_detail"),
    path("bsg_update/<slug:slug>/", bsg_view.BSGUpdateView.as_view(), name="bsg_update"),
    path("bsg_delete/<slug:slug>/", bsg_view.bsg_delete, name="bsg_delete"),
    path("bsg_list/", bsg_view.BSGListView.as_view(), name="bsg_list"),
    path("bsg_search/", bsg_view.search, name="bsg_search"),

    #! Journal Batch 
    path("jrb_add/", jrb_view.JRBCreateView.as_view(), name="jrb_add"),
    path("jrb_detail/<slug:slug>/", jrb_view.JRBDetailView.as_view(), name="jrb_detail"),
    path("jrb_update/<slug:slug>/", jrb_view.JRBUpdateView.as_view(), name="jrb_update"),
    path("jrb_delete/<slug:slug>/", jrb_view.jrb_delete, name="jrb_delete"),
    path("jrb_list/", jrb_view.JRBListView.as_view(), name="jrb_list"),
    path("jrb_search/", jrb_view.search, name="jrb_search"),

    #! Journal Entry
    path("jre_add/", jre_view.JRECreateView.as_view(), name="jre_add"),
    path("jre_add_single/", jre_view.JRECreateSingle.as_view(), name="jre_add_single"),
    path("jre_detail/<slug:slug>/", jre_view.JREDetailView.as_view(), name="jre_detail"),
    path("jre_update/<slug:slug>/", jre_view.JREUpdateView.as_view(), name="jre_update"),
    path("jre_delete/<slug:slug>/", jre_view.jre_delete, name="jre_delete"),
    path("jre_list/", jre_view.JREListView.as_view(), name="jre_list"),
    path("jre_search/", jre_view.search, name="jre_search"),

    #! Trial Balance
    path("report/trial_balance/", rep_view.TBListView.as_view(), name="report_tb"),
    path("report/trial_balance/search/", rep_view.tb_search, name="report_tb_search"),
    
    path("report/general_ledger/", rep_view.GNLListView.as_view(), name="report_gnl"),
    path("report/general_ledger/search/", rep_view.gnl_search, name="report_gnl_search"),
]
