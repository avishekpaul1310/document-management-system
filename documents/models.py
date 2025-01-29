from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Document(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_shared = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-uploaded_at']

    def get_shared_users(self):
        return SharedDocument.objects.filter(document=self)

    def is_user_allowed(self, user, permission_level='VIEW'):
        if user == self.owner:
            return True
        try:
            shared_doc = SharedDocument.objects.get(document=self, shared_with=user)
            permission_levels = {
                'VIEW': 0,
                'COMMENT': 1,
                'EDIT': 2,
                'MANAGE': 3
            }
            return permission_levels[shared_doc.permission_level] >= permission_levels[permission_level]
        except SharedDocument.DoesNotExist:
            return False    

class SharedDocument(models.Model):
    PERMISSION_LEVELS = [
        ('VIEW', 'View Only'),
        ('COMMENT', 'Can Comment'),
        ('EDIT', 'Can Edit'),
        ('MANAGE', 'Can Manage'),
    ]
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE)
    permission_level = models.CharField(max_length=10, choices=PERMISSION_LEVELS, default='VIEW')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_by_user')
    shared_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['document', 'shared_with']

class DocumentAccessHistory(models.Model):
    ACTION_TYPES = [
        ('VIEW', 'Viewed'),
        ('EDIT', 'Edited'),
        ('SHARE', 'Shared'),
        ('COMMENT', 'Commented'),
    ]
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

class Comment(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    class Meta:
        ordering = ['created_at']

class Annotation(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='annotations')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    position_x = models.FloatField()
    position_y = models.FloatField()
    page_number = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)