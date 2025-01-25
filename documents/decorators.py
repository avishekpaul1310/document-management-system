# documents/decorators.py
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.shortcuts import redirect
from functools import wraps

def user_is_document_owner(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        document = view_func.get_object() if hasattr(view_func, 'get_object') else None
        if document and document.owner == request.user:
            return view_func(request, *args, **kwargs)
        messages.error(request, "You don't have permission to access this document.")
        return redirect('document_list')
    return _wrapped_view