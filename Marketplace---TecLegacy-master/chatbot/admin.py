from django.contrib import admin
from .models import ChatbotQuery

@admin.register(ChatbotQuery)
class ChatbotQueryAdmin(admin.ModelAdmin):
    list_display = ['query', 'created_at']
    search_fields = ['query', 'response']
    list_filter = ['created_at']