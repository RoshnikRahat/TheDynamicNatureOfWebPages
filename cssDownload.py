import warnings
warnings.filterwarnings("ignore")
import os, sys
from urllib.error import HTTPError
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
import requests
import time
from bs4 import BeautifulSoup
import difflib
from datetime import datetime
import sys


##### GLOBAL VARAIBLE ####
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
    Source code was acqurired from: https://stackoverflow.com/a/27760083
    '''
    SCROLL_PAUSE_TIME = 0.01

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
    filename_url=make_filename(url)
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
    style_tag_contents = [style_tag.get_attribute('innerHTML') for style_tag in style_tags]
    #print(style_tag_contents)

    # Get links to external style sheets
    link_tags = driver.find_elements(By.TAG_NAME, 'link')
    style_urls = [link_tag.get_attribute('href') for link_tag in link_tags if link_tag.get_attribute('rel') == 'stylesheet']
    #contains the url with the links to the css sheets i.e   'https://static.files.bbci.co.uk/orbit/bcb90eb83a0e2941e357dbcf14018b41/css/orbit-v5-ltr.min.css
    #print(style_urls)
    
    #create a directory to store style sheets
    path=f"css_files_{filename_url}_{COUNT}"
    try:
        os.makedirs(path)  # Create a directory to store style sheets
    except Exception as e:
        print("Directory already exists")
    
    for idx, style_content in enumerate(style_tag_contents):
        with open(path+f"/styleTag_{idx}.css", "w") as style_file:
            #print("the style content is",style_content)
            style_file.write(style_content)
    
    retrived_CSS_file_paths=[]
    # retrives the .css file assocciated with each url
    for idx, style_url in enumerate(style_urls):
            file_path =path+ f"/stylesheet_{idx}.css"
            urllib.request.urlretrieve(style_url, file_path)
            retrived_CSS_file_paths.append(file_path)

    # Continue with the rest of the code...
    return style_urls,retrived_CSS_file_paths,style_tag_contents


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


def compare_CSS_Urls(urlListold,urlListNew):
    return urlListold==urlListNew

def compare_CSS_styletag_contents(oldStyleContent,newStyleContent):
    changes= not(oldStyleContent==newStyleContent)
    if changes:
        # additional functionality to compare struvture using url.request.parser if analysis reveals changes
        try:
            import css_parser  # Replace with your preferred CSS parser library
        except ImportError:
            css_parser = None  # Handle the case where the parser library is missing


        structure_changes=[]
        if css_parser:
            for content1,content2 in oldStyleContent,newStyleContent:
                parsed1 = css_parser.parse(content1)
                parsed2 = css_parser.parse(content2)
                structure_changes.append(parsed1 == parsed2) 
                
        return False,structure_changes
    return True,[]





# we need some global variable to make css file paths unique for each count
# reminder: move data to csv
def main():
    global COUNT
    CSS_df=pd.DataFrame(columns=['time','COUNT','url','style_urls_new','retrieved_CSS_file_paths_new','style_tag_contents_new','isCSS_URl_Same'])
    start_time = time.time()
    # This retrives the first CSS files

    style_urls_old,retrived_CSS_file_paths_old,style_tag_contents_old = collect_page(url, options)
    COUNT+=1
    while time.time() - start_time < monitoring_duration:
        # wait for the required interval
        time.sleep(download_interval)
        # download the updated CSS
        style_urls_new,retrived_CSS_file_paths_new,style_tag_contents_new = collect_page(url, options)
        # for CSS there will be three kinds of Comparisions, internal, external_tag and external content

        #external source
        isCSS_URl_Same=compare_CSS_Urls(style_urls_old,style_urls_new)
        #internal source comparision
        is_Internal_CSS_Same=compare_CSS_styletag_contents(style_tag_contents_old,style_tag_contents_new)

        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        row_data = {
            'time':current_datetime,
            'COUNT': COUNT,
            'url': url,
            'style_urls_new': style_urls_new,
            'retrieved_CSS_file_paths_new': retrived_CSS_file_paths_new,
            'style_tag_contents_new': style_tag_contents_new,
            'isCSS_URl_Same':isCSS_URl_Same,
            'is_Internal_CSS_Same':is_Internal_CSS_Same[0],
            'internal_CSS_changes':is_Internal_CSS_Same[1]
            
        }
        # Append the dictionary as a new row to the DataFrame
        CSS_df.loc[len(CSS_df)] = row_data

        CSS_df.to_csv(str(datetime.now().date())+make_filename(url)+"CSS_dataFrame")
        print("Saved to data Frame")
        
        #Updating the Values: Important for all comparisions
        style_urls_old,retrived_CSS_file_paths_old,style_tag_contents_old=style_urls_new,retrived_CSS_file_paths_new,style_tag_contents_new 
        



    update_count=0 # populate with the total updates
    print(f"Monitoring complete. Total updates: {update_count}")

if __name__ == "__main__":
    main()
