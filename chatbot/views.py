"""
views.py — Chatbot App
----------------------
Handles the chat interface and the JSON API endpoint for AJAX messages.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services.ai_service import answer_financial_question
import json
import logging

logger = logging.getLogger(__name__)

def chat_view(request):
    """Render the main chat page interface."""
    return render(request, "chatbot/chat.html")

@csrf_exempt
def chat_api(request):
    """
    JSON endpoint for sending messages to the chatbot.
    Expects POST request with JSON body {"message": "..."}.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()
            
            if not user_message:
                return JsonResponse({"error": "Mensaje vacío."}, status=400)
                
            # Here we route to our rule-based AI service.
            bot_response = answer_financial_question(user_message)
            
            return JsonResponse({"response": bot_response})
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON no válido."}, status=400)
        except Exception as e:
            logger.error(f"Error in chat_api: {e}")
            return JsonResponse({"error": "Ocurrió un error interno."}, status=500)
            
    return JsonResponse({"error": "Método no permitido."}, status=405)
