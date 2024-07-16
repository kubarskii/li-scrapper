from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from linkedin_scraper import Person, actions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from urllib.parse import urlparse

import json

import time
import random


def random_delay(min_delay=3, max_delay=8):
    time.sleep(random.uniform(min_delay, max_delay))


def login(driver, email, password):
    actions.login(driver, email, password)
    random_delay()


def is_logged_in(driver):
    driver.get('https://www.linkedin.com/feed/')
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div.feed-identity-module'))
        )
        return True
    except:
        return False


def move_mouse_naturally(driver, element):
    actions = ActionChains(driver)
    element_location = element.location
    element_size = element.size
    start_x = random.randint(
        0, driver.execute_script("return window.innerWidth"))
    start_y = random.randint(
        0, driver.execute_script("return window.innerHeight"))
    end_x = element_location['x'] + element_size['width'] / 2
    end_y = element_location['y'] + element_size['height'] / 2

    steps = 100  # Number of steps to move the mouse
    for i in range(steps):
        x = start_x + (end_x - start_x) * i / steps
        y = start_y + (end_y - start_y) * i / steps
        actions.move_by_offset(x - actions._driver.w3c_actions.pointer_parameters.origin.x,
                               y - actions._driver.w3c_actions.pointer_parameters.origin.y)
        actions.perform()
        random_delay(0.01, 0.05)


driver = webdriver.Chrome()

email = "gmail.com"
password = ""

# Perform initial login
login(driver, email, password)

driver.get('https://www.linkedin.com/search/results/people/?keywords=venture%20capital%20partners&network=%5B%22S%22%5D&origin=GLOBAL_SEARCH_HEADER&sid=jk%2C')
links = []

# Scroll and paginate through search results
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.entity-result__title-line .app-aware-link'))
    )
    elements = driver.find_elements(
        By.CSS_SELECTOR, '.entity-result__title-line .app-aware-link')
    random_delay()
    for elem in elements:
        link = elem.get_attribute('href')
        parsedUrlObj = urlparse(link)
        url = parsedUrlObj._replace(query="").geturl()
        links.append(url + '/overlay/contact-info/')
    random_delay()
    try:
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        random_delay()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '.artdeco-pagination__button--next'))
        )
        next_button = driver.find_element(
            By.CSS_SELECTOR, '.artdeco-pagination__button--next')
        if next_button.get_attribute('disabled'):
            break

        move_mouse_naturally(driver, next_button)
        random_delay()
        next_button.click()
        random_delay()
    except Exception as e:
        break

# Save links to a JSON file
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(links, f, ensure_ascii=False, indent=4)

# Scrape LinkedIn profiles
people = []

for url in links:
    if url is not None:
        driver.get(url)
        random_delay()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body')))
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.artdeco-modal__content')))
            name = driver.find_element(
                By.CSS_SELECTOR, 'h1#pv-contact-info').text
            details = driver.find_elements(
                By.CSS_SELECTOR, '.pv-contact-info__contact-type a')
            hrefs = [d.get_attribute('href') for d in details]
            people.append({'name': name, 'link': url, 'hrefs': hrefs})
            random_delay()
        except Exception as e:
            print(f"Error scraping {url}: {e}")

# Save people data to a JSON file
with open('people.json', 'w', encoding='utf-8') as f:
    json.dump(people, f, ensure_ascii=False, indent=4)

# Close the driver
driver.quit()
