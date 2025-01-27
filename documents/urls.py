# documents/urls.py
from django.urls import path
from . import views
from .views.sharing import SharedDocumentListView, ShareDocumentView
from .views import (
    DocumentListView, DocumentDetailView, DocumentCreateView,
    DocumentUpdateView, DocumentDeleteView, DocumentDownloadView,
    CategoryListView, CategoryDetailView, CategoryCreateView,
    CategoryUpdateView, CategoryDeleteView
)

urlpatterns = [
    # Existing document URLs
    path('', views.DocumentListView.as_view(), name='document_list'),
    path('document/new/', views.DocumentCreateView.as_view(), name='document_create'),
    path('document/<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('document/<int:pk>/edit/', views.DocumentUpdateView.as_view(), name='document_update'),
    path('document/<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='document_delete'),
    path('document/<int:pk>/version/add/', views.add_version, name='add_version'),
    path('document/<int:pk>/version/<int:version_number>/download/', views.download_version, name='download_version'),
    
    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/new/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    path('categories/<int:pk>/', 
         views.CategoryDetailView.as_view(), 
         name='category_detail'),
    path('document/<int:pk>/version/new/', 
         views.DocumentVersionCreateView.as_view(), 
         name='document_version_create'),
    path('document/<int:pk>/versions/', 
         views.DocumentVersionListView.as_view(), 
         name='document_versions'),
     path('document/<int:pk>/version/new/', 
         views.DocumentVersionCreateView.as_view(), 
         name='document_version_create'),
    path('document/<int:pk>/versions/', 
         views.DocumentVersionListView.as_view(), 
         name='document_versions'),
    path('search/', views.DocumentSearchView.as_view(), name='document_search'),
    path('shared/', SharedDocumentListView.as_view(), name='shared_documents'),
    path('document/<int:pk>/share/', ShareDocumentView.as_view(), name='share_document'),
]