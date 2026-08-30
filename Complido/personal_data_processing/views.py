from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

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
)

from entities.models import Entity
from users.models import User


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
        "personal_data_processing/processing_detail.html",
        {
            "processing": processing,
        },
    )


@login_required
def processing_delete(request, id):

    processing = get_object_or_404(
        DataProcessing,
        id=id
    )

    if request.method == "POST":

        processing_name = processing.name

        processing.delete()

        messages.success(
            request,
            f"Le traitement « {processing_name} » a été supprimé avec succès."
        )

        return redirect(
            "personal_data_processing:processings_list"
        )

    return redirect(
        "personal_data_processing:processing_detail",
        id=processing.id
    )



@login_required
def processing_create(request):
    """
    Création d'un nouveau traitement de données personnelles.
    """

    # =========================================================
    # GET
    # =========================================================

    if request.method == "GET":

        context = {
            "users": User.objects.all().order_by("last_name", "first_name"),
            "entities": Entity.objects.all().order_by("name"),
            "legal_bases": LegalBasis.objects.all(),
            "data_categories": DataCategory.objects.all(),
            "data_subject_categories": DataSubjectCategory.objects.all(),
            "recipients": Recipient.objects.all(),
            "subprocessors": Subprocessor.objects.all(),
            "operation_types": OperationType.objects.all(),
            "security_measures": SecurityMeasure.objects.all(),
        }

        return render(
            request,
            "personal_data_processing/processing_create.html",
            context,
        )

    # =========================================================
    # POST
    # =========================================================

    if request.method == "POST":

        try:

            with transaction.atomic():

                # =================================================
                # 1. RÉCUPÉRATION DES DONNÉES PRINCIPALES
                # =================================================

                name = request.POST.get("name", "").strip()
                description = request.POST.get("description", "").strip()

                entity_id = request.POST.get("entity")
                user_id = request.POST.get("user")

                status = request.POST.get(
                    "status",
                    DataProcessing.Status.DRAFT,
                )

                purpose = request.POST.get("purpose", "").strip()
                subpurpose = request.POST.get("subpurpose", "").strip()

                description_purpose = request.POST.get(
                    "description_purpose",
                    "",
                ).strip()

                legal_basis_id = request.POST.get("legal_basis")

                retention_period = request.POST.get(
                    "retention_period",
                    "",
                ).strip()

                international_transfer = (
                    request.POST.get("international_transfer") == "on"
                )

                aipd_required = (
                    request.POST.get("aipd_required") == "on"
                )


                # =================================================
                # 2. VALIDATIONS MINIMALES
                # =================================================

                if not name:
                    raise ValueError(
                        "Le nom du traitement est obligatoire."
                    )

                if not entity_id:
                    raise ValueError(
                        "L'organisation est obligatoire."
                    )

                if not legal_basis_id:
                    raise ValueError(
                        "La base légale est obligatoire."
                    )

                if not purpose:
                    raise ValueError(
                        "La finalité est obligatoire."
                    )

                if not retention_period:
                    raise ValueError(
                        "La durée de conservation est obligatoire."
                    )


                # =================================================
                # 3. CRÉATION DU TRAITEMENT
                # =================================================

                processing = DataProcessing.objects.create(

                    name=name,

                    description=description,

                    entity_id=entity_id,

                    status=status,

                    user_id=user_id if user_id else None,

                    purpose=purpose,

                    subpurpose=subpurpose,

                    description_purpose=description_purpose,

                    legal_basis_id=legal_basis_id,

                    retention_period=retention_period,

                    international_transfer=international_transfer,

                    aipd_required=aipd_required,

                )


                # =================================================
                # 4. CATÉGORIES DE DONNÉES
                # =================================================

                data_category_ids = request.POST.getlist(
                    "data_categories"
                )

                if data_category_ids:

                    processing.data_categories.set(
                        data_category_ids
                    )


                # =================================================
                # 5. CATÉGORIES DE PERSONNES CONCERNÉES
                # =================================================

                data_subject_category_ids = request.POST.getlist(
                    "data_subject_categories"
                )

                if data_subject_category_ids:

                    processing.data_subject_categories.set(
                        data_subject_category_ids
                    )


                # =================================================
                # 6. DESTINATAIRES
                # =================================================

                recipient_ids = request.POST.getlist(
                    "recipients"
                )

                if recipient_ids:

                    processing.recipients.set(
                        recipient_ids
                    )


                # =================================================
                # 7. SOUS-TRAITANTS
                # =================================================

                subprocessor_ids = request.POST.getlist(
                    "subprocessors"
                )

                if subprocessor_ids:

                    processing.subprocessors.set(
                        subprocessor_ids
                    )


                # =================================================
                # 8. OPÉRATIONS
                # =================================================

                operation_type_ids = request.POST.getlist(
                    "operation_type"
                )

                operation_orders = request.POST.getlist(
                    "operation_order"
                )

                operation_descriptions = request.POST.getlist(
                    "operation_description"
                )


                for index, operation_type_id in enumerate(
                    operation_type_ids
                ):

                    if not operation_type_id:
                        continue


                    # Ordre

                    try:

                        display_order = int(
                            operation_orders[index]
                        )

                    except (
                        ValueError,
                        IndexError,
                    ):

                        display_order = index + 1


                    # Description

                    try:

                        operation_description = (
                            operation_descriptions[index].strip()
                        )

                    except IndexError:

                        operation_description = ""


                    processing.processing_operations.create(

                        operation_type_id=operation_type_id,

                        display_order=display_order,

                        description=operation_description,

                    )


                # =================================================
                # 9. MESURES DE SÉCURITÉ
                # =================================================

                security_measure_ids = request.POST.getlist(
                    "security_measures"
                )


                for security_measure_id in security_measure_ids:

                    status_key = (
                        f"security_status_{security_measure_id}"
                    )

                    comment_key = (
                        f"security_comment_{security_measure_id}"
                    )


                    security_status = request.POST.get(
                        status_key,
                        "PLANNED",
                    )


                    security_comment = request.POST.get(
                        comment_key,
                        "",
                    ).strip()


                    processing.processing_security_measures.create(

                        security_measure_id=security_measure_id,

                        status=security_status,

                        comment=security_comment,

                    )


            # =====================================================
            # 10. MESSAGE DE SUCCÈS
            # =====================================================

            messages.success(
                request,
                f"Le traitement « {processing.name} » a été créé avec succès.",
            )


            # =====================================================
            # 11. REDIRECTION VERS LE DÉTAIL
            # =====================================================

            return redirect(
                "processing_detail",
                id=processing.id,
            )


        except ValueError as error:

            messages.error(
                request,
                str(error),
            )


        except Exception as error:

            messages.error(
                request,
                "Une erreur est survenue lors de la création du traitement.",
            )


    # =========================================================
    # EN CAS D'ERREUR : RÉAFFICHAGE DU FORMULAIRE
    # =========================================================

    context = {

        "users": User.objects.all().order_by(
            "last_name",
            "first_name",
        ),

        "entities": Entity.objects.all().order_by(
            "name"
        ),

        "legal_bases": LegalBasis.objects.all(),

        "data_categories": DataCategory.objects.all(),

        "data_subject_categories": (
            DataSubjectCategory.objects.all()
        ),

        "recipients": Recipient.objects.all(),

        "subprocessors": Subprocessor.objects.all(),

        "operation_types": OperationType.objects.all(),

        "security_measures": SecurityMeasure.objects.all(),

    }


    return render(
        request,
        "personal_data_processing/processing_create.html",
        context,
    )


