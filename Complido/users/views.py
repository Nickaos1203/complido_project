from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render

# from .forms import LoginForm, RegisterForm


User = get_user_model()


def home(request):
    return render(request, "users/home.html")


def login_view(request):
    if request.method != "POST":
        return redirect("homepage")

    username = request.POST.get("username")
    password = request.POST.get("password")

    next_url = request.POST.get("next")

    user = authenticate(
        request,
        username=username,
        password=password,
    )

    if user is not None:

        login(request, user)

        messages.success(
            request,
            f"Bienvenue {user.get_full_name() or user.username} !"
        )

        return redirect(next_url or "homepage")

    messages.error(
        request,
        "Identifiant ou mot de passe incorrect."
    )

    return redirect(next_url or "homepage")


@login_required
def logout_view(request):
    logout(request)

    messages.success(
        request,
        "Vous avez été déconnecté."
    )

    return redirect("homepage")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            messages.success(
                request,
                "Votre compte a été créé avec succès."
            )

            return redirect("dashboard")

    else:
        form = RegisterForm()

    return render(
        request,
        "users/register.html",
        {
            "form": form,
        },
    )