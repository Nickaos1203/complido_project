from django.test import TestCase

# Create your tests here.
import pytest

@pytest.mark.django_db
def test_creation_traitement(client, user):
    client.force_login(user)

    response = client.post(
        "/data_processings/create/",
        {
            "nom": "Gestion des candidatures",
        }
    )

    assert response.status_code in [200, 302]