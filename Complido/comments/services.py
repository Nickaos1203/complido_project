from mistralai.client import Mistral
from django.conf import settings

client = Mistral(api_key=settings.MISTRAL_API_KEY)

def get_chat_response(messages):
    """
    messages : liste de dicts {"role": "user"|"assistant"|"system", "content": "..."}
    """
    response = client.chat.complete(
        model=settings.MISTRAL_MODEL,
        messages=messages,
    )
    return response.choices[0].message.content