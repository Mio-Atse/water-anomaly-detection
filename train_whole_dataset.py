import os
import pandas as pd
import numpy as np
from pyod.models.iforest import IForest
from pyod.models.knn import KNN
from pyod.models.lof import LOF
from pyod.models.auto_encoder import AutoEncoder
from sklearn.preprocessing import StandardScaler
import joblib

def process_file(file_path, value_column, contamination=0.01):
    print(value_column)
    print(f"Processing file: {file_path}")
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        if value_column == 'GROSS_CONSUMPTION' or value_column =='DAILY_AVERAGE_CONSUMPTION':
            df['datetime'] = pd.to_datetime(df['READING_START_DATE'], format='%d/%m/%Y %H:%M')
        else:

            df['datetime'] = pd.to_datetime(df['datetime'], format='%d/%m/%Y %H:%M:%S')
        df = df.sort_values('datetime')

        print(f"DataFrame shape: {df.shape}")
        print(f"Columns: {df.columns}")

        # Extract hour and day of week
        df['hour'] = df['datetime'].dt.hour
        df['day_of_week'] = df['datetime'].dt.dayofweek

        # Calculate rolling statistics
        window_size = 7
        df['diff'] = df[value_column].diff()
        df['rolling_mean'] = df['diff'].rolling(window=window_size).mean()
        df['rolling_std'] = df['diff'].rolling(window=window_size).std()

        # Calculate Z-scores
        df['z_score'] = (df['diff'] - df['rolling_mean']) / df['rolling_std']

        # Prepare features for anomaly detection
        features = ['diff', 'day_of_week', 'rolling_mean', 'rolling_std']

        # Handle NaN values
        df[features] = df[features].fillna(df[features].mean())
        
        # Check for remaining NaN values
        if df[features].isnull().values.any():
            print("NaN values found after filling with mean:")
            print(df[features].isnull().sum())
            df[features] = df[features].fillna(0)  # Fallback to filling NaNs with 0 if any are left

        X = df[features].values

        # Standardize the features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        return X_scaled
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
        return None

def train_and_save_models(folder_path, value_column, model_save_path, contamination=0.01):
    print(f"Starting training with folder_path: {folder_path}")

    # Define models
    models = {
        'IForest': IForest(contamination=contamination, random_state=42),
        'KNN': KNN(contamination=contamination, n_neighbors=5),
        'LOF': LOF(contamination=contamination),
        'AutoEncoder': AutoEncoder(contamination=contamination)
    }

    try:
        file_list = os.listdir(folder_path)
        print(f"Files in directory: {file_list}")
        
        X_combined = []

        for filename in file_list:
            if filename.endswith('.csv'):
                file_path = os.path.join(folder_path, filename)

                X_scaled = process_file(file_path, value_column, contamination)
                if X_scaled is not None:
                    X_combined.append(X_scaled)

        if X_combined:
            X_combined = np.vstack(X_combined)
            print(f"Combined feature matrix shape: {X_combined.shape}")

            # Ensure the model save path exists
            os.makedirs(model_save_path, exist_ok=True)

            for model_name, model in models.items():
                model.fit(X_combined)
                model_filename = os.path.join(model_save_path, f'{model_name}_model.pkl')
                joblib.dump(model, model_filename)
                print(f"Saved {model_name} model to {model_filename}")

    except Exception as e:
        print(f"Error in training and saving models: {str(e)}")

# Set the dataset type and value column based on the user's choice
dataset_type = input("Enter dataset type (helios/queensland/datamill): ").lower()
while dataset_type not in ['helios', 'queensland', 'datamill']:
    dataset_type = input("Invalid input. Please enter 'helios', 'queensland', or 'datamill': ").lower()

if dataset_type == 'helios':
    folder_path = './dataset/helios/user_helios_sorted'
    
    value_type = input("Enter data type (daily/total): ").lower()
    
    while value_type not in ['daily', 'total']:
        value_type = input("Invalid input. Please enter 'daily' or 'total': ").lower()
    
    if value_type == 'daily':
        model_save_path = './models/helios/daily'
        value_column = 'diff'
    else:
        model_save_path = './models/helios/total'
        value_column = 'meter reading'

elif dataset_type == 'queensland':
    
    value_type = input("Enter data type (daily/total): ").lower()
    
    while value_type not in ['daily', 'total']:
        value_type = input("Invalid input. Please enter 'daily' or 'total': ").lower()
    
    if value_type == 'daily':
        folder_path = './dataset/queensland/user_sorted_pulse'
        model_save_path = './models/queensland/daily'
        value_column = 'Pulse1'
    else:
        folder_path = './dataset/queensland/user_sorted_pulsetot'
        model_save_path = './models/queensland/total'
        value_column = 'Pulse1_Total'

else:
    folder_path = './dataset/datamill/user_datamill_sorted'  # Replace with the actual path
    value_type = input("Enter data type (daily/total): ").lower()
    while value_type not in ['daily', 'total']:
        value_type = input("Invalid input. Please enter 'daily' or 'total': ").lower()
    
    if value_type == 'daily':
        model_save_path = './models/datamill/daily/'
        value_column = 'DAILY_AVERAGE_CONSUMPTION'
    else:
        model_save_path = './models/datamill/total/'
        value_column = 'GROSS_CONSUMPTION'

print(f"Selected dataset type: {dataset_type}")
print(f"Selected pulse type: {value_column}")
print(f"Folder path: {folder_path}")
print(f"Model save path: {model_save_path}")

try:
    train_and_save_models(folder_path, value_column, model_save_path, contamination=0.01)
except Exception as e:
    print(f"An error occurred: {str(e)}")
