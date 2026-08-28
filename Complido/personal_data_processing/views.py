from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from .models import DataProcessing
from .forms import PersonalDataProcessingForm

User = get_user_model()


@login_required
def processings_list(request):
    """
    Affiche la liste de tous les traitements.
    """
    processings = DataProcessing.objects.all()
    context = {"processings": processings,}

    return render(request, "personal_data_processing/processings_list.html", context)


@login_required
def processing_detail(request, id):

    processing = get_object_or_404(
        DataProcessing.objects
        .select_related(
            "entity",
            "user",
            "legal_basis",
        )
        .prefetch_related(
            "data_categories",
            "data_subject_categories",
            "recipients",
            "subprocessors",
            "processing_operations__operation_type",
            "processing_security_measures__security_measure",
        ),
        id=id,
    )

    return render(
        request,
        "entities/data_processings/processing_detail.html",
        {
            "processing": processing,
        },
    )


@login_required
def processing_update(request, id):
    """
    Permet de modifier un traitement.
    """
    processing = get_object_or_404(DataProcessing, id=id)

    if request.method == "POST":
        form = PersonalDataProcessingForm(request.POST, instance=processing)

        if form.is_valid():
            form.save()
            return redirect("personal_data_processing:processing_detail", id=processing.id)

    else:
        form = PersonalDataProcessingForm(instance=processing)

    context = {
        "form": form,
        "processing": processing,
        }

    return render(request, "personal_data_processing/processing_form.html", context)


@login_required
def processing_delete(request, id):
    """
    Supprime un traitement après confirmation.
    """
    processing = get_object_or_404(DataProcessing, id=id)

    if request.method == "POST":
        processing.delete()
        return redirect(
            "personal_data_processing:processing_list"
        )

    context = {"processing": processing,}

    return render(request, "personal_data_processing/processing_confirm_delete.html", context)