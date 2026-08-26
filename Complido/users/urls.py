from django.urls import path
from .views import home

app_name = "users"

urlpatterns = [
    path("", home, name='homepage'),
    # path("login/", UserLoginView.as_view(), name="login",),
    # path("logout/", UserLogoutView.as_view(), name="logout",),
    # path("profile/", profile, name='profile',),
    # path("profile/update/", profile_update, name="profile_update",),
]