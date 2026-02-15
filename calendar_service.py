from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from config import GOOGLE_CREDENTIALS_FILE

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def get_calendar_service():
    """Create a calendar service using service account credentials."""
    credentials = Credentials.from_service_account_file(
        GOOGLE_CREDENTIALS_FILE,
        scopes=SCOPES
    )
    service = build('calendar', 'v3', credentials=credentials)
    return service