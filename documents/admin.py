# documents/admin.py
from django.contrib import admin
from django.db import models  # Add this import
from .models import Document, DocumentVersion, Category, SharedDocument

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'status', 'version', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'tags')
    date_hierarchy = 'created_at'

@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ('document', 'version_number', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('document__title', 'notes')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at', 'updated_at')
    list_filter = ('created_at', 'owner')
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'

@admin.register(SharedDocument)
class SharedDocumentAdmin(admin.ModelAdmin):
    list_display = ('document', 'shared_by', 'shared_with', 'permission', 'shared_at', 'is_active')
    list_filter = ('permission', 'is_active', 'shared_at')
    search_fields = ('document__title', 'shared_by__username', 'shared_with__username')
    date_hierarchy = 'shared_at'
    raw_id_fields = ('document', 'shared_by', 'shared_with')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(
                models.Q(document__owner=request.user) |
                models.Q(shared_by=request.user) |
                models.Q(shared_with=request.user)
            )
        return qs