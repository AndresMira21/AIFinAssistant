"""
urls.py — Chatbot App
"""

from django.urls import path
from . import views

app_name = "chatbot"

urlpatterns = [
    path("", views.chat_view, name="chat"),
    path("api/", views.chat_api, name="chat_api"),
    path("api/history/<int:session_id>/", views.get_chat_history, name="chat_history"),
    path("api/delete/<int:session_id>/", views.delete_chat, name="chat_delete"),
]
