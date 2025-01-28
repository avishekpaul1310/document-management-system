# documents/tests/__init__.py
from django.conf import settings

def pytest_configure():
    settings.TEST_MODE = True