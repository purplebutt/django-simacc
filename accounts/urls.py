from django.urls import path
from . import views as vw

app_name='accounts'

urlpatterns = [
    path("profile/<slug:slug>/", vw.ProfileDetailView.as_view(), name="profile_detail"),
    path("myprofile/", vw.my_profile, name="myprofile"),
    path("update_picture/", vw.image_update, name="update_picture"),
]
