from datetime import datetime, timedelta
from gdrive_sensor.utils.connection import drive_service

def is_file_new(file_id, last_checked_time):
    # Get the file metadata
    file = drive_service.files().get(fileId=file_id, fields='createdTime, modifiedTime', supportsAllDrives=True).execute()
    
    created_time = file.get('createdTime')
    modified_time = file.get('modifiedTime')

    # Convert to datetime objects
    created_time_dt = datetime.fromisoformat(created_time[:-1])  # Remove 'Z' and convert
    # modified_time_dt = datetime.fromisoformat(modified_time[:-1])  # Remove 'Z' and convert
    print(created_time_dt)
    # print(modified_time_dt)

    # Check if the file is new
    if created_time_dt > last_checked_time #or modified_time_dt > last_checked_time:
        return True  # The file is new
    return False  # The file is not new

# Example usage
file_id = '19IjeqoK_60hMuj00cU9v4Xc-TqC-S_noEU-wd6o2Ghk'
last_checked_time = datetime.now() - timedelta(microseconds=1)  # Check for files created/modified in the last microseconds

if is_file_new(file_id, last_checked_time):
    print("The file is new.")
else:
    print("The file is not new.")