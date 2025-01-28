# documents/tests/test_functional.py
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from documents.models import Document
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentManagementTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        logger.info("Setting up Chrome WebDriver...")
        try:
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in headless mode
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            # Setup ChromeDriver with explicit service
            service = Service(ChromeDriverManager().install())
            cls.selenium = webdriver.Chrome(
                service=service,
                options=chrome_options
            )
            cls.selenium.implicitly_wait(10)
            logger.info("Chrome WebDriver setup completed successfully")
        
        except Exception as e:
            logger.error(f"Failed to setup Chrome WebDriver: {str(e)}")
            raise

    @classmethod
    def tearDownClass(cls):
        logger.info("Tearing down Chrome WebDriver...")
        if hasattr(cls, 'selenium'):
            cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        logger.info("Setting up test user...")
        self.user = User.objects.create_user(
            username='testuser',
            password='12345',
            email='test@example.com'
        )

    def test_document_upload_workflow(self):
        """Test the document upload workflow"""
        logger.info("Starting document upload workflow test...")
        try:
            # Login
            self.selenium.get(f'{self.live_server_url}/login/')
            logger.info(f"Navigated to login page: {self.live_server_url}/login/")
            
            username_input = self.selenium.find_element(By.NAME, "username")
            username_input.send_keys('testuser')
            
            password_input = self.selenium.find_element(By.NAME, "password")
            password_input.send_keys('12345')
            
            self.selenium.find_element(By.XPATH, "//button[text()='Login']").click()
            logger.info("Logged in successfully")

            # Navigate to document upload
            self.selenium.get(f'{self.live_server_url}/documents/create/')
            logger.info("Navigated to document creation page")
            
            # Fill form
            title_input = self.selenium.find_element(By.NAME, "title")
            title_input.send_keys('Selenium Test Document')
            logger.info("Filled document form")
            
            # Submit form
            self.selenium.find_element(By.XPATH, "//button[text()='Create Document']").click()
            logger.info("Submitted document form")
            
            # Verify document creation
            self.assertTrue(
                Document.objects.filter(title='Selenium Test Document').exists(),
                "Document was not created successfully"
            )
            logger.info("Document creation verified")
            
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            self.selenium.save_screenshot('test_failure.png')
            raise

    def test_document_view(self):
        """Test viewing a document"""
        logger.info("Starting document view test...")
        try:
            # Create a test document
            doc = Document.objects.create(
                title='Test View Document',
                owner=self.user
            )
            logger.info(f"Created test document with ID: {doc.id}")

            # Login
            self.selenium.get(f'{self.live_server_url}/login/')
            username_input = self.selenium.find_element(By.NAME, "username")
            username_input.send_keys('testuser')
            password_input = self.selenium.find_element(By.NAME, "password")
            password_input.send_keys('12345')
            self.selenium.find_element(By.XPATH, "//button[text()='Login']").click()
            logger.info("Logged in successfully")

            # Navigate to document detail
            self.selenium.get(f'{self.live_server_url}/documents/{doc.pk}/')
            logger.info(f"Navigated to document detail page for ID: {doc.pk}")
            
            # Verify document title is present
            title_element = self.selenium.find_element(By.CLASS_NAME, "document-title")
            self.assertEqual(
                title_element.text,
                'Test View Document',
                "Document title does not match"
            )
            logger.info("Document title verified")
            
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            self.selenium.save_screenshot('test_failure.png')
            raise