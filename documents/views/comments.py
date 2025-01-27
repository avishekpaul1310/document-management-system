# documents/views/comments.py
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseRedirect

from ..models import Document, Comment, DocumentPermission

class CommentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Comment
    fields = ['content']
    template_name = 'documents/comment_form.html'
    
    def test_func(self):
        document = self.get_document()
        return document.can_user_access(self.request.user, DocumentPermission.COMMENT)
    
    def get_document(self):
        return get_object_or_404(Document, pk=self.kwargs['document_id'])
    
    def form_valid(self, form):
        form.instance.document = self.get_document()
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Comment added successfully.')
        return response
    
    def get_success_url(self):
        return reverse_lazy('document_detail', kwargs={'pk': self.kwargs['document_id']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document'] = self.get_document()
        context['current_time'] = "2025-01-27 22:02:29"
        context['current_user'] = "avishekpaul1310"
        return context

class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    fields = ['content']
    template_name = 'documents/comment_form.html'
    
    def test_func(self):
        return self.get_object().author == self.request.user
    
    def get_success_url(self):
        return reverse_lazy('document_detail', kwargs={'pk': self.get_object().document.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Comment updated successfully.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document'] = self.get_object().document
        context['current_time'] = "2025-01-27 22:02:29"
        context['current_user'] = "avishekpaul1310"
        return context

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'documents/comment_confirm_delete.html'
    
    def test_func(self):
        return self.get_object().author == self.request.user
    
    def get_success_url(self):
        return reverse_lazy('document_detail', kwargs={'pk': self.get_object().document.pk})
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Comment deleted successfully.')
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document'] = self.get_object().document
        context['current_time'] = "2025-01-27 22:02:29"
        context['current_user'] = "avishekpaul1310"
        return context