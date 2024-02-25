from selenium import webdriver
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import os

# URL to extract HTML from
url = "https://dawn.com"

driver = webdriver.Chrome()

try:

    driver.get(url)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Extract the HTML of the page
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    iframes = soup.find_all('iframe')
    # Concatenate iframe 
    iframe_str = ' | '.join(str(iframe) for iframe in iframes)
    # Prepare data to append to CSV
    data = []
    csv_file = 'frames_data.csv'
    file_exists = os.path.exists(csv_file)
    
    if file_exists:
        # Read the last row of the CSV file
        try:
            with open(csv_file, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip the first row (titles)
                previous_row = list(reader)[-1]  # Get the last row
        except IndexError:
            previous_row = None
        
        # Compare the iframes with the iframes in the previous row
        if previous_row and len(previous_row) > 5:
            previous_iframes = previous_row[5]  
            previous_iframes_list = previous_iframes.split(' | ')
            
            modified_iframes = []
            # Check each iframe in the new list against the previous list
            for iframe in iframes:
                if str(iframe) not in previous_iframes_list:
                    modified_iframes.append(str(iframe))
            
            modified_iframes_str = ' | '.join(modified_iframes)
            modified = 'Yes' if modified_iframes else 'No'
        else:
            modified_iframes_str = iframe_str
            modified = 'Null'
        webname = "Dawn"
        category = "News"
        
        data.append([webname, category, url, current_time, modified, iframe_str, modified_iframes_str])
    
    # Append data to CSV file
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Web Name', 'Category', 'URL', 'Time', 'Modified', 'Iframe', 'Modified Iframes']) 
        writer.writerows(data)
    
    print("Data appended to iframes_data.csv successfully.")
    
finally:

    driver.quit()
