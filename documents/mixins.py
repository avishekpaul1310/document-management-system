from django.utils import timezone
from .models import DocumentAccessLog

class DocumentAccessLogMixin:
    def log_access(self, document, action, additional_data=None):
        DocumentAccessLog.objects.create(
            document=document,
            user=self.request.user,
            action=action,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT'),
            additional_data=additional_data
        )