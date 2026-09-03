import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()


@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="TestPassword123!",
        first_name="Nicolas",
        last_name="Test",
    )

    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.first_name == "Nicolas"
    assert user.last_name == "Test"
    assert user.is_active is True


@pytest.mark.django_db
def test_password_is_hashed():
    user = User.objects.create_user(
        username="testuser",
        password="TestPassword123!",
    )

    assert user.password != "TestPassword123!"
    assert user.check_password("TestPassword123!")


@pytest.mark.django_db
def test_register_creates_user(client):
    response = client.post(
        reverse("users:register"),
        {
            "first_name": "Jean",
            "last_name": "Dupont",
            "username": "jeandupont",
            "email": "jean@example.com",
            "department": "RH",
            "password1": "TestPassword123!",
            "password2": "TestPassword123!",
        }
    )

    assert response.status_code == 302

    user = User.objects.get(
        username="jeandupont"
    )

    assert user.first_name == "Jean"
    assert user.last_name == "Dupont"
    assert user.email == "jean@example.com"
    assert user.department == "RH"

    # Le rôle n'est pas choisi à l'inscription.
    assert user.role == User.Role.REFERENT


@pytest.mark.django_db
def test_login_success(client):
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="TestPassword123!",
    )

    response = client.post(
        reverse("users:login"),
        {
            "username": "testuser",
            "password": "TestPassword123!",
        }
    )

    assert response.status_code == 302
    assert client.session.get("_auth_user_id") == str(user.pk)


@pytest.mark.django_db
def test_login_failure(client):
    User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="TestPassword123!",
    )

    response = client.post(
        reverse("users:login"),
        {
            "username": "testuser",
            "password": "WrongPassword123!",
        }
    )

    assert response.status_code == 302
    assert "_auth_user_id" not in client.session