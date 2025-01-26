# documents/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Document, DocumentVersion, Category
import os

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter category description'
            })
        }

class DocumentForm(forms.ModelForm):
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = ['.pdf', '.doc', '.docx', '.txt']

    class Meta:
        model = Document
        fields = ['title', 'description', 'file', 'category', 'status', 'tags']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Enter document description'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter document title'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter tags separated by commas'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={
                'class': 'form-select'
            })
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(owner=user)

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size
            if file.size > self.MAX_FILE_SIZE:
                raise ValidationError('File size must be under 5MB.')

            # Check file extension
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in self.ALLOWED_EXTENSIONS:
                raise ValidationError(
                    f'Only the following file types are allowed: {", ".join(self.ALLOWED_EXTENSIONS)}'
                )

        return file

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if tags:
            # Convert tags to lowercase and remove extra spaces
            tags = ','.join(tag.strip().lower() for tag in tags.split(',') if tag.strip())
        return tags

class DocumentVersionForm(forms.ModelForm):
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

    class Meta:
        model = DocumentVersion
        fields = ['file', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Enter version notes (optional)'
            }),
            'file': forms.FileInput(attrs={'class': 'form-control'})
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > self.MAX_FILE_SIZE:
                raise ValidationError('File size must be under 5MB.')
        return file