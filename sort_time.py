import os
import pandas as pd

# Function to sort data and save to specified folder
def sort_and_save(input_folder, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Iterate over all CSV files in the input folder
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.csv'):
            file_path = os.path.join(input_folder, file_name)
            
            # Read the CSV file
            df = pd.read_csv(file_path, parse_dates=['datetime'], dayfirst=True)
            
            # Sort the DataFrame by 'datetime' column
            df_sorted = df.sort_values(by='datetime')
            
            # Format the 'datetime' column
            df_sorted['datetime'] = df_sorted['datetime'].dt.strftime('%d/%m/%Y %H:%M:%S')
            
            # Save the sorted DataFrame to a new CSV file
            output_file_path = os.path.join(output_folder, file_name)
            df_sorted.to_csv(output_file_path, index=False)

# Directories
pulse_input_folder = 'pulse'
pulse_total_input_folder = 'pulsetotal'
sorted_pulse_output_folder = 'sorted_pulse'
sorted_pulse_total_output_folder = 'sorted_pulsetot'

# Sort and save the files
sort_and_save(pulse_input_folder, sorted_pulse_output_folder)
sort_and_save(pulse_total_input_folder, sorted_pulse_total_output_folder)
