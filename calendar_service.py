import os.path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError  # <-- Add this import
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            except RefreshError:
                # Refresh token failed; delete token and re-authenticate
                print("Refresh token invalid. Re-authenticating...")
                os.remove('token.json')
                creds = None

        if not creds:
            # No valid credentials; start OAuth flow
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(
                port=0, access_type='offline', prompt='consent')
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service