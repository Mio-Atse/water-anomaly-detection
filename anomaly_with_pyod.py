import os
import pandas as pd
import numpy as np
from pyod.models.iforest import IForest
from pyod.models.knn import KNN
from pyod.models.lof import LOF
from pyod.models.auto_encoder import AutoEncoder
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

def process_file(file_path, contamination=0.01, models=None):
    # Read the CSV file
    df = pd.read_csv(file_path, sep=';') if 'helios' in file_path else pd.read_csv(file_path)
    
    # Convert datetime to pandas datetime
    df['datetime'] = pd.to_datetime(df['datetime'], format='%d/%m/%Y %H:%M:%S') if 'helios' in file_path else pd.to_datetime(df['time'], format='%Y-%m-%d %H:%M:%S')
    
    # Sort by datetime
    df = df.sort_values('datetime') if 'helios' in file_path else df.sort_values('time')
    
    # Extract hour and day of week
    df['hour'] = df['datetime'].dt.hour
    df['day_of_week'] = df['datetime'].dt.dayofweek
    
    # Calculate rolling statistics
    window_size = 24 if 'helios' in file_path else 7
    df['diff'] = df['diff'] if 'helios' in file_path else df['Value'].diff()
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
        model.fit(X_scaled)
        outlier_scores = model.decision_function(X_scaled)
        df[f'{model_name}_anomaly_score'] = outlier_scores
        df[f'{model_name}_is_anomaly'] = model.predict(X_scaled)
        z_score_threshold = 3
        df[f'{model_name}_is_validated_anomaly'] = (df[f'{model_name}_is_anomaly'] == 1) & (abs(df['z_score']) > z_score_threshold)
        results[model_name] = df[f'{model_name}_is_validated_anomaly'].sum()
    
    return df, results

def plot_results(df, user_key, dataset_type, results):
    plt.figure(figsize=(12, 6))
    x = df['datetime'] if 'helios' in dataset_type else df['time']
    y = df['diff']
    title = f'Validated Anomalies for {user_key}'
    
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

def main(folder_path, dataset_type, contamination=0.01):
    # Define models
    models = {
        'IForest': IForest(contamination=contamination, random_state=42),
        'KNN': KNN(contamination=contamination, n_neighbors=5),
        'LOF': LOF(contamination=contamination),
        'AutoEncoder': AutoEncoder(contamination=contamination, hidden_neurons=[25, 2, 25], epochs=10)
    }
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            
            df, results = process_file(file_path, contamination, models)
            
            user_key = df['user key'].iloc[0] if 'helios' in dataset_type else filename
            
            print(f"Processing data for file: {filename}")
            print(f"Total data points: {len(df)}")
            for model_name, count in results.items():
                print(f"{model_name} validated anomalies: {count}")
            
            # Plot the results
            plot_results(df, user_key, dataset_type, results)

# Get user input for dataset type
dataset_type = input("Enter dataset type (helios/queensland): ").lower()
while dataset_type not in ['helios', 'queensland']:
    dataset_type = input("Invalid input. Please enter 'helios' or 'queensland': ").lower()

# Set the folder path based on the dataset type
if dataset_type == 'helios':
    folder_path = './dataset/helios/user dataset/'
else:
    folder_path = './dataset_correct/'  # Replace with the actual path

main(folder_path, dataset_type, contamination=0.01)
