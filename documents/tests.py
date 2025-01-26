# documents/tests.py
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Document, Category
import tempfile

class DocumentSystemTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Description',
            owner=self.user
        )
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.txt')
        self.temp_file.write(b'Test content')
        self.temp_file.seek(0)
        
    def test_document_creation(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('document_create'), {
            'title': 'Test Document',
            'description': 'Test Description',
            'file': self.temp_file,
            'category': self.category.id,
            'status': 'DRAFT'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after creation
        self.assertTrue(Document.objects.filter(title='Test Document').exists())

    def test_document_list(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('document_list'))
        self.assertEqual(response.status_code, 200)

    def test_category_creation(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('category_create'), {
            'name': 'New Category',
            'description': 'New Description'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(name='New Category').exists())