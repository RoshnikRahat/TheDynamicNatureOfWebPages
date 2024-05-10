import csv
import os

# Open the data.csv file for reading
with open('data.csv', 'r') as csvfile:
    csv_reader = csv.reader(csvfile)
    
    # Skip the header row
    next(csv_reader)
    
    # Iterate over each row in the CSV file
    for row in csv_reader:
        # Extract the name from the third column
        name = row[2]
        
        # Create a new text file with the extracted name
        new_txt_filename = f"{name}.txt"
        
        # Check if the file already exists, if it does, create a unique name
        counter = 1
        while os.path.exists(new_txt_filename):
            new_txt_filename = f"{name}_{counter}.txt"
            counter += 1
        
        # Create an empty text file with the determined filename
        open(new_txt_filename, 'a').close()
