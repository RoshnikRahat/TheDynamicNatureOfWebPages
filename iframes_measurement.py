from selenium import webdriver
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import os
import requests

# Function to get HTML content
def get_html(url):
    headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    response = requests.get(url, headers=headers)
    return response.text

# Function to find all iframes
def find_all_iframes(soup):
    iframes = soup.find_all('iframe')
    for iframe in soup.find_all('iframe'):
        nested_soup = BeautifulSoup(iframe['srcdoc'], 'html.parser') if 'srcdoc' in iframe.attrs else None
        if nested_soup:
            iframes += find_all_iframes(nested_soup)
    return iframes

# Function to process a single URL
def process_url(url, category, csv_file):
    try:
        csv_file = csv_file + ".csv"
        html = get_html(url)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        soup = BeautifulSoup(html, 'html.parser')
        iframes = find_all_iframes(soup)

        iframe_str = ' | '.join(str(iframe) for iframe in iframes)
        data = []

        file_exists = os.path.exists(csv_file)
        
        if file_exists:
            try:
                with open(csv_file, mode='r') as file:
                    reader = csv.reader(file)
                    next(reader)  # Skip header
                    previous_row = list(reader)[-1]
            except IndexError:
                previous_row = None

            if previous_row and len(previous_row) > 5:
                previous_iframes = previous_row[5]
                previous_iframes_list = previous_iframes.split(' | ')
                modified_iframes = [str(iframe) for iframe in iframes if str(iframe) not in previous_iframes_list]
                modified_iframes_str = ' | '.join(modified_iframes)
                modified = 'Yes' if modified_iframes else 'No'
            else:
                modified_iframes_str = iframe_str
                modified = 'Null'

        else:
            modified_iframes_str = iframe_str
            modified = 'Null'
        webname = "Chrome"
        data.append([webname, category, url, current_time, modified, iframe_str, modified_iframes_str])


        with open(csv_file, mode='a') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['URL', 'Category', 'Time', 'Modified', 'Iframe', 'Modified Iframes'])
            writer.writerows(data)

        print("Data appended to %s successfully." % csv_file)

        
    finally:
        print("Processing done for:", url)

# Main function to read dataset.csv and process each URL
def main():
    with open('dataset.csv', mode='r') as file:
     
        reader = csv.DictReader(file)
        for row in reader:
            print("processing %s",row['Website'] )
            process_url(row['Website'], row['Category'], row['CSV'])

if __name__ == "__main__":
    main()