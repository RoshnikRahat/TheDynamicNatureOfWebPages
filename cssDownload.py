import warnings
warnings.filterwarnings("ignore")
import os, sys
from urllib.error import HTTPError
from skimage.metrics import structural_similarity as ssim
from selenium import webdriver
import mysql.connector
from PIL import Image
import argparse, hashlib
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import multiprocessing as mp
from itertools import product
import re
import pandas as pd
import urllib
import json
import numpy as np
import time
import itertools
from subprocess import check_output
import more_itertools as mit
def url_2_host(url):
    '''
    Remove http(s):// from the url
    '''
    return url.split("/")[-1]

def scroll_to_bottom(driver):
    '''
    Given an active webdriver, scroll to the bottom of the page manually to load lazy loaded images
    Source code was acqurired from: https://stackoverflow.com/a/27760083
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
        time.sleep(0.01)
        curr = curr + next
        
    driver.implicitly_wait(10)
    return last_height
    
def collect_page(url, options):
    '''
    Collects the page data and downloads the images and style sheets from the given URL.
    '''
    print("Collecting page data")
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

    # Get style elements
    style_tags = driver.find_elements(By.TAG_NAME, 'style')
    style_contents = [style_tag.get_attribute('innerHTML') for style_tag in style_tags]

    # Get links to external style sheets
    link_tags = driver.find_elements(By.TAG_NAME, 'link')
    style_urls = [link_tag.get_attribute('href') for link_tag in link_tags if link_tag.get_attribute('rel') == 'stylesheet']
    print(style_urls)
    # Download style sheets
    try:
        os.makedirs(f"{host}/styles")  # Create a directory to store style sheets
    except Exception as e:
        print("Directory already exists")
    
    for idx, style_content in enumerate(style_contents):
        with open(f"style{idx}.css", "w") as style_file:
            style_file.write(style_content)
    
    for idx, style_url in enumerate(style_urls):
        urllib.request.urlretrieve(style_url, f"stylesheet{idx}.css")

    # Continue with the rest of the code...

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("--test-type")
options.add_argument('--allow-insecure-localhost')
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# if MOBILE:
#     # Mobile emulation, currently configured for Nexus 5
#     mobile_emulation = {
#         "deviceMetrics": { "width": PHONE_WIDTH, "height": PHONE_HEIGHT, "pixelRatio": PIXEL_RATIO},
#         "userAgent": "Mozilla/5.0 (Linux; Android 8.1.0; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/115.0.5790.170 Mobile Safari/535.19" }
#     options.add_experimental_option("mobileEmulation", mobile_emulation)
#     options.add_experimental_option("excludeSwitches", ["disable-popup-blocking"])

if True:
    options.add_argument('headless')
    options.add_argument('fullscreen')
options.set_capability("acceptInsecureCerts", True)

# Collect page data and store on disk
url = "https://www.bbc.com/"


results, js_results, total_kbs = collect_page(url, options)

print()