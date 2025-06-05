from datetime import datetime, timedelta, timezone
from googleapiclient.errors import HttpError
from gdrive_sensor.utils.connection import drive_service

def is_file_deleted(file_id):
    try:
        # Get the file metadata
        file = drive_service.files().get(fileId=file_id, fields='id, name, trashed', supportsAllDrives=True).execute()
        
        # Check if the file is trashed
        if file.get('trashed'):
            return True  # The file is deleted (in the trash)
        return False  # The file is not deleted
    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # Handle errors (e.g., file not found)

from dateutil import parser

def is_file_new(file_id, last_checked_time):
    # Get the file metadata
    file = drive_service.files().get(fileId=file_id, fields='createdTime, modifiedTime', supportsAllDrives=True).execute()
    
    created_time_str = file.get('createdTime')
    created_time_dt = datetime.fromisoformat(created_time_str[:-1]) if created_time_str.endswith('Z') else datetime.fromisoformat(created_time_str)
    print(created_time_dt)
    print(last_checked_time)

    # Check if the file is new
    return created_time_dt > last_checked_time

def has_file_been_modified(file_id, last_checked_time):
    # Get the file metadata
    file = drive_service.files().get(fileId=file_id, fields='modifiedTime', supportsAllDrives=True).execute()
    
    # Get the modified time and convert it to a datetime object
    modified_time_str = file.get('modifiedTime')
    modified_time_dt = datetime.fromisoformat(modified_time_str[:-1]) if modified_time_str.endswith('Z') else datetime.fromisoformat(modified_time_str)
    print(modified_time_dt)
    print(last_checked_time)

    # Compare with the last checked time
    return modified_time_dt > last_checked_time  # Returns False if modified


# # Example usage
# file_id = '19IjeqoK_60hMuj00cU9v4Xc-TqC-S_noEU-wd6o2Ghk'

# if is_file_deleted(file_id):
#     print("The file has been deleted (trashed).")
# else:
#     print("The file is not deleted.")

# Example usage
file_id = '1H56WazBIs-TTNjLCdOT2ngjYv8SiU0aNnpyjVQ-Dv9c'
time_format = "%Y-%m-%d %H:%M:%S.%f"
last_checked_time_str = datetime.now(timezone.utc).strftime(time_format) # - timedelta(days=1)  # Check for files created/modified in the last day
last_checked_time_dt = datetime.strptime(last_checked_time_str, time_format) - timedelta(days=1)

if is_file_new(file_id, last_checked_time_dt):
    print("The file is new.")
else:
    print("The file is not new.")

# # Example usage
# file_id = '1H56WazBIs-TTNjLCdOT2ngjYv8SiU0aNnpyjVQ-Dv9c'
# last_checked_time = datetime.now() #- timedelta(days=1)  # Check for modifications in the last day

# if has_file_been_modified(file_id, last_checked_time):
#     print("The file has been modified since the last check.")
# else:
#     print("The file has not been modified since the last check.")