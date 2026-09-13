import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse

from personal_data_processing.models import (
    DataProcessing,
    LegalBasis,
    ProcessingLegalBasis,
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
        entity="COMPLIDO",
    )


@pytest.fixture
def dpo_user(db):
    """
    Création d'un utilisateur DPO de test.
    """

    return User.objects.create_user(
        username="dpo",
        email="dpo@example.com",
        password="TestPassword123!",
        entity="COMPLIDO",
        role=User.Role.DPO,
    )


@pytest.fixture
def another_user(db):
    """
    Création d'un autre utilisateur de la même entité.
    """

    return User.objects.create_user(
        username="anotheruser",
        email="another@example.com",
        password="TestPassword123!",
        entity="COMPLIDO",
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
def processing(db, user, legal_basis):
    """
    Création d'un traitement de données de test.
    """

    processing = DataProcessing.objects.create(
        name="Gestion des candidatures",
        description="Traitement des candidatures",
        entity=user.entity,
        user=user,
        status="DRAFT",
        purpose="Gérer les candidatures",
        description_purpose="Gestion du recrutement",
        retention_period="2 ans",
    )

    ProcessingLegalBasis.objects.create(
        processing=processing,
        legal_basis=legal_basis,
    )

    return processing


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
# 1.1. LISTE DES TRAITEMENTS DE L'ENTITÉ
# ============================================================

@pytest.mark.django_db
def test_processing_list(
    client,
    user,
    processing,
):
    """
    Vérifie qu'un utilisateur authentifié peut consulter
    les traitements de son entité.
    """

    client.force_login(user)

    response = client.get(
        reverse(
            "personal_data_processing:processings_list"
        )
    )

    assert response.status_code == 200
    assert processing in response.context["processings"]


# ============================================================
# 2. CRÉATION D'UN TRAITEMENT
# ============================================================

@pytest.mark.django_db
def test_processing_create(
    client,
    user,
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
            "status": "DRAFT",
            "purpose": "Gérer les candidatures",
            "description_purpose": "Gestion du recrutement",
            "legal_basis": legal_basis.id,
            "retention_period": "2 ans",
        }
    )

    assert response.status_code == 302

    assert DataProcessing.objects.filter(
        name="Gestion des candidatures",
        user=user,
        entity=user.entity,
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
    Vérifie qu'un utilisateur authentifié peut consulter
    un traitement de son entité.
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
    legal_basis,
):
    """
    Vérifie que le créateur d'un traitement peut le modifier.
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

    assert processing.user == user
    assert processing.entity == user.entity


# ============================================================
# 4.1. MODIFICATION PAR UN DPO
# ============================================================

@pytest.mark.django_db
def test_processing_update_by_dpo(
    client,
    dpo_user,
    processing,
    legal_basis,
):
    """
    Vérifie qu'un DPO peut modifier un traitement
    appartenant à son entité.
    """

    client.force_login(dpo_user)

    response = client.post(
        reverse(
            "personal_data_processing:processing_update",
            kwargs={
                "id": processing.id
            },
        ),
        {
            "name": "Traitement modifié par le DPO",
            "description": "Description modifiée par le DPO",
            "status": "DRAFT",
            "purpose": "Nouvelle finalité",
            "description_purpose": "Nouvelle description",
            "legal_basis": legal_basis.id,
            "retention_period": "3 ans",
        }
    )

    assert response.status_code == 302

    processing.refresh_from_db()

    assert processing.name == (
        "Traitement modifié par le DPO"
    )

    assert processing.entity == dpo_user.entity


# ============================================================
# 4.2. MODIFICATION PAR UN AUTRE UTILISATEUR
# ============================================================

@pytest.mark.django_db
def test_processing_update_forbidden(
    client,
    another_user,
    processing,
):
    """
    Vérifie qu'un utilisateur qui n'est ni le créateur
    ni le DPO de l'entité ne peut pas modifier le traitement.
    """

    client.force_login(another_user)

    response = client.post(
        reverse(
            "personal_data_processing:processing_update",
            kwargs={
                "id": processing.id
            },
        ),
        {
            "name": "Modification interdite",
        }
    )

    assert response.status_code == 302

    processing.refresh_from_db()

    assert processing.name != "Modification interdite"


# ============================================================
# 4.3. MODIFICATION PAR UN DPO D'UNE AUTRE ENTITÉ
# ============================================================

@pytest.mark.django_db
def test_processing_update_by_dpo_other_entity(
    client,
    processing,
):
    """
    Vérifie qu'un DPO d'une autre entité ne peut pas
    modifier le traitement.
    """

    other_dpo = User.objects.create_user(
        username="otherdpo",
        email="otherdpo@example.com",
        password="TestPassword123!",
        entity="TROPICO",
        role=User.Role.DPO,
    )

    client.force_login(other_dpo)

    response = client.post(
        reverse(
            "personal_data_processing:processing_update",
            kwargs={
                "id": processing.id
            },
        ),
        {
            "name": "Modification interdite",
        }
    )

    assert response.status_code == 404

    processing.refresh_from_db()

    assert processing.name != "Modification interdite"


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
    Vérifie que le créateur d'un traitement peut le supprimer.
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


# ============================================================
# 5.1. SUPPRESSION PAR UN DPO
# ============================================================

@pytest.mark.django_db
def test_processing_delete_by_dpo(
    client,
    dpo_user,
    processing,
):
    """
    Vérifie qu'un DPO peut supprimer un traitement
    appartenant à son entité.
    """

    client.force_login(dpo_user)

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


# ============================================================
# 5.2. SUPPRESSION PAR UN AUTRE UTILISATEUR
# ============================================================

@pytest.mark.django_db
def test_processing_delete_forbidden(
    client,
    another_user,
    processing,
):
    """
    Vérifie qu'un utilisateur qui n'est ni le créateur
    ni le DPO de l'entité ne peut pas supprimer le traitement.
    """

    client.force_login(another_user)

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

    assert DataProcessing.objects.filter(
        id=processing_id
    ).exists()


# ============================================================
# 5.3. SUPPRESSION PAR UN DPO D'UNE AUTRE ENTITÉ
# ============================================================

@pytest.mark.django_db
def test_processing_delete_by_dpo_other_entity(
    client,
    processing,
):
    """
    Vérifie qu'un DPO d'une autre entité ne peut pas
    supprimer le traitement.
    """

    other_dpo = User.objects.create_user(
        username="otherdpo",
        email="otherdpo@example.com",
        password="TestPassword123!",
        entity="TROPICO",
        role=User.Role.DPO,
    )

    client.force_login(other_dpo)

    processing_id = processing.id

    response = client.post(
        reverse(
            "personal_data_processing:processing_delete",
            kwargs={
                "id": processing_id
            },
        )
    )

    assert response.status_code == 404

    assert DataProcessing.objects.filter(
        id=processing_id
    ).exists()