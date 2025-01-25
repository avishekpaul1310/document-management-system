# documents/models.py
from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.conf import settings

class Document(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('IN_REVIEW', 'In Review'),
        ('FINAL', 'Final'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='documents/')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    tags = models.CharField(max_length=200, blank=True, help_text='Comma separated tags')
    version = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('document_detail', kwargs={'pk': self.pk})
    
    def get_latest_version(self):
        return self.versions.first()

    def create_new_version(self, file, notes=''):
        version = DocumentVersion.objects.create(
            document=self,
            file=file,
            version_number=self.version + 1,
            notes=notes
        )
        self.version = version.version_number
        self.save()
        return version

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