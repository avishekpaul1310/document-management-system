# documents/urls.py
from django.urls import path
from . import views

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
]