from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render


from .forms import UserRegisterForm


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

        return redirect("personal_data_processing:processings_list")

    messages.error(
        request,
        "Identifiant ou mot de passe incorrect."
    )

    return redirect("users:homepage")


@login_required
def logout_view(request):
    logout(request)

    messages.success(
        request,
        "Vous avez été déconnecté."
    )

    return redirect("homepage")


def register(request):

    if request.method == "POST":
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            # Connexion automatique après création du compte
            login(request, user)

            return redirect("personal_data_processing:processings_list")

    else:
        form = UserRegisterForm()

    return render(
        request,
        "users/register.html",
        {
            "form": form,
        }
    )