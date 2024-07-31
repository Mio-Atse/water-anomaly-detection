import csv
import os
import sys
import shutil
import pandas as pd
from collections import defaultdict
from datetime import datetime
import pytz

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def convert_time_format(time_str):
    try:
        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
    except ValueError:
        try:
            dt = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            print(f"Unable to parse datetime: {time_str}")
            return time_str

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=pytz.UTC)
    else:
        dt = dt.astimezone(pytz.UTC)

    return dt.strftime('%d/%m/%Y %H:%M:%S')

def preprocess_queensland(input_folder, output_folder):
    ensure_dir(input_folder)
    ensure_dir(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith('.csv'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f'processed_{filename}')
            
            df = pd.read_csv(input_path)
            df['time'] = df['time'].apply(convert_time_format)
            df = df.rename(columns={'time': 'datetime'})
            df.to_csv(output_path, index=False)

            print(f"Processed file: {output_path}")

    print("Queensland preprocessing complete. Check the output folder for processed files.")

def split_queensland(input_folder, pulse_folder, pulsetotal_folder):
    ensure_dir(pulse_folder)
    ensure_dir(pulsetotal_folder)

    pulse_files = {}
    pulsetotal_files = {}

    for filename in sorted(os.listdir(input_folder)):
        if filename.endswith('.csv'):
            data = defaultdict(lambda: defaultdict(list))
            
            with open(os.path.join(input_folder, filename), 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    object_id = row['ManagedObjectid']
                    series = row['Series']
                    data[object_id][series].append(row)
            
            for object_id, series_data in data.items():
                for series, rows in series_data.items():
                    if series == 'P1':
                        folder = pulse_folder
                        file_dict = pulse_files
                        fieldnames = ['datetime', 'Pulse1']
                        value_field = 'Pulse1'
                    elif series == 'T1':
                        folder = pulsetotal_folder
                        file_dict = pulsetotal_files
                        fieldnames = ['datetime', 'Pulse1_Total']
                        value_field = 'Pulse1_Total'
                    else:
                        continue
                    
                    filename = f"{object_id}_{value_field}.csv"
                    file_path = os.path.join(folder, filename)
                    
                    if object_id not in file_dict:
                        f = open(file_path, 'a', newline='')
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        
                        if os.path.getsize(file_path) == 0:
                            writer.writeheader()
                        
                        file_dict[object_id] = (f, writer)
                    
                    f, writer = file_dict[object_id]
                    for row in rows:
                        writer.writerow({
                            'datetime': row['datetime'],
                            value_field: row['Value']
                        })

                    print(f"Processed series {series} for {object_id}: {file_path}")

    for f, writer in pulse_files.values():
        f.close()
    for f, writer in pulsetotal_files.values():
        f.close()

    print("Queensland dataset processing complete.")

def process_helios_dataset(input_folder, output_folder):
    ensure_dir(output_folder)
    all_data = pd.DataFrame()

    for file_name in os.listdir(input_folder):
        if (file_name.endswith('.csv')):
            file_path = os.path.join(input_folder, file_name)
            data = pd.read_csv(file_path, delimiter=';')
            all_data = pd.concat([all_data, data])

    all_data = all_data[['user key', 'datetime', 'meter reading', 'diff']]
    user_keys = all_data['user key'].unique()

    for user_key in user_keys:
        user_data = all_data[all_data['user key'] == user_key]
        user_data = user_data[['datetime', 'meter reading', 'diff']]
        output_file = os.path.join(output_folder, f'{user_key}.csv')
        user_data.to_csv(output_file, index=False, sep=';')
        print(f"Created file: {output_file}")

    print("Helios dataset files created successfully.")

def process_datamill_dataset(input_folder, output_folder):
    ensure_dir(output_folder)

    for file_name in os.listdir(input_folder):
        if file_name.endswith('.csv'):
            file_path = os.path.join(input_folder, file_name)
            data = pd.read_csv(file_path)

            data = data.dropna(subset=['POSTCODE_OUTCODE'])
            postcodes = data['POSTCODE_OUTCODE'].unique()

            for postcode in postcodes:
                postcode_data = data[data['POSTCODE_OUTCODE'] == postcode]
                selected_columns = postcode_data[['READING_START_DATE', 'READING_END_DATE', 
                                                  'READING_START_READING', 'READING_END_READING', 
                                                  'GROSS_CONSUMPTION', 'DAILY_AVERAGE_CONSUMPTION']]
                output_file = os.path.join(output_folder, f'{postcode}.csv')
                selected_columns.to_csv(output_file, index=False)
                print(f"Processed postcode {postcode}: {output_file}")

    print("Datamill dataset files created successfully.")

def main():
    dataset_choice = input("Which dataset do you want to process? (queensland/helios/datamill): ").strip().lower()

    if dataset_choice == 'queensland':
        queensland_input_folder = './dataset/queensland/org_dataset/'
        queensland_preprocessed_folder = './dataset/queensland/dataset_correct'
        pulse_folder = './dataset/queensland/pulse'
        pulsetotal_folder = './dataset/queensland/pulsetotal'
        
        preprocess_queensland(queensland_input_folder, queensland_preprocessed_folder)
        split_queensland(queensland_preprocessed_folder, pulse_folder, pulsetotal_folder)
        shutil.rmtree("./dataset/queensland/dataset_correct")
        
    elif dataset_choice == 'helios':
        input_folder = './dataset/helios/org_dataset'
        output_folder = './dataset/helios/user_dataset'
        process_helios_dataset(input_folder, output_folder)
    elif dataset_choice == 'datamill':
        input_folder = './dataset/datamill/org_dataset'
        output_folder = './dataset/datamill/user_dataset'
        process_datamill_dataset(input_folder, output_folder)
    else:
        print("Invalid choice. Please choose 'queensland', 'helios', or 'datamill'.")

if __name__ == "__main__":
    main()
