import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

def plot_water_usage_from_files(csv_folder, dataset_type='queensland'):
    # Find all CSV files in the specified folder
    csv_files = glob.glob(os.path.join(csv_folder, '*.csv'))

    # Iterate through each CSV file
    for csv_file in csv_files:
        print(f"Processing file: {csv_file}")
        
        # Read the CSV file into a DataFrame
        if dataset_type == 'helios':
            df = pd.read_csv(csv_file, sep=';')
        else:
            df = pd.read_csv(csv_file)

        # Process data based on dataset type
        if dataset_type == 'queensland':
            process_queensland_data(df, csv_file)
        elif dataset_type == 'helios':
            process_helios_data(df, csv_file)
        elif dataset_type == 'datamill':
            process_datamil_data(df, csv_file)
        else:
            print(f"Unknown dataset type: {dataset_type}")

def process_queensland_data(df, csv_file):
    # Convert 'time' column to datetime format
    df['time'] = pd.to_datetime(df['time'])

    # Filter only the rows where typeM is 'Pulse1_Total' and Value is numeric
    filtered_data = df[df['typeM'] == 'Pulse1_Total']
    filtered_data['Value'] = pd.to_numeric(filtered_data['Value'], errors='coerce')

    # Group by 'time' and sum 'Value' for water usage over time
    usage_by_time = filtered_data.groupby('time')['Value'].sum()

    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(usage_by_time.index, usage_by_time.values, marker='o', linestyle='-')
    plt.title(f'Water Usage Over Time (Queensland) - {os.path.basename(csv_file)}')
    plt.xlabel('Time')
    plt.ylabel('Total Water Usage')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def process_helios_data(df, csv_file):
    # Convert 'datetime' column to datetime format
    df['datetime'] = pd.to_datetime(df['datetime'], format='%d/%m/%Y %H:%M:%S')

    # Sort the dataframe by datetime
    df = df.sort_values('datetime')

    # Get unique user keys
    user_keys = df['user key'].unique()

    # Plot data for each user key
    for user_key in user_keys:
        # Filter data for the current user
        user_data = df[df['user key'] == user_key]

        # Plotting
        plt.figure(figsize=(12, 6))
        plt.plot(user_data['datetime'], user_data['diff'], marker='o', linestyle='-')
        plt.title(f'Meter Reading Over Time (Helios) - User: {user_key}\nFile: {os.path.basename(csv_file)}')
        plt.xlabel('Time')
        plt.ylabel('Meter Reading')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

def process_datamil_data(df, csv_file):
    # Convert date columns to datetime format
    df['READING_START_DATE'] = pd.to_datetime(df['READING_START_DATE'], format='%d/%m/%Y %H:%M')
    df['READING_END_DATE'] = pd.to_datetime(df['READING_END_DATE'], format='%d/%m/%Y %H:%M')

    # Sort the dataframe by start date
    df = df.sort_values('READING_START_DATE')

    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(df['READING_START_DATE'], df['GROSS_CONSUMPTION'], marker='o', linestyle='-')
    plt.title(f'Gross Consumption Over Time (Datamil) - {os.path.basename(csv_file)}')
    plt.xlabel('Time')
    plt.ylabel('Gross Consumption')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    # Specify the folder where your CSV files are located
    csv_folder = './dataset/datamill'

    # Specify the dataset type: 'queensland', 'helios', or 'datamil'
    dataset_type = 'datamill'  # Change this to the desired dataset type

    # Call the function to plot water usage for each CSV file
    plot_water_usage_from_files(csv_folder, dataset_type)