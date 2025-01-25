# documents/admin.py
from django.contrib import admin
from .models import Document, DocumentVersion

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'version', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'tags')
    date_hierarchy = 'created_at'

@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ('document', 'version_number', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('document__title', 'notes')