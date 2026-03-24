"""
views.py — Chatbot App
----------------------
Handles the chat interface and the JSON API endpoint for AJAX messages.
"""

import json
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services.ai_service import answer_financial_question
from .models import ChatSession, ChatMessage

logger = logging.getLogger(__name__)

def chat_view(request):
    """Render the main chat page interface with session history."""
    sessions = ChatSession.objects.all()
    return render(request, "chatbot/chat.html", {"sessions": sessions})

@csrf_exempt
def chat_api(request):
    """
    JSON endpoint for sending messages to the chatbot with session persistence.
    Expects POST request with JSON body {"message": "...", "session_id": int|null}.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()
            session_id = data.get("session_id")
            
            if not user_message:
                return JsonResponse({"error": "Mensaje vacío."}, status=400)
            
            # 1. Get or Create Session
            if session_id:
                try:
                    session = ChatSession.objects.get(id=session_id)
                except ChatSession.DoesNotExist:
                    session = ChatSession.objects.create(title=user_message[:50])
            else:
                session = ChatSession.objects.create(title=user_message[:50])

            # 2. Save User Message
            ChatMessage.objects.create(session=session, role='user', content=user_message)

            # 3. Get AI Response
            bot_response = answer_financial_question(user_message)

            # 4. Save Bot Message
            ChatMessage.objects.create(session=session, role='bot', content=bot_response)

            return JsonResponse({
                "response": bot_response,
                "session_id": session.id,
                "session_title": session.title
            })
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON no válido."}, status=400)
        except Exception as e:
            logger.error(f"Error in chat_api: {e}")
            return JsonResponse({"error": str(e)}, status=500)
            
    return JsonResponse({"error": "Método no permitido."}, status=405)

def get_chat_history(request, session_id):
    """Return all messages for a specific session."""
    try:
        session = ChatSession.objects.get(id=session_id)
        messages = session.messages.all()
        history = [
            {'role': m.role, 'content': m.content, 'created_at': m.created_at.isoformat()}
            for m in messages
        ]
        return JsonResponse({'history': history, 'title': session.title})
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Sesión no encontrada'}, status=404)

@csrf_exempt
def delete_chat(request, session_id):
    """Delete a chat session."""
    if request.method == 'POST':
        try:
            session = ChatSession.objects.get(id=session_id)
            session.delete()
            return JsonResponse({'status': 'success'})
        except ChatSession.DoesNotExist:
            return JsonResponse({'error': 'Sesión no encontrada'}, status=404)
    return JsonResponse({'error': 'Método no permitido'}, status=405)
