import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.common.by import By
import re
import os

def remove_empty_quotes(content):
    modified_content = content.replace("\\'", "'")
    return modified_content
# Function to extract content from iframes
def extract_iframe_content(driver):
    frames = driver.find_elements(By.TAG_NAME, 'iframe')
    iframe_contents = []
    for frame in frames:
        try:
            driver.switch_to.frame(frame)
            iframe_contents.append(driver.page_source)
        except:
            pass
        finally:
            driver.switch_to.default_content()
    return iframe_contents

def extract_iframes(text):
    """Extract iframes from the given text."""
    if not isinstance(text, str):
        raise ValueError("Input must be a string.")
    
    iframes = []
    # Assuming iframes are enclosed within <iframe> tags
    start = text.find("<iframe")
    while start != -1:
        end = text.find("</iframe>", start)
        if end != -1:
            iframes.append(text[start:end + 9])  # Include the closing tag
            start = text.find("<iframe", end)
        else:
            break
    return iframes

def compare_iframes(file1_text, file2_text):
    """Compare iframes between two texts."""
    iframes_file1 = extract_iframes(str(file1_text))
    iframes_file2 = extract_iframes(str(file2_text))

    missing_in_file1 = [iframe for iframe in iframes_file2 if iframe not in iframes_file1]
    missing_in_file2 = [iframe for iframe in iframes_file1 if iframe not in iframes_file2]

    return missing_in_file1, missing_in_file2

# Read URLs and filenames from data.csv
row_content = []
with open('mydata.csv', 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader, None)
    for row in csvreader:
        if len(row) >= 6:  # Ensure the row has at least 4 columns
            row_content.append((row[0],row[1],row[2], row[5]))  # Assuming URL is in the third column and filename in the fourth column

# Assuming chromedriver_path is defined somewhere in your script as the path to the ChromeDriver executable
chromedriver_path = '/Users/wajihanaveed/Downloads/chromedriver-mac-arm64/chromedriver'


try:
    for category, url, filename,webname in row_content:
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service)
        driver.execute_cdp_cmd("Network.clearBrowserCache", {})
        driver.get(url)
        time.sleep(5)

        # Extract content from main page
        main_page_content = driver.page_source

        # Extract content from iframes
        iframe_contents = extract_iframe_content(driver)

        # Define the regular expression pattern to extract iframe content
        iframe_pattern = r'<iframe.*?</iframe>'

        # Find all occurrences of the pattern in the content
        matches = re.findall(iframe_pattern, main_page_content, re.DOTALL)

        # Count the number of matches
        num_matches = len(matches)

        with open(f'{filename}.csv', mode='a+', newline='') as file:
            writer = csv.writer(file, delimiter='±')

            # Check if it's the first entry after the header
            file.seek(0)
            has_header = csv.Sniffer().has_header(file.read(1024))
            file.seek(0)
            first_entry = not has_header or not bool(list(csv.reader(file))[1:])

            if not first_entry:
                with open(f'previous_iframes_{filename}.txt', 'r') as file:
                    previous_iframes = file.read()

                previous_iframes = remove_empty_quotes(previous_iframes)

                with open("filea.txt", "w") as file:
                    file.write(previous_iframes)
                with open("fileb.txt", "w") as file:
                    file.write('\n'.join(matches))

                missing_in_file1, missing_in_file2 = compare_iframes(previous_iframes, '\n'.join(matches))

                num_iframes = extract_iframes('\n'.join(matches))

                if len(missing_in_file2) != 0 and len(missing_in_file1) != 0:
                    iframes_difference = "Yes"
                    num_new_iframes = len(missing_in_file1)
                    num_removed_iframes = len(missing_in_file2)
                    new_iframes = missing_in_file1
                    removed_iframes = missing_in_file2
                    num_iframes = len(num_iframes)
                elif len(missing_in_file2) != 0 and len(missing_in_file1) == 0: 
                    iframes_difference = "Yes"
                    num_new_iframes = "None"
                    num_removed_iframes = len(missing_in_file2)
                    new_iframes = "None"
                    removed_iframes = missing_in_file2
                    num_iframes = len(num_iframes)
                elif len(missing_in_file2) == 0 and len(missing_in_file1) != 0: 
                    iframes_difference = "Yes"
                    num_new_iframes = len(missing_in_file1)
                    num_removed_iframes = 0
                    new_iframes = missing_in_file1
                    removed_iframes = "None"
                    num_iframes = len(num_iframes)
                else:
                    iframes_difference = "None"
                    num_new_iframes = "None"
                    num_removed_iframes = "None"
                    new_iframes = "None"
                    removed_iframes = "None"
            else:
                new_iframes = "None"
                removed_iframes = "None"
                num_iframes = num_matches
                iframes_difference = "None"
                num_new_iframes = "None"
                num_removed_iframes = "None"

            row = [webname, category, 'Chrome', time.strftime('%Y-%m-%d %H:%M:%S'), iframes_difference, num_iframes, num_new_iframes, num_removed_iframes, new_iframes, removed_iframes, matches]
            with open(f'previous_iframes_{filename}.txt', 'w') as file:
                file.write(str(row[-1]))

            writer.writerow(row)
            with open(f'{filename}.txt', 'a', encoding='utf-8') as file:
                file.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write(f"URL: {url}\n\n")
                file.write(main_page_content)
                file.write("\n\n-----------------------------------------\n\n")
except Exception as e:
    print(e)
finally:
    print("done")
    driver.quit()
