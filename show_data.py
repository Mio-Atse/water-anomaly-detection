import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

def plot_water_usage_from_files(csv_folder, dataset_type, consumption_type=None):
    # Find all CSV files in the specified folder
    csv_files = glob.glob(os.path.join(csv_folder, '*.csv'))

    if not csv_files:
        print(f"No CSV files found in {csv_folder}")
        return

    # Iterate through each CSV file
    for csv_file in csv_files:
        print(f"Processing file: {csv_file}")
        
        try:
            # Read the CSV file into a DataFrame
            if dataset_type == 'helios':
                df = pd.read_csv(csv_file, sep=',')
            else:
                df = pd.read_csv(csv_file)

            # Process data based on dataset type
            if dataset_type == 'queensland':
                process_queensland_data(df, csv_file, consumption_type)
            elif dataset_type == 'helios':
                process_helios_data(df, csv_file, consumption_type)
            elif dataset_type == 'datamill':
                process_datamill_data(df, csv_file,consumption_type)
            else:
                print(f"Unknown dataset type: {dataset_type}")
        except Exception as e:
            print(f"Error processing {csv_file}: {str(e)}")

            
def process_queensland_data(df, csv_file, queensland_type):
    print(f"Columns in the dataframe: {df.columns.tolist()}")
    
    # Check if 'datetime' column exists
    if 'datetime' not in df.columns:
        print("No 'datetime' column found. Please check the data structure.")
        return

    # Convert datetime column to datetime format
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Determine the value column based on queensland_type
    if queensland_type == 'pulse':
        value_column = 'Pulse1'
    elif queensland_type == 'pulsetotal':
        value_column = 'Pulse1_Total'
    else:
        print(f"Unknown Queensland data type: {queensland_type}")
        return

    if value_column not in df.columns:
        print(f"'{value_column}' column not found. Please check the data structure.")
        return

    # Convert value column to numeric, handling any non-numeric values
    df[value_column] = pd.to_numeric(df[value_column], errors='coerce')

    # Sort the dataframe by datetime
    df = df.sort_values('datetime')

    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(df['datetime'], df[value_column], marker='o', linestyle='-')
    plt.title(f'Water Usage Over Time (Queensland - {queensland_type}) - {os.path.basename(csv_file)}')
    plt.xlabel('Time')
    plt.ylabel('Water Usage')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def process_helios_data(df, csv_file, consumption_type):
    # Convert 'datetime' column to datetime format
    df['datetime'] = pd.to_datetime(df['datetime'], format='%d/%m/%Y %H:%M:%S')

    # Sort the dataframe by datetime
    df = df.sort_values('datetime')

    # Choose the column to plot based on consumption type
    if consumption_type == 'daily':
        y_column = 'diff'  # Daily consumption column
        ylabel = 'Daily Consumption'
    elif consumption_type == 'total':
        y_column = 'meter reading'  # Total consumption column
        ylabel = 'Meter Reading'
    else:
        print(f"Unknown consumption type: {consumption_type}")
        return

    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(df['datetime'], df[y_column], marker='o', linestyle='-')
    plt.title(f'{ylabel} Over Time (Helios)\nFile: {os.path.basename(csv_file)}')
    plt.xlabel('Time')
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def process_datamill_data(df, csv_file,consumption_type):
    # Convert date columns to datetime format
    df['READING_START_DATE'] = pd.to_datetime(df['READING_START_DATE'], format='%d/%m/%Y %H:%M')
    # Sort the dataframe by start date

    df = df.sort_values('READING_START_DATE')

    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(df['READING_START_DATE'], df[consumption_type], marker='o', linestyle='-')
    plt.title(f'Gross Consumption Over Time (Datamill) - {os.path.basename(csv_file)}')
    plt.xlabel('Time')
    plt.ylabel('Gross Consumption')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    # Define input folders for each dataset
    dataset_folders = {
        'queensland': {
            'pulse': './dataset/queensland/user_sorted_pulse',
            'pulsetotal': './dataset/queensland/user_sorted_pulsetot'
        },
        'helios': './dataset/helios/user_helios_sorted',
        'datamill': './dataset/datamill/user_datamill_sorted'
    }

    # Ask user which dataset to show
    print("Available datasets:")
    for key in dataset_folders.keys():
        print(f"- {key}")
    
    dataset_type = input("Enter the dataset type you want to display: ").lower()

    if dataset_type in dataset_folders:
        if dataset_type == 'queensland':
            print("Queensland dataset options:")
            print("- daily")
            print("- total")
            queensland_type = input("Enter the Queensland dataset type (pulse or pulsetotal): ").lower()
            if queensland_type in dataset_folders['queensland']:
                csv_folder = dataset_folders['queensland'][queensland_type]
                plot_water_usage_from_files(csv_folder, dataset_type, queensland_type)
            else:
                print("Invalid Queensland dataset type. Please choose 'pulse' or 'pulsetotal'.")
        elif dataset_type == 'helios':
            print("Helios consumption options:")
            print("- daily")
            print("- total")
            consumption_type = input("Enter the Helios consumption type (daily or total): ").lower()
            csv_folder = dataset_folders[dataset_type]
            plot_water_usage_from_files(csv_folder, dataset_type, consumption_type)
        else:
            print("Datamill consumption options:")
            print("- daily")
            print("- total")
            user_input_cons= input("Enter the Datamill consumption type (daily or total): ").lower()
            csv_folder = dataset_folders[dataset_type]
            if user_input_cons == 'daily':
                consumption_type = 'DAILY_AVERAGE_CONSUMPTION'
            else:
                consumption_type = 'GROSS_CONSUMPTION'

            plot_water_usage_from_files(csv_folder, dataset_type,consumption_type)
    else:
        print("Invalid dataset type. Please choose from the available options.")
