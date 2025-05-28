# from gdrive_sensor.utils.functions import handle_bundle_changes, get_new_start_page_token
from gdrive_sensor.utils.connection import drive_service
from gdrive_sensor import START_PAGE_TOKEN, CURRENT_PAGE_TOKEN, NEXT_PAGE_TOKEN
from pprint import pprint

file_id = "1xwMF6ANuy2qZ-kxUkNdReMU7ZMizQmmiG9G8ATACTn4"
driveId = "0AJflT9JpikpnUk9PVA"
# change_token = "76"
# start_token = "67"
# change_token = "76"
# start_token = "84"

# START_PAGE_TOKEN = '67'
# CURRENT_PAGE_TOKEN = '86'

# results = drive_service.changes().list(
#     driveId=driveId, 
#     includeItemsFromAllDrives=True, 
#     supportsAllDrives=True,
#     pageToken=start_token,
#     includeRemoved=True,
#     spaces='drive'
# ).execute()
# changes = results.get('changes')
# nextPageToken = results.get('nextPageToken')
# newStartPageToken = results.get('newStartPageToken')
# print()
# print(nextPageToken)
# print(newStartPageToken)
# print()
# pprint(changes)


results = drive_service.changes().list(
    driveId=driveId, 
    includeItemsFromAllDrives=True, 
    supportsAllDrives=True,
    pageToken='67',
    includeRemoved=True,
    includeCorpusRemovals=True,
    spaces='drive'
).execute()
changes = results.get('changes')
# nextPageToken = results.get('nextPageToken')
# newStartPageToken = results.get('newStartPageToken')
print()
# print(nextPageToken)
# print(newStartPageToken)
print()
pprint(changes)

# item = handle_bundle_changes(id=file_id, driveId=driveId, pageToken=change_token)
# [item['fileId'] for item in items]
# pprint(changes)
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