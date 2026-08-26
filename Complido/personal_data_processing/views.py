from django.shortcuts import render, get_object_or_404, redirect

from .models import DataProcessing
from .forms import PersonalDataProcessingForm


def processings_list(request):
    """
    Affiche la liste de tous les traitements.
    """
    processings = PersonalDataProcessing.objects.all()
    context = {"processings": processings,}

    return render(request, "personal_data_processing/processings_list.html", context)


def processing_detail(request, id):
    """
    Affiche le détail d'un traitement.
    """
    processing = get_object_or_404(PersonalDataProcessing, id=id)
    context = {"processing": processing,}

    return render(request, "personal_data_processing/processing_detail.html", context)


def processing_update(request, id):
    """
    Permet de modifier un traitement.
    """
    processing = get_object_or_404(PersonalDataProcessing, id=id)

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


def processing_delete(request, id):
    """
    Supprime un traitement après confirmation.
    """
    processing = get_object_or_404(PersonalDataProcessing, id=id)

    if request.method == "POST":
        processing.delete()
        return redirect(
            "personal_data_processing:processing_list"
        )

    context = {"processing": processing,}

    return render(request, "personal_data_processing/processing_confirm_delete.html", context)