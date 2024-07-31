import os
import pandas as pd
import shutil
def replace_semicolons(input_folder, output_folder):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Iterate over all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.csv'):
            # Construct full file path
            input_file_path = os.path.join(input_folder, filename)
            output_file_path = os.path.join(output_folder, filename)

            # Read the CSV file with semicolons as delimiter
            df = pd.read_csv(input_file_path, delimiter=';')

            # Save the DataFrame to a new CSV file with commas as delimiter
            df.to_csv(output_file_path, index=False, sep=',')

            print(f"Processed file: {filename}")

# Example usage
input_folder = './dataset/helios/user_helios_sorted_semicol'
output_folder = './dataset/helios/user_helios_sorted'

replace_semicolons(input_folder, output_folder)
try:
        shutil.rmtree('./dataset/helios/user_helios_sorted_semicol')
        print("Helios files removed successfully.")
except:
        print("Helios files couldn't be removed")