@login_required
def processing_update(request, id):

    # =========================================================
    # RÉCUPÉRATION DU TRAITEMENT
    # =========================================================

    processing = get_object_or_404(
        DataProcessing,
        id=id
    )


    # =========================================================
    # POST
    # =========================================================

    if request.method == "POST":

        try:

            with transaction.atomic():

                # =================================================
                # INFORMATIONS GÉNÉRALES
                # =================================================

                processing.name = request.POST.get(
                    "name",
                    ""
                ).strip()

                processing.description = request.POST.get(
                    "description",
                    ""
                ).strip()

                processing.status = request.POST.get(
                    "status",
                    DataProcessing.Status.DRAFT
                )

                user_id = request.POST.get("user")

                if user_id:
                    processing.user_id = user_id
                else:
                    processing.user = None


                entity_id = request.POST.get("entity")

                if entity_id:
                    processing.entity_id = entity_id


                # =================================================
                # FINALITÉ
                # =================================================

                processing.purpose = request.POST.get(
                    "purpose",
                    ""
                ).strip()

                processing.subpurpose = request.POST.get(
                    "subpurpose",
                    ""
                ).strip()

                processing.description_purpose = request.POST.get(
                    "description_purpose",
                    ""
                ).strip()


                # =================================================
                # BASE LÉGALE
                # =================================================

                legal_basis_id = request.POST.get(
                    "legal_basis"
                )

                if legal_basis_id:
                    processing.legal_basis_id = legal_basis_id


                # =================================================
                # CONSERVATION
                # =================================================

                processing.retention_period = request.POST.get(
                    "retention_period",
                    ""
                ).strip()


                # =================================================
                # CONFORMITÉ
                # =================================================

                processing.international_transfer = (
                    request.POST.get(
                        "international_transfer"
                    ) == "on"
                )

                processing.aipd_required = (
                    request.POST.get(
                        "aipd_required"
                    ) == "on"
                )


                # =================================================
                # SAUVEGARDE DU TRAITEMENT
                # =================================================

                processing.save()


                # =================================================
                # CATÉGORIES DE DONNÉES
                # =================================================

                data_categories = request.POST.getlist(
                    "data_categories"
                )

                processing.data_categories.set(
                    data_categories
                )


                # =================================================
                # PERSONNES CONCERNÉES
                # =================================================

                data_subject_categories = request.POST.getlist(
                    "data_subject_categories"
                )

                processing.data_subject_categories.set(
                    data_subject_categories
                )


                # =================================================
                # DESTINATAIRES
                # =================================================

                recipients = request.POST.getlist(
                    "recipients"
                )

                processing.recipients.set(
                    recipients
                )


                # =================================================
                # SOUS-TRAITANTS
                # =================================================

                subprocessors = request.POST.getlist(
                    "subprocessors"
                )

                processing.subprocessors.set(
                    subprocessors
                )


                # =================================================
                # OPÉRATIONS
                # =================================================

                # On supprime les anciennes associations.
                processing.processing_operations.all().delete()


                operation_types = request.POST.getlist(
                    "operation_type"
                )

                operation_orders = request.POST.getlist(
                    "operation_order"
                )

                operation_descriptions = request.POST.getlist(
                    "operation_description"
                )


                for index, operation_type_id in enumerate(
                    operation_types
                ):

                    if not operation_type_id:
                        continue


                    # Sécurité au cas où les listes POST
                    # n'auraient pas exactement la même longueur.

                    order = 1

                    if index < len(operation_orders):

                        try:
                            order = int(
                                operation_orders[index]
                            )

                        except (ValueError, TypeError):
                            order = index + 1


                    description = ""

                    if index < len(operation_descriptions):

                        description = (
                            operation_descriptions[index]
                            or ""
                        ).strip()


                    ProcessingOperation.objects.create(

                        processing=processing,

                        operation_type_id=operation_type_id,

                        display_order=order,

                        description=description,

                    )


                # =================================================
                # MESURES DE SÉCURITÉ
                # =================================================

                # On supprime les anciennes associations.

                processing.processing_security_measures.all().delete()


                security_measure_ids = request.POST.getlist(
                    "security_measures"
                )


                for security_measure_id in security_measure_ids:

                    status = request.POST.get(
                        f"security_status_{security_measure_id}",
                        ProcessingSecurityMeasure.Status.PLANNED
                    )


                    comment = request.POST.get(
                        f"security_comment_{security_measure_id}",
                        ""
                    ).strip()


                    ProcessingSecurityMeasure.objects.create(

                        processing=processing,

                        security_measure_id=security_measure_id,

                        status=status,

                        comment=comment,

                    )


                # =================================================
                # MESSAGE DE SUCCÈS
                # =================================================

                messages.success(
                    request,
                    "Le traitement a été modifié avec succès."
                )


                return redirect(
                    "personal_data_processing:processing_detail",
                    id=processing.id
                )


        except Exception as e:

            messages.error(
                request,
                f"Une erreur est survenue lors de la modification du traitement : {e}"
            )


    # =========================================================
    # GET
    # =========================================================

    context = {

        "processing": processing,

        "users": User.objects.all(),

        "entities": Entity.objects.all(),

        "legal_bases": LegalBasis.objects.all(),

        "data_categories": DataCategory.objects.all(),

        "data_subject_categories": DataSubjectCategory.objects.all(),

        "recipients": Recipient.objects.all(),

        "subprocessors": Subprocessor.objects.all(),

        "operation_types": OperationType.objects.all(),

        "security_measures": SecurityMeasure.objects.all(),

    }


    return render(
        request,
        "personal_data_processing/processing_create.html",
        context
    )