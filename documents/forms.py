# documents/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Document, DocumentVersion, Category, SharedDocument, DocumentPermission
from django.contrib.auth import get_user_model
import os

User = get_user_model()

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
            
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.txt'
            }),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > self.MAX_FILE_SIZE:
                raise ValidationError('File size must be under 5MB.')
            # Check file extension
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in ['.pdf', '.doc', '.docx', '.txt']:
                raise ValidationError('Only PDF, DOC, DOCX, and TXT files are allowed.')
        return file
    
class DocumentSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search documents...'
        })
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=Category.objects.all(),
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Status')] + Document.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter tags (comma separated)'
        })
    )
    created_after = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    created_before = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(owner=user)

class AdvancedSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title, description or content...'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=None,  # We'll set this in __init__
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Document.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by tags (comma separated)',
            'data-role': 'tagsinput'  # For Bootstrap Tags Input
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('-updated_at', 'Most Recent'),
            ('title', 'Title (A-Z)'),
            ('-title', 'Title (Z-A)'),
            ('-created_at', 'Creation Date'),
            ('category', 'Category'),
        ],
        required=False,
        initial='-updated_at',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set category queryset to user's categories
        self.fields['category'].queryset = Category.objects.filter(owner=user)

class ShareDocumentForm(forms.ModelForm):
    class Meta:
        model = SharedDocument
        fields = ['shared_with', 'permission', 'valid_until']
        widgets = {
            'valid_until': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'shared_with': forms.Select(attrs={'class': 'form-select'}),
            'permission': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.document = kwargs.pop('document')
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        
        # Exclude document owner and already shared users from the choices
        exclude_users = [self.document.owner]
        exclude_users.extend(
            self.document.shared_users.values_list('id', flat=True)
        )
        self.fields['shared_with'].queryset = User.objects.exclude(
            id__in=exclude_users
        ).order_by('username')

        # Set permission choices based on user's permission level
        if self.user != self.document.owner:
            user_permission = self.document.get_user_permission(self.user)
            if user_permission != DocumentPermission.MANAGE:
                self.fields['permission'].choices = [
                    (p.value, p.label) for p in DocumentPermission 
                    if DocumentPermission(p.value).value <= user_permission
                ]

    def clean_valid_until(self):
        valid_until = self.cleaned_data.get('valid_until')
        if valid_until and valid_until <= timezone.now():
            raise forms.ValidationError("The expiration date must be in the future")
        return valid_until