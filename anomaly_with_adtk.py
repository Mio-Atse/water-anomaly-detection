import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
from adtk.data import validate_series
from adtk.detector import ThresholdAD, InterQuartileRangeAD, PersistAD, LevelShiftAD, VolatilityShiftAD

def process_datamill(file_path):
    df = pd.read_csv(file_path)
    df['READING_START_DATE'] = pd.to_datetime(df['READING_START_DATE'], format='%d/%m/%Y %H:%M')
    df = df.set_index('READING_START_DATE')
    return df['GROSS_CONSUMPTION']

def process_helios(file_path, option):
    df = pd.read_csv(file_path, sep=';')
    df['datetime'] = pd.to_datetime(df['datetime'], format='%d/%m/%Y %H:%M:%S')
    df = df.set_index('datetime')
    if option == 'daily':
        return df['diff']
    else:  # total
        return df['meter reading']

def process_queensland(file_path, option):
    df = pd.read_csv(file_path)
    df['datetime'] = pd.to_datetime(df['datetime'], format='%d/%m/%Y %H:%M:%S')
    df = df.set_index('datetime')
    if option == 'pulse1':
        return df['Pulse1']
    else:  # pulse1_total
        return df['Pulse1_Total']

def detect_anomalies(s, contamination, z_score_threshold):
    s = validate_series(s)
    
    threshold_ad = ThresholdAD(high=s.mean() + z_score_threshold * s.std(), 
                               low=s.mean() - z_score_threshold * s.std())
    iqr_ad = InterQuartileRangeAD(c=1.5)
    persist_ad = PersistAD(c=3.0, side='positive')
    level_shift_ad = LevelShiftAD(c=2.0, side='both', window=5)
    volatility_shift_ad = VolatilityShiftAD(c=1.5, side='positive', window=30)

    anomalies = {}
    anomalies['Threshold'] = threshold_ad.detect(s).fillna(False)
    anomalies['IQR'] = iqr_ad.fit_detect(s).fillna(False)
    anomalies['Persist'] = persist_ad.fit_detect(s).fillna(False)
    anomalies['LevelShift'] = level_shift_ad.fit_detect(s).fillna(False)
    try:
        anomalies['VolatilityShift'] = volatility_shift_ad.fit_detect(s).fillna(False)
    except RuntimeError as e:
        print(f"VolatilityShiftAD could not be applied: {e}")
        anomalies['VolatilityShift'] = pd.Series(False, index=s.index)

    return anomalies


def plot_consensus_anomalies(s, anomalies, file_path):
    # Calculate the consensus anomalies where all models agree
    consensus_anomalies = pd.DataFrame(anomalies).all(axis=1)

    # Drop any missing values to avoid index alignment issues
    consensus_anomalies = consensus_anomalies.dropna()
    s = s.dropna()

    # Filter the consensus anomalies
    consensus_indices = consensus_anomalies[consensus_anomalies].index

    # Ensure indices in s align with the consensus_indices
    consensus_values = s.loc[consensus_indices]

    # Check if both consensus_indices and consensus_values have the same length
    if len(consensus_indices) != len(consensus_values):
        print(f"Index mismatch detected. Length of indices: {len(consensus_indices)}, Length of values: {len(consensus_values)}")
        return

    # Plot the data and anomalies
    plt.figure(figsize=(12, 6))
    plt.plot(s, label='Data', color='blue')
    plt.scatter(consensus_indices, 
                consensus_values, 
                label='Consensus Anomaly', 
                marker='o', 
                color='red', 
                s=20)
    plt.title(f"Consensus Anomalies detected in {os.path.basename(file_path)}")
    plt.legend()
    plt.show()


def main(folder_path, dataset_type, option, contamination, z_score_threshold):
    file_list = glob.glob(os.path.join(folder_path, '*.csv'))
    
    for file_path in file_list:
        print(f"Processing file: {file_path}")
        
        if dataset_type == 'datamill':
            s = process_datamill(file_path)
        elif dataset_type == 'helios':
            s = process_helios(file_path, option)
        elif dataset_type == 'queensland':
            s = process_queensland(file_path, option)
        
        anomalies = detect_anomalies(s, contamination, z_score_threshold)
        
        total_consensus_anomalies = sum(pd.DataFrame(anomalies).all(axis=1))
        print(f"Total consensus anomalies across all models: {total_consensus_anomalies}")
        
        plot_consensus_anomalies(s, anomalies, file_path)

if __name__ == "__main__":
    dataset_type = input("Enter dataset type (helios/queensland/datamill): ").lower()
    while dataset_type not in ['helios', 'queensland', 'datamill']:
        dataset_type = input("Invalid input. Please enter 'helios', 'queensland', or 'datamill': ").lower()

    if dataset_type == 'helios':
        option = input("Enter option (daily/total): ").lower()
        while option not in ['daily', 'total']:
            option = input("Invalid input. Please enter 'daily' or 'total': ").lower()
    elif dataset_type == 'queensland':
        option = input("Enter option (pulse1/pulse1_total): ").lower()
        while option not in ['pulse1', 'pulse1_total']:
            option = input("Invalid input. Please enter 'pulse1' or 'pulse1_total': ").lower()
    else:
        option = 'default'

    try:
        z_score_threshold = float(input("Enter Z-score threshold (default 1 for datamill and helios, 3 for queensland): "))
    except ValueError:
        print("Invalid Z-score threshold. Using default value of 3.")
        z_score_threshold = 3

    try:
        contamination = float(input("Enter contamination factor (default 0.01): "))
    except ValueError:
        print("Invalid contamination factor. Using default value of 0.01.")
        contamination = 0.01

    if dataset_type == 'helios':
        folder_path = './dataset/helios/user_helios_sorted/'
    elif dataset_type == 'queensland':
        if option == 'pulse1':
            folder_path = './dataset/queensland/user_sorted_pulse/'
        else:
            folder_path = './dataset/queensland/user_sorted_pulsetot/'
    else:
        folder_path = './dataset/datamill/user_datamill_sorted/'

    main(folder_path, dataset_type, option, contamination, z_score_threshold)
