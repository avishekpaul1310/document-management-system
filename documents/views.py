from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.http import FileResponse
from .models import Document, DocumentVersion,Category, DocumentAccessLog
from .forms import DocumentForm, DocumentVersionForm, CategoryForm, AdvancedSearchForm
import os
from django.utils import timezone
from .mixins import DocumentAccessLogMixin

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

class DocumentDetailView(LoginRequiredMixin, DocumentAccessLogMixin, DetailView):
    model = Document
    template_name = 'documents/document_detail.html'
    context_object_name = 'document'

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)

    def get_context_data(self, request, *args, **kwargs):
        context = super().get_context_data(request, *args, **kwargs)
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
    
class DocumentDownloadView(LoginRequiredMixin, DocumentAccessLogMixin, DetailView):
    model = Document

    def get(self, request, *args, **kwargs):
        document = self.get_object()
        self.log_access(document, 'DOWNLOAD')
        return redirect(document.file.url)

class DocumentUpdateView(LoginRequiredMixin, DocumentAccessLogMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    fields = ['title', 'description', 'category', 'status', 'tags']
    template_name = 'documents/document_form.html'

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        self.log_access(self.object, 'EDIT', {
            'changed_fields': form.changed_data
        })
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
    
class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = 'documents/category_detail.html'
    context_object_name = 'category'

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)
    
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
        form.instance.version_number = document.version + 1
        response = super().form_valid(form)
        
        # Update document version number
        document.version = form.instance.version_number
        document.save()
        
        messages.success(self.request, 'New version uploaded successfully.')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document'] = get_object_or_404(Document, pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        return reverse('document_detail', kwargs={'pk': self.kwargs['pk']})

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
        context['document'] = get_object_or_404(Document, pk=self.kwargs['pk'])
        return context
    
class DocumentSearchView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'documents/document_search.html'
    context_object_name = 'documents'
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AdvancedSearchForm(
            self.request.user,
            initial=self.request.GET
        )
        context['current_time'] = timezone.now()
        context['current_user'] = self.request.user
        return context
    
    def get_queryset(self):
        form = AdvancedSearchForm(self.request.user, self.request.GET)
        queryset = Document.objects.filter(owner=self.request.user)

        if form.is_valid():
            # Text search
            query = form.cleaned_data.get('query')
            if query:
                # Exact title match gets priority
                title_exact = Q(title__iexact=query)
                title_contains = Q(title__icontains=query)
                description_contains = Q(description__icontains=query)
                tags_contains = Q(tags__icontains=query)
                
                # First try exact match
                exact_matches = queryset.filter(title_exact)
                if exact_matches.exists():
                    queryset = exact_matches
                else:
                    # Then try partial matches
                    queryset = queryset.filter(
                        title_contains | description_contains | tags_contains
                    )

            # Category filter
            category = form.cleaned_data.get('category')
            if category:
                queryset = queryset.filter(category=category)

            # Status filter
            status = form.cleaned_data.get('status')
            if status:
                queryset = queryset.filter(status=status)

            # Tags filter
            tags = form.cleaned_data.get('tags')
            if tags:
                for tag in tags.split(','):
                    tag = tag.strip()
                    if tag:
                        queryset = queryset.filter(tags__icontains=tag)

            # Date range filter
            date_from = form.cleaned_data.get('date_from')
            if date_from:
                queryset = queryset.filter(created_at__date__gte=date_from)

            date_to = form.cleaned_data.get('date_to')
            if date_to:
                queryset = queryset.filter(created_at__date__lte=date_to)

            # Sorting
            sort_by = form.cleaned_data.get('sort_by')
            if sort_by:
                queryset = queryset.order_by(sort_by)
            else:
                queryset = queryset.order_by('-updated_at')

        return queryset.distinct()
    
class DocumentAccessLogView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = DocumentAccessLog
    template_name = 'documents/access_logs.html'
    context_object_name = 'logs'
    paginate_by = 50

    def test_func(self):
        document = Document.objects.get(pk=self.kwargs['pk'])
        return document.can_user_access(self.request.user, DocumentPermission.MANAGE)

    def get_queryset(self):
        return DocumentAccessLog.objects.filter(
            document_id=self.kwargs['pk']
        ).select_related('user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document'] = Document.objects.get(pk=self.kwargs['pk'])
        context['current_time'] = "2025-01-27 22:38:02"
        context['current_user'] = "avishekpaul1310"
        return context