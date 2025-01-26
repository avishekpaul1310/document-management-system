# documents/tests.py
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Document, Category, DocumentVersion
import tempfile
import os

User = get_user_model()

class DocumentManagementTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
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
        self.test_file = SimpleUploadedFile(
            "test_doc.txt",
            b"This is a test document content",
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
        
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    def tearDown(self):
        # Clean up uploaded files
        if self.document.file:
            if os.path.isfile(self.document.file.path):
                os.remove(self.document.file.path)

    def test_category_operations(self):
        """Test category CRUD operations"""
        # Test category creation
        response = self.client.post(reverse('category_create'), {
            'name': 'New Category',
            'description': 'New Description'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(name='New Category').exists())
        
        # Test category update
        category = Category.objects.get(name='New Category')
        response = self.client.post(
            reverse('category_update', kwargs={'pk': category.pk}),
            {'name': 'Updated Category', 'description': 'Updated Description'}
        )
        self.assertEqual(response.status_code, 302)
        category.refresh_from_db()
        self.assertEqual(category.name, 'Updated Category')

    def test_document_operations(self):
        """Test document CRUD operations"""
        # Test document creation
        new_file = SimpleUploadedFile(
            "another_doc.txt",
            b"This is another test document",
            content_type="text/plain"
        )
        
        response = self.client.post(reverse('document_create'), {
            'title': 'New Document',
            'description': 'New Description',
            'file': new_file,
            'category': self.category.id,
            'status': 'DRAFT'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Document.objects.filter(title='New Document').exists())
        
        # Test document update
        document = Document.objects.get(title='New Document')
        response = self.client.post(
            reverse('document_update', kwargs={'pk': document.pk}),
            {
                'title': 'Updated Document',
                'description': 'Updated Description',
                'category': self.category.id,
                'status': 'IN_REVIEW'
            }
        )
        self.assertEqual(response.status_code, 302)
        document.refresh_from_db()
        self.assertEqual(document.title, 'Updated Document')

    def test_document_versioning(self):
        """Test document versioning functionality"""
        new_version_file = SimpleUploadedFile(
            "version2.txt",
            b"This is version 2 content",
            content_type="text/plain"
        )
        
        # Test adding new version
        response = self.client.post(
            reverse('add_version', kwargs={'pk': self.document.pk}),
            {
                'file': new_version_file,
                'notes': 'Version 2 notes'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.document.refresh_from_db()
        self.assertEqual(self.document.version, 2)

    def test_document_search_and_filter(self):
        """Test search and filter functionality"""
        # Test search
        response = self.client.get(reverse('document_list'), {'q': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Document')
        
        # Test category filter
        response = self.client.get(reverse('document_list'), {'category': self.category.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Document')
        
        # Test status filter
        response = self.client.get(reverse('document_list'), {'status': 'DRAFT'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Document')

    def test_authorization(self):
        """Test authorization and permissions"""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        # Try to access document with other user
        self.client.logout()
        self.client.login(username='otheruser', password='otherpass123')
        
        response = self.client.get(
            reverse('document_detail', kwargs={'pk': self.document.pk})
        )
        self.assertEqual(response.status_code, 404)  # Should not find other user's document