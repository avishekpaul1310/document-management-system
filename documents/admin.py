from django.contrib import admin
from .models import Category, Document

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'category', 'uploaded_at', 'is_shared')
    list_filter = ('category', 'is_shared', 'uploaded_at')
    search_fields = ('title', 'description')