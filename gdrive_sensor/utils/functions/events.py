from ..connection import drive_service
from datetime import datetime
from koi_net.protocol.event import EventType
from koi_net.processor.knowledge_object import RID

# List shared drives
def list_shared_drives(service):
    results = service.drives().list().execute()
    drives = results.get('drives', [])

    if not drives:
        print('No shared drives found.')
    else:
        print('Shared drives:')
        for drive in drives:
            print(f"Drive ID: {drive['id']}, Name: {drive['name']}")

def is_file_new_from_time(file_id):
    files_response = drive_service.files().get(
        fileId=file_id,
        fields='createdTime, modifiedTime', 
        supportsAllDrives=True
    ).execute()
    created_time_str = files_response.get('createdTime')
    created_time_dt = datetime.fromisoformat(created_time_str[:-1]) if created_time_str.endswith('Z') else datetime.fromisoformat(created_time_str)
    modified_time_str = files_response.get('modifiedTime')
    modified_time_dt = datetime.fromisoformat(modified_time_str[:-1]) if modified_time_str.endswith('Z') else datetime.fromisoformat(modified_time_str)
    time_difference = abs((modified_time_dt - created_time_dt).total_seconds())
    return time_difference <= 300

def is_file_new_with_revisions(file_id):
    revisions_response = drive_service.revisions().list(fileId=file_id).execute()
    revisions = revisions_response.get('revisions', [])
    # Sort revisions by modifiedTime
    # time_difference = 0
    # # Get the second revision if it exists
    # if len(revisions) >= 2:
    #     sorted_revisions = sorted(revisions, key=lambda r: r.get('modifiedTime'))
    #     second_revision = sorted_revisions[1]
    #     second_modifiedTime_str = second_revision['modifiedTime']
    #     second_modified_time_dt = datetime.fromisoformat(second_modifiedTime_str[:-1]) if second_modifiedTime_str.endswith('Z') else datetime.fromisoformat(second_modifiedTime_str)
    #     # print(f"Second Revision ID: {second_revision['id']}, Modified Time: {second_revision['modifiedTime']}")
        
    # time_difference = abs((modified_time_dt - created_time_dt).total_seconds())
    # Check if the difference is within 5 minutes (300 seconds)
    return (len(revisions) <= 2) or is_file_new_from_time(file_id)

# def get_UN_event_type(kobj: KnowledgeObject):
#     if is_file_new(kobj.rid.reference):
#         return EventType.NEW  
#     else:
#         return EventType.UPDATE 
    
# def get_FUN_event_type(change_dict: dict, kobj: KnowledgeObject):
#     change = change_dict[kobj.rid.reference]
#     # Google Considers a new file a change
#     if change['removed'] is False:
#         return get_UN_event_type(kobj)
#     else:
#         return EventType.FORGET

def get_UN_event_type_with_time(rid: RID):
    if is_file_new_from_time(rid.reference):
        return EventType.NEW  
    else:
        return EventType.UPDATE 
    
def get_FUN_event_type_with_time(change_dict: dict, rid: RID):
    change = change_dict[rid.reference]
    # Google Considers a new file a change
    if change['removed'] is False:
        return is_file_new_from_time(rid)
    else:
        return EventType.FORGET

def get_UN_event_type(rid: RID):
    if is_file_new_with_revisions(rid.reference):
        return EventType.NEW  
    else:
        return EventType.UPDATE 

def get_FUN_event_type(change_dict: dict, rid: RID):
    change = change_dict[rid.reference]
    # Google Considers a new file a change
    if change['removed'] is False:
        return get_UN_event_type(rid)
    else:
        return EventType.FORGET

def has_file_been_modified(file_id, last_checked_time):
    # Get the file metadata
    file = drive_service.files().get(fileId=file_id, fields='modifiedTime', supportsAllDrives=True).execute()
    
    # Get the modified time and convert it to a datetime object
    modified_time_str = file.get('modifiedTime')
    modified_time_dt = datetime.fromisoformat(modified_time_str[:-1]) if modified_time_str.endswith('Z') else datetime.fromisoformat(modified_time_str)

    # Compare with the last checked time
    return modified_time_dt > last_checked_time  # Returns False if modified

def is_file_deleted(rid: RID):
    file_id = rid.reference
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

# def publish(rid_obj, manifest, event_type):
#     publish_event = None
#     if event_type is EventType.NEW:
#         publish_event = Event(rid=rid_obj, event_type=EventType.NEW, manifest=manifest)
#     elif event_type is EventType.UPDATE:
#         publish_event = Event(rid=rid_obj, event_type=EventType.UPDATE, manifest=manifest)