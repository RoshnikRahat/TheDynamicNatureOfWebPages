import os
import requests
from bs4 import BeautifulSoup
import hashlib
import shutil
import base64
from string import ascii_lowercase

# Website URL 
website_url = "https://www.bbc.com"

# Directories to save previous and current data
previous_directory = "previous_data"
current_directory = "current_data"

# Global counter for handling long filenames
global_filename_counter = 0

def download_html(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print("Failed to download HTML")
        return None

def download_images(img_srcs, directory):
    global global_filename_counter
    downloaded_images = []
    for img_src in img_srcs:
        try:
            response = requests.get(img_src)
            if response.status_code == 200:
                image_data = response.content
                filename = os.path.join(directory, img_src.split("/")[-1])
                try:
                    with open(filename, "wb") as f:
                        f.write(image_data)
                except OSError as e:
                    print(f"Error writing file: {e}")
                    # If filename is too long, rename the file using global counter
                    filename = os.path.join(directory, generate_filename(global_filename_counter))
                    with open(filename, "wb") as f:
                        f.write(image_data)
                downloaded_images.append(filename)
                global_filename_counter += 1
            else:
                print(f"Failed to download image: {img_src}")
        except Exception as e:
            print(f"Error downloading image: {e}")
            # If the error occurs, handle it appropriately

            # handle base64-encoded image data URLs

            if img_src.startswith("data:"):
                base64_data = img_src.split(",")[1]
                image_data = base64.b64decode(base64_data)
                filename = os.path.join(directory, img_src.split("/")[-1])
                with open(filename, "wb") as f:
                    f.write(image_data)
                downloaded_images.append(filename)
            else:
                # Attempt to prepend 'https://' and try again
                try:
                    response = requests.get(f"https:/{img_src}")
                    if response.status_code == 200:
                        image_data = response.content
                        filename = os.path.join(directory, img_src.split("/")[-1])
                        with open(filename, "wb") as f:
                            f.write(image_data)
                        downloaded_images.append(filename)
                    
                    else:
                        print(f"Failed to download image after prepending 'https:/': {img_src}")
                except Exception as e:
                    print(f"Error downloading image after prepending 'https:/': {e}")
                    
    return downloaded_images

def generate_filename(counter):
    # Convert counter value to corresponding alphabet character (a-z)
    # This is for handling long filenames and assigning them to random filenames a-z 
    if counter < len(ascii_lowercase):
        return f"{ascii_lowercase[counter]}"
    else:
        return f"image_{counter}"

def calculate_hash(filename):
    with open(filename, "rb") as f:
        image_data = f.read()
    return hashlib.sha256(image_data).hexdigest()

def compare_directories():
    prev_files = os.listdir(previous_directory)
    current_files = os.listdir(current_directory)

    #prev_hashes = {}
    #current_hashes = {}
    #compare 
    """
    for file in prev_files:
        prev_hashes[file] = calculate_hash(os.path.join(previous_directory, file))

    for file in current_files:
        current_hashes[file] = calculate_hash(os.path.join(current_directory, file))

    if prev_hashes == current_hashes:
        print("Website images are the same.")
    """
    
    if set(prev_files) == set(current_files):
        prev_hashes = [calculate_hash(os.path.join(previous_directory, file)) for file in prev_files]
        current_hashes = [calculate_hash(os.path.join(current_directory, file)) for file in current_files]

        if prev_hashes != current_hashes:
            print("Website images have changed!")
        else:
            print("Website images are the same.")
    else:
        print("Number of images has changed.")

def main():
    global global_filename_counter
    # Make current directory if it doesn't exist 
    if not os.path.exists(current_directory):
        os.makedirs(current_directory)

    # Download HTML and images to current directory
    current_html = download_html(website_url)
    soup = BeautifulSoup(current_html, 'html.parser')
    current_img_srcs = [img['src'] for img in soup.find_all('img', src=True)]
    current_images = download_images(current_img_srcs, current_directory)

    # Compare previous and current directories 
    if os.path.exists(previous_directory):
        if(len(os.listdir(previous_directory)) > 0) : 
            compare_directories()

    # Move contents of current directory to previous directory
    if os.path.exists(previous_directory):
        shutil.rmtree(previous_directory)
    shutil.move(current_directory, previous_directory)

    # Reset current directory
    os.makedirs(current_directory)

    # Reset global counter
    global_filename_counter = 0

if __name__ == "__main__":
    main()