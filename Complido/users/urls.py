from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import (
    home,
    login_view,
    logout_view,
    register
)

app_name = "users"

urlpatterns = [
    path("", home, name='homepage'),
    path("login/", login_view, name="login",),
    path("logout/", LogoutView.as_view(), name="logout",),
    path("register/", register, name="register",),
    # path("profile/", profile, name='profile',),
    # path("profile/update/", profile_update, name="profile_update",),
]