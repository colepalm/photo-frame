import os.path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from googleapiclient.discovery import build

# If modifying these scopes, delete the token.json file.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def get_calendar_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            return
    service = build('calendar', 'v3', credentials=creds)
    return service
