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

# Example usage
file_id = '19IjeqoK_60hMuj00cU9v4Xc-TqC-S_noEU-wd6o2Ghk'

if is_file_deleted(file_id):
    print("The file has been deleted (trashed).")
else:
    print("The file is not deleted.")