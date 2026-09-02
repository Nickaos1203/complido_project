from django.shortcuts import render

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import get_chat_response
from .models import Conversation, Message

SYSTEM_PROMPT = {
    "role": "system",
    "content": "Tu es un assistant français utile et concis.",
}

@csrf_exempt
def chat_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    body = json.loads(request.body)
    user_message = body.get("message", "").strip()
    if not user_message:
        return JsonResponse({"error": "Message vide"}, status=400)

    # Récupère/crée la conversation (utilisateur authentifié ou session)
    if request.user.is_authenticated:
        conversation, _ = Conversation.objects.get_or_create(
            user=request.user
        )
    else:
        session_key = request.session.session_key or ""
        conversation, _ = Conversation.objects.get_or_create(
            session_key=session_key
        )

    # Sauvegarde le message utilisateur
    Message.objects.create(
        conversation=conversation, role="user", content=user_message
    )

    # Reconstruit l'historique
    history = [SYSTEM_PROMPT]
    for m in conversation.messages.all():
        history.append({"role": m.role, "content": m.content})

    try:
        reply = get_chat_response(history)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    # Sauvegarde la réponse du bot
    Message.objects.create(
        conversation=conversation, role="assistant", content=reply
    )

    return JsonResponse({"reply": reply})