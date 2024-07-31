
mdkir dataset && cd dataset
mkdir datamill helios queensland

Datamill
cd datamill
unzip 201011\ YW\ Customer\ Meter\ Data.zip && sudo rm -rf 201011\ YW\ Customer\ Meter\ Data.zip 
unzip 201112\ YW\ Customer\ Meter\ Data.zip && sudo rm -rf 201112\ YW\ Customer\ Meter\ Data.zip  
unzip 201213\ YW\ Customer\ Meter\ Data.zip && sudo rm -rf 201213\ YW\ Customer\ Meter\ Data.zip  
unzip 201314\ YW\ Customer\ Meter\ Data.zip && sudo rm -rf 201314\ YW\ Customer\ Meter\ Data.zip 
sudo rm -rf README\ YW\ Customer\ Meter\ Data.txt
mv 20* org_dataset/

Queensland
cd ..
cd queensland
mdkir org_dataset
sudo rm -rf digital-meter-data-schema.xlsx && rm -rf managedobject_details.csv 
cd Digital\ Meter\ Data\ \ -\ July\ 2022 
mv Dig* ../org_dataset/
rm -r Digital\ Meter\ Data\ \ -\ July\ 2022

Helios
cd ..
cd helios
mkdir org_dataset
mv swm_trialA_1K.csv org_dataset/

First use split_datasets.py file to save corrected datasets one by one. Choose option for each dataset by typing on terminal.
Note: Helios dataset may take a long time
After using split_datasets.py file, use sort_time.py file with same method, choosing dataset from terminal, to sort data according to time.

Also run replace_semicolon.py to correct semicolon to column for helios dataset

