from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

from .forms import LoginForm, UserProfileForm
from django.contrib.auth.decorators import login_required


class UserLoginView(LoginView):
    template_name = "users/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("dashboard")


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("users:login")


@login_required
def profile(request):
    return render(
        request,
        "users/profile.html",
        {
            "profile_user": request.user,
        },
    )


@login_required
def profile_update(request):

    if request.method == "POST":
        form = UserProfileForm(
            request.POST,
            instance=request.user,
        )

        if form.is_valid():
            form.save()

            return redirect("users:profile")

    else:
        form = UserProfileForm(
            instance=request.user,
        )

    return render(
        request,
        "users/profile_form.html",
        {
            "form": form,
        },
    )