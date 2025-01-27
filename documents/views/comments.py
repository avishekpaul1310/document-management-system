# views/comments.py
class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['content']
    template_name = 'documents/comment_form.html'
    
    def form_valid(self, form):
        form.instance.document_id = self.kwargs['document_id']
        form.instance.author = self.request.user
        return super().form_valid(form)