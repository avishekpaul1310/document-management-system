# documents/tests/test_functional.py
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from django.contrib.auth.models import User

class DocumentManagementTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_document_upload_workflow(self):
        # Create test user
        user = User.objects.create_user(username='testuser', password='12345')
        
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