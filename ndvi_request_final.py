"""
Sentinel Hub NDVI Data Retrieval and Analysis Script
----------------------------------------------------
This script interacts with the Sentinel Hub API to retrieve, process, 
and analyze NDVI data.
It performs the following steps:

1. Imports necessary libraries and configures logging.
2. Defines configuration parameters for OAuth2 authentication and API endpoints.
3. Creates a function to obtain an OAuth2 session using client credentials.
4. Defines a function to send a request to the Sentinel Hub API to retrieve data.
5. Creates a function to extract the contents of a TAR file.
6. Defines a function to calculate NDVI statistics (mean, minimum, maximum) from 
    a GeoTIFF file.
7. Creates a function to save the calculated NDVI statistics to a JSON file.
8. Orchestrates the entire process in the main function:
   a. Obtains an OAuth2 session.
   b. Defines an evalscript for data processing.
   c. Creates a request payload with specific parameters and bounds.
   d. Sends the request to the API and saves the response as a TAR file.
   e. Extracts the TAR file to a specified directory.
   f. Calculates NDVI statistics from the extracted GeoTIFF file.
   g. Saves the NDVI statistics to a JSON file.

The script is designed to handle errors gracefully, logging any issues that occur 
during execution.

Note: Replace CLIENT_ID and CLIENT_SECRET with your actual Sentinel Hub credentials
as described here: 
https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Overview/Authentication.html
"""

# Import libraries
import os
import json
import tarfile
import numpy as np
import rasterio
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
CLIENT_ID = '<your_client_ID>'
CLIENT_SECRET = '<your_client_secret>'
TOKEN_URL = 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token'
PROCESS_URL = 'https://sh.dataspace.copernicus.eu/api/v1/process'
TAR_FILE = 'retrieved_files.tar'
EXTRACT_PATH = 'retrieved_files'
TIF_FILE = os.path.join(EXTRACT_PATH, 'default.tif')
JSON_FILE = 'ndvi_statistics.json'
POLYGON_COORDINATES = [
    [13.431473, 45.843278],
    [13.407070, 45.901024],
    [13.374575, 45.944087],
    [13.401089, 45.984709],
    [13.480989, 46.000895],
    [13.524993, 45.966807],
    [13.572922, 45.916585],
    [13.499877, 45.885294],
    [13.431473, 45.843278],
]

# OAuth2 session
def get_oauth_session(client_id: str, client_secret: str) -> None:
    """
    Create and return an OAuth2 session for accessing the Sentinel Hub API.

    Parameters:
        client_id (str): The client ID for the OAuth2 application.
        client_secret (str): The client secret for the OAuth2 application.

    Returns:
        None: If an error occurs during the OAuth2 session creation.
        oauth (OAuth2Session): An authenticated OAuth2 session object for making API requests.
        
    Raises:
        Exception: If there is an error during the OAuth2 session creation or token fetching.

    Note:
        This function uses the requests_oauthlib library to create the OAuth2 session.
        It logs any errors that occur during the session creation using the logging module.
    """
    try:
        client = BackendApplicationClient(client_id=client_id)
        oauth = OAuth2Session(client=client)
        oauth.fetch_token(token_url=TOKEN_URL, client_secret=client_secret, include_client_id=True)
        return oauth
    except Exception as e:
        logging.error("Error obtaining OAuth2 session: %s", e)
        raise

# Request data from Sentinel Hub API
def request_data(oauth, request_payload) -> bool:
    """
    Send a POST request to the Sentinel Hub API to retrieve data 
    based on the provided request payload.

    Parameters:
        oauth (OAuth2Session): An authenticated OAuth2 session object for making API requests.
        request_payload (json): The request payload JSON containing the necessary parameters
                                for data retrieval.

    Returns:
        bool: True if the data is successfully retrieved and saved to the TAR_FILE, False otherwise.

    Raises:
        Exception: If there is an error during the data request or writing the response content to the TAR_FILE.

    Note:
        This function uses the requests_oauthlib library to make the POST request.
        It logs any errors that occur during the data request using the logging module.
    """
    try:
        response = oauth.post(PROCESS_URL, json=request_payload, headers={"Accept": "application/tar"})
        if response.status_code == 200:
            with open(TAR_FILE, "wb") as f:
                f.write(response.content)
            logging.info("Data successfully retrieved and saved to %s", TAR_FILE)
            return True
        else:
            logging.error("Request failed with status code %s: %s", response.status_code, response.text)
            return False
    except Exception as e:
        logging.error("Error during data request: %s", e)
        return False

