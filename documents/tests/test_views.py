# documents/tests/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from documents.models import Document, Category

class DocumentViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        
    def test_document_creation_flow(self):
        # Test creating a new document
        response = self.client.post(reverse('document_create'), {
            'title': 'New Document',
            'description': 'Test Description',
            'status': 'DRAFT'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Document.objects.filter(title='New Document').exists())

    def test_document_sharing_flow(self):
        other_user = User.objects.create_user(username='other', password='12345')
        doc = Document.objects.create(title='Share Test', owner=self.user)
        
        # Test sharing document
        response = self.client.post(reverse('share_document', kwargs={'pk': doc.pk}), {
            'shared_with': other_user.id,
            'permission': DocumentPermission.VIEW_ONLY
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(doc.shared_users.filter(id=other_user.id).exists())