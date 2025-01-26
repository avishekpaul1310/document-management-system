from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.http import FileResponse
from django.utils.decorators import method_decorator
from .models import Document, DocumentVersion,Category
from .forms import DocumentForm, DocumentVersionForm, CategoryForm
from .decorators import user_is_document_owner
import os

class DocumentListView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'documents/document_list.html'
    context_object_name = 'documents'
    paginate_by = 10
    ordering = ['-updated_at']

    def get_queryset(self):
        queryset = Document.objects.filter(owner=self.request.user)
        query = self.request.GET.get('q')
        category_id = self.request.GET.get('category')
        status_filter = self.request.GET.get('status')
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__icontains=query)
            )
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        if status_filter and status_filter != 'ALL':
            queryset = queryset.filter(status=status_filter)
            
        return queryset.order_by(self.ordering[0])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(owner=self.request.user)
        context['current_category'] = self.request.GET.get('category')
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

    # Add this method here
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

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

    # Add this method here
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

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

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'documents/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add document count for each category
        categories = context['categories']
        for category in categories:
            category.doc_count = category.documents.count()
        return context

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'documents/category_form.html'
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Category created successfully!')
        return super().form_valid(form)

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'documents/category_form.html'
    success_url = reverse_lazy('category_list')

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)
    def form_valid(self, form):
        messages.success(self.request, 'Category updated successfully!')
        return super().form_valid(form)

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'documents/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Category deleted successfully!')
        return super().delete(request, *args, **kwargs)
    
    class DocumentVersionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
     model = DocumentVersion
    form_class = DocumentVersionForm
    template_name = 'documents/document_version_form.html'

    def test_func(self):
        document = get_object_or_404(Document, pk=self.kwargs['pk'])
        return document.owner == self.request.user

    def form_valid(self, form):
        document = get_object_or_404(Document, pk=self.kwargs['pk'])
        form.instance.document = document
        response = super().form_valid(form)
        # Create new version and update document
        document.create_new_version(
            file=form.cleaned_data['file'],
            notes=form.cleaned_data['notes']
        )
        messages.success(self.request, 'New version uploaded successfully.')
        return response

    def get_success_url(self):
        return reverse_lazy('document_detail', kwargs={'pk': self.kwargs['pk']})

class DocumentVersionListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = DocumentVersion
    template_name = 'documents/document_versions.html'
    context_object_name = 'versions'

    def test_func(self):
        document = get_object_or_404(Document, pk=self.kwargs['pk'])
        return document.owner == self.request.user

    def get_queryset(self):
        document = get_object_or_404(Document, pk=self.kwargs['pk'])
        return document.versions.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        document = get_object_or_404(Document, pk=self.kwargs['pk'])
        context['document'] = document
        return context
