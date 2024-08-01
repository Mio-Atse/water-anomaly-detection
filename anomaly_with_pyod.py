import os
import pandas as pd
import numpy as np
from pyod.models.iforest import IForest
from pyod.models.knn import KNN
from pyod.models.lof import LOF
from pyod.models.auto_encoder import AutoEncoder
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

def process_file(file_path, dataset_type, option, contamination=0.01, models=None, z_score_threshold=3):
    # Read the CSV file
    df = pd.read_csv(file_path, sep=';') if 'helios' in dataset_type else pd.read_csv(file_path)

    # Convert datetime to pandas datetime
    if dataset_type == 'helios':
        df['datetime'] = pd.to_datetime(df['datetime'], format='%d/%m/%Y %H:%M:%S')
        if option == 'daily':
            df['diff'] = df['diff']
        elif option == 'total':
            df['diff'] = df['meter reading'].diff()

    elif dataset_type == 'queensland':
        try:
            df['datetime'] = pd.to_datetime(df['datetime'], format='%d/%m/%Y %H:%M:%S')
            if option == 'daily':
                df['diff'] = df['Pulse1'].diff()
            elif option == 'total':
                df['diff'] = df['Pulse1_Total'].diff()
        except ValueError as e:
            print(f"Error converting datetime: {e}")
            print(f"First few datetime values: {df['datetime'].head()}")
            raise
    
    elif dataset_type == 'datamill':
        df['datetime'] = pd.to_datetime(df['READING_START_DATE'], format='%d/%m/%Y %H:%M')
        if option == 'daily':
            df['diff'] = df['DAILY_AVERAGE_CONSUMPTION'].diff()
        else:
            df['diff'] = df['GROSS_CONSUMPTION'].diff()

    # Sort by datetime
    df = df.sort_values('datetime')

    # Extract hour and day of week
    df['hour'] = df['datetime'].dt.hour
    df['day_of_week'] = df['datetime'].dt.dayofweek

    # Calculate rolling statistics
    window_size = 24 if dataset_type == 'helios' else 7
    df['rolling_mean'] = df['diff'].rolling(window=window_size).mean()
    df['rolling_std'] = df['diff'].rolling(window=window_size).std()

    # Calculate Z-scores
    df['z_score'] = (df['diff'] - df['rolling_mean']) / df['rolling_std']

    # Prepare features for anomaly detection
    features = ['diff', 'hour', 'day_of_week', 'rolling_mean', 'rolling_std']

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
        model.fit(X_scaled)
        outlier_scores = model.decision_function(X_scaled)
        df[f'{model_name}_anomaly_score'] = outlier_scores
        df[f'{model_name}_is_anomaly'] = model.predict(X_scaled)
        df[f'{model_name}_is_validated_anomaly'] = (df[f'{model_name}_is_anomaly'] == 1) & (abs(df['z_score']) > z_score_threshold)
        results[model_name] = df[f'{model_name}_is_validated_anomaly'].sum()

    return df, results

def plot_results(df, user_key, dataset_type, results):
    plt.figure(figsize=(12, 6))
    x = df['datetime']
    y = df['diff']
    title = f'Validated Anomalies for {user_key} ({dataset_type})'
    
    plt.plot(x, y, label='Consumption', alpha=0.5)
    
    for model_name in results:
        validated_anomalies = df[df[f'{model_name}_is_validated_anomaly']]
        plt.scatter(validated_anomalies[x.name], validated_anomalies[y.name], label=f'{model_name} Validated Anomalies')
    
    plt.title(title)
    plt.xlabel('DateTime')
    plt.ylabel('Consumption Difference')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def main(folder_path, dataset_type, option, contamination, z_score_threshold):
    # Define models
    models = {
        'IForest': IForest(contamination=contamination, random_state=42),
        'KNN': KNN(contamination=contamination, n_neighbors=5),
        'LOF': LOF(contamination=contamination),
        'AutoEncoder': AutoEncoder(contamination=contamination, epoch_num=10)
    }
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            
            df, results = process_file(file_path, dataset_type, option, contamination, models, z_score_threshold)
            
            user_key = filename
            
            print(f"Processing data for file: {filename}")
            print(f"Total data points: {len(df)}")
            for model_name, count in results.items():
                print(f"{model_name} validated anomalies: {count}")
            
            # Plot the results
            plot_results(df, user_key, dataset_type, results)

# Get user input for dataset type
dataset_type = input("Enter dataset type (helios/queensland/datamill): ").lower()
while dataset_type not in ['helios', 'queensland', 'datamill']:
    dataset_type = input("Invalid input. Please enter 'helios', 'queensland', or 'datamill': ").lower()

# Get user input for options
if dataset_type == 'helios':
    option = input("Enter option (daily/total): ").lower()
    while option not in ['daily', 'total']:
        option = input("Invalid input. Please enter 'daily' or 'total': ").lower()
elif dataset_type == 'queensland':
    option = input("Enter option (daily/total): ").lower()
    while option not in ['daily', 'total']:
        option = input("Invalid input. Please enter 'daily' or 'total': ").lower()
elif dataset_type == 'datamill':
    option = input("Enter option (daily/total): ").lower()
    while option not in ['daily', 'total']:
        option = input("Invalid input. Please enter 'daily' or 'total': ").lower()
# Get user input for Z-score and contamination
try:
    z_score_threshold = float(input("Enter Z-score threshold (default 1 for datamill and helios 3 for queensland): "))
except ValueError:
    print("Invalid Z-score threshold. Using default value of 3.")
    z_score_threshold = 3

try:
    contamination = float(input("Enter contamination factor (default 0.01): "))
except ValueError:
    print("Invalid contamination factor. Using default value of 0.01.")
    contamination = 0.01

# Set the folder path based on the dataset type
if dataset_type == 'helios':
    folder_path = './dataset/helios/user_helios_sorted/'
elif dataset_type == 'queensland':
    if option == 'daily':
        folder_path = './dataset/queensland/user_sorted_pulse/'
    else:
        folder_path = './dataset/queensland/user_sorted_pulsetot/'
else:
    folder_path = './dataset/datamill/user_datamill_sorted/'

main(folder_path, dataset_type, option, contamination, z_score_threshold)
