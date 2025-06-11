import uuid
from googleapiclient.errors import HttpError
from gdrive_sensor.utils.connection import drive_service
from gdrive_sensor import SHARED_DRIVE_ID, START_PAGE_TOKEN
from pprint import pprint

def subscribe_to_drive_changes(driveId, start_page_token, host: str = '0.0.0.0'):
    channel_id = str(uuid.uuid4())  # Generate a unique channel ID
    channel_address = f'https://{host}/google-drive-listener'  # Your webhook URL
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
        response = drive_service.changes().watch(
          driveId=driveId, 
          includeItemsFromAllDrives=True, 
          supportsAllDrives=True,
          includeRemoved=True,
          includeLabels=True,
          spaces='drive',
          pageToken=start_page_token,
          body=resource
        ).execute()
        # print(f"Subscribed to Drive changes with channel ID: {response['id']}")
        # print()
        pprint(response)
        return response['id']
    except HttpError as error:
        print(f"An error occurred: {error}")


# start_page_token = fetch_start_page_token(service=drive_service)
# start_page_token = START_PAGE_TOKEN
# channel_id = subscribe_to_drive_changes(driveId=SHARED_DRIVE_ID, start_page_token=start_page_token, host='koi-net.block.science')
# print()
# print(start_page_token)
# print(channel_id)


def subscribe_to_file_changes(fileId, host: str = '0.0.0.0'):
    # channel_id = str(uuid.uuid4())  # Generate a unique channel ID
    channel_id = '0677680e-2aa7-4673-a3eb-94951fbbd5d8'
    channel_address = f'https://{host}/google-drive-listener'  # Your webhook URL
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
        response = drive_service.files().watch(
          fileId=fileId, 
          supportsAllDrives=True,
          body=resource
        ).execute()
        # print(f"Subscribed to Drive changes with channel ID: {response['id']}")
        # print()
        pprint(response)
        return response['id']
    except HttpError as error:
        print(f"An error occurred: {error}")


# start_page_token = fetch_start_page_token(service=drive_service)
# start_page_token = START_PAGE_TOKEN
fileId = '1xaI-rRZdkGQajXUJg65StBpbblyK1wwIhpiS1AiBygA'
channel_id = subscribe_to_file_changes(fileId=fileId, host='koi-net.block.science')
# channel_id = subscribe_to_file_changes(fileId=fileId)
print()
# print(channel_id)