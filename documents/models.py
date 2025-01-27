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
        related_name='shared_with_me'
    )

    def get_user_permission(self, user):
        """Get the permission level for a specific user"""
        if user == self.owner:
            return DocumentPermission.MANAGE
        try:
            share = self.shares.get(
                shared_with=user,
                is_active=True,
                valid_until__isnull=True) | \
                self.shares.get(
                    shared_with=user,
                    is_active=True,
                    valid_until__gt=timezone.now()
                )
            return share.permission
        except SharedDocument.DoesNotExist:
            return None

    def can_user_access(self, user, required_permission=DocumentPermission.VIEW_ONLY):
        """Check if a user has at least the required permission level"""
        if user == self.owner:
            return True
        
        permission = self.get_user_permission(user)
        if not permission:
            return False

        permission_levels = {
            DocumentPermission.VIEW_ONLY: 0,
            DocumentPermission.COMMENT: 1,
            DocumentPermission.EDIT: 2,
            DocumentPermission.MANAGE: 3
        }

        return permission_levels[permission] >= permission_levels[required_permission]
    
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