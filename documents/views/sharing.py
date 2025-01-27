# documents/views/sharing.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from ..models import Document, SharedDocument, DocumentPermission
from ..forms import ShareDocumentForm 

class SharedDocumentListView(LoginRequiredMixin, ListView):
    model = SharedDocument
    template_name = 'documents/shared_document_list.html'
    context_object_name = 'shared_documents'

    def get_queryset(self):
        return SharedDocument.objects.filter(
            Q(document__owner=self.request.user) |
            Q(shared_by=self.request.user) |
            Q(shared_with=self.request.user)
        ).select_related('document', 'shared_by', 'shared_with')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_time'] = timezone.now()
        context['current_user'] = self.request.user
        context['shared_by_me'] = self.get_queryset().filter(shared_by=self.request.user)
        context['shared_with_me'] = self.get_queryset().filter(shared_with=self.request.user)
        return context

class ShareDocumentView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = SharedDocument
    form_class = ShareDocumentForm
    template_name = 'documents/share_document.html'
    
    def test_func(self):
        document = self.get_document()
        return document.owner == self.request.user or document.can_user_access(self.request.user, DocumentPermission.MANAGE)
    
    def get_document(self):
        return get_object_or_404(Document, pk=self.kwargs['pk'])
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['document'] = self.get_document()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document'] = self.get_document()
        return context
    
    def form_valid(self, form):
        form.instance.document = self.get_document()
        form.instance.shared_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f'Document shared successfully with {form.instance.shared_with}')
        return response
    
    def get_success_url(self):
        return reverse_lazy('document_detail', kwargs={'pk': self.kwargs['pk']})