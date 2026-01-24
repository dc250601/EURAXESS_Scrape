import time
from tqdm.auto import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager



def setup_driver_and_page(config):
    options = webdriver.ChromeOptions()
 
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    url = "https://euraxess.ec.europa.eu/jobs/search"
    driver.get(url)
    wait = WebDriverWait(driver, config.LONG_DELAY)
    try:
        cookie_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='#accept']")))
        cookie_btn.click()
        print("Cookie banner closed.")
    except:
        print("Cookie banner not found or already closed.")

    return driver, wait

def click_next_page(config, driver):
    flag = False

    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "li.ecl-pagination__item--next a")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
        time.sleep(config.MICRO_DELAY)

        next_button.click()

        time.sleep(config.SHORT_DELAY)
        flag = True 

    except Exception as e:
        return False
    return flag


def add_filters(config,driver, wait, filter_name, filter_elements):

    try:
        filter_xpath = f"//label[contains(., '{filter_name}')]/following::input[contains(@class, 'ecl-select')][1]"  
        filter_input = wait.until(EC.element_to_be_clickable((By.XPATH, filter_xpath)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", filter_input)
        time.sleep(config.MICRO_DELAY)
        filter_input.click()
        print(f"Expanded filter: {filter_name}")
        time.sleep(config.MICRO_DELAY)

    except Exception as e:
        print(f"Could not open filter '{filter_name}'. Error: {e}")


    for option_name in filter_elements:
        try:
            xpath_selector = f"//span[contains(@class, 'ecl-checkbox__label-text') and contains(., '{option_name}')]"
            option_element = wait.until(EC.presence_of_element_located((By.XPATH, xpath_selector)))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", option_element)
            time.sleep(config.MICRO_DELAY)
            option_element.click()
            time.sleep(config.MICRO_DELAY)

        except Exception as e:
            print(f"Could not select '{option_name}'. Error: {e}")

    print("Research fields selected.")

    try:
        filter_input.click()
        print(f"Collapsed filter: {filter_name}")
        time.sleep(config.MICRO_DELAY)
    except Exception as e:
        print(f"Could not collapse filter '{filter_name}'. Error: {e}")


    try:
        apply_button = wait.until(EC.element_to_be_clickable((By.ID, "edit-submit")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", apply_button)
        time.sleep(config.MICRO_DELAY)
        apply_button.click()
        time.sleep(config.LONG_DELAY)

    except Exception as e:
        print(f"Could not click 'Apply filters'. Error: {e}")

def get_job_data(config, driver, wait):
    data = []
    next_page = True
    page_number = 0

    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.unformatted-list")))
        print("Job list is visible.")
    except:
        print("Timeout: Job list did not load.")

        
    while next_page:
        page_number += 1
        print(f"\n--- Scraping Page {page_number} ---")
        job_cards = driver.find_elements(By.CSS_SELECTOR, "ul.unformatted-list > li")
        for card in job_cards:
            try:
                title_element = card.find_element(By.CSS_SELECTOR, "h3.ecl-content-block__title a")
                title = title_element.text.strip()
                link = title_element.get_attribute("href")

                date_element = card.find_element(By.XPATH, ".//li[contains(., 'Posted on:')]")
                date_posted = date_element.text.replace("Posted on:", "").strip()

                try:
                    country_element = card.find_element(By.CSS_SELECTOR, ".ecl-label--highlight")
                    country = country_element.text.strip()
                except:
                    country = "N/A"
                data.append({
                    "Title": title,
                    "Country": country,
                    "Link": link,
                    "date_posted": date_posted
                })
                
                # print("Title:", title, " | Country:", country, " | Date Posted:", date_posted, " | Link:", link)
            except Exception as e:
                
                continue
        next_page = click_next_page(config,driver)

    return data