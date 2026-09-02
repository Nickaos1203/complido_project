from django.urls import path
from .views import chat_view

app_name = "comments"

urlpatterns = [
    path("api/chat/", chat_view, name="api_chat"),
]