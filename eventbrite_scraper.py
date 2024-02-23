#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

def scrape_google(driver, query):
    google_url = f"https://www.google.com/search?q={query}"
    driver.get(google_url)
    time.sleep(2)  

    # Find the first search result link
    try:
        search_result = driver.find_element(By.CSS_SELECTOR, 'div.TzHB6b')
    except:
        search_result = driver.find_element(By.CSS_SELECTOR, 'div.MjjYud')
    # Click on the first search result
    try:
        search_link = search_result.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
        driver.get(search_link)
        time.sleep(2)
    except:
        pass

    # Extract information from the resulting page
    url = driver.current_url
    try:
        snippet = driver.find_element(By.CSS_SELECTOR, 'p').text
    except:
        snippet = ''
        
    return {'snippet': snippet, 'link': url}

def extract_event_details(event):
    try:
        event_name = event.find_element(By.CSS_SELECTOR, 'h1.event-title').text
    except:
        event_name = ''
    try:
        date = event.find_element(By.CSS_SELECTOR, '.start-date').get_attribute('datetime')
    except:
        date = ''
    try:
        location = event.find_element(By.CSS_SELECTOR, '.location-info__address').text.split('\n')[1]
    except:
        location = event.find_element(By.CSS_SELECTOR, '.location-info__address-text').text
    try:
        description = event.find_element(By.CSS_SELECTOR, 'div.eds-text--left').text
    except:
        try:
            description = event.find_element(By.CSS_SELECTOR, '.eds-l-mar-top-3.description-items').text
        except:
            description = ''
    try:
        organizer = event.find_element(By.CSS_SELECTOR, '.descriptive-organizer-info-mobile__name-link').text
    except:
        try:
            organizer = event.find_element(By.CSS_SELECTOR, '.descriptive-organizer-info__name-link').text
        except:
            organizer = ''

    return event_name, date, location, description, organizer

def scrape_event_details(driver, link):
    driver.get(link)
    time.sleep(2)
    try:
        view_details_button = driver.find_element(By.CSS_SELECTOR, 'button.expired-view-details')
        view_details_button.click()
        time.sleep(2)
    except:
        pass
    try:
        view_all_button = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="view-event-details-button"]')
        view_all_button.click()
        time.sleep(2)
    except:
        pass

    event_name, date, location, description, organizer = extract_event_details(driver)
    
    return event_name, date, location, description, organizer

def scrape_eventbrite_events(driver, url):
    driver.get(url)
    data_list = []
    visited_links = set()

    for _ in range(2):
        try:
            events = driver.find_elements(By.CSS_SELECTOR, '.SearchResultPanelContentEventCardList-module__eventList___1YEh_ li')
            for event in events:
                link_element = event.find_element(By.CSS_SELECTOR, "a:first-child")
                link = link_element.get_attribute("href")

                if link not in visited_links:
                    driver.execute_script("window.open('', '_blank');")
                    driver.switch_to.window(driver.window_handles[-1])
                    
                    event_name, date, location, description, organizer = scrape_event_details(driver, link)
                    search_query = f"{event_name} {organizer}"
                    google_search_results = scrape_google(driver, search_query)
                    
                    # Extract snippet and link from Google search results
                    snippet = google_search_results.get('snippet', '')
                    link = google_search_results.get('link', '')


                    data = {
                        'Event Name': event_name,
                        'Date': date,
                        'Location': location,
                        'Description': description,
                        'Organizer': organizer,
                        'Google Search Result': snippet,
                        'Google Search Link': link
                    }

                    data_list.append(data)
                    visited_links.add(link)

                    # Close the current tab and switch back to the main window
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    time.sleep(2)

            next_page = driver.find_element(By.CSS_SELECTOR, 'button[data-spec="page-next"] svg')
            time.sleep(2)
            next_page.click()
            time.sleep(5)
        except Exception as e:
            print(e)
            continue
    return data_list

def save_to_csv(data_list, filename):
    keys = data_list[0].keys() if data_list else []
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data_list)

def main():
    chrome_driver_path = 'C:/Users/Vijay Computers/Documents/Web_Scraping/chromedriver-win64/chromedriver.exe'
    chrome_service = Service(chrome_driver_path)

    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    # options.add_argument('--no-sandbox')
    # options.headless = True
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=chrome_service, options=options)
    url = "https://www.eventbrite.com/d/india/all-events/"
    data_list = scrape_eventbrite_events(driver, url)
    save_to_csv(data_list, 'event_data.csv')
    driver.quit()

if __name__ == "__main__":
    main()


# In[ ]:




