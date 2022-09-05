from django.urls import path
from . import views as vw

app_name='cover'

urlpatterns = [
    path('', vw.homepage, name="homepage"),
    path('require/login/', vw.login_required, name="require_login"),
    path('errors/modal/', vw.htmx_modal_error, name="htmx_modal_error"),
    path('errors/403/<str:msg>/', vw.error_forbidden, name="error403"),
    path('errors/400/<str:method>/<str:url>/<str:msg>/', vw.error_bad_request, name="error400"),
    path('errors/405/<str:allowed>/<str:msg>/', vw.error_not_allowed, name="error405"),
]
