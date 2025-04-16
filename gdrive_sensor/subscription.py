import uuid
from googleapiclient.errors import HttpError
from utils.connection import drive_service

def fetch_start_page_token():
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
    service = drive_service

    # pylint: disable=maybe-no-member
    response = service.changes().getStartPageToken().execute()
    print(f'Start token: {response.get("startPageToken")}')

  except HttpError as error:
    print(f"An error occurred: {error}")
    response = None

  return response.get("startPageToken")


def fetch_changes(saved_start_page_token):
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
    service = drive_service

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


# start_page_token = fetch_start_page_token()
# changes = fetch_changes(saved_start_page_token=start_page_token)
# pprint(changes)

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
    except HttpError as error:
        print(f"An error occurred: {error}")

# subscribe_to_drive_changes()