from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from .models import Document, DocumentVersion
from .forms import DocumentForm, DocumentVersionForm
from .decorators import user_is_document_owner

class DocumentListView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'documents/document_list.html'
    context_object_name = 'documents'
    paginate_by = 10
    ordering = ['-updated_at']

    def get_queryset(self):
        queryset = Document.objects.filter(owner=self.request.user)
        query = self.request.GET.get('q')
        status_filter = self.request.GET.get('status')
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__icontains=query)
            )
        
        if status_filter and status_filter != 'ALL':
            queryset = queryset.filter(status=status_filter)
            
        return queryset.order_by(self.ordering[0])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_search'] = self.request.GET.get('q', '')
        context['current_status'] = self.request.GET.get('status', 'ALL')
        context['status_choices'] = Document.STATUS_CHOICES
        return context

class DocumentDetailView(LoginRequiredMixin, DetailView):
    model = Document
    template_name = 'documents/document_detail.html'
    context_object_name = 'document'

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['versions'] = self.object.versions.all().order_by('-version_number')
        context['version_form'] = DocumentVersionForm()
        return context

class DocumentCreateView(LoginRequiredMixin, CreateView):
    model = Document
    form_class = DocumentForm
    template_name = 'documents/document_form.html'
    success_url = reverse_lazy('document_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Document created successfully!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Document'
        context['button_text'] = 'Create Document'
        return context

class DocumentUpdateView(LoginRequiredMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = 'documents/document_form.html'

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Document updated successfully!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Document'
        context['button_text'] = 'Update Document'
        return context

class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = Document
    template_name = 'documents/document_confirm_delete.html'
    success_url = reverse_lazy('document_list')

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Document deleted successfully!')
        return super().delete(request, *args, **kwargs)

@login_required
def add_version(request, pk):
    document = get_object_or_404(Document, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        form = DocumentVersionForm(request.POST, request.FILES)
        if form.is_valid():
            version = form.save(commit=False)
            version.document = document
            version.version_number = document.version + 1
            version.save()
            
            document.version = version.version_number
            document.save()
            
            messages.success(request, f'Version {version.version_number} added successfully!')
            return redirect('document_detail', pk=pk)
    else:
        form = DocumentVersionForm()
    
    return render(request, 'documents/version_form.html', {
        'form': form,
        'document': document
    })

@login_required
def download_version(request, pk, version_number):
    document = get_object_or_404(Document, pk=pk, owner=request.user)
    version = get_object_or_404(DocumentVersion, document=document, version_number=version_number)
    
    response = FileResponse(version.file, as_attachment=True)
    response['Content-Disposition'] = f'attachment; filename="{document.title}_v{version_number}{os.path.splitext(version.file.name)[1]}"'
    return response