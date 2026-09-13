import pytest

from comments.services import get_chat_response


@pytest.mark.django_db
def test_mistral_returns_response(mocker):
    """
    Vérifie que le service retourne correctement
    le contenu de la réponse Mistral.
    """

    mock_response = mocker.Mock()
    mock_choice = mocker.Mock()

    mock_choice.message.content = (
        "Une donnée personnelle est une information "
        "se rapportant à une personne identifiée ou identifiable."
    )

    mock_response.choices = [mock_choice]

    mocker.patch(
        "comments.services.client.chat.complete",
        return_value=mock_response,
    )

    messages = [
        {
            "role": "user",
            "content": "Qu'est-ce qu'une donnée personnelle ?",
        }
    ]

    response = get_chat_response(messages)

    assert response == (
        "Une donnée personnelle est une information "
        "se rapportant à une personne identifiée ou identifiable."
    )


@pytest.mark.django_db
def test_mistral_receives_messages(mocker):
    """
    Vérifie que les messages sont correctement transmis
    à l'API Mistral.
    """

    mock_response = mocker.Mock()
    mock_choice = mocker.Mock()
    mock_choice.message.content = "Réponse RGPD"
    mock_response.choices = [mock_choice]

    mock_complete = mocker.patch(
        "comments.services.client.chat.complete",
        return_value=mock_response,
    )

    messages = [
        {
            "role": "user",
            "content": "Qu'est-ce qu'un traitement de données ?",
        }
    ]

    get_chat_response(messages)

    mock_complete.assert_called_once()

    call_kwargs = mock_complete.call_args.kwargs

    assert call_kwargs["messages"] == messages


@pytest.mark.django_db
def test_mistral_uses_configured_model(mocker, settings):
    """
    Vérifie que le modèle Mistral configuré
    dans les paramètres Django est utilisé.
    """

    mock_response = mocker.Mock()
    mock_choice = mocker.Mock()
    mock_choice.message.content = "Réponse RGPD"
    mock_response.choices = [mock_choice]

    mock_complete = mocker.patch(
        "comments.services.client.chat.complete",
        return_value=mock_response,
    )

    settings.MISTRAL_MODEL = "mistral-small-latest"

    messages = [
        {
            "role": "user",
            "content": "Qu'est-ce que le RGPD ?",
        }
    ]

    get_chat_response(messages)

    call_kwargs = mock_complete.call_args.kwargs

    assert call_kwargs["model"] == "mistral-small-latest"


@pytest.mark.django_db
def test_mistral_api_error(mocker):
    """
    Vérifie qu'une erreur provenant de l'API Mistral
    est correctement remontée.
    """

    mocker.patch(
        "comments.services.client.chat.complete",
        side_effect=Exception("Erreur API Mistral"),
    )

    messages = [
        {
            "role": "user",
            "content": "Qu'est-ce que le RGPD ?",
        }
    ]

    with pytest.raises(
        Exception,
        match="Erreur API Mistral",
    ):
        get_chat_response(messages)


@pytest.mark.django_db
def test_mistral_empty_response(mocker):
    """
    Vérifie le comportement du service lorsqu'une
    réponse vide est retournée par Mistral.
    """

    mock_response = mocker.Mock()
    mock_choice = mocker.Mock()
    mock_choice.message.content = ""
    mock_response.choices = [mock_choice]

    mocker.patch(
        "comments.services.client.chat.complete",
        return_value=mock_response,
    )

    messages = [
        {
            "role": "user",
            "content": "Qu'est-ce qu'une donnée personnelle ?",
        }
    ]

    response = get_chat_response(messages)

    assert response == ""