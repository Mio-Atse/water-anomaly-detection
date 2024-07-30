import pandas as pd
import matplotlib.pyplot as plt
from adtk.data import validate_series
from adtk.detector import (
    ThresholdAD, QuantileAD, PersistAD, SeasonalAD, 
    InterQuartileRangeAD, AutoregressionAD
)
import glob
import os

def plot_water_usage_from_files(csv_folder):
    # Find all CSV files in the specified folder
    csv_files = glob.glob(os.path.join(csv_folder, '*.csv'))

    # Iterate through each CSV file
    for csv_file in csv_files:
        print(f"Processing file: {csv_file}")

        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file)

        # Convert 'time' column to datetime format
        df['time'] = pd.to_datetime(df['time'])

        # Filter only the rows where typeM is 'Pulse1_Total' and Value is numeric
        filtered_data = df[df['typeM'] == 'Pulse1_Total']
        filtered_data['Value'] = pd.to_numeric(filtered_data['Value'], errors='coerce')

        # Group by 'time' and sum 'Value' for water usage over time
        usage_by_time = filtered_data.groupby('time')['Value'].sum()

        # Create and validate the time series
        series = validate_series(usage_by_time)

        # Define anomaly detection methods
        threshold_ad = ThresholdAD(high=series.quantile(0.99), low=series.quantile(0.01))
        quantile_ad = QuantileAD(high=0.99, low=0.01)
        persist_ad = PersistAD(min_duration='1 hour', threshold=series.quantile(0.99))
        seasonal_ad = SeasonalAD(c=3.0, side='both')
        iqr_ad = InterQuartileRangeAD(c=1.5)
        autoregression_ad = AutoregressionAD(n_steps=10, step_size=1)

        # Detect anomalies
        anomalies_threshold = threshold_ad.detect(series)
        anomalies_quantile = quantile_ad.fit_detect(series)
        anomalies_persist = persist_ad.detect(series)
        anomalies_seasonal = seasonal_ad.detect(series)
        anomalies_iqr = iqr_ad.detect(series)
        anomalies_autoregression = autoregression_ad.fit_detect(series)  # Fixed

        # Visualize anomaly detections
        def plot_anomalies(series, anomalies, title):
            plt.figure(figsize=(15, 5))
            plt.plot(series.index, series.values, label='Data')
            anomalies = anomalies.fillna(False)  # Handle NaN values
            plt.scatter(series[anomalies].index, series[anomalies].values, color='red', label='Anomalies')
            plt.title(title)
            plt.legend()
            plt.xlabel('Time')
            plt.ylabel('Value')
            plt.tight_layout()
            plt.show()

        # Plot each anomaly detection method
        plot_anomalies(series, anomalies_threshold, 'Threshold Anomalies')
        plot_anomalies(series, anomalies_quantile, 'Quantile Anomalies')
        plot_anomalies(series, anomalies_persist, 'Persist Anomalies')
        plot_anomalies(series, anomalies_seasonal, 'Seasonal Anomalies')
        plot_anomalies(series, anomalies_iqr, 'IQR Anomalies')
        plot_anomalies(series, anomalies_autoregression, 'Autoregression Anomalies')

        # Combine anomaly detections
        anomalies_combined = (anomalies_threshold | anomalies_quantile |
                              anomalies_persist | anomalies_seasonal |
                              anomalies_iqr | anomalies_autoregression)

        # Plot combined anomalies
        plot_anomalies(series, anomalies_combined, 'Combined Anomalies')

        # Print results
        print("Threshold Anomalies:\n", anomalies_threshold)
        print("Quantile Anomalies:\n", anomalies_quantile)
        print("Persist Anomalies:\n", anomalies_persist)
        print("Seasonal Anomalies:\n", anomalies_seasonal)
        print("IQR Anomalies:\n", anomalies_iqr)
        print("Autoregression Anomalies:\n", anomalies_autoregression)
        print("Combined Anomalies:\n", anomalies_combined)

