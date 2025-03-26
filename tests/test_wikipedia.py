import unittest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException, 
    StaleElementReferenceException, 
    NoSuchElementException
)

class JurajDobrilaWikipediaTest(unittest.TestCase):
    def setUp(self):
        # Adding options for headless mod
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1280,800")
        chrome_options.add_argument("--allow-insecure-localhost")
        
        # WebDriver initialization
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        self.wait = WebDriverWait(self.driver, 100)
    
    def test_juraj_dobrila_history(self):
        # Open wikipedia and search for "Juraj Dobrila"
        self.driver.get('https://hr.wikipedia.org/')
        
        search_input = self.wait.until(
            EC.element_to_be_clickable((By.ID, 'searchInput'))
        )
        
        search_input.click()
        search_input.send_keys("Juraj Dobrila" + Keys.RETURN)
        
        # Check if new page is open
        self.wait.until(
            EC.url_contains('Juraj_Dobrila')
        )
        
        # Chose tab History
        history_link = self.wait.until(
        EC.element_to_be_clickable((By.ID, 'ca-history'))
        )
        history_link.click()
        
        # Check if URL-a contains history
        self.wait.until(
        EC.url_contains('action=history')
        )

        # Click on filter verisons button
        filter = self.wait.until(
            EC.element_to_be_clickable((By.ID, 'mw-history-search'))
        )
        filter.click()
             
        # Add date and submit
        date = "2020-07-01"
        filter_date_field = self.wait.until(
            EC.element_to_be_clickable((By.ID, 'mw-input-date-range-to'))
        )


        actions = ActionChains(self.driver)
        actions.click(filter_date_field)
        actions.send_keys(date)
        actions.perform()


        submit_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[type="submit"]'))
        )

        submit_button.click()

        # 5. Check if fist result contains correct correct timestamp
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                first_result = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//section[@id='pagehistory']/ul/li[1]//*[contains(@class, 'mw-changeslist-date')]"))
                )
            except (TimeoutException, StaleElementReferenceException, NoSuchElementException) as e:
                print(f"Attempt {attempt + 1} failed: {type(e).__name__}")
    
        timestamp_text = first_result.text

        self.assertEqual(
            timestamp_text, 
            '21:33, 24. travnja 2020.',
            f"Očekivani timestamp nije pronađen. Pronađen: {timestamp_text}"
        )

    def tearDown(self):
        self.driver.quit()

if __name__ == '__main__':
    unittest.main(verbosity=2)
    
