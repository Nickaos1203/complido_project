from django.test import TestCase

# Create your tests here.
import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_login_page(client):
    response = client.get(reverse("login"))
    assert response.status_code == 200