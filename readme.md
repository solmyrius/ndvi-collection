# NDVI Plots data extractor

This tool is for extracting NDVI data from Sentinel 2 images through Google EE.
- Data extracted as mean value for plots provided
- Data extracted as time series
- Clouded plots are excluded to collect all possible data
- Data range may be fitted
- Clouds threshold may be fitted

## Installation & authorisation

Tool uses python3 environment. Dependencies are listed in requirements.txt

To use Google Earth Engine you need service account with granted access to 
Google EE

How to create Service Account and grant access for it refer: https://developers.google.com/earth-engine/guides/service_account

You need download JSON key file from Google

After that edit file ee_config.py and add following information:

KEY = ... here path to your json keyfile
SERVICE_ACCOUNT = ... here is name of your service account
PROJECT = ... here is name of your project (arbitrary name)

## Data retrieval

Settings for data retrieval mau be changed editing ee_config.py

- SOURCE_KML_FILE - location of .kml file with plots shapes
- DATA_FILE - .csv file used to store retrieved data. If file not empty only newly retrieved data is changed
- DATE_START - date from which to start data polling
- DATE_END - date when end data polling
- CLD_PRB_THRESH - clouds probability threshold (used for maps only)
- SQUARE_SIDE - plot background are squares with the side provided with this setting. Measured in coordinate degrees 0.01 deg ~= 1 km

To start data retrieval process type:

`python get.py`

Data will be retrieved form Google EE and stored in .csv file. If file already have data for other days - these data will be preserved 