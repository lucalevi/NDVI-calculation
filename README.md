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

## Usage
1. Clone the repository
```sh
git clone https://github.com/yourusername/ndvi-data-retrieval.git
cd ndvi-data-retrieval
```

2. Update the 'CLIENT_ID' and 'CLIENT_SECRET' in the script with your Sentinel Hub credentials. Look [here](https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Overview/Authentication.html) for a detailed guide on how to get your own credentials.

3. Run the script
   ```sh
   python ndvi_retrieval.py
   ```

## Configuration
Modify the evalscript and request_payload within the script to customize the data request (e.g., change the coordinates, time range, or data type).

## Sentinel Hub API and Copernicus
This script utilizes the Sentinel Hub API, a powerful interface provided by Copernicus, the European Space Agency's Earth observation program. Sentinel Hub enables easy and efficient access to satellite data for a variety of applications, including agriculture, forestry, and environmental monitoring.

For more information about Sentinel Hub and Copernicus, visit:

- [Sentinel Hub documentation](https://documentation.dataspace.copernicus.eu/APIs/SentinelHub.html)
- [Copernicus Programme](https://www.copernicus.eu/en)
- [Copernicus Browser](https://browser.dataspace.copernicus.eu/?zoom=5&lat=50.16282&lng=20.78613&themeId=DEFAULT-THEME&visualizationUrl=https%3A%2F%2Fsh.dataspace.copernicus.eu%2Fogc%2Fwms%2Fa91f72b5-f393-4320-bc0f-990129bd9e63&datasetId=S2_L2A_CDAS&demSource3D="MAPZEN"&cloudCoverage=30&dateMode=SINGLE)




