from ..connection import drive_service
from googleapiclient.errors import HttpError
from pprint import pprint
import uuid

# Function to list types, names, IDs, and URIs of all folders and files in Google Drive
# list_all_folders_and_files_with_details
def fetch_start_page_token(service, drive_id=None):
  """Retrieve page token for the current state of the account or a specific drive.
  Returns & prints : start page token

  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """
  try:
    # pylint: disable=maybe-no-member
    if drive_id:
      response = service.changes().getStartPageToken(
        driveId=drive_id,
        supportsAllDrives=True
      ).execute()
    else:
      response = service.changes().getStartPageToken().execute()
    
    # print(f'Start token: {response.get("startPageToken")}')
    # print(response)
    return response.get("startPageToken")

  except HttpError as error:
    print(f"An error occurred: {error}")
    response = None

  return response.get("startPageToken")

def get_change_results(driveId, pageToken):
    return drive_service.changes().list(
        driveId=driveId, 
        includeItemsFromAllDrives=True, 
        supportsAllDrives=True,
        includeRemoved=True,
        pageToken=pageToken,
        spaces='drive'
    ).execute()

def fetch_files(drive_service, driveId, pageToken=None):
    original_files = []
    changed_files = []
    
    while True:
        # Prepare the request with the page token if it exists
        response = drive_service.files().list(
            driveId=driveId, 
            includeItemsFromAllDrives=True, 
            supportsAllDrives=True,
            pageToken=pageToken,
            corpora='drive'
        ).execute() # Use await here
        
        # Process the files in the response
        original_files.extend(response.get('files', []))  # Collect original files
        changed_files.extend(response.get('changedFiles', []))  # Collect changed files (if applicable)

        # Get the next page token
        page_token = response.get('nextPageToken')
        if not page_token:  # Exit the loop if there are no more pages
            break

    return original_files, changed_files

def fetch_changes(service, saved_start_page_token, drive_id=None):
  """Retrieve the list of changes for the currently authenticated user or a specific drive.
      prints changed file's ID
  Args:
      saved_start_page_token : StartPageToken for the current state of the
      account.
      drive_id : Optional ID of the specific drive to retrieve changes from.
  Returns: saved start page token.

  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """
  try:
    # Begin with our last saved start token for this user or the
    # current token from getStartPageToken()
    page_token = saved_start_page_token
    # pylint: disable=maybe-no-member

    while page_token is not None:
      if drive_id:
        response = (
            service.changes().list(
               driveId=drive_id,
               supportsAllDrives=True, 
               includeItemsFromAllDrives=True, 
               pageToken=page_token, 
               spaces="drive"
            ).execute()
        )
      else:
        response = (
            service.changes().list(pageToken=page_token, spaces="drive").execute()
        )
        
      changes = response.get("changes")  
      for change in changes:
        # Process change
        print(f'Change found for file: {change.get("fileId")}')
      if "newStartPageToken" in response:
        # Last page, save this token for the next polling interval
        saved_start_page_token = response.get("newStartPageToken")
      page_token = response.get("nextPageToken")
    return changes, saved_start_page_token

  except HttpError as error:
    print(f"An error occurred: {error}")
    saved_start_page_token = None

    return saved_start_page_token

def subscribe_to_file_changes(fileId: str, ttl: int, host: str = '0.0.0.0'):
    channel_id = str(uuid.uuid4())  # Generate a unique channel ID
    channel_address = f'https://{host}/google-drive-listener'  # Your webhook URL
    resource = {
        'id': channel_id,
        'type': 'web_hook',
        'address': channel_address,
        'params': {
            'ttl': ttl  # Time-to-live for the channel in seconds
        }
    }

    try:
        # Call the changes.watch method
        response = drive_service.files().watch(
          fileId=fileId, 
          supportsAllDrives=True,
          body=resource
        ).execute()
        # print(f"Subscribed to Drive changes with channel ID: {response['id']}")
        # print()
        # pprint(response)
        # return response['id']
        return response
    except HttpError as error:
        print(f"An error occurred: {error}")

