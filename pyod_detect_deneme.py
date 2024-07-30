import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from pyod.models.copod import COPOD

# Path to the dataset folder
data_path = './dataset/helios/user dataset'

# Read all CSV files in the directory
all_files = [os.path.join(data_path, f) for f in os.listdir(data_path) if f.endswith('.csv')]

# Initialize an empty DataFrame to hold all the data
all_data = pd.DataFrame()

# Loop through the files and concatenate the data
for file in all_files:
    # Read the CSV file
    data = pd.read_csv(file, delimiter=';')

    # Parse the datetime column
    data['datetime'] = pd.to_datetime(data['datetime'], format='%d/%m/%Y %H:%M:%S')

    # Drop rows with missing values
    data.dropna(inplace=True)

    # Append the data to the all_data DataFrame
    all_data = pd.concat([all_data, data], ignore_index=True)

# Extract the feature columns
X = all_data[['meter reading', 'diff']]

# Split the data into training and testing sets (here we use all data for training)
x_train, x_test = train_test_split(X, test_size=0.2, random_state=42)

# Initialize the COPOD model
clf = COPOD()

# Train the COPOD model
clf.fit(x_train)

# Choose one specific file to predict anomalies
selected_file = all_files[0]  # Change the index to select a different file

# Read the selected file
selected_data = pd.read_csv(selected_file, delimiter=';')

# Parse the datetime column
selected_data['datetime'] = pd.to_datetime(selected_data['datetime'], format='%d/%m/%Y %H:%M:%S')

# Drop rows with missing values
selected_data.dropna(inplace=True)

# Extract the feature columns
X_selected = selected_data[['meter reading', 'diff']]

# Predict anomalies for the selected file
y_selected_scores = clf.decision_function(X_selected)

# Plot the anomaly scores
plt.figure(figsize=(14, 7))
plt.plot(X_selected.index, y_selected_scores, 'ro-', label='Anomaly Scores')
plt.title(f'Anomaly Scores for {os.path.basename(selected_file)}')
plt.xlabel('Index')
plt.ylabel('Anomaly Score')
plt.legend()
plt.show()
