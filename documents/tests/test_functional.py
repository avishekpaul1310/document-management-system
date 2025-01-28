# documents/tests/test_functional.py
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from documents.models import Document
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

class DocumentManagementTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode (no GUI)
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Initialize Chrome WebDriver with ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        cls.selenium = webdriver.Chrome(
            service=service,
            options=chrome_options
        )
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        if cls.selenium:
            cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='12345',
            email='test@example.com'
        )

    def test_document_upload_workflow(self):
        try:
            # Login
            self.selenium.get(f'{self.live_server_url}/login/')
            username_input = self.selenium.find_element(By.NAME, "username")
            username_input.send_keys('testuser')
            password_input = self.selenium.find_element(By.NAME, "password")
            password_input.send_keys('12345')
            self.selenium.find_element(By.XPATH, "//button[text()='Login']").click()

            # Navigate to document upload
            self.selenium.get(f'{self.live_server_url}/documents/create/')
            
            # Fill form
            title_input = self.selenium.find_element(By.NAME, "title")
            title_input.send_keys('Selenium Test Document')
            
            # Submit form
            self.selenium.find_element(By.XPATH, "//button[text()='Create Document']").click()
            
            # Verify document creation
            self.assertTrue(Document.objects.filter(title='Selenium Test Document').exists())
            
        except Exception as e:
            # Take screenshot on failure
            self.selenium.save_screenshot('test_failure.png')
            raise e

    def test_document_view(self):
        # Create a test document
        doc = Document.objects.create(
            title='Test View Document',
            owner=self.user
        )

        try:
            # Login
            self.selenium.get(f'{self.live_server_url}/login/')
            username_input = self.selenium.find_element(By.NAME, "username")
            username_input.send_keys('testuser')
            password_input = self.selenium.find_element(By.NAME, "password")
            password_input.send_keys('12345')
            self.selenium.find_element(By.XPATH, "//button[text()='Login']").click()

            # Navigate to document detail
            self.selenium.get(f'{self.live_server_url}/documents/{doc.pk}/')
            
            # Verify document title is present
            title_element = self.selenium.find_element(By.CLASS_NAME, "document-title")
            self.assertEqual(title_element.text, 'Test View Document')
            
        except Exception as e:
            # Take screenshot on failure
            self.selenium.save_screenshot('test_failure.png')
            raise e