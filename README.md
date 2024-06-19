# NDVI Data Retrieval and Analysis
[This Python script](https://github.com/lucalevi/NDVI-calculation/blob/main/ndvi_request_final.py)
retrieves and analyzes Normalized Difference Vegetation Index (NDVI) data for a specified region using the Sentinel Hub API provided by Copernicus, the Earth observation program managed by the European Space Agency (ESA).

## Overview
This script performs the following tasks:

1. Authentication: Uses OAuth2 to authenticate with the Sentinel Hub API.
2. Data Request: Sends a request to the Sentinel Hub API to retrieve NDVI data for a specified region and time range.
3. Data Extraction: Downloads the data as a TAR file and extracts the contents.
4. NDVI Calculation: Reads the extracted TIFF file and calculates the mean, minimum, and maximum NDVI values.
5. JSON Export: Exports the NDVI statistics to a JSON file.

## Requirements
- Python 3.x
- oauthlib
- requests-oauthlib
- rasterio
- numpy
- tarfile
- os
- json
- logging

### Installation
To install the required packages, run:
```sh
pip install oauthlib requests-oauthlib rasterio numpy
```



