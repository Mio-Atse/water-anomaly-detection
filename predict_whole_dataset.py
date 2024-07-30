import os
import pandas as pd
import numpy as np
import pickle
from pyod.models.iforest import IForest
from pyod.models.knn import KNN
from pyod.models.lof import LOF
from pyod.models.auto_encoder import AutoEncoder
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import joblib

def load_models(models_path):
    models = {}
    for model_name in ['IForest_model', 'KNN_model', 'LOF_model', 'AutoEncoder_model']:
        model_file = os.path.join(models_path, f'{model_name}.pkl')
        if os.path.exists(model_file):
            try:
                models[model_name] = joblib.load(model_file)
                print(f"Loaded {model_name} model.")
            except Exception as e:
                print(f"Error loading {model_name} model: {str(e)}")
        else:
            print(f"Model file {model_file} does not exist.")
    return models

def process_file(file_path, contamination=0.01, models=None):
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

        X = df[features].values

        # Standardize the features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Initialize results dictionary
        results = {}

        # Anomaly Detection Models
        for model_name, model in models.items():
            outlier_scores = model.decision_function(X_scaled)
            df[f'{model_name}_anomaly_score'] = outlier_scores
            df[f'{model_name}_is_anomaly'] = model.predict(X_scaled)
            z_score_threshold = 1 #3 for helios
            df[f'{model_name}_is_validated_anomaly'] = (df[f'{model_name}_is_anomaly'] == 1) & (abs(df['z_score']) > z_score_threshold)
            results[model_name] = df[f'{model_name}_is_validated_anomaly'].sum()

        # Create a new column for points that are anomalies according to all methods
        df['all_methods_anomaly'] = df[[f'{model_name}_is_validated_anomaly' for model_name in models]].all(axis=1)
        results['all_methods'] = df['all_methods_anomaly'].sum()

        return df, results
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
        return None, None

def plot_results(df, user_key, dataset_type, results):
    try:
        plt.figure(figsize=(12, 6))
        x = df['datetime']
        y = df['diff'] if 'helios' in dataset_type else df['Pulse1_Total']
        title = f'Anomalies Detected by All Methods for {user_key}'

        plt.plot(x, y, label='Consumption', alpha=0.5)

        all_methods_anomalies = df[df['all_methods_anomaly']]
        plt.scatter(all_methods_anomalies[x.name], all_methods_anomalies[y.name], label='Anomalies (All Methods)', color='red')

        plt.title(title)
        plt.xlabel('DateTime')
        plt.ylabel('Consumption' if 'helios' in dataset_type else 'Consumption')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Error plotting results: {str(e)}")

def main(folder_path, models_path, dataset_type, contamination=0.01):
    print(f"Starting main function with folder_path: {folder_path} and models_path: {models_path}")

    # Load pre-trained models
    models = load_models(models_path)

    # Check if models are loaded correctly
    if not models:
        print("No models loaded. Exiting.")
        return

    try:
        file_list = os.listdir(folder_path)
        print(f"Files in directory: {file_list}")
        
        for filename in file_list:
            if filename.endswith('.csv'):
                file_path = os.path.join(folder_path, filename)

                df, results = process_file(file_path, contamination, models)

                if df is not None and results is not None:
                    user_key = df['user key'].iloc[0] if 'helios' in dataset_type else filename.split('.')[0]

                    print(f"Processing data for file: {filename}")
                    print(f"Total data points: {len(df)}")
                    for model_name, count in results.items():
                        print(f"{model_name} validated anomalies: {count}")

                    # Plot the results
                    plot_results(df, user_key, dataset_type, results)
                else:
                    print(f"Skipping file {filename} due to processing error")
    except Exception as e:
        print(f"Error in main function: {str(e)}")

# Get user input for dataset type
dataset_type = input("Enter dataset type (helios/queensland): ").lower()
while dataset_type not in ['helios', 'queensland']:
    dataset_type = input("Invalid input. Please enter 'helios' or 'queensland': ").lower()

# Set the folder path and models path based on the dataset type
if dataset_type == 'helios':
    folder_path = './dataset/helios/user dataset'
    models_path = './models/helios'
else:
    folder_path = './sorted_pulsetot'  # Replace with the actual path
    models_path = './'

print(f"Selected dataset type: {dataset_type}")
print(f"Folder path: {folder_path}")
print(f"Models path: {models_path}")

try:
    main(folder_path, models_path, dataset_type, contamination=0.01)
except Exception as e:
    print(f"An error occurred: {str(e)}")
