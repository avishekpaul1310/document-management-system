# documents/tests/test_performance.py
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.test.client import Client
import time

class PerformanceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_document_list_performance(self):
        # Create 100 test documents
        for i in range(100):
            Document.objects.create(
                title=f'Test Document {i}',
                owner=self.user
            )

        start_time = time.time()
        response = self.client.get(reverse('document_list'))
        end_time = time.time()

        # Assert response time is under 1 second
        self.assertLess(end_time - start_time, 1.0)
        self.assertEqual(response.status_code, 200)