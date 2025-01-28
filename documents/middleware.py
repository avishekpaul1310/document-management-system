# documents/middleware.py

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.urls import resolve
from .models import Document, DocumentPermission
import logging

logger = logging.getLogger(__name__)

class DocumentPermissionMiddleware:
    """
    Middleware to handle document permissions across the application.
    Checks if users have appropriate permissions before accessing document-related views.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Views that require specific permissions
        self.permission_map = {
                    'document_detail': DocumentPermission.VIEW,
                    'document_update': DocumentPermission.EDIT,
                    'document_delete': DocumentPermission.MANAGE,
                    'document_share': DocumentPermission.MANAGE,
                    'document_version_create': DocumentPermission.EDIT,
                    'document_versions': DocumentPermission.VIEW,
                    'document_download': DocumentPermission.VIEW,
                    'comment_create': DocumentPermission.COMMENT,
                    'comment_edit': DocumentPermission.COMMENT,
                    'comment_delete': DocumentPermission.COMMENT,
        }

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            return None

        try:
            # Get the URL name
            url_name = resolve(request.path_info).url_name
            
            # Skip if the view doesn't require permission checking
            if url_name not in self.permission_map:
                return None

            # Get document ID from kwargs or query params
            document_id = view_kwargs.get('pk') or request.GET.get('document_id')
            if not document_id:
                return None

            # Get the document
            document = get_object_or_404(Document, pk=document_id)
            required_permission = self.permission_map[url_name]

            # Check if user has required permission
            if not document.can_user_access(request.user, required_permission):
                logger.warning(
                    f"Permission denied for user {request.user.username} "
                    f"accessing {url_name} for document {document_id}"
                )
                raise PermissionDenied(
                    f"You don't have {required_permission} permission for this document."
                )

            # Log successful access
            logger.info(
                f"User {request.user.username} granted {required_permission} "
                f"access to document {document_id}"
            )
            
            # Add document and permission to request for use in view
            request.document = document
            request.document_permission = required_permission
            
            return None

        except Exception as e:
            logger.error(
                f"Error in DocumentPermissionMiddleware: {str(e)}", 
                exc_info=True
            )
            raise