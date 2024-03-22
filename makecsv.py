import pandas as pd

# Step 1: Read the CSV file directly without specifying a full path
data = pd.read_csv('data.csv')  # Reading 'data.csv' from the current directory
file_names = data['CSV'].unique()  # Extracting unique filenames from the 'CSV' column

# Step 2: Iterate through the filenames and create new CSV files in the same directory
for file_name in file_names:
    # Create an empty DataFrame or one with a predefined structure if necessary
    df = pd.DataFrame()
    
    # Define the filename for the new CSV file
    full_path = f'{file_name}.csv'
    
    # Save the DataFrame to a new CSV file in the current directory
    df.to_csv(full_path, index=False)
    
    print(f'Created {full_path}')
