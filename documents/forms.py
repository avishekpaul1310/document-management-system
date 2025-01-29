from django import forms
from .models import Document

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'description', 'file', 'category', 'is_shared']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }