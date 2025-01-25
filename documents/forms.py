from django import forms
from django.core.exceptions import ValidationError
from .models import Document, DocumentVersion
import os
import magic

class DocumentForm(forms.ModelForm):
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_TYPES = {
        'application/pdf': '.pdf',
        'application/msword': '.doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'text/plain': '.txt'
    }

    class Meta:
        model = Document
        fields = ['title', 'description', 'file', 'status', 'tags']
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
            'file': forms.FileInput(attrs={'class': 'form-control'})
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size
            if file.size > self.MAX_FILE_SIZE:
                raise ValidationError('File size must be under 5MB.')

            # Check file type
            try:
                mime = magic.from_buffer(file.read(1024), mime=True)
                file.seek(0)  # Reset file pointer
                
                if mime not in self.ALLOWED_TYPES:
                    allowed_extensions = ', '.join(self.ALLOWED_TYPES.values())
                    raise ValidationError(f'Only the following file types are allowed: {allowed_extensions}')
            except IOError:
                raise ValidationError('Error reading file. Please try again.')

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