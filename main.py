from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from linkedin_scraper import Person, actions
from selenium import webdriver
from selenium.webdriver.common.by import By

from urllib.parse import urlparse

import json

import time
import random


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


def random_delay(min_delay=1, max_delay=2):
    time.sleep(random.uniform(min_delay, max_delay))


driver = webdriver.Chrome()

email = "@gmail.com"
password = ""
# if email and password isnt given, it'll prompt in terminal
actions.login(driver, email, password)
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
        if not is_logged_in(driver):
            login(driver, email, password)
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
