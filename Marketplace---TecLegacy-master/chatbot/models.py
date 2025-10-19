from django.db import models


class ChatbotQuery(models.Model):
    query = models.CharField(max_length=255)
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'consulta chatbot'
        verbose_name_plural = 'consultas chatbot'

    def __str__(self):
        return self.query