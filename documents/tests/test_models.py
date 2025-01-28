# documents/tests/test_models.py
from django.test import TestCase
from django.contrib.auth.models import User
from documents.models import Document, Category, SharedDocument, DocumentPermission

class DocumentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='Test Category', owner=self.user)
        self.document = Document.objects.create(
            title='Test Document',
            owner=self.user,
            category=self.category
        )

    def test_document_creation(self):
        self.assertEqual(self.document.title, 'Test Document')
        self.assertEqual(self.document.owner, self.user)
        self.assertEqual(self.document.version, 1)

    def test_document_permissions(self):
        other_user = User.objects.create_user(username='other', password='12345')
        SharedDocument.objects.create(
            document=self.document,
            shared_by=self.user,
            shared_with=other_user,
            permission=DocumentPermission.VIEW_ONLY
        )
        self.assertTrue(self.document.can_user_access(other_user, DocumentPermission.VIEW_ONLY))
        self.assertFalse(self.document.can_user_access(other_user, DocumentPermission.EDIT))