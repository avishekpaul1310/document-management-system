# documents/tests/test_settings.py
from django.test.runner import DiscoverRunner

class CustomTestRunner(DiscoverRunner):
    def setup_databases(self, **kwargs):
        # Use in-memory database for faster tests
        return super().setup_databases(**kwargs)

    def teardown_databases(self, old_config, **kwargs):
        # Clean up after tests
        super().teardown_databases(old_config, **kwargs)