from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

# Initialize browser with anti-detection settings
def setup_driver():
    chrome_options = webdriver.ChromeOptions()
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
    chrome_options.add_argument('--incognito')  # Add incognito mode

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1920, 1080) 

    return driver


# Main function
def linkedin_connect_bot():
    driver = setup_driver()

    try:
        # 1. Login using li_at cookie
        print("Logging in to LinkedIn using cookie...")
        driver.get("https://www.linkedin.com")

        # Add your li_at cookie here
        li_at_cookie = {
            'name': 'li_at',
            'value': 'AQEDAQBZP4AADziKAAABl_izDHYAAAGYHL-Qdk4ATzo9b7sAXGHNP11cfiManyyvo9oCH71GteGWkspM7WHhXpR1c7xPur_QpOlR73w2kheZDf2ytlu4eqO9hMkMNP7aF5E7KpnmDDfhVIpyDBx7AnvQ',  # Replace with your actual li_at cookie
            'domain': '.linkedin.com'
        }

        driver.add_cookie(li_at_cookie)

        # Refresh to apply cookie
        driver.get("https://www.linkedin.com")
        time.sleep(random.uniform(2, 4))

        # Verify login
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "global-nav__me")))
        print("Login successful")

        # 2. Search for profiles
        print("Searching for profiles...")
        search_term = "Family Office"  # Your search term
        driver.get(f"https://www.linkedin.com/search/results/people/?keywords={search_term.replace(' ', '%20')}")
        time.sleep(random.uniform(3, 5))

        # 3. Send connection requests
        connection_count = 0
        max_connections = 3
        page_count = 0
        max_pages = 100

        while connection_count < max_connections and page_count < max_pages:
            print(f"\nProcessing page {page_count + 1}...")

            # Scroll to load more results
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.8);")
            time.sleep(random.uniform(2, 4))

            # Find all Connect buttons using multiple selector strategies
            connect_selectors = [
                "//button[.//span[text()='Connect']]",
                "//button[contains(@aria-label, 'Connect')]",
                "button[data-control-name='connect']"
            ]

            connect_buttons = []
            for selector in connect_selectors:
                try:
                    if selector.startswith("//"):
                        connect_buttons = driver.find_elements(By.XPATH, selector)
                    else:
                        connect_buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    if connect_buttons:
                        break
                except:
                    continue

            print(f"Found {len(connect_buttons)} connect buttons")

            for button in connect_buttons:
                if connection_count >= max_connections:
                    break

                try:
                    # Scroll to button properly
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", button)
                    time.sleep(random.uniform(1, 2))

                    # Wait until clickable
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(button))

                    # Try normal click first, fallback to JS click
                    try:
                        button.click()
                    except:
                        driver.execute_script("arguments[0].click();", button)

                    time.sleep(random.uniform(1, 2))
                    try:
                        send_selectors = [
                            "//button[.//span[text()='Send']]",
                            "button[aria-label='Send now']",
                            "//button[.//span[text()='Send without a note']]",
                            "button[aria-label='Send without a note']"
                        ]

                        for selector in send_selectors:
                            try:
                                by = By.XPATH if selector.startswith("//") else By.CSS_SELECTOR
                                send_button = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable((by, selector)))
                                send_button.click()
                                connection_count += 1
                                print(f"Sent connection {connection_count}/{max_connections}")
                                time.sleep(random.uniform(3, 6))  # Random delay
                                break
                            except:
                                continue
                        else:
                            print("Couldn't find send button - may already be connected")
                            raise Exception("Send button not found")


                    except Exception as e:
                        print(f"Error sending invitation: {str(e)}")
                        try:
                            cancel_button = WebDriverWait(driver, 3).until(
                                EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Cancel']]")))
                            cancel_button.click()
                        except:
                            pass
                        continue

                except Exception as e:
                    print(f"Error with Connect button: {str(e)}")
                    continue

            # Go to next page if needed
            if connection_count < max_connections:
                try:
                    next_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Next']")))
                    next_button.click()
                    page_count += 1
                    time.sleep(random.uniform(4, 7))  # Longer delay between pages
                except:
                    print("No more pages available or next button not found")
                    break

    except Exception as e:
        print(f"Fatal error: {str(e)}")
        # Save screenshot for debugging
        driver.save_screenshot('error.png')
        print("Saved screenshot as error.png")

    finally:
        print(f"\nFinished. Sent {connection_count} connection requests")
        driver.quit()

if __name__ == "__main__":
    linkedin_connect_bot()
