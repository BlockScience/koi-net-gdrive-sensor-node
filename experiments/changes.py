from gdrive_sensor.utils.functions import handle_bundle_changes, get_new_start_page_token
from gdrive_sensor.utils.connection import drive_service
from pprint import pprint

file_id = "1xwMF6ANuy2qZ-kxUkNdReMU7ZMizQmmiG9G8ATACTn4"
driveId = "0AJflT9JpikpnUk9PVA"
change_token = "76"
start_token = "67"

results = drive_service.changes().list(
    driveId=driveId, 
    includeItemsFromAllDrives=True, 
    supportsAllDrives=True,
    pageToken=start_token,
    spaces='drive'
).execute()
changes = results.get('changes')

# item = handle_bundle_changes(id=file_id, driveId=driveId, pageToken=change_token)
# [item['fileId'] for item in items]
pprint(changes)
# filtered_changes = [change for change in changes if change['fileId'] == file_id]
# pprint(filtered_changes)

# def get_new_start_page_token(start_token=None):
#     results = drive_service.changes().list(
#         driveId=driveId, 
#         includeItemsFromAllDrives=True, 
#         supportsAllDrives=True,
#         pageToken=start_token,
#         spaces='drive'
#     ).execute()
    
#     # Extract the next page token
#     next_page_token = results.get('newStartPageToken')
    
#     return next_page_token

# Example usage
# next_token = get_new_start_page_token(driveId, start_token)
# print(f"Next Page Token: {next_token}")