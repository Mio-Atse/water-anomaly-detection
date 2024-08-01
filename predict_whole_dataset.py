import os
import pandas as pd
import numpy as np
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

def process_file(file_path, contamination, models, dataset_type, value_type, value_column):
    print(f"Processing file: {file_path}")
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        df['datetime'] = pd.to_datetime(df['datetime'], format='%d/%m/%Y %H:%M:%S')
        df = df.sort_values('datetime')

        print(f"DataFrame shape: {df.shape}")
        print(f"Columns: {df.columns}")

        # Extract hour and day of week
        df['hour'] = df['datetime'].dt.hour
        df['day_of_week'] = df['datetime'].dt.dayofweek

        # Calculate rolling statistics
        window_size = 24 if dataset_type == 'helios' else 7
        df['diff'] = df[value_column].diff()
        df['rolling_mean'] = df[value_column].rolling(window=window_size).mean()
        df['rolling_std'] = df[value_column].rolling(window=window_size).std()

        # Calculate Z-scores
        df['z_score'] = (df[value_column] - df['rolling_mean']) / df['rolling_std']

        # Prepare features for anomaly detection
        features = ['hour', 'day_of_week', 'rolling_mean', 'rolling_std']

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
            try:
                outlier_scores = model.decision_function(X_scaled)
                df[f'{model_name}_anomaly_score'] = outlier_scores
                df[f'{model_name}_is_anomaly'] = model.predict(X_scaled)
                z_score_threshold = 3 if dataset_type == 'helios' else 1
                df[f'{model_name}_is_validated_anomaly'] = (df[f'{model_name}_is_anomaly'] == 1) & (abs(df['z_score']) > z_score_threshold)
                results[model_name] = df[f'{model_name}_is_validated_anomaly'].sum()
            except Exception as e:
                print(f"Error applying {model_name} model: {str(e)}")

        # Create a new column for points that are anomalies according to all methods
        df['all_methods_anomaly'] = df[[f'{model_name}_is_validated_anomaly' for model_name in models]].all(axis=1)
        results['all_methods'] = df['all_methods_anomaly'].sum()

        return df, results
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
        return None, None
    
    
def plot_results(df, user_key, dataset_type, value_type, value_column, results):
    try:
        plt.figure(figsize=(12, 6))
        x = df['datetime']
        y = df[value_column]
        title = f'Anomalies Detected by All Methods for {user_key}'

        plt.plot(x, y, label='Consumption', alpha=0.5)

        all_methods_anomalies = df[df['all_methods_anomaly']]
        plt.scatter(all_methods_anomalies[x.name], all_methods_anomalies[y.name], label='Anomalies (All Methods)', color='red')

        plt.title(title)
        plt.xlabel('DateTime')
        plt.ylabel('Consumption')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Error plotting results: {str(e)}")

def main(folder_path, model_save_path, dataset_type, value_type, value_column, contamination=0.01):
    print(f"Starting main function with folder_path: {folder_path} and model_save_path: {model_save_path}")

    # Load pre-trained models
    models = load_models(model_save_path)

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

                df, results = process_file(file_path, contamination, models, dataset_type, value_type, value_column)

                if df is not None and results is not None:
                    user_key = df['user key'].iloc[0] if dataset_type == 'helios' else filename.split('.')[0]

                    print(f"Processing data for file: {filename}")
                    print(f"Total data points: {len(df)}")
                    for model_name, count in results.items():
                        print(f"{model_name} validated anomalies: {count}")

                    # Plot the results
                    plot_results(df, user_key, dataset_type, value_type, value_column, results)
                else:
                    print(f"Skipping file {filename} due to processing error")
    except Exception as e:
        print(f"Error in main function: {str(e)}")

# Get user input for dataset type and value type
dataset_type = input("Enter dataset type (helios/queensland/datamill): ").lower()
while dataset_type not in ['helios', 'queensland', 'datamill']:
    dataset_type = input("Invalid input. Please enter 'helios', 'queensland', or 'datamill': ").lower()

value_type = input("Enter data type (daily/total): ").lower()
while value_type not in ['daily', 'total']:
    value_type = input("Invalid input. Please enter 'daily' or 'total': ").lower()

# Set the folder path, model save path, and value column based on the dataset type and value type
if dataset_type == 'helios':
    folder_path = './dataset/helios/user_helios_sorted'
    model_save_path = f'./models/helios/{value_type}'
    value_column = 'diff' if value_type == 'daily' else 'meter reading'
elif dataset_type == 'queensland':
    folder_path = f'./dataset/queensland/user_sorted_pulse{"tot" if value_type == "total" else ""}'
    model_save_path = f'./models/queensland/{value_type}'
    value_column = 'Pulse1' if value_type == 'daily' else 'Pulse1_Total'
else:  # datamill
    folder_path = './dataset/datamill/user_datamill_sorted'
    model_save_path = f'./models/datamill/{value_type}'
    value_column = 'DAILY_AVERAGE_CONSUMPTION' if value_type == 'daily' else 'GROSS_CONSUMPTION'

print(f"Selected dataset type: {dataset_type}")
print(f"Selected value type: {value_type}")
print(f"Value column: {value_column}")
print(f"Folder path: {folder_path}")
print(f"Model save path: {model_save_path}")

try:
    main(folder_path, model_save_path, dataset_type, value_type, value_column, contamination=0.01)
except Exception as e:
    print(f"An error occurred: {str(e)}")