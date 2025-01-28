# documents/models.py
from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ValidationError

class DocumentPermission(models.TextChoices):
    VIEW_ONLY = 'VIEW', 'View Only'
    COMMENT = 'COMMENT', 'Comment'
    EDIT = 'EDIT', 'Edit'
    MANAGE = 'MANAGE', 'Manage'

class SharedDocument(models.Model):
    document = models.ForeignKey(
        'Document',
        on_delete=models.CASCADE,
        related_name='shares'
    )
    shared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shared_documents'
    )
    shared_with = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_shares'
    )
    permission = models.CharField(
        max_length=10,
        choices=DocumentPermission.choices,
        default=DocumentPermission.VIEW_ONLY
    )
    shared_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Leave empty for indefinite access"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive shares don't grant access"
    )

    class Meta:
        ordering = ['-shared_at']
        unique_together = ['document', 'shared_with']
        verbose_name = 'Shared Document'
        verbose_name_plural = 'Shared Documents'

    def __str__(self):
        return f"{self.document.title} - Shared with {self.shared_with.username}"

    def clean(self):
        # Prevent sharing with document owner
        if self.shared_with == self.document.owner:
            raise ValidationError("Cannot share document with its owner")
        
        # Prevent sharing by non-owners without MANAGE permission
        if self.shared_by != self.document.owner:
            try:
                share = SharedDocument.objects.get(
                    document=self.document,
                    shared_with=self.shared_by,
                    is_active=True
                )
                if share.permission != DocumentPermission.MANAGE:
                    raise ValidationError(
                        "You need MANAGE permission to share this document"
                    )
            except SharedDocument.DoesNotExist:
                raise ValidationError(
                    "Only the document owner or users with MANAGE permission can share"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='categories'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['name']
        unique_together = ['name', 'owner']  # Prevent duplicate category names per user

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'pk': self.pk})

# Update Document model to include category# documents/models.py
class Document(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('IN_REVIEW', 'In Review'),
        ('FINAL', 'Final'),
    ]
    
    shared_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='SharedDocument',
        related_name='shared_with_me',
        through_fields=('document', 'shared_with')
    )

    def get_user_permission(self, user):
        """Get the permission level for a specific user"""
        if user == self.owner:
            return DocumentPermission.MANAGE
        try:
            share = self.shares.filter(
                shared_with=user,
                is_active=True
            ).filter(
                models.Q(valid_until__isnull=True) |
                models.Q(valid_until__gt=timezone.now())
            ).first()
            return share.permission if share else None
        except SharedDocument.DoesNotExist:
            return None

    def can_user_access(self, user, permission_level):
        """Check if user has the required permission level for this document."""
        if user == self.owner:
            return True
            
        share = self.shares.filter(shared_with=user, is_active=True).first()
        if not share:
            return False

        permission_hierarchy = {
            DocumentPermission.VIEW: 0,
            DocumentPermission.COMMENT: 1,
            DocumentPermission.EDIT: 2,
            DocumentPermission.MANAGE: 3
        }

        required_level = permission_hierarchy.get(permission_level, 0)
        user_level = permission_hierarchy.get(share.permission, 0)

        return user_level >= required_level
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='documents/')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    tags = models.CharField(max_length=200, blank=True, help_text='Comma separated tags')
    version = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('document_detail', kwargs={'pk': self.pk})

class DocumentVersion(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    file = models.FileField(upload_to='document_versions/')
    version_number = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-version_number']

    def __str__(self):
        return f"{self.document.title} - v{self.version_number}"
    
# Add this to documents/models.py after the DocumentVersion model

class DocumentAccessLog(models.Model):
    ACTION_CHOICES = [
        ('VIEW', 'Viewed'),
        ('DOWNLOAD', 'Downloaded'),
        ('EDIT', 'Edited'),
        ('SHARE', 'Shared'),
        ('COMMENT', 'Commented'),
    ]
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='access_logs'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='document_access_logs'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES
    )
    accessed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )
    user_agent = models.TextField(blank=True)
    additional_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional context about the action"
    )

    class Meta:
        ordering = ['-accessed_at']
        verbose_name = 'Document Access Log'
        verbose_name_plural = 'Document Access Logs'

    def __str__(self):
        return f"{self.document.title} - {self.get_action_display()} by {self.user.username}"