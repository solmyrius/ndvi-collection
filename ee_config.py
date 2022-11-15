import ee

from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

"""
Authorization settings
"""
KEY = "gc_key/arborise-4044f15d5b0a.json"
SERVICE_ACCOUNT = "arborise-ee@arborise.iam.gserviceaccount.com"
PROJECT = 'arborise'

"""
Data source and output settings 
"""
SOURCE_KML_FILE = "data/parcelle.kml"
DATA_FILE = "arborise_data.csv"
DATE_START = "2021-01-01"
DATE_END = "2022-11-15"
CLD_PRB_THRESH = 30  # Used for maps drawings only
SQUARE_SIDE = 0.02  # Side of background square in degrees


def ee_auth():
    ee_creds = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY)
    ee.Initialize(ee_creds)


def ee_session_init():

    credentials = service_account.Credentials.from_service_account_file(KEY)
    scoped_credentials = credentials.with_scopes(
        ['https://www.googleapis.com/auth/cloud-platform']
    )

    return AuthorizedSession(scoped_credentials)
