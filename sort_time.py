import os
import pandas as pd
import sys
import shutil

def replace_semicolons_with_commas(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path, delimiter=';')
    
    # Replace all semicolons with commas in the entire DataFrame
    df = df.applymap(lambda x: str(x).replace(';', ',') if isinstance(x, str) else x)
    
    return df

def sort_and_save_datamill(input_folder, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Iterate over all CSV files in the input folder
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.csv'):
            file_path = os.path.join(input_folder, file_name)
            
            try:
                # Read the CSV file
                df = pd.read_csv(file_path, parse_dates=['READING_START_DATE'], dayfirst=True)
                
                # Sort the DataFrame by 'READING_START_DATE' column
                df_sorted = df.sort_values(by='READING_START_DATE')
                
                # Format the 'READING_START_DATE' column
                df_sorted['READING_START_DATE'] = df_sorted['READING_START_DATE'].dt.strftime('%d/%m/%Y %H:%M')
                
                # Save the sorted DataFrame to a new CSV file
                output_file_path = os.path.join(output_folder, file_name)
                df_sorted.to_csv(output_file_path, index=False)
                
                print(f"Successfully processed and sorted {file_name}")
            
            except Exception as e:
                print(f"Error processing file {file_name}: {e}")


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
            
            print(f"Successfully sorted {file_name}")

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
                                 names=['datetime', 'meter reading', 'diff'], header=0)
                
                # Sort the DataFrame by 'datetime' column
                df_sorted = df.sort_values(by='datetime')
                
                # Format the 'datetime' column
                df_sorted['datetime'] = df_sorted['datetime'].dt.strftime('%d/%m/%Y %H:%M:%S')
                
                # Save the sorted DataFrame to a new CSV file
                output_file_path = os.path.join(output_folder, file_name)
                df_sorted.to_csv(output_file_path, index=False, sep=';')
                
                print(f"Successfully sorted {file_name}")
            
            except ValueError as e:
                print(f"Error processing file {file_name}: {e}")

# Prompt user to select the dataset to sort
dataset_choice = input("Which dataset would you like to sort? Enter 'Queensland', 'Helios', or 'DataMill': ").strip().lower()

if dataset_choice == 'queensland':
    # Directories for Queensland dataset
    pulse_input_folder = './dataset/queensland/pulse'
    pulse_total_input_folder = './dataset/queensland/pulsetotal'
    sorted_pulse_output_folder = './dataset/queensland/user_sorted_pulse'
    sorted_pulse_total_output_folder = './dataset/queensland/user_sorted_pulsetot'

    # Sort and save the files for Queensland dataset
    sort_and_save_queensland(pulse_input_folder, sorted_pulse_output_folder)
    sort_and_save_queensland(pulse_total_input_folder, sorted_pulse_total_output_folder)
    
    try:
        shutil.rmtree("./dataset/queensland/pulse")
        shutil.rmtree("./dataset/queensland/pulsetotal")
        print("Queensland files removed successfully.")
    except:
        print("Queensland files couldn't be removed")
        
elif dataset_choice == 'helios':
    # Directories for Helios dataset
    helios_input_folder = './dataset/helios/user_dataset/'
    helios_output_folder = './dataset/helios/user_helios_sorted_semicol/'

    # Sort and save the files for Helios dataset
    sort_and_save_helios(helios_input_folder, helios_output_folder)
    
    
    try:
        shutil.rmtree("./dataset/helios/user_dataset")
        print("Helios files removed successfully.")
    except:
        print("Helios files couldn't be removed")
    

elif dataset_choice == 'datamill':
    # Directories for DataMill dataset
    datamill_input_folder = './dataset/datamill/user_dataset'
    datamill_output_folder = './dataset/datamill/user_datamill_sorted'

    # Sort and save the files for DataMill dataset
    sort_and_save_datamill(datamill_input_folder, datamill_output_folder)

    try:
        shutil.rmtree("./dataset/datamill/user_dataset")
        print("DataMill files removed successfully.")
    except:
        print("DataMill files couldn't be removed")
else:
    print("Invalid choice. Please enter 'Queensland', 'Helios', or 'DataMill'.")