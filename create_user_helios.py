import os
import pandas as pd

def process_helios_dataset(input_folder, output_folder):
    # Ensure the output directory exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Initialize an empty DataFrame to concatenate all data
    all_data = pd.DataFrame()

    # Read all CSV files in the input folder
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.csv'):
            file_path = os.path.join(input_folder, file_name)
            data = pd.read_csv(file_path, delimiter=';')

            # Concatenate data
            all_data = pd.concat([all_data, data])

    # Filter to keep only the necessary columns
    all_data = all_data[['user key', 'datetime', 'meter reading', 'diff']]

    # Get unique user keys
    user_keys = all_data['user key'].unique()

    # Create separate files for each user, excluding 'user key'
    for user_key in user_keys:
        user_data = all_data[all_data['user key'] == user_key]
        user_data = user_data[['datetime', 'meter reading', 'diff']]
        user_data.to_csv(os.path.join(output_folder, f'{user_key}.csv'), index=False, sep=';')

    print("Helios dataset files created successfully.")

def process_datamill_dataset(input_folder, output_folder):
    # Ensure the output directory exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file_name in os.listdir(input_folder):
        if file_name.endswith('.csv'):
            file_path = os.path.join(input_folder, file_name)
            data = pd.read_csv(file_path)

            # Filter out rows with NaN POSTCODE_OUTCODE
            data = data.dropna(subset=['POSTCODE_OUTCODE'])

            # Get unique POSTCODE_OUTCODE values
            postcodes = data['POSTCODE_OUTCODE'].unique()

            # Create separate files for each POSTCODE_OUTCODE
            for postcode in postcodes:
                postcode_data = data[data['POSTCODE_OUTCODE'] == postcode]
                # Select the required columns
                selected_columns = postcode_data[['READING_START_DATE', 'READING_END_DATE', 
                                                  'READING_START_READING', 'READING_END_READING', 
                                                  'GROSS_CONSUMPTION', 'DAILY_AVERAGE_CONSUMPTION']]
                selected_columns.to_csv(os.path.join(output_folder, f'{postcode}.csv'), index=False)

    print("Datamill dataset files created successfully.")

def main():
    dataset_choice = input("Which dataset do you want to process? (helios/datamill): ").strip().lower()

    if dataset_choice == 'helios':
        input_folder = './dataset/helios/org dataset full'
        output_folder = './dataset/helios/user_dataset_solid'
        process_helios_dataset(input_folder, output_folder)
    elif dataset_choice == 'datamill':
        input_folder = './dataset/datamill/org dataset'
        output_folder = './dataset/datamill/user_dataset'
        process_datamill_dataset(input_folder, output_folder)
    else:
        print("Invalid choice. Please choose either 'helios' or 'datamill'.")

if __name__ == "__main__":
    main()
