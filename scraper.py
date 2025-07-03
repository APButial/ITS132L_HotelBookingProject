from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common import NoSuchElementException

import json
import time
import os

prefectures = [
    "Aichi",
    "Akita",
    "Aomori",
    "Chiba",
    "Ehime",
    "Fukui",
    "Fukuoka",
    "Fukushima",
    "Gifu",
    "Gunma",
    "Hiroshima",
    "Hokkaido",
    "Hyogo",
    "Ibaraki",
    "Ishikawa",
    "Iwate",
    "Kagawa",
    "Kagoshima",
    "Kanagawa",
    "Kochi",
    "Kumamoto",
    "Kyoto",
    "Mie",
    "Miyagi",
    "Miyazaki",
    "Nagano",
    "Nagasaki",
    "Nara",
    "Niigata",
    "Oita",
    "Okayama",
    "Osaka",
    "Okinawa",
    "Saga",
    "Saitama",
    "Shiga",
    "Shimane",
    "Shizuoka",
    "Tochigi",
    "Tokushima",
    "Tokyo",
    "Tottori",
    "Toyama",
    "Wakayama",
    "Yamagata",
    "Yamaguchi",
    "Yamanashi"
]

def append_to_json(data):
    file = 'dataset.json'
    if not os.path.exists(file):
        json_data = []
    else:
        with open(file, 'r') as f:
            try:
                json_data = json.load(f)
                if not isinstance(json_data, list):
                    raise ValueError("JSON data is not a list.")
            except (json.JSONDecodeError, ValueError) as e:
                print("Error reading JSON file:", e)
                return
            
    json_data.append(data)

    with open(file, 'w') as f:
        json.dump(json_data, f, indent=4)

def handle_no_such_element_exception(data_extraction_task):
    try:
        return data_extraction_task()
    except NoSuchElementException as e:
        return None

# create a Chrome web driver instance
driver = webdriver.Chrome(service=Service())

# connect to the target page

# Jul, Aug, Sep
driver.get('https://www.booking.com/searchresults.html?label=gen173nr-1FCAQoggI49ANIM1gEaLQBiAEBmAExuAEZyAEP2AEB6AEB-AECiAIBqAIDuAKi1q7CBsACAdICJGMxYTFjNmE2LWE4NWMtNGE0MS1iNzE3LWMyZmYwMGY1YjA4MtgCBeACAQ&aid=304142&ss=Japan&efdco=1&lang=en-us&src=searchresults&dest_id=106&dest_type=country&ac_position=2&ac_click_type=b&ac_langcode=en&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=483d2091b1d00dd7&checkin=2025-06-13&checkout=2025-06-14&ltfd=1%3A5%3A7-2025_8-2025_9-2025%3A1%3A&group_adults=2&no_rooms=1&group_children=0&nflt=ht_id%3D204')

# Oct, Nov, Dec
#driver.get('https://www.booking.com/searchresults.html?label=gen173nr-1FCAQoggI49ANIM1gEaLQBiAEBmAExuAEZyAEP2AEB6AEB-AECiAIBqAIDuALyq6rCBsACAdICJDBmMTNhYTQ2LWEzZTUtNDNmYi1hZDhmLTBjZTNlZmIxYzc5NNgCBeACAQ&aid=304142&ss=Japan&efdco=1&lang=en-us&src=searchresults&dest_id=106&dest_type=country&ac_position=1&ac_click_type=b&ac_langcode=en&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=6aa43eb9890b055d&checkin=2025-06-12&checkout=2025-06-13&ltfd=1%3A5%3A10-2025_11-2025_12-2025%3A1%3A&group_adults=2&no_rooms=1&group_children=0&nflt=ht_id%3D204')
    
# handle the sign-in alert
try:
    # wait up to 20 seconds for the sign-in alert to appear
    close_button = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[role=\"dialog\"] button[aria-label=\"Dismiss sign-in info.\"]"))
    )
    # click the close button
    close_button.click()
except TimeoutException:
    print("Sign-in modal did not appear, continuing...")


# scroll down until end of hotel listing is reached
undetected_count = 0
while undetected_count < 5: 
    try:
        load_button = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.de576f5064.b46cd7aad7.d0a01e3d83.dda427e6b5.bbf83acb81.a0ddd706cc'))
        )
        load_button.click()
        driver.implicitly_wait(3)
        undected_count = 0
        print("Load More Results detected.")
    except TimeoutException:
        print("Load More Results button is not detected.")
        undetected_count += 1
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    driver.execute_script('window.scrollBy(0, -window.innerHeight);') # scroll up to see if load button is there

