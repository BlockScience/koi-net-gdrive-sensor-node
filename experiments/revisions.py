from gdrive_sensor.utils.connection import drive_service
from gdrive_sensor.config import SHARED_DRIVE_ID
from pprint import pprint

# Assuming you have already authenticated and have a drive_service instance
file_id = '1xaI-rRZdkGQajXUJg65StBpbblyK1wwIhpiS1AiBygA'  # Replace with your actual file ID

# Get the revision history
# revisions = drive_service.revisions().list(fileId=file_id).execute()

revisions_response = drive_service.revisions().list(
    fileId=file_id,
).execute()

# Print the revision history
# for revision in revisions.get('revisions', []):
#     pprint(revision)
    # print(f"Revision ID: {revision['id']}, Modified Time: {revision['modifiedTime']}")

latest_revision = None
latest_time = None
revisions = sorted(revisions_response.get('revisions', []), key=lambda r: r.get('modifiedTime'))

for revision in revisions:
    modified_time = revision.get('modifiedTime')
    if latest_time is None or modified_time > latest_time:
        latest_time = modified_time
        latest_revision = revision

# Print the latest revision details
if latest_revision:
    print(f"Latest Revision ID: {latest_revision['id']}, Modified Time: {latest_revision['modifiedTime']}")
    pprint(revisions_response)
else:
    print("No revisions found.")