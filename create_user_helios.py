import pandas as pd

# Read the dataset
file_path = './dataset/helios/swm_trialA_1K.csv'
data = pd.read_csv(file_path, delimiter=';')

# Get unique user keys
user_keys = data['user key'].unique()

# Create separate files for each user
for user_key in user_keys:
    user_data = data[data['user key'] == user_key]
    user_data.to_csv(f'{user_key}.csv', index=False, sep=';')

print("Files created successfully.")
