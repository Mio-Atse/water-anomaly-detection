import os
import pandas as pd

# Function to sort data and save to specified folder for Queensland dataset
def sort_and_save_queensland(input_folder, output_folder):
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

# Function to sort data and save to specified folder for Helios dataset
def sort_and_save_helios(input_folder, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Iterate over all CSV files in the input folder
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.csv'):
            file_path = os.path.join(input_folder, file_name)
            
            try:
                # Read the CSV file with proper column names and delimiter
                df = pd.read_csv(file_path, delimiter=';', parse_dates=['datetime'], dayfirst=True,
                                 names=['user key', 'datetime', 'meter reading', 'diff'], header=0)
                
                # Sort the DataFrame by 'datetime' column
                df_sorted = df.sort_values(by='datetime')
                
                # Format the 'datetime' column
                df_sorted['datetime'] = df_sorted['datetime'].dt.strftime('%d/%m/%Y %H:%M:%S')
                
                # Save the sorted DataFrame to a new CSV file
                output_file_path = os.path.join(output_folder, file_name)
                df_sorted.to_csv(output_file_path, index=False, sep=';')
            
            except ValueError as e:
                print(f"Error processing file {file_name}: {e}")

# Prompt user to select the dataset to sort
dataset_choice = input("Which dataset would you like to sort? Enter 'Queensland' or 'Helios': ").strip().lower()

if dataset_choice == 'queensland':
    # Directories for Queensland dataset
    pulse_input_folder = 'pulse'
    pulse_total_input_folder = 'pulsetotal'
    sorted_pulse_output_folder = 'sorted_pulse'
    sorted_pulse_total_output_folder = 'sorted_pulsetot'

    # Sort and save the files for Queensland dataset
    sort_and_save_queensland(pulse_input_folder, sorted_pulse_output_folder)
    sort_and_save_queensland(pulse_total_input_folder, sorted_pulse_total_output_folder)

elif dataset_choice == 'helios':
    # Directories for Helios dataset
    helios_input_folder = './dataset/helios/user dataset/'
    helios_output_folder = './dataset/helios/user_dataset_sorted/'

    # Sort and save the files for Helios dataset
    sort_and_save_helios(helios_input_folder, helios_output_folder)

else:
    print("Invalid choice. Please enter 'Queensland' or 'Helios'.")