# Extract TAR file
def extract_tar_file(tar_path : str, extract_to : str) -> None:
    """
    Extracts the contents of a TAR file to a specified directory.

    Parameters:
        tar_path (str): The path to the TAR file to be extracted.
        extract_to (str): The directory where the contents of the TAR file will be extracted.

    Returns:
        None

    Raises:
        Exception: If there is an error during the extraction process.

    Note:
        This function uses the tarfile module to open and extract the contents of the TAR file.
        It logs any errors that occur during the extraction process using the logging module.
    """
    try:
        with tarfile.open(tar_path) as tar:
            tar.extractall(path=extract_to)
        logging.info("Files extracted to %s", extract_to)
    except Exception as e:
        logging.error("Error extracting TAR file: %s", e)
        raise

# Calculate NDVI statistics
def calculate_ndvi_statistics(tif_file : str) -> dict:
    """
    Calculates the mean, minimum, and maximum values of NDVI (Normalized Difference Vegetation Index) 
    from a given GeoTIFF file.

    Parameters:
        tif_file (str): The path to the GeoTIFF file containing the NDVI data.

    Returns:
        dict: A dictionary containing the mean, minimum, and maximum NDVI values.

    Raises:
        Exception: If there is an error reading the GeoTIFF file or calculating the NDVI statistics.

    Note:
        This function assumes that the NDVI data is stored in the first band of the GeoTIFF file.
        It divides the NDVI values by 10000 before calculating the statistics to get a proper NDVI value 
        (having a maximum value of 1).
    """
    try:
        with rasterio.open(tif_file) as src:
            raster_data = src.read(1) / 10000  # Read the first band and divide by 10000
            ndvi_mean = np.mean(raster_data)
            ndvi_min = np.min(raster_data)
            ndvi_max = np.max(raster_data)
            return {"mean_ndvi": ndvi_mean, "min_ndvi": ndvi_min, "max_ndvi": ndvi_max}
    except Exception as e:
        logging.error("Error calculating NDVI statistics: %s", e)
        raise

# Save statistics to JSON file
def save_to_json(data: dict, json_file: str) -> None:
    """
    Save the provided data to a JSON file.

    Parameters:
        data (dict): The data to be saved. It should be a dictionary.
        json_file (str): The path to the JSON file where the data will be saved.

    Returns:
        None

    Raises:
        Exception: If there is an error while opening or writing to the JSON file.

    Note:
        This function uses the json module to dump the data into a JSON file.
        It logs an information message if the data is successfully saved to the JSON file.
        If an error occurs during the process, it logs an error message and raises an exception.
    """
    try:
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=4)
        logging.info("NDVI statistics exported to %s", json_file)
    except Exception as e:
        logging.error("Error saving JSON file: %s", e)
        raise

def main() -> None:
    """
    The main function orchestrates the entire process of retrieving data 
    from the Sentinel Hub API,
    processing it using an evalscript, extracting the data from the TAR file, 
    calculating NDVI statistics,
    and saving the statistics to a JSON file.

    Returns:
        None

    Raises:
        Exception: If any error occurs during the process.
    """
    try:
        oauth = get_oauth_session(CLIENT_ID, CLIENT_SECRET)

        evalscript = """
        //VERSION=3
        function setup() {
            return {
                input: [
                    {
                        bands: ["S2", "S3"],
                    },
                ],
                output: [
                    {
                        id: "default",
                        bands: 1,
                        sampleType: "INT16",
                    },
                    {
                        id: "ndvi_image",
                        bands: 3,
                        sampleType: "AUTO",
                    },
                ],
            }
        }

        function evaluatePixel(sample) {
            let NDVI = index(sample.S3, sample.S2)
            const viz = ColorGradientVisualizer.createWhiteGreen(-0.1, 1.0)
            return {
                default: [NDVI * 10000],
                ndvi_image: viz.process(NDVI),
            }
        }
        """

        request_payload = {
            "input": {
                "bounds": {
                    "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                          POLYGON_COORDINATES
                        ],
                    },
                },
                "data": [
                    {
                        "type": "sentinel-3-slstr",
                        "dataFilter": {
                            "timeRange": {
                                "from": "2020-06-20T00:00:00Z",
                                "to": "2020-06-20T23:59:59Z",
                            },
                            "orbitDirection": "DESCENDING",
                        },
                    }
                ],
            },
            "output": {
                "width": 512,
                "height": 512,
                "responses": [
                    {
                        "identifier": "default",
                        "format": {"type": "image/tiff"},
                    },
                ],
            },
            "evalscript": evalscript,
        }

        if request_data(oauth, request_payload):
            extract_tar_file(TAR_FILE, EXTRACT_PATH)
            ndvi_stats = calculate_ndvi_statistics(TIF_FILE)
            save_to_json(ndvi_stats, JSON_FILE)

    except Exception as e:
        logging.error("An error occurred in the main process: %s", e)


# If the script is the main process, run the main function
if __name__ == "__main__":
    main()
