import os, pickle
from ..config import SENSOR
from googleapiclient.discovery import build, Resource
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
SCOPES = ['https://www.googleapis.com/auth/drive']
# current_directory = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = f'{SENSOR}/credentials.json'

def create_drive_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    drive_service = build('drive', 'v3', credentials=creds)
    doc_service = build('docs', 'v1', credentials=creds)
    sheet_service = build('sheets', 'v4', credentials=creds)
    slides_service = build('slides', 'v1', credentials=creds)
    return (drive_service, doc_service, sheet_service, slides_service)
drive_service, doc_service, sheet_service, slides_service = create_drive_service()