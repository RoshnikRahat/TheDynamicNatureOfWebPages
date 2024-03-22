from selenium import webdriver
from selenium.webdriver.common.by import By
import os

# URL of the website you want to scrape
url = 'https://cnn.com/'

# Assuming chromedriver_path is defined somewhere in your script as the path to the ChromeDriver executable
chrome_driver_path = '/Users/wajihanaveed/Downloads/chromedriver-mac-arm64/chromedriver'
# Set up Chrome options
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run Chrome in headless mode (without opening the browser window)
options.add_argument('--disable-gpu')  # Disable GPU acceleration (useful in headless mode)

# Initialize Chrome WebDriver
driver = webdriver.Chrome(options=options)

# Load the webpage
driver.get(url)

# Function to recursively extract HTML content of an element and its children
def extract_html(element):
    html_content = element.get_attribute('outerHTML')
    children = element.find_elements(By.XPATH, './*')
    for child in children:
        html_content += extract_html(child)
    return html_content

# Extract HTML content of the webpage
html_content = extract_html(driver.find_element(By.XPATH, '/html'))

# Close the WebDriver
driver.quit()

# Print the HTML content
#print(html_content)
with open('info2.txt', 'w', encoding='utf-8') as file:
    file.write(html_content)
