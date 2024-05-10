import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.common.by import By
import re

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

url = 'https://dawn.com/'

# Assuming chromedriver_path is defined somewhere in your script as the path to the ChromeDriver executable
chromedriver_path = '/Users/wajihanaveed/Downloads/chromedriver-mac-arm64/chromedriver'

try:
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service)
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
    # print("maches")
    # print(matches)

    # Count the number of matches
    num_matches = len(matches)
    print("here")
    with open('new_csv.csv', mode='a+', newline='') as file:
        
        writer = csv.writer(file, delimiter='±')
      

        # Check if it's the first entry after the header
        file.seek(0)
        has_header = csv.Sniffer().has_header(file.read(1024))
        file.seek(0)
        first_entry = not has_header or not bool(list(csv.reader(file))[1:])

        # If it's not the first entry, compare with the last entry
        if not first_entry:
            # file.seek(0)
            # reader = csv.reader(file)
            # # print("1")
            # previous_row = list(reader)[-1]  # Get the last row in the CSV
            # # print("previous_row")
            # # print(previous_row)
            # input_string = str(previous_row)
            # # Split the string by "±"
            # split_by_delimiter = input_string.split('±')

            # # Access the last element
            # last_element = split_by_delimiter[-1]

            # # print("Last Element:", last_element)
 

            # # Extract the content after the last '±'
            # previous_iframes = last_element
            with open('previous_iframes.txt', 'r') as file:
                # Read the entire contents of the file
                previous_iframes = file.read()
            # Access the last element (last column) in the list
            #previous_iframes = columns[-1]
            # print("previous_iframes")
            # print(previous_iframes)
            # print("3")
            # Open a file in write mode ("w" mode)
            def remove_empty_quotes(content):
               

                # # Replace "" with "
                # modified_content = content.replace('""', '"')
                # modified_content = modified_content.replace("\\\\'", "'")
                # modified_content = modified_content.replace("\\\'", "'")
                # modified_content = modified_content.replace("''", "'")
                # # modified_content = content.replace('\\\\'', ''')
                modified_content = content.replace("\\'", "'")


                return modified_content

           
            previous_iframes = remove_empty_quotes(previous_iframes)
            # print("Empty quotes removed and written to output file.")
            with open("filea.txt", "w") as file:
                # Write to the file
                file.write(previous_iframes)
            with open("fileb.txt", "w") as file:
                # Write to the file
                file.write('\n'.join(matches))

            missing_in_file1, missing_in_file2 = compare_iframes(previous_iframes, '\n'.join(matches))
            print("4")
            # with open("fileb.txt", "w") as file:
            #     file.write('\n'.join(matches))
            # with open("filea.txt", "w") as file:
            #     file.write(previous_iframes)



            # print("Iframes missing in file1 but present in file2:")
            # print(len(missing_in_file1))
            # for iframe in missing_in_file1:
            #     print(iframe)

            # print("\nIframes missing in file2 but present in file1:")
            # print(len(missing_in_file2))
            # for iframe in missing_in_file2:
            #     print(iframe)

            # Update the Num Iframes field
            num_iframes = extract_iframes('\n'.join(matches))

            # Check if current iframes are different from the previous entry's iframes
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


        # Replace empty fields with "None"
        # matches = [match.replace('\n', ' ') for match in matches]
        # print("check here")
        # print(matches)
        row = ['Dawn', 'News', 'Chrome', time.strftime('%Y-%m-%d %H:%M:%S'), iframes_difference, num_iframes, num_new_iframes, num_removed_iframes, new_iframes, removed_iframes, matches]
        # row = ["None" if cell == '' else cell for cell in row]
        # print("check")
        # 
        # print(row[-1])
        with open('previous_iframes.txt', 'w') as file:
            file.write(str(row[-1]))

        # Write the data to the CSV
        writer.writerow(row)
        with open('dawn.txt', 'a', encoding='utf-8') as file:
            # Write header information
            file.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write(f"URL: {url}\n\n")
            
            # Write main page content
            file.write(main_page_content)
            
            # Write a dashed line
            file.write("\n\n-----------------------------------------\n\n")


except Exception as e:
    print(e)
finally:
    print("done")
    driver.quit()
