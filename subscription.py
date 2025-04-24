import uuid
from googleapiclient.errors import HttpError
from gdrive_sensor.utils.connection import drive_service
from pprint import pprint

def fetch_start_page_token(service):
  """Retrieve page token for the current state of the account.
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
    response = service.changes().getStartPageToken().execute()
    print(f'Start token: {response.get("startPageToken")}')

  except HttpError as error:
    print(f"An error occurred: {error}")
    response = None

  return response.get("startPageToken")


def fetch_changes(service, saved_start_page_token):
  """Retrieve the list of changes for the currently authenticated user.
      prints changed file's ID
  Args:
      saved_start_page_token : StartPageToken for the current state of the
      account.
  Returns: saved start page token.

  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """
#   creds, _ = google.auth.default()
  try:
    # create drive api client
    # service = build("drive", "v3", credentials=creds)
    # service = drive_service

    # Begin with our last saved start token for this user or the
    # current token from getStartPageToken()
    page_token = saved_start_page_token
    # pylint: disable=maybe-no-member

    while page_token is not None:
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

  except HttpError as error:
    print(f"An error occurred: {error}")
    saved_start_page_token = None

  return saved_start_page_token


start_page_token = fetch_start_page_token(service=drive_service)
changes = fetch_changes(service=drive_service, saved_start_page_token=start_page_token)
print("Changes:")
pprint(changes)

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
        print(f"Subscribed to Drive changes with channel ID: {response['id']}")
        print()
        pprint(response)
    except HttpError as error:
        print(f"An error occurred: {error}")

subscribe_to_drive_changes(start_page_token)

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
            pageToken=start_page_token,
            body=resource
        ).execute()
        
        print(f"Subscribed to changes for file ID: {file_id}")
        return response
    except Exception as e:
        print(f"An error occurred while subscribing to file changes: {e}")
        return None

file_id = 'YOUR_FILE_ID'  # Replace with the actual file ID
channel_id = 'YOUR_CHANNEL_ID'  # Unique ID for the channel
channel_token = 'YOUR_CHANNEL_TOKEN'  # Token for the channel (optional)
webhook_host: str = '0.0.0.0'
channel_address = f'https://{webhook_host}/notifications'  # URL to receive notifications

# response = subscribe_to_file_changes(file_id, channel_id, channel_token, channel_address)

# if response:
#     print("Subscription response:", response)
# else:
#     print("Failed to subscribe to file changes.")