# import requests
# from urllib.parse import urljoin

# base_url = "https://www.bbc.com"

# def get_cache_headers(url):
#     try:
#         response = requests.head(url)
#         response.raise_for_status()  # Raise an exception for non-200 status codes
#         return response.headers
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching headers for {url}: {e}")
#         return None

# def crawl_website(base_url):
#     queue = [base_url]
#     visited = set()

#     while queue:
#         url = queue.pop(0)

#         if url in visited:
#             continue

#         visited.add(url)

#         headers = get_cache_headers(url)
#         print("Headers",headers)
#         if headers:
#             print(f"Headers for {url}:")
#             for header, value in headers.items():
#                 print(f"{header}: {value}")

#         try:
#             response = requests.get(url)
#             response.raise_for_status()  # Raise an exception for non-200 status codes

#             for link in response.links:
#                 if link.url.startswith("/"):
#                     link_url = urljoin(base_url, link.url)
#                     queue.append(link_url)
#         except requests.exceptions.RequestException as e:
#             print(f"Error processing {url}: {e}")

# if __name__ == "__main__":
#     crawl_website(base_url)
#########################################################################

import re
import os
import sys
import time
import urllib.request
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

COUNT =0 # this can be made more meaningful by assocciating it with the current time

monitoring_duration= 60*10*6# in seconds
download_interval=60*10 #every 5 mins: 60*5

def url_2_host(url):
    '''
    Remove http(s):// from the url
    '''
    return url.split("/")[-1]

def scroll_to_bottom(driver):
    '''
    Given an active webdriver, scroll to the bottom of the page manually to load lazy loaded images
    Source code was acquired from: https://stackoverflow.com/a/27760083
    '''
    SCROLL_PAUSE_TIME = 0.05

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Slow scroll through page to activate images
    curr = 0
    next = 20
    while curr + next <= last_height:
        driver.execute_script(f"window.scrollTo({curr}, {curr + next});")
        time.sleep(0.05)
        curr = curr + next
        
    driver.implicitly_wait(10)
    return last_height

def make_filename(url):
    """Converts a URL into a valid filename with appropriate substitutions.

    Args:
        url: The URL to convert.

    Returns:
        The generated filename.
    """

    # Remove URL schema and query string
    filename = re.sub(r"^https?://", "", url)
    filename = re.sub(r"\?.*$", "", filename)

    # Substitute common invalid characters
    filename = re.sub(r"[^\w\-_. ]", "_", filename)  # Replace any non-word, non-hyphen, non-underscore, non-dot, non-space characters with _
    filename = re.sub(r"[\s]+", "_", filename)  # Replace multiple whitespaces with a single _
    filename = filename.strip("_")  # Remove leading/trailing underscores

    # Handle extensions (if present)
    match = re.search(r"\.[^.]+$", filename)
    if match:
        extension = match.group()
        filename = filename[:-len(extension)]  # Remove extension
        filename = filename.strip("_")  # Remove leading/trailing underscores after extension removal

    # Truncate filename if it's too long (optional for specific systems)
    max_length = 255  # Adjust this as needed
    if len(filename) > max_length:
        filename = filename[:max_length - len(extension)] + extension  # Ensure extension is preserved

    return filename + extension

def collect_page(url, options):
    '''
    Collects the page data and downloads the images and style sheets from the given URL.
    '''

    global COUNT
    print("Collecting page data")
    filename_url = make_filename(url)
    # Performance metrics setup for websize 
    logging_prefs = {'performance': 'INFO'}    
    options.set_capability('goog:loggingPrefs', logging_prefs)

    # Overall page data
    page_data = {}
    host = url_2_host(url)

    # Define driver options 
    driver = webdriver.Chrome(service=Service(), options=options) # Start web driver
    driver.get(url)

    
    # Scroll to the bottom of the page to activate lazy loading
    scroll_to_bottom(driver)


    # For CSS
    # Get links to external style sheets
    link_tags = driver.find_elements(By.TAG_NAME, 'link')
    style_urls = [link_tag.get_attribute('href') for link_tag in link_tags if link_tag.get_attribute('rel') == 'stylesheet']

    # For images:

    # For javascript,
    # Find all script elements
    script_tags = driver.find_elements(By.TAG_NAME, 'script')
    js_urls = [script_tag.get_attribute('src') for script_tag in script_tags if script_tag.get_attribute('src')]

    print("we retrive the css file data")
    # Retrieve the .css file associated with each URL and fetch cache headers
    print(style_urls)
    for _, style_url in enumerate(style_urls):       
        # Fetching cache headers
        print("CSS CACHE HEADER RETRIVAL")
        response = urllib.request.urlopen(style_url)
        cache_headers = response.getheaders()
        print(f"Cache Headers for {style_url}: {cache_headers}")

    print(len(js_urls))
    for _, js_url in enumerate(js_urls):       
        # Fetching cache headers
        print("JS CACHE HEADER RETRIVAL")
        response = urllib.request.urlopen(js_url)
        cache_headers = response.getheaders()
        print(f"Cache Headers for {js_url}: {cache_headers}")

    return style_urls


options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("--test-type")
options.add_argument('--allow-insecure-localhost')
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

if True:
    options.add_argument('headless')
    options.add_argument('fullscreen')
options.set_capability("acceptInsecureCerts", True)

# Collect page data and store on disk
url = sys.argv[1]
# Example usage: python script.py https://example.com
style_urls = collect_page(url, options)

