# documents/tests/verify_selenium.py
import os
import sys
from datetime import datetime

def verify_installation():
    print("=== Selenium Installation Verification ===")
    print(f"Current directory: {os.getcwd()}")
    print(f"Verification time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    
    try:
        import selenium
        print(f"✓ Selenium installed (version: {selenium.__version__})")
        
        from selenium.webdriver.common.by import By
        print("✓ Successfully imported By from selenium.webdriver.common.by")
        
        from selenium import webdriver
        print("✓ Successfully imported webdriver")
        
        import webdriver_manager
        print(f"✓ Webdriver Manager installed (version: {webdriver_manager.__version__})")
        
        from webdriver_manager.chrome import ChromeDriverManager
        print("✓ Successfully imported ChromeDriverManager")
        
        print("\nAll required selenium packages are properly installed!")
        
    except ImportError as e:
        print(f"\n❌ Error during import: {e}")
        print(f"Python path: {sys.path}")
        return False
    
    return True

if __name__ == "__main__":
    success = verify_installation()
    if not success:
        print("\nSome packages are missing or not properly installed.")
        sys.exit(1)