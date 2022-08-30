from django.urls import path
from . import views as vw

app_name='cover'

urlpatterns = [
    path('', vw.homepage, name="homepage"),
    path('errors/modal/', vw.htmx_modal_error, name="htmx_modal_error"),
    path('require/login/', vw.login_required, name="require_login"),
]
