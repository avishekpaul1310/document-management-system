# documents/management/commands/update_search_vectors.py
from django.core.management.base import BaseCommand
from documents.models import Document

class Command(BaseCommand):
    help = 'Updates search vectors for all documents'

    def handle(self, *args, **options):
        documents = Document.objects.all()
        count = 0
        for document in documents:
            document.update_search_vector()
            count += 1
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated search vectors for {count} documents')
        )