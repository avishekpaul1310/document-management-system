from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Document, Category
from .forms import DocumentForm

@login_required
def document_list(request):
    category_id = request.GET.get('category')
    if category_id:
        documents = Document.objects.filter(
            owner=request.user,
            category_id=category_id
        )
    else:
        documents = Document.objects.filter(owner=request.user)
    
    categories = Category.objects.all()
    return render(request, 'documents/document_list.html', {
        'documents': documents,
        'categories': categories,
        'current_category': category_id
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