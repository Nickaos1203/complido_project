from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Prefetch

from .forms import PersonalDataProcessingForm

from django.contrib import messages
from django.db import transaction

from .models import (
    DataProcessing,
    LegalBasis,
    DataCategory,
    DataSubjectCategory,
    Recipient,
    Subprocessor,
    OperationType,
    SecurityMeasure,
    ProcessingLegalBasis,
    ProcessingDataCategory,
    ProcessingOperation,
    ProcessingSecurityMeasure,
)

from users.models import User


User = get_user_model()


@login_required
def processings_list(request):
    """
    Affiche la liste de tous les traitements de l'entité
    de l'utilisateur connecté.
    """
    processings = (
        DataProcessing.objects
        .filter(entity=request.user.entity)
        .select_related("user")
        .order_by("-updated_at")
    )

    context = {"processings": processings,}

    return render(request, "personal_data_processing/processings_list.html", context)



@login_required
def processing_detail(request, id):
    """
    Affiche les détails d'un traitement de données personnelles.
    """

    processing = get_object_or_404(
        DataProcessing.objects
        .select_related("user")
        .prefetch_related(
            Prefetch(
                "processing_legal_basis",
                queryset=ProcessingLegalBasis.objects.select_related(
                    "legal_basis"
                )
            ),
            Prefetch(
                "processing_data_categories",
                queryset=ProcessingDataCategory.objects.select_related(
                    "data_category"
                )
            ),
            Prefetch(
                "processing_operations",
                queryset=ProcessingOperation.objects.select_related(
                    "operation_type"
                ).order_by("display_order")
            ),
            Prefetch(
                "processing_security_measures",
                queryset=ProcessingSecurityMeasure.objects.select_related(
                    "security_measure"
                )
            ),
            "data_subject_categories",
            "recipients",
            "subprocessors",
        ), id=id, entity=request.user.entity,
    )

    context = {"processing": processing,}
    return render(request, "personal_data_processing/processing_detail.html", context)


@login_required
@transaction.atomic
def processing_create(request):
    """
    Crée un nouveau traitement de données personnelles.
    """

    if request.method == "POST":
        # ---------------------------------------------------------
        # 1. Récupération de l'entité de l'utilisateur connecté
        # ---------------------------------------------------------
        entity = getattr(request.user, "entity", None)

        if entity is None:
            messages.error(request, "Aucune entité n'est associée à votre compte.")
            return redirect("processing_list")

        # ---------------------------------------------------------
        # 2. Informations générales
        # ---------------------------------------------------------
        name = request.POST.get("name", "").strip()

        # Seul le nom est obligatoire
        if not name:
            messages.error(request, "Le nom du traitement est obligatoire.")
            return render(
                request,
                "processing/processing_create.html",
                {
                    "legal_bases": LegalBasis.objects.all(),
                    "data_categories": DataCategory.objects.all(),
                    "data_subject_categories": DataSubjectCategory.objects.all(),
                    "recipients": Recipient.objects.all(),
                    "subprocessors": Subprocessor.objects.all(),
                    "operation_types": OperationType.objects.all(),
                    "security_measures": SecurityMeasure.objects.all(),
                }
            )

        # ---------------------------------------------------------
        # 3. Création du traitement
        # ---------------------------------------------------------
        processing = DataProcessing.objects.create(
            name=name,
            description=request.POST.get("description", "").strip(),
            entity=entity,
            user=request.user,
            status=request.POST.get("status", DataProcessing.Status.DRAFT),
            purpose=request.POST.get("purpose", "").strip(),
            subpurpose=request.POST.get("subpurpose", "").strip(),
            description_purpose=request.POST.get("description_purpose", "").strip(),
            retention_period=request.POST.get("retention_period", "").strip(),
            international_transfer=(request.POST.get("international_transfer") == "on"),
            aipd_required=(request.POST.get("aipd_required") == "on"),
        )

        # ---------------------------------------------------------
        # Base légale
        # ---------------------------------------------------------
        legal_basis_id = request.POST.get("legal_basis")
        legal_basis_justification = request.POST.get("legal_basis_justification", "").strip()

        if legal_basis_id:
            ProcessingLegalBasis.objects.create(processing=processing, legal_basis_id=legal_basis_id, justification=legal_basis_justification,)

        # ---------------------------------------------------------
        # 5. Catégories de données
        # ---------------------------------------------------------
        data_category_ids = request.POST.getlist("data_category")
        data_enumerations = request.POST.getlist("data_enumeration")

        for index, category_id in enumerate(data_category_ids):
            if not category_id:
                continue

            enumeration = ""

            if index < len(data_enumerations):
                enumeration = data_enumerations[index].strip()

            ProcessingDataCategory.objects.create(
                processing=processing,
                data_category_id=category_id,
                data_enumeration=enumeration,
            )

        # ---------------------------------------------------------
        # 6. Catégories de personnes concernées
        # ---------------------------------------------------------
        subject_category_ids = request.POST.getlist("data_subject_categories")
        processing.data_subject_categories.set(subject_category_ids)

        # ---------------------------------------------------------
        # 7. Destinataires
        # ---------------------------------------------------------

        recipient_ids = request.POST.getlist("recipients")
        processing.recipients.set(recipient_ids)

        # ---------------------------------------------------------
        # 8. Sous-traitants
        # ---------------------------------------------------------
        subprocessor_ids = request.POST.getlist("subprocessors")
        processing.subprocessors.set(subprocessor_ids)

        # ---------------------------------------------------------
        # 9. Types d'opérations
        # ---------------------------------------------------------

        operation_type_ids = request.POST.getlist("operation_type")
        operation_descriptions = request.POST.getlist("operation_description")

        for index, operation_type_id in enumerate(operation_type_ids):

            if not operation_type_id:
                continue

            description = ""

            if index < len(operation_descriptions):
                description = operation_descriptions[index].strip()

            ProcessingOperation.objects.create(
                processing=processing,
                operation_type_id=operation_type_id,
                display_order=index + 1,
                description=description,
            )

        # ---------------------------------------------------------
        # 10. Mesures de sécurité
        # ---------------------------------------------------------
        security_measure_ids = request.POST.getlist("security_measure")
        security_statuses = request.POST.getlist("security_status")
        security_comments = request.POST.getlist("security_comment")

        for index, security_measure_id in enumerate(security_measure_ids):

            if not security_measure_id:
                continue

            status = (security_statuses[index] if index < len(security_statuses) else ProcessingSecurityMeasure.Status.PLANNED)
            comment = (security_comments[index].strip() if index < len(security_comments) else "")
            ProcessingSecurityMeasure.objects.create(
                processing=processing,
                security_measure_id=security_measure_id,
                status=status,
                comment=comment,
            )

        # ---------------------------------------------------------
        # 11. Succès
        # ---------------------------------------------------------
        messages.success(request, f"Le traitement « {processing.name} » a été créé avec succès.")

        return redirect("personal_data_processing:processing_detail", id=processing.id)

    # -------------------------------------------------------------
    # GET : affichage du formulaire
    # -------------------------------------------------------------
    context = {
        "entity": getattr(request.user, "entity", None),
        "legal_bases": LegalBasis.objects.all(),
        "data_categories": DataCategory.objects.all(),
        "data_subject_categories": (DataSubjectCategory.objects.all()),
        "recipients": Recipient.objects.all(),
        "subprocessors": Subprocessor.objects.all(),
        "operation_types": OperationType.objects.all(),
        "security_measures": (SecurityMeasure.objects.all()),
    }

    return render(request, "personal_data_processing/processing_create.html", context)


