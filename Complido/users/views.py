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
    user = authenticate(request, username=username, password=password,)

    if user is not None:
        login(request, user)
        messages.success(
            request,
            f"Bienvenue {user.get_full_name() or user.username} !"
        )

        return redirect("personal_data_processing:processings_list")

    messages.error(request, "Identifiant ou mot de passe incorrect.")
    return redirect("users:homepage")



@login_required
def logout_view(request):
    logout(request)

    messages.success(request, "Vous avez été déconnecté.")
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

    return render(request, "users/register.html", {"form": form,})



@login_required
def user_detail(request):
    """
    Affiche les informations de l'utilisateur connecté.
    """

    user = request.user

    context = {
        "user": user,
    }

    return render(
        request,
        "users/user_detail.html",
        context
    )



@login_required
def user_update(request):
    """
    Permet à l'utilisateur connecté de modifier ses informations personnelles.
    """
    user = request.user

    if request.method == "POST":
        user.last_name = request.POST.get("last_name", "").strip()
        user.first_name = request.POST.get("first_name", "").strip()
        user.username = request.POST.get("username", "").strip()
        user.email = request.POST.get("email", "").strip()

        # Vérification du nom d'utilisateur
        if not user.username:
            messages.error(
                request,
                "Le nom d'utilisateur est obligatoire."
            )
            return render(
                request,
                "user/user_update.html",
                {"user": user}
            )

        # Vérification de l'adresse e-mail
        if not user.email:
            messages.error(
                request,
                "L'adresse e-mail est obligatoire."
            )
            return render(
                request,
                "user/user_update.html",
                {"user": user}
            )

        user.save()

        messages.success(
            request,
            "Vos informations ont été modifiées avec succès."
        )

        return redirect("users:profile")

    context = {
        "user": user,
    }

    return render(
        request,
        "users/user_update.html",
        context
    )