from googleapiclient.discovery import build
from gdrive_sensor.utils.connection import drive_service

# List of channel IDs and resource IDs to stop
channels = [
    {'id': '235c87ae-a4d9-4588-9072-82fc21246f8e', 'resourceId': 'bUdBZpHVEzgFSWGQObzdqBKJ65A'},
    {'id': 'b89cb0f4-738a-48c7-9b15-0daba6a3c3de', 'resourceId': 'bUdBZpHVEzgFSWGQObzdqBKJ65A'},
    {'id': 'a1dc1854-ff72-4228-9263-f794b0ba3ebb', 'resourceId': 'bUdBZpHVEzgFSWGQObzdqBKJ65A'},
    {'id': '28c1bb15-8980-4457-9796-2366bb0d7d3a', 'resourceId': 'bUdBZpHVEzgFSWGQObzdqBKJ65A'},
    {'id': '9bb144f6-9620-4825-a5a0-c7418e0dd0ad', 'resourceId': 'bUdBZpHVEzgFSWGQObzdqBKJ65A'},
    {'id': 'b89cb0f4-738a-48c7-9b15-0daba6a3c3de', 'resourceId': 'bUdBZpHVEzgFSWGQObzdqBKJ65A'},
    {'id': '4aa1d309-c1e0-4bd9-aec9-82020c0d89bd', 'resourceId': 'bUdBZpHVEzgFSWGQObzdqBKJ65A'},
    {'id': '5e8251c5-e900-4528-9ee4-a5a13345fe0e', 'resourceId': 'bUdBZpHVEzgFSWGQObzdqBKJ65A'},
    {'id': 'ab6a75c6-e7d2-4df0-abd7-7a2f9cbdbd39', 'resourceId': 'bUdBZpHVEzgFSWGQObzdqBKJ65A'},
    {'id': '3cbb2e29-fff3-4d63-af9f-ec8c1f3dd67d', 'resourceId': 'bUdBZpHVEzgFSWGQObzdqBKJ65A'},
    {'id': '30ed5494-ff28-4e20-a805-f49fc214e6ed', 'resourceId': 'bUdBZpHVEzgFSWGQObzdqBKJ65A'},
    {'id': 'a1dc1854-ff72-4228-9263-f794b0ba3ebb', 'resourceId': 'bUdBZpHVEzgFSWGQObzdqBKJ65A'},
    {'id': 'b89cb0f4-738a-48c7-9b15-0daba6a3c3de', 'resourceId': 'bUdBZpHVEzgFSWGQObzdqBKJ65A'},
    {'id': 'a1dc1854-ff72-4228-9263-f794b0ba3ebb', 'resourceId': 'bUdBZpHVEzgFSWGQObzdqBKJ65A'},
    {'id': '3cbb2e29-fff3-4d63-af9f-ec8c1f3dd67d', 'resourceId': 'bUdBZpHVEzgFSWGQObzdqBKJ65A'},
    {'id': 'de617c75-426b-4e30-abe6-4293e54de50a', 'resourceId': 'bUdBZpHVEzgFSWGQObzdqBKJ65A'},
    {'id': '5e8251c5-e900-4528-9ee4-a5a13345fe0e', 'resourceId': 'bUdBZpHVEzgFSWGQObzdqBKJ65A'},
    # Add more channels as needed
]

# Stop each channel
for channel in channels:
    stop_request_body = {
        'id': channel['id'],
        'resourceId': channel['resourceId'],
    }
    try:
        drive_service.channels().stop(body=stop_request_body).execute()
        print(f"Stopped channel: {channel['id']}")
    except Exception as e:
        print(f"Failed to stop channel {channel['id']}: {e}")
