from django.db import models

class ChatSession(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=150, help_text="Título autogenerado basado en la primera pregunta", default="Nuevo Chat")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ChatMessage(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('bot', 'Bot'),
    )
    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.session_id}] {self.role}: {self.content[:30]}..."
