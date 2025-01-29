from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User  # Add this line
from .models import (
    Document, Category, SharedDocument, 
    DocumentAccessHistory, Comment, Annotation
)
from .forms import DocumentForm

def check_document_permission(user, document, required_level):
    if user == document.owner:
        return True
    try:
        shared_doc = SharedDocument.objects.get(document=document, shared_with=user)
        permission_levels = {
            'VIEW': 0,
            'COMMENT': 1,
            'EDIT': 2,
            'MANAGE': 3
        }
        return permission_levels[shared_doc.permission_level] >= permission_levels[required_level]
    except SharedDocument.DoesNotExist:
        return False

def log_document_access(user, document, action, details=''):
    DocumentAccessHistory.objects.create(
        user=user,
        document=document,
        action=action,
        details=details
    )

# Add these new view functions
@login_required
def share_document(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if not check_document_permission(request.user, document, 'MANAGE'):
        raise PermissionDenied
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        permission_level = request.POST.get('permission_level')
        user_to_share_with = get_object_or_404(User, id=user_id)
        
        SharedDocument.objects.update_or_create(
            document=document,
            shared_with=user_to_share_with,
            defaults={
                'permission_level': permission_level,
                'shared_by': request.user
            }
        )
        
        log_document_access(
            request.user, 
            document, 
            'SHARE', 
            f'Shared with {user_to_share_with.username} ({permission_level})'
        )
        
        messages.success(request, f'Document shared with {user_to_share_with.username}')
        return redirect('documents:document_detail', pk=pk)
    
    return render(request, 'documents/share_document.html', {
        'document': document,
        'users': User.objects.exclude(id=request.user.id)
    })

@login_required
def add_comment(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if not check_document_permission(request.user, document, 'COMMENT'):
        raise PermissionDenied
    
    if request.method == 'POST':
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        
        comment = Comment.objects.create(
            document=document,
            author=request.user,
            content=content,
            parent_id=parent_id if parent_id else None
        )
        
        log_document_access(request.user, document, 'COMMENT')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'comment_id': comment.id,
                'author': comment.author.username,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
            
        return redirect('documents:document_detail', pk=pk)
    
    return redirect('documents:document_detail', pk=pk)

@login_required
def add_annotation(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if not check_document_permission(request.user, document, 'COMMENT'):
        raise PermissionDenied
    
    if request.method == 'POST':
        annotation = Annotation.objects.create(
            document=document,
            author=request.user,
            content=request.POST.get('content'),
            position_x=request.POST.get('x'),
            position_y=request.POST.get('y'),
            page_number=request.POST.get('page', 1)
        )
        
        log_document_access(request.user, document, 'COMMENT', 'Added annotation')
        
        return JsonResponse({
            'status': 'success',
            'annotation_id': annotation.id
        })
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def document_list(request):
    documents = Document.objects.filter(owner=request.user)
    categories = Category.objects.all()
    return render(request, 'documents/document_list.html', {
        'documents': documents,
        'categories': categories
    })

@login_required
def document_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.owner = request.user
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('documents:document_list')
    else:
        form = DocumentForm()
    return render(request, 'documents/document_upload.html', {'form': form})

@login_required
def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if document.owner == request.user or document.is_shared:
        return render(request, 'documents/document_detail.html', {'document': document})
    messages.error(request, 'You do not have permission to view this document.')
    return redirect('documents:document_list')

@login_required
def document_delete(request, pk):
    document = get_object_or_404(Document, pk=pk, owner=request.user)
    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Document deleted successfully!')
    return redirect('documents:document_list')