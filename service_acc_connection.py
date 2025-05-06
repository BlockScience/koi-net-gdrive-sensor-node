import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from gdrive_sensor.config import CREDENTIALS
from gdrive_sensor.utils import list_shared_drives
from dotenv import load_dotenv

load_dotenv()

# Define the required scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']  # Adjust based on your needs

# Authenticate using the service account
creds = service_account.Credentials.from_service_account_file(
    filename=CREDENTIALS,
    scopes=SCOPES
)

# Build the Drive service
# drive_service = build('drive', 'v3', credentials=delegated_creds)
drive_service = build('drive', 'v3', credentials=creds)


# Now you can access the shared folder with limited scope
SHARED_DRIVE_ID = os.environ["SHARED_DRIVE_ID"]  # Replace with your folder ID
# print(SHARED_DRIVE_ID)

# List shared drives


list_shared_drives(drive_service)

try:
    results = drive_service.files().list(
        q=f"'{SHARED_DRIVE_ID}' in parents", 
        includeItemsFromAllDrives=True, 
        supportsAllDrives=True
    ).execute()
    files = results.get('files', [])

    if not files:
        print("No files found.")
    else:
        for file in files:
            print(f"Found file: {file.get('name')} ({file.get('id')})")
except Exception as e:
      print(f"An error occurred: {e}")