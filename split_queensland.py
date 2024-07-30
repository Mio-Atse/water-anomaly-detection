import csv
import os
from collections import defaultdict

# Function to ensure directory exists
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Create main folders
ensure_dir('pulse')
ensure_dir('pulsetotal')

# Initialize dictionaries to hold open file handles and writers
pulse_files = {}
pulsetotal_files = {}

# Process all CSV files in the dataset_correct folder
for filename in sorted(os.listdir('./dataset_correct')):
    if filename.endswith('.csv'):
        data = defaultdict(lambda: defaultdict(list))
        
        # Read the CSV file
        with open(os.path.join('./dataset_correct', filename), 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                object_id = row['ManagedObjectid']
                series = row['Series']
                data[object_id][series].append(row)
        
        # Process and write data
        for object_id, series_data in data.items():
            for series, rows in series_data.items():
                if series == 'P1':  # Pulse1
                    folder = 'pulse'
                    file_dict = pulse_files
                    fieldnames = ['datetime', 'Pulse1']
                    value_field = 'Pulse1'
                elif series == 'T1':  # Pulse1_Total
                    folder = 'pulsetotal'
                    file_dict = pulsetotal_files
                    fieldnames = ['datetime', 'Pulse1_Total']
                    value_field = 'Pulse1_Total'
                else:
                    continue  # Skip other series types
                
                filename = f"{object_id}_{value_field}.csv"
                file_path = os.path.join(folder, filename)
                
                if object_id not in file_dict:
                    # Open the file in append mode and create a DictWriter
                    f = open(file_path, 'a', newline='')
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    
                    # If file is newly created, write the header
                    if os.path.getsize(file_path) == 0:
                        writer.writeheader()
                    
                    file_dict[object_id] = (f, writer)
                
                # Append data to the CSV file
                f, writer = file_dict[object_id]
                for row in rows:
                    writer.writerow({
                        'datetime': row['datetime'],
                        value_field: row['Value']
                    })

# Close all file handles
for f, writer in pulse_files.values():
    f.close()
for f, writer in pulsetotal_files.values():
    f.close()

print("Data processing complete.")