def process_helios_data(csv_file):
    # Read the first 1000 rows of the CSV file into a DataFrame
    df = pd.read_csv(csv_file, delimiter=';')

    # Convert 'datetime' column to datetime format
    df['datetime'] = pd.to_datetime(df['datetime'], format='%d/%m/%Y %H:%M:%S')

    # Sort the dataframe by datetime
    df = df.sort_values('datetime')

    # Create and validate the time series
    series = validate_series(df.set_index('datetime')['diff'])

    # Define anomaly detection methods
    threshold_ad = ThresholdAD(high=series.quantile(0.9999), low=series.quantile(0.0001))
    quantile_ad = QuantileAD(high=0.99999, low=0.00001)
    persist_ad = PersistAD(c=3.0, side='positive')  # Fixed
    seasonal_ad = SeasonalAD(c=3.0, side='both')
    iqr_ad = InterQuartileRangeAD(c=1.5)
    autoregression_ad = AutoregressionAD(n_steps=7*2, step_size=24, c=3.0)

    # Detect anomalies
    anomalies_threshold = threshold_ad.detect(series)
    anomalies_quantile = quantile_ad.fit_detect(series)
    anomalies_persist = persist_ad.fit_detect(series)
    #anomalies_seasonal = seasonal_ad.fit_detect(series)
    anomalies_iqr = iqr_ad.fit_detect(series)
    anomalies_autoregression = autoregression_ad.fit_detect(series)  # Fixed

    # Combine anomaly detections
    anomalies_combined = (anomalies_threshold | anomalies_quantile |
                          anomalies_persist | #anomalies_seasonal |
                          anomalies_iqr | anomalies_autoregression)

    # Visualize anomaly detections
    def plot_anomalies(series, anomalies, title):
        plt.figure(figsize=(15, 5))
        plt.plot(series.index, series.values, label='Data')
        anomalies = anomalies.fillna(False)  # Handle NaN values
        plt.scatter(series[anomalies].index, series[anomalies].values, color='red', label='Anomalies')
        plt.title(title)
        plt.legend()
        plt.xlabel('Time')
        plt.ylabel('Meter Reading')
        plt.tight_layout()
        plt.show()

    # Plot each anomaly detection method
    plot_anomalies(series, anomalies_threshold, 'Threshold Anomalies')
    plot_anomalies(series, anomalies_quantile, 'Quantile Anomalies')
    plot_anomalies(series, anomalies_persist, 'Persist Anomalies')
    #plot_anomalies(series, anomalies_seasonal, 'Seasonal Anomalies')
    plot_anomalies(series, anomalies_iqr, 'IQR Anomalies')
    plot_anomalies(series, anomalies_autoregression, 'Autoregression Anomalies')

    # Plot combined anomalies
    plot_anomalies(series, anomalies_combined, 'Combined Anomalies')

    # Print results
    print("Threshold Anomalies:\n", anomalies_threshold)
    print("Quantile Anomalies:\n", anomalies_quantile)
    print("Persist Anomalies:\n", anomalies_persist)
    #print("Seasonal Anomalies:\n", anomalies_seasonal)
    print("IQR Anomalies:\n", anomalies_iqr)
    print("Autoregression Anomalies:\n", anomalies_autoregression)
    print("Combined Anomalies:\n", anomalies_combined)

def main():
    dataset_choice = input("Choose dataset (1 for water meter, 2 for Helios): ")

    if dataset_choice == '1':
        # Specify the folder where your water meter CSV files are located
        csv_folder = './dataset/queensland/july/Digital Meter Data  - July02.csv'
        # Call the function to plot water usage for each CSV file
        plot_water_usage_from_files(csv_folder)
    elif dataset_choice == '2':
        # Specify the Helios CSV file
        csv_file = './dataset/helios/user dataset/fddc248c-0b61-4f1e-85a0-f672e6fd0d48.csv'
        # Call the function to process and plot Helios data
        process_helios_data(csv_file)
    else:
        print("Invalid choice. Please choose 1 or 2.")

if __name__ == '__main__':
    main()
