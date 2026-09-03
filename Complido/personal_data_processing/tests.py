import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse

from entities.models import Entity

from personal_data_processing.models import (
    DataProcessing,
    LegalBasis,
)


User = get_user_model()




# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def user(db):
    """
    Création d'un utilisateur de test.
    """
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="TestPassword123!",
    )


@pytest.fixture
def entity(db):
    """
    Création d'une entité de test.
    """
    return Entity.objects.create(
        name="Entreprise de test",
    )


@pytest.fixture
def legal_basis(db):
    """
    Création d'une base légale de test.
    """
    return LegalBasis.objects.create(
        name="Consentement",
        description="Consentement de la personne concernée",
    )


@pytest.fixture
def processing(db, user, entity, legal_basis):
    """
    Création d'un traitement de données de test.
    """
    return DataProcessing.objects.create(
        name="Gestion des candidatures",
        description="Traitement des candidatures",
        entity=entity,
        user=user,
        status="DRAFT",
        purpose="Gérer les candidatures",
        description_purpose="Gestion du recrutement",
        legal_basis=legal_basis,
        retention_period="2 ans",
    )


# ============================================================
# 1. ACCÈS À LA LISTE DES TRAITEMENTS
# ============================================================

@pytest.mark.django_db
def test_processing_list_requires_login(client):
    """
    Vérifie qu'un utilisateur non authentifié
    ne peut pas accéder à la liste des traitements.
    """

    response = client.get(
        reverse(
            "personal_data_processing:processings_list"
        )
    )

    assert response.status_code == 302


# ============================================================
# 2. CRÉATION D'UN TRAITEMENT
# ============================================================

@pytest.mark.django_db
def test_processing_create(
    client,
    user,
    entity,
    legal_basis,
):
    """
    Vérifie qu'un utilisateur authentifié
    peut créer un traitement.
    """

    client.force_login(user)

    response = client.post(
        reverse(
            "personal_data_processing:processing_create"
        ),
        {
            "name": "Gestion des candidatures",
            "description": "Traitement des candidatures",
            "entity": entity.id,
            "user": user.id,
            "status": "DRAFT",
            "purpose": "Gérer les candidatures",
            "description_purpose": "Gestion du recrutement",
            "legal_basis": legal_basis.id,
            "retention_period": "2 ans",
        }
    )

    assert response.status_code == 302

    assert DataProcessing.objects.filter(
        name="Gestion des candidatures"
    ).exists()


# ============================================================
# 3. CONSULTATION D'UN TRAITEMENT
# ============================================================

@pytest.mark.django_db
def test_processing_detail(
    client,
    user,
    processing,
):
    """
    Vérifie qu'un utilisateur authentifié
    peut consulter un traitement.
    """

    client.force_login(user)

    response = client.get(
        reverse(
            "personal_data_processing:processing_detail",
            kwargs={
                "id": processing.id
            },
        )
    )

    assert response.status_code == 200

    assert response.context["processing"] == processing


# ============================================================
# 4. MODIFICATION D'UN TRAITEMENT
# ============================================================

@pytest.mark.django_db
def test_processing_update(
    client,
    user,
    processing,
    entity,
    legal_basis,
):
    """
    Vérifie qu'un utilisateur authentifié
    peut modifier un traitement.
    """

    client.force_login(user)

    response = client.post(
        reverse(
            "personal_data_processing:processing_update",
            kwargs={
                "id": processing.id
            },
        ),
        {
            "name": "Traitement modifié",
            "description": "Nouvelle description",
            "entity": entity.id,
            "user": user.id,
            "status": "DRAFT",
            "purpose": "Nouvelle finalité",
            "description_purpose": "Nouvelle description",
            "legal_basis": legal_basis.id,
            "retention_period": "3 ans",
        }
    )

    assert response.status_code == 302

    processing.refresh_from_db()

    assert processing.name == "Traitement modifié"

    assert processing.description == (
        "Nouvelle description"
    )

    assert processing.purpose == (
        "Nouvelle finalité"
    )

    assert processing.retention_period == "3 ans"


# ============================================================
# 5. SUPPRESSION D'UN TRAITEMENT
# ============================================================

@pytest.mark.django_db
def test_processing_delete(
    client,
    user,
    processing,
):
    """
    Vérifie qu'un utilisateur authentifié
    peut supprimer un traitement.
    """

    client.force_login(user)

    processing_id = processing.id

    response = client.post(
        reverse(
            "personal_data_processing:processing_delete",
            kwargs={
                "id": processing_id
            },
        )
    )

    assert response.status_code == 302

    assert not DataProcessing.objects.filter(
        id=processing_id
    ).exists()