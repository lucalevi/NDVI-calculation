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
CLIENT_ID = 'sh-4363f05e-8c9d-45d7-9b99-62a5cadfe8c7'
CLIENT_SECRET = 'LXN1y7JsNBhCYyXltQZiJ6hYJGmVYDVR'
TOKEN_URL = 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token'
PROCESS_URL = 'https://sh.dataspace.copernicus.eu/api/v1/process'
TAR_FILE = 'retrieved_files.tar'
EXTRACT_PATH = 'retrieved_files'
TIF_FILE = os.path.join(EXTRACT_PATH, 'default.tif')
JSON_FILE = 'ndvi_statistics.json'

# OAuth2 session
def get_oauth_session(client_id, client_secret):
    try:
        client = BackendApplicationClient(client_id=client_id)
        oauth = OAuth2Session(client=client)
        oauth.fetch_token(token_url=TOKEN_URL, client_secret=client_secret, include_client_id=True)
        return oauth
    except Exception as e:
        logging.error("Error obtaining OAuth2 session: %s", e)
        raise

# Request data from Sentinel Hub API
def request_data(oauth, request_payload):
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
def extract_tar_file(tar_path, extract_to):
    try:
        with tarfile.open(tar_path) as tar:
            tar.extractall(path=extract_to)
        logging.info("Files extracted to %s", extract_to)
    except Exception as e:
        logging.error("Error extracting TAR file: %s", e)
        raise

# Calculate NDVI statistics
def calculate_ndvi_statistics(tif_file):
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
def save_to_json(data, json_file):
    try:
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=4)
        logging.info("NDVI statistics exported to %s", json_file)
    except Exception as e:
        logging.error("Error saving JSON file: %s", e)
        raise

def main():
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
                            [
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

if __name__ == "__main__":
    main()
