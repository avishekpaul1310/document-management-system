# documents/tests.py
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Document, Category, DocumentVersion
import os

class DocumentManagementTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test category
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Description',
            owner=self.user
        )
        
        # Create test document with proper file handling
        self.test_file_content = b"This is a test document content"
        self.test_file = SimpleUploadedFile(
            "test_doc.txt",
            self.test_file_content,
            content_type="text/plain"
        )
        
        self.document = Document.objects.create(
            title='Test Document',
            description='Test Description',
            file=self.test_file,
            owner=self.user,
            category=self.category,
            status='DRAFT'
        )
        
        # Set up the test client
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    def test_authentication(self):
        """Test authentication requirements"""
        # Test login required
        self.client.logout()
        response = self.client.get(reverse('document_list'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        
        # Test successful login
        logged_in = self.client.login(username='testuser', password='testpass123')
        self.assertTrue(logged_in)

    def test_category_list(self):
        """Test category listing"""
        response = self.client.get(reverse('category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Category')

    def test_document_list(self):
        """Test document listing"""
        response = self.client.get(reverse('document_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Document')

    def test_document_operations(self):
        """Test document CRUD operations"""
        # Test document creation
        new_file = SimpleUploadedFile(
            "another_doc.txt",
            b"This is another test document",
            content_type="text/plain"
        )
        
        form_data = {
            'title': 'New Document',
            'description': 'New Description',
            'category': self.category.id,
            'status': 'DRAFT',
            'tags': 'test,document'
        }
        
        form_files = {
            'file': new_file
        }
        
        response = self.client.post(
            reverse('document_create'),
            data={**form_data, **form_files}
        )
        
        self.assertEqual(response.status_code, 302)  # Should redirect after creation
        self.assertTrue(Document.objects.filter(title='New Document').exists())
        
        # Test document update
        document = Document.objects.get(title='New Document')
        update_data = {
            'title': 'Updated Document',
            'description': 'Updated Description',
            'category': self.category.id,
            'status': 'IN_REVIEW',
            'tags': 'test,updated'
        }
        
        response = self.client.post(
            reverse('document_update', kwargs={'pk': document.pk}),
            data=update_data
        )
        
        self.assertEqual(response.status_code, 302)
        document.refresh_from_db()
        self.assertEqual(document.title, 'Updated Document')

    def test_category_specific_operations(self):
        """Test category-specific operations"""
        # Create a new category
        category_data = {
            'name': 'Test Category 2',
            'description': 'Another test category'
        }
        
        response = self.client.post(
            reverse('category_create'),
            data=category_data
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(name='Test Category 2').exists())
        
        # Test category listing
        response = self.client.get(reverse('category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Category 2')
        
        # Test category update
        category = Category.objects.get(name='Test Category 2')
        update_data = {
            'name': 'Updated Category',
            'description': 'Updated test category'
        }
        
        response = self.client.post(
            reverse('category_update', kwargs={'pk': category.pk}),
            data=update_data
        )
        
        self.assertEqual(response.status_code, 302)
        category.refresh_from_db()
        self.assertEqual(category.name, 'Updated Category')

    def test_file_validation(self):
     """Test file validation"""
    # Test file size validation
    large_file = SimpleUploadedFile(
        "large_file.txt",
        b"x" * (6 * 1024 * 1024),  # 6MB file (larger than 5MB limit)
        content_type="text/plain"
    )
    
    form_data = {
        'title': 'Large File Test',
        'description': 'Testing file size validation',
        'category': self.category.id,
        'status': 'DRAFT',
        'tags': 'test,validation'
    }
    
    response = self.client.post(
        reverse('document_create'),
        data={**form_data, 'file': large_file},
        follow=True  # Follow redirects
    )
    
    # Check that the form was invalid
    self.assertFalse(Document.objects.filter(title='Large File Test').exists())
    self.assertContains(response, 'File size must be under 5MB')

    # Test invalid file type
    invalid_file = SimpleUploadedFile(
        "test.exe",
        b"Invalid file content",
        content_type="application/x-msdownload"
    )
    
    response = self.client.post(
        reverse('document_create'),
        data={**form_data, 'file': invalid_file},
        follow=True
    )
    
    self.assertFalse(Document.objects.filter(title='Large File Test').exists())
    self.assertContains(response, 'Only the following file types are allowed')

    def tearDown(self):
        # Clean up uploaded files
        if self.document.file:
            if os.path.isfile(self.document.file.path):
                os.remove(self.document.file.path)
        # Clean up any other test files
        for doc in Document.objects.all():
            if doc.file and os.path.isfile(doc.file.path):
                os.remove(doc.file.path)
        # Delete the test user and related objects
        self.user.delete()