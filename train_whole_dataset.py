import os
import pandas as pd
import numpy as np
from pyod.models.iforest import IForest
from pyod.models.knn import KNN
from pyod.models.lof import LOF
from pyod.models.auto_encoder import AutoEncoder
from sklearn.preprocessing import StandardScaler
import joblib

def process_file(file_path, contamination=0.01):
    print(f"Processing file: {file_path}")
    try:
        # Read the CSV file
        if 'helios' in file_path:
            df = pd.read_csv(file_path, sep=';')
            df['datetime'] = pd.to_datetime(df['datetime'], format='%d/%m/%Y %H:%M:%S')
            df = df.sort_values('datetime')
            value_column = 'diff'
        else:  # Queensland dataset
            df = pd.read_csv(file_path)
            df['datetime'] = pd.to_datetime(df['datetime'], format='%d/%m/%Y %H:%M:%S')
            df = df.sort_values('datetime')
            value_column = 'Pulse1_Total'

        print(f"DataFrame shape: {df.shape}")
        print(f"Columns: {df.columns}")

        # Extract hour and day of week
        df['hour'] = df['datetime'].dt.hour
        df['day_of_week'] = df['datetime'].dt.dayofweek

        # Calculate rolling statistics
        window_size = 24 if 'helios' in file_path else 7
        df['diff'] = df[value_column] if 'helios' in file_path else df[value_column].diff()
        df['rolling_mean'] = df['diff'].rolling(window=window_size).mean()
        df['rolling_std'] = df['diff'].rolling(window=window_size).std()

        # Calculate Z-scores
        df['z_score'] = (df['diff'] - df['rolling_mean']) / df['rolling_std']

        # Prepare features for anomaly detection
        features = ['diff', 'hour', 'day_of_week', 'rolling_mean', 'rolling_std'] if 'helios' in file_path else ['diff', 'day_of_week', 'rolling_mean', 'rolling_std']

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

def train_and_save_models(folder_path, dataset_type, contamination=0.01):
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

                X_scaled = process_file(file_path, contamination)
                if X_scaled is not None:
                    X_combined.append(X_scaled)

        if X_combined:
            X_combined = np.vstack(X_combined)
            print(f"Combined feature matrix shape: {X_combined.shape}")

            for model_name, model in models.items():
                model.fit(X_combined)
                joblib.dump(model, f'{model_name}_model.pkl')
                print(f"Saved {model_name} model")

    except Exception as e:
        print(f"Error in training and saving models: {str(e)}")

# Set the folder path based on the dataset type
dataset_type = input("Enter dataset type (helios/queensland): ").lower()
while dataset_type not in ['helios', 'queensland']:
    dataset_type = input("Invalid input. Please enter 'helios' or 'queensland': ").lower()

if dataset_type == 'helios':
    folder_path = './dataset/helios/user dataset'
else:
    folder_path = './sorted_pulsetot'  # Replace with the actual path

print(f"Selected dataset type: {dataset_type}")
print(f"Folder path: {folder_path}")

try:
    train_and_save_models(folder_path, dataset_type, contamination=0.1)
except Exception as e:
    print(f"An error occurred: {str(e)}")
