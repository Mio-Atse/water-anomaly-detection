# Data Preparation
## 1. Download and Organize Datasets

Begin by setting up the necessary directories for the datasets.

```bash
mkdir dataset && cd dataset
mkdir datamill helios queensland
```
Please download the datasets from the following links and place them into the corresponding directories within the `dataset` folder:

- **[Datamill Dataset](https://datamillnorth.org/dataset/2jqzm/customer-meter-data/)**: Download the dataset and unzip it into the `dataset/datamill/` directory.
- **[Queensland Dataset](https://www.data.qld.gov.au/dataset/digital-water-meter-dataset-explanation)**: Download the dataset and organize it into the `dataset/queensland/` directory.
- **[Helios Dataset](https://pubs.hellenicdataservice.gr/dataset/78776f38-a58b-4a2a-a8f9-85b964fe5c95)**: Download the dataset and place it in the `dataset/helios/` directory.

### Folder Structure

After organizing the datasets, your `dataset` folder should look like this:
```
dataset/
├── datamill/
│ └── org_dataset/
│   ├── 201011_YW_Customer_Meter_Data
│   ├── 201112_YW_Customer_Meter_Data
│   ├── 201213_YW_Customer_Meter_Data
│   └── 201314_YW_Customer_Meter_Data
├── queensland/
│ └── org_dataset/
│   └── Digital_Meter_Data_July_2022
└── helios/
  └── org_dataset/
    └── swm_trialA_1K.csv
```


## 2. Directory Setup
### 2.1 Datamill Dataset
```
cd datamill
unzip 201011\ YW\ Customer\ Meter\ Data.zip && sudo rm -rf 201011\ YW\ Customer\ Meter\ Data.zip
unzip 201112\ YW\ Customer\ Meter\ Data.zip && sudo rm -rf 201112\ YW\ Customer\ Meter\ Data.zip
unzip 201213\ YW\ Customer\ Meter\ Data.zip && sudo rm -rf 201213\ YW\ Customer\ Meter\ Data.zip
unzip 201314\ YW\ Customer\ Meter\ Data.zip && sudo rm -rf 201314\ YW\ Customer\ Meter\ Data.zip
sudo rm -rf README\ YW\ Customer\ Meter\ Data.txt
mv 20* org_dataset/
```
### 2.2 Queensland Dataset
```
cd ..
cd queensland
mkdir org_dataset
sudo rm -rf digital-meter-data-schema.xlsx && rm -rf managedobject_details.csv
cd Digital\ Meter\ Data\ \ -\ July\ 2022
mv Dig* ../org_dataset/
rm -r Digital\ Meter\ Data\ \ -\ July\ 2022
```
### 2.3 Helios Dataset
```
cd ..
cd helios
mkdir org_dataset
mv swm_trialA_1K.csv org_dataset/
```
## 3 Using Dataset Scripts

### 3.1 Split Datasets
- Use the `split_datasets.py` script to save corrected datasets.
- For each dataset, select the appropriate option in the terminal.

  **Note:** The Helios dataset may take a long time to process.

### 3.2 Sort Datasets by Time
- After splitting the datasets, use the `sort_time.py` script.
- Choose the dataset in the terminal, and the script will sort the data by time.

### 3.3 Correct Semicolons (Helios Dataset)
- Run the `replace_semicolon.py` script to replace semicolons with commas in the Helios dataset.

# Usage
- Use `anomaly_detection_water_meter.ipynb` to use all scripts at one file on Google Colab. Make sure to upload your datasets on your respective Google Drive path. 
- Use `anomaly_with_pyod.py` for anomaly detection with the Python PYOD library.
   - Train the files one by one for detection.
- Use `anomaly_with_adtk.py` for anomaly detection with the Python ADTK library using pretrained models.
- Use `train_whole_dataset.py` to train models on the entire datasets. The trained models will be saved in their respective folders under the `models` directory.
  **Note:** The Helios dataset may take longer to process, but for other datasets, it will take approximately 1 hour. It is strongly recommended to use Google Colab for training.
- Use `predict_whole_dataset.py` to make predictions using the trained models.