@login_required
def processing_update(request, id):
    """
    Modifie un traitement de données personnelles.

    La modification est autorisée uniquement si :
    - l'utilisateur connecté est le créateur du traitement ;
    - ou l'utilisateur possède le rôle DPO au sein de la même entité.

    Un utilisateur ne peut jamais modifier un traitement
    appartenant à une autre entité.
    """

    # =========================================================
    # RÉCUPÉRATION DU TRAITEMENT
    # =========================================================
    processing = get_object_or_404(DataProcessing, id=id, entity=request.user.entity)

    # =========================================================
    # CONTRÔLE DES DROITS
    # =========================================================

    is_creator = (processing.user_id == request.user.id)
    is_dpo = (request.user.role == User.Role.DPO)

    if not is_creator and not is_dpo:
        messages.error(request, "Vous n'êtes pas autorisé à modifier ce traitement.")

        return redirect("personal_data_processing:processing_detail", id=processing.id)

    # =========================================================
    # POST : MODIFICATION
    # =========================================================

    if request.method == "POST":
        # -----------------------------------------------------
        # Nom du traitement
        # -----------------------------------------------------
        name = request.POST.get("name", "").strip()

        if not name:
            messages.error(request, "Le nom du traitement est obligatoire.")
            return render(
                request,
                "personal_data_processing/processing_update.html",
                {
                    "processing": processing,
                    "legal_bases": LegalBasis.objects.all(),
                    "data_categories": DataCategory.objects.all(),
                    "data_subject_categories": (DataSubjectCategory.objects.all()),
                    "recipients": Recipient.objects.all(),
                    "subprocessors": Subprocessor.objects.all(),
                    "operation_types": OperationType.objects.all(),
                    "security_measures": SecurityMeasure.objects.all(),
                }
            )

        # =====================================================
        # TRANSACTION
        # =====================================================

        with transaction.atomic():
            # -------------------------------------------------
            # INFORMATIONS GÉNÉRALES
            # -------------------------------------------------
            processing.name = name
            processing.description = request.POST.get("description", "").strip()
            processing.status = request.POST.get("status", DataProcessing.Status.DRAFT)
            processing.purpose = request.POST.get("purpose", "").strip()
            processing.subpurpose = request.POST.get("subpurpose", "").strip()
            processing.description_purpose = request.POST.get("description_purpose", "").strip()
            processing.retention_period = request.POST.get("retention_period", "").strip()
            processing.international_transfer = (request.POST.get("international_transfer") == "on")
            processing.aipd_required = (request.POST.get("aipd_required") == "on")

            # L'entité ne doit jamais venir du formulaire.
            processing.entity = request.user.entity
            processing.save()

            # =================================================
            # BASE LÉGALE
            # =================================================

            ProcessingLegalBasis.objects.filter(processing=processing).delete()
            legal_basis_id = request.POST.get("legal_basis")
            legal_basis_justification = request.POST.get("legal_basis_justification", "").strip()

            if legal_basis_id:
                ProcessingLegalBasis.objects.create(
                    processing=processing,
                    legal_basis_id=legal_basis_id,
                    justification=legal_basis_justification
                )

            # =================================================
            # CATÉGORIES DE DONNÉES
            # =================================================

            ProcessingDataCategory.objects.filter(processing=processing).delete()
            data_category_ids = request.POST.getlist("data_category")
            data_enumerations = request.POST.getlist("data_enumeration")

            for index, category_id in enumerate(data_category_ids):
                if not category_id:
                    continue

                enumeration = ""

                if index < len(data_enumerations):
                    enumeration = data_enumerations[
                        index
                    ].strip()

                ProcessingDataCategory.objects.create(
                    processing=processing,
                    data_category_id=category_id,
                    data_enumeration=enumeration
                )

            # =================================================
            # PERSONNES CONCERNÉES
            # =================================================

            processing.data_subject_categories.set(request.POST.getlist("data_subject_categories"))

            # =================================================
            # DESTINATAIRES
            # =================================================

            processing.recipients.set(request.POST.getlist("recipients"))

            # =================================================
            # SOUS-TRAITANTS
            # =================================================

            processing.subprocessors.set(request.POST.getlist("subprocessors"))

            # =================================================
            # OPÉRATIONS
            # =================================================

            ProcessingOperation.objects.filter(processing=processing).delete()
            operation_type_ids = request.POST.getlist("operation_type")
            operation_descriptions = request.POST.getlist("operation_description")

            for index, operation_type_id in enumerate(operation_type_ids):
                if not operation_type_id:
                    continue

                description = ""

                if index < len(operation_descriptions):
                    description = operation_descriptions[index].strip()

                ProcessingOperation.objects.create(
                    processing=processing,
                    operation_type_id=operation_type_id,
                    display_order=index + 1,
                    description=description
                )

            # =================================================
            # MESURES DE SÉCURITÉ
            # =================================================

            ProcessingSecurityMeasure.objects.filter(processing=processing).delete()
            security_measure_ids = request.POST.getlist("security_measure")
            security_statuses = request.POST.getlist("security_status")
            security_comments = request.POST.getlist("security_comment")

            for index, security_measure_id in enumerate(security_measure_ids):
                if not security_measure_id:
                    continue

                status = (
                    security_statuses[index]
                    if index < len(security_statuses)
                    else ProcessingSecurityMeasure.Status.PLANNED
                )

                comment = (
                    security_comments[index].strip()
                    if index < len(security_comments)
                    else ""
                )

                ProcessingSecurityMeasure.objects.create(
                    processing=processing,
                    security_measure_id=security_measure_id,
                    status=status,
                    comment=comment
                )

        # =====================================================
        # SUCCÈS
        # =====================================================

        messages.success(request, f"Le traitement « {processing.name} » " "a été modifié avec succès.")
        return redirect("personal_data_processing:processing_detail", id=processing.id)

    # =========================================================
    # GET : FORMULAIRE
    # =========================================================

    context = {
        "processing": processing,
        "legal_bases": LegalBasis.objects.all(),
        "data_categories": DataCategory.objects.all(),
        "data_subject_categories": (DataSubjectCategory.objects.all()),
        "recipients": Recipient.objects.all(),
        "subprocessors": Subprocessor.objects.all(),
        "operation_types": OperationType.objects.all(),
        "security_measures": (SecurityMeasure.objects.all()),
    }

    return render(request, "personal_data_processing/processing_update.html", context)


