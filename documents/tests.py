# documents/tests.py
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Document, Category, DocumentVersion
import os

class DocumentManagementTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
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
        
        # Create test document
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
        
        # Set up the test client and login
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

    def test_document_detail(self):
        """Test document detail view"""
        response = self.client.get(
            reverse('document_detail', kwargs={'pk': self.document.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Document')

    def test_document_create(self):
        """Test document creation"""
        new_file = SimpleUploadedFile(
            "new_doc.txt",
            b"This is a new test document",
            content_type="text/plain"
        )
        
        form_data = {
            'title': 'New Document',
            'description': 'New Description',
            'category': self.category.id,
            'status': 'DRAFT',
            'tags': 'test,document',
            'file': new_file
        }
        
        response = self.client.post(reverse('document_create'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Should redirect after creation
        self.assertTrue(Document.objects.filter(title='New Document').exists())

    def test_document_update(self):
        """Test document update"""
        update_data = {
            'title': 'Updated Document',
            'description': 'Updated Description',
            'category': self.category.id,
            'status': 'IN_REVIEW',
            'tags': 'test,updated'
        }
        
        response = self.client.post(
            reverse('document_update', kwargs={'pk': self.document.pk}),
            data=update_data
        )
        
        self.assertEqual(response.status_code, 302)
        self.document.refresh_from_db()
        self.assertEqual(self.document.title, 'Updated Document')

    def test_file_validation(self):
        """Test file validation"""
        # Test file size validation (larger than 5MB)
        large_file = SimpleUploadedFile(
            "large_file.txt",
            b"x" * (6 * 1024 * 1024),
            content_type="text/plain"
        )
        
        form_data = {
            'title': 'Large File Test',
            'description': 'Testing file size validation',
            'category': self.category.id,
            'status': 'DRAFT',
            'tags': 'test,validation',
            'file': large_file
        }
        
        response = self.client.post(
            reverse('document_create'),
            data=form_data,
            follow=True
        )
        
        self.assertFalse(Document.objects.filter(title='Large File Test').exists())

    def tearDown(self):
        """Clean up after tests"""
        # Clean up uploaded files
        if self.document.file:
            if os.path.isfile(self.document.file.path):
                os.remove(self.document.file.path)
                
        # Clean up test files in media directory
        for doc in Document.objects.all():
            if doc.file and os.path.isfile(doc.file.path):
                os.remove(doc.file.path)
                
        # Delete test data
        self.user.delete()  # This will cascade delete related objects

        # documents/tests.py
    def test_document_versioning(self):
     """Test document version control functionality"""
    # Create a new version of the document
    new_version_file = SimpleUploadedFile(
        "version2.txt",
        b"This is version 2 content",
        content_type="text/plain"
    )
    
    response = self.client.post(
        reverse('document_version_create', kwargs={'pk': self.document.pk}),
        {
            'file': new_version_file,
            'notes': 'Updated content for version 2'
        }
    )
    
    # Check if redirect was successful
    self.assertEqual(response.status_code, 302)
    
    # Refresh document from database
    self.document.refresh_from_db()
    
    # Check if version number was incremented
    self.assertEqual(self.document.version, 2)
    
    # Check if version was created
    self.assertTrue(
        self.document.versions.filter(version_number=2).exists()
    )
    
    # Test version listing
    response = self.client.get(
        reverse('document_versions', kwargs={'pk': self.document.pk})
    )
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'version2.txt')
    self.assertContains(response, 'Updated content for version 2')