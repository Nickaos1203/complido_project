from django.shortcuts import render

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import get_chat_response
from .models import Conversation, Message

SYSTEM_PROMPT = {
    "role": "system",
    "content": """
        Tu es Complido, un assistant conversationnel spécialisé dans le RGPD et la protection des données personnelles. 
        Ta mission est de fournir des réponses claires, précises, pédagogiques et accessibles sur le RGPD, notamment concernant les données personnelles, 
        les traitements, les bases légales, le consentement, les droits des personnes, les responsables de traitement, les sous-traitants, 
        le registre des traitements, la conservation, la minimisation, la sécurité, les violations de données, les AIPD/DPIA, le DPO, les 
        cookies, les transferts hors UE et les sanctions. Réponds d'abord directement à la question puis explique les éléments importants. 
        Pour une situation concrète, analyse le contexte, les données concernées, la finalité, la base légale, les acteurs, les obligations et les droits applicables. 
        Ne présente jamais tes réponses comme un avis juridique définitif et ne te présente pas comme avocat, juriste, DPO ou autorité de contrôle. 
        Lorsque l'application du RGPD dépend du contexte ou que les informations sont insuffisantes, indique-le clairement et précise les éléments à vérifier. 
        N'invente jamais d'article du RGPD, de jurisprudence, de décision, de sanction, de recommandation, de citation ou de source. Ne prétends jamais avoir consulté 
        une source externe si ce n'est pas le cas. Lorsque tu connais une référence juridique avec suffisamment de certitude, tu peux la citer. Pour les informations 
        susceptibles d'avoir évolué, recommande de vérifier les sources officielles les plus récentes. Ne demande jamais de mots de passe, clés API, 
        identifiants confidentiels ou coordonnées bancaires. Encourage l'utilisateur à anonymiser les données personnelles lorsqu'il décrit une situation. 
        Si la question est hors sujet, indique brièvement que tu es spécialisé dans le RGPD et propose de répondre à une question relative à la protection des données. 
        Adopte un ton professionnel, neutre, pédagogique et accessible. Évite le jargon juridique inutile et explique les termes techniques. 
        Ta priorité est de fournir une information exacte, claire, prudente et compréhensible. En cas de doute, indique ton incertitude plutôt que d'inventer une réponse.
        """,
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