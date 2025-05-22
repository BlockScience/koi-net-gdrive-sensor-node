import uuid
from googleapiclient.errors import HttpError
from gdrive_sensor.utils.connection import drive_service
from gdrive_sensor.config import SHARED_DRIVE_ID
from pprint import pprint

def fetch_start_page_token(service, drive_id=None):
  """Retrieve page token for the current state of the account or a specific drive.
  Returns & prints : start page token

  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """
#   creds, _ = google.auth.default()

  try:
    # create drive api client
    # service = build("drive", "v3", credentials=creds)
    # service = drive_service

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
        
      for change in response.get("changes"):
        # Process change
        print(f'Change found for file: {change.get("fileId")}')
      if "newStartPageToken" in response:
        # Last page, save this token for the next polling interval
        saved_start_page_token = response.get("newStartPageToken")
      page_token = response.get("nextPageToken")
    return saved_start_page_token

  except HttpError as error:
    print(f"An error occurred: {error}")
    saved_start_page_token = None

    return saved_start_page_token

# start_page_token = fetch_start_page_token(
#   service=drive_service, drive_id=SHARED_DRIVE_ID
# )
# print("Start Page Token:")
# print(type(start_page_token))
# print(start_page_token)
start_page_token = 67
change_token = fetch_changes(
  service=drive_service, drive_id=SHARED_DRIVE_ID, saved_start_page_token=start_page_token
)
print("Changes:")
print(type(change_token))
pprint(change_token)
print("Eq:")
pprint(start_page_token == change_token)

from gdrive_sensor.utils.functions import handle_bundle_changes
from gdrive_sensor.utils.connection import drive_service
from pprint import pprint

file_id = "1xwMF6ANuy2qZ-kxUkNdReMU7ZMizQmmiG9G8ATACTn4"
driveId = "0AJflT9JpikpnUk9PVA"
# change_token = "76"
# change_token = "67"

results = drive_service.changes().list(
    driveId=driveId, 
    includeItemsFromAllDrives=True, 
    supportsAllDrives=True,
    pageToken=76,
    spaces='drive'
).execute()
items = results.get('files', [])

# item = handle_bundle_changes(id=file_id, driveId=driveId, pageToken=change_token)
pprint(items)


def subscribe_to_drive_changes(start_page_token, host: str = '0.0.0.0'):
    channel_id = str(uuid.uuid4())  # Generate a unique channel ID
    channel_address = f'https://{host}/notifications'  # Your webhook URL
    resource = {
        'id': channel_id,
        'type': 'web_hook',
        'address': channel_address,
        'params': {
            'ttl': 3600  # Time-to-live for the channel in seconds
        }
    }

    try:
        # Call the changes.watch method
        response = drive_service.changes().watch(pageToken=start_page_token, body=resource).execute()
        # print(f"Subscribed to Drive changes with channel ID: {response['id']}")
        # print()
        pprint(response)
        return response['id']
    except HttpError as error:
        print(f"An error occurred: {error}")

# start_page_token = fetch_start_page_token(service=drive_service)
# channel_id = subscribe_to_drive_changes(start_page_token=start_page_token, host='0.0.0.0')
# print()
# print(start_page_token)
# print(channel_id)

def subscribe_to_file_changes(file_id: str, channel_id: str, channel_token: str, channel_address: str):
    # Create the resource for the channel
    resource = {
        'id': channel_id,  # Unique ID for the channel
        'type': 'web_hook',  # Type of notification
        'address': channel_address,  # URL to send notifications to
        'params': {
            'ttl': 3600  # Time to live for the notification channel (in seconds)
        }
    }

    try:
        # Subscribe to changes for the specified file
        response = drive_service.changes().watch(
            # pageToken=start_page_token,
            pageToken=channel_token,
            body=resource
        ).execute()
        
        print(f"Subscribed to changes for file ID: {file_id}")
        return response
    except Exception as e:
        print(f"An error occurred while subscribing to file changes: {e}")
        return None

# file_id = '1hjLliYLOgDWGpSI1sh3I0TgxsBRqQUAWLaI2oYNxG6g'  # Replace with the actual file ID
# channel_token = fetch_start_page_token(service=drive_service)  # Token for the channel (optional)
# webhook_host: str = '0.0.0.0'
# channel_id = subscribe_to_drive_changes(start_page_token=channel_token, host=webhook_host)  # Unique ID for the channel
# channel_address = f'https://{webhook_host}/notifications'  # URL to receive notifications
# print()
# print(file_id)
# print(channel_id)
# print(channel_token)
# print(channel_address)

# response = subscribe_to_file_changes(file_id, channel_id, channel_token, channel_address)

# if response:
#     print("Subscription response:", response)
# else:
#     print("Failed to subscribe to file changes.")