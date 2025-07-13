from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

def setup_driver():
    chrome_options = webdriver.ChromeOptions()
    
    # Basic anti-detection settings
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Stability options
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless=new')
    # Disable user data directory completely
    chrome_options.add_argument('--disable-application-cache')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-default-apps')
    
    # Configure service
    service = Service(ChromeDriverManager().install())
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.maximize_window()
        return driver
    except Exception as e:
        print(f"Error initializing driver: {str(e)}")
        raise

def linkedin_connect_bot():
    driver = None
    try:
        driver = setup_driver()
        
        # 1. Login using cookie
        print("Logging in to LinkedIn...")
        driver.get("https://www.linkedin.com")
        time.sleep(2) 
        # Add cookie (replace with your actual li_at cookie)
        li_at_cookie = {
            'name': 'li_at',
            'value': 'AQEDAQBZP4AADziKAAABl_izDHYAAAGYHL-Qdk4ATzo9b7sAXGHNP11cfiManyyvo9oCH71GteGWkspM7WHhXpR1c7xPur_QpOlR73w2kheZDf2ytlu4eqO9hMkMNP7aF5E7KpnmDDfhVIpyDBx7AnvQ',         'domain': '.linkedin.com'
        }
        
        driver.add_cookie(li_at_cookie)
        driver.get("https://www.linkedin.com/feed/")
        driver.refresh()
        time.sleep(random.uniform(2, 4))
        
        # Verify login
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "global-nav__me"))
        )
        print("Login successful")

        # 2. Search for profiles
        search_term = "Family Office"
        print(f"Searching for: {search_term}")
        driver.get(f"https://www.linkedin.com/search/results/people/?keywords={search_term.replace(' ', '%20')}")
        time.sleep(random.uniform(3, 5))

        # 3. Connection logic
        connection_count = 0
        max_connections = 3
        
        while connection_count < max_connections:
            # Find connect buttons (excluding pending connections)
            buttons = driver.find_elements(
                By.XPATH, "//button[contains(., 'Connect') and not(contains(., 'Pending'))]"
            )
            
            print(f"Found {len(buttons)} connect buttons")
            
            for button in buttons:
                if connection_count >= max_connections:
                    break
                
                try:
                    # Scroll to button
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", 
                        button
                    )
                    time.sleep(random.uniform(1, 2))
                    
                    # Click button
                    button.click()
                    time.sleep(random.uniform(1, 2))
                    
                    # Handle send button
                    try:
                        send_btn = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable(
                                (By.XPATH, "//button[contains(., 'Send')]")
                            )
                        )
                        send_btn.click()
                        connection_count += 1
                        print(f"Sent connection {connection_count}/{max_connections}")
                        time.sleep(random.uniform(5, 8))
                    except:
                        print("Couldn't find send button")
                        try:
                            driver.find_element(
                                By.XPATH, "//button[contains(@aria-label, 'Dismiss')]"
                            ).click()
                        except:
                            pass
                        continue
                        
                except Exception as e:
                    print(f"Error with button: {str(e)}")
                    continue
            
            # Scroll to load more results
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(3, 5))
    
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        if driver:
    
            print("Saved screenshot as error.png")
    finally:
        if driver:
            print(f"\nFinished. Sent {connection_count} connection requests")
            driver.quit()

if __name__ == "__main__":
    linkedin_connect_bot()
