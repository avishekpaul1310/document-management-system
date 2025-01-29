from django.urls import  path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.document_list, name='document_list'),
    path('upload/', views.document_upload, name='document_upload'),
    path('document/<int:pk>/', views.document_detail, name='document_detail'),
    path('document/<int:pk>/delete/', views.document_delete, name='document_delete'),
    path('<int:pk>/share/', views.share_document, name='share_document'),
    path('<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('<int:pk>/annotation/', views.add_annotation, name='add_annotation'),
]