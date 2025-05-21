from pprint import pprint
from gdrive_sensor.utils.functions import bundle_list, list_shared_drives
from gdrive_sensor.utils.connection import drive_service
from gdrive_sensor.utils.functions import fetch_start_page_token, fetch_changes
from gdrive_sensor.config import SHARED_DRIVE_ID
from koi_net.protocol.event import Event, EventType
from rid_lib.ext import Bundle

# Example usage
# query = f"'1OwnHDuusN9ZiFgUzmttR-cLDbU0sS4z3' in parents"
driveId = SHARED_DRIVE_ID
query = f"\'{driveId}\' in parents"

# query = f"'koi' in parents"
# query = f"mimeType='{folderType}' or mimeType!='{folderType}'"
start_page_token = fetch_start_page_token(
   service=drive_service, drive_id=SHARED_DRIVE_ID
)
print(start_page_token)


def fetch_files(drive_service, driveId, pageToken=None):
    original_files = []
    changed_files = []
    
    while True:
        # Prepare the request with the page token if it exists
        # if not pageToken:
        # response = drive_service.changes().list(
        #     driveId=driveId, 
        #     includeItemsFromAllDrives=True, 
        #     supportsAllDrives=True,
        #     pageToken=pageToken
        # ).execute() # Use await here

        # page_token = response.get('nextPageToken')
        # print(pageToken)

        response = drive_service.files().list(
            driveId=driveId, 
            includeItemsFromAllDrives=True, 
            supportsAllDrives=True,
            pageToken=pageToken,
            corpora='drive'
        ).execute() # Use await here
        
        
        
        # Process the files in the response
        original_files.extend(response.get('files', []))  # Collect original files
        changed_files.extend(response.get('changes', []))  # Collect changed files (if applicable)

        # Get the next page token
        page_token = response.get('nextPageToken')
        print(pageToken)
        if not page_token:  # Exit the loop if there are no more pages
            break

    return original_files, changed_files


original_files, changed_files = fetch_files(
  drive_service=drive_service, 
  driveId=SHARED_DRIVE_ID,
  pageToken=None
)
print(original_files)
print()
print(changed_files)
print()
exit()
# change_token = fetch_changes(
#   service=drive_service, drive_id=SHARED_DRIVE_ID, saved_start_page_token=start_page_token
# )
start_page_token = '51'
bundles = bundle_list(driveId=driveId)
# bundles = bundle_list(query=query, driveId=driveId, pageToken=start_page_token)
# bundles = bundle_list(query=query, driveId=driveId, pageToken=change_token)
# bundles = bundle_list(driveId=driveId, pageToken=start_page_token)
bundle: Bundle = bundles[0]
bundle_manifest = dict(bundle.manifest)
rid_obj = bundle.manifest.rid
bundle_contents = dict(bundle.contents)
print("Examples:")
print()
print("nextPageToken:")
bundle.contents['nextPageToken']
print()
print("Manifest:")
pprint(bundle_manifest)
print()
print("Contents:")
# pprint(bundle_contents)
print()
print("RID Obj:")
print(rid_obj)
print()
print("Event:")
event = Event(rid=rid_obj, event_type=EventType.NEW, manifest=bundle_manifest)
print(event)
print()
print()

# list_shared_drives(drive_service)



# bundle_dict = bundles[1].to_json()
# bundle_dict['contents'] = 'masked'
exit()