@login_required
def processings_list_by_user(request):
    """
    Affiche la liste des traitements créés par l'utilisateur connecté.
    """

    processings = (
        DataProcessing.objects
        .filter(
            user=request.user,
            entity=request.user.entity
        )
        .select_related("user")
        .order_by("-updated_at")
    )

    return render(request, "personal_data_processing/processings_list_by_user.html", {"processings": processings,})


@login_required
def processing_delete(request, id):
    """
    Supprime un traitement.

    La suppression est autorisée uniquement au créateur du traitement
    ou au DPO de l'entité à laquelle appartient le traitement.
    """
    processing = get_object_or_404(DataProcessing, id=id, entity=request.user.entity)

    # Vérification des droits
    is_creator = processing.user_id == request.user.id
    is_dpo = request.user.role == User.Role.DPO

    if not is_creator and not is_dpo:
        messages.error(request, "Vous n'êtes pas autorisé à supprimer ce traitement.")
        return redirect("personal_data_processing:processing_detail", id=processing.id)

    # Suppression uniquement en POST
    if request.method == "POST":
        processing.delete()
        messages.success(request, "Le traitement a été supprimé avec succès.")
        return redirect("personal_data_processing:processings_list")

    # Si la requête est en GET, on affiche une confirmation
    return render(request, "personal_data_processing/processing_delete.html", {"processing": processing,})