# select all property items on the page
property_items = driver.find_elements(By.CSS_SELECTOR, "[data-testid=\"property-card\"]")

# get all urls from hotel listing
urls = []
for property_item in property_items:
    url = handle_no_such_element_exception(lambda: property_item.find_element(By.CSS_SELECTOR, "a[data-testid=\"property-card-desktop-single-image\"]").get_attribute("href"))
    urls.append(url)

# start scraping
hotel_count = 0
for url in urls:
    driver.get(url)
    time.sleep(5)
    
    title = handle_no_such_element_exception(lambda: driver.find_element(By.CSS_SELECTOR, '.ddb12f4f86.pp-header__title').text)
    address = handle_no_such_element_exception(lambda: driver.find_element(By.CSS_SELECTOR, '.b99b6ef58f.cb4b7a25d9').text)
    try:
        address = address.split('\n')[0]
        for prefecture in prefectures:
            if prefecture in address:
                address = prefecture            
    except Exception:
        pass

    check_in = handle_no_such_element_exception(lambda: driver.find_element(By.CSS_SELECTOR, '[data-testid=\"date-display-field-start\"]').text)
    check_out = handle_no_such_element_exception(lambda: driver.find_element(By.CSS_SELECTOR, '[data-testid=\"date-display-field-end\"]').text)

    review_score = None
    review_count = None
    try:
        review_score = handle_no_such_element_exception(lambda: driver.find_element(By.CSS_SELECTOR, '.hotel_large_photp_score.featured_review_score.js-fly-content-tooltip.hp_lightbox_score_block')).get_attribute("data-review-score")    
        review_count = handle_no_such_element_exception(lambda: driver.find_element(By.CSS_SELECTOR, '.f63b14ab7a.fb14de7f14.eaa8455879').text)
    except Exception:
        pass
        
    try:
        review_count = review_count.split()[1]
    except Exception:
        pass

    popular_facilities_container = handle_no_such_element_exception(lambda: driver.find_element(By.CSS_SELECTOR, '[data-testid=\"property-most-popular-facilities-wrapper\"]'))
    popular_facilities = ""
    try:
        popular_facilities_list = handle_no_such_element_exception(lambda: popular_facilities_container.find_elements(By.CSS_SELECTOR, '.f6b6d2a959'))
        for f in popular_facilities_list:
            popular_facilities += (f.text.lower() + ',')
    except Exception:
        pass
    
    if popular_facilities != "":
        popular_facilities = popular_facilities[:-1]

    price_table = handle_no_such_element_exception(lambda: driver.find_element(By.ID, 'hprt-table'))
    max_occupancies = None
    prices = None
    try:
        max_occupancies = handle_no_such_element_exception(lambda: price_table.find_elements(By.CSS_SELECTOR, '.c-occupancy-icons.hprt-occupancy-occupancy-info'))
        prices = handle_no_such_element_exception(lambda: price_table.find_elements(By.CSS_SELECTOR, '.hp-price-left-align.hprt-table-cell.hprt-table-cell-price'))
    except Exception:
        pass

    price = None
    # get the corresponding price for the max_occupancies, this only gets the first price for a room with max 2 occupancy
    try:
        for ind, max_occupancy in enumerate(max_occupancies):
            if max_occupancy.find_element(By.CSS_SELECTOR, '.bui-u-sr-only').text == 'Max. people: 2':
                price = handle_no_such_element_exception(lambda: prices[ind].find_element(By.CSS_SELECTOR, '.prco-valign-middle-helper').text)
                break
    except Exception:
        pass

    # populate a new item with the scraped data
    item = {
      "url": url,
      "title": title,
      "address": address,
      "check_in_date": check_in,
      "check_out_date": check_out,
      "review_score": review_score,
      "review_count": review_count,
      "popular_facilities": popular_facilities,
      "price": price
    }
    # add the new item to the list of scraped items
    append_to_json(item)
    print(f"Processed hotels: {hotel_count+1}")
    hotel_count += 1

print("Scraping successful.")
# close the web driver and release its resources
driver.quit()
