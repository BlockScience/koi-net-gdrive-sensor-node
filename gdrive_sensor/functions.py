import os
from pprint import pprint
from rid_lib.ext import Cache, Effector, CacheBundle, Event, EventType

from utils import get_parent_ids
from utils.connection import drive_service, doc_service, sheet_service, slides_service
from utils.types import GoogleDrive, GoogleDoc, docsType, folderType, sheetsType, presentationType

cache = Cache(f"{os.getcwd()}/my_cache")
effector = Effector(cache)

def bundle_dir(item: dict):
    if not item['mimeType'] == folderType:
        print(f"Required MIME type for document: {folderType}")
        raise ValueError(f"Invalid MIME type for document: {item['mimeType']}")

def publish(rid_obj, bundle, event_type):
    publish_event = None
    if event_type is EventType.NEW:
        publish_event = Event(rid=rid_obj, event_type=EventType.NEW, manifest=bundle.manifest)
    elif event_type is EventType.UPDATE:
        publish_event = Event(rid=rid_obj, event_type=EventType.UPDATE, manifest=bundle.manifest)

def bundle_obj(item: dict, content: dict):
    rid_obj: GoogleDoc = GoogleDrive.from_reference(item['id']).google_object(item['mimeType'])
    if cache.exists(rid_obj) == False:
        cache.bundle_and_write(rid=rid_obj, data=dict(content))
    rid = rid_obj.__str__()
    print(rid)
    bundle: CacheBundle = cache.read(rid)
    return bundle

def bundle_folder(item: dict):
    raise_mimeTypeError(item, folderType)
    return bundle_obj(item, item)

def bundle_parent_folders(item: dict):
    parent_folder_ids = get_parent_ids(item)
    bundles = []
    for parent_folder_id in parent_folder_ids:
        parent_item = drive_service.files().get(fileId=parent_folder_id).execute()
        bundle = bundle_folder(parent_item)
        bundles.append(bundle)
    return bundles

def raise_mimeTypeError(item: dict, mimeType: str):
   if not item['mimeType'] == mimeType:
        print(f"Required MIME type for document: {mimeType}")
        raise ValueError(f"Invalid MIME type for document: {item['mimeType']}")

def bundle_doc(item: dict):
    raise_mimeTypeError(item, docsType)
    document = doc_service.documents().get(documentId=item['id']).execute()
    return bundle_obj(item, document)

def bundle_sheet(item: dict):
    raise_mimeTypeError(item, sheetsType)
    spreadsheet = sheet_service.spreadsheets().get(spreadsheetId=item['id']).execute()
    return bundle_obj(item, spreadsheet)

def bundle_slides(item: dict):
    raise_mimeTypeError(item, presentationType)
    presentation = slides_service.presentations().get(presentationId=item['id']).execute()
    return bundle_obj(item, presentation)

# Function to list types, names, IDs, and URIs of all folders and files in Google Drive
# list_all_folders_and_files_with_details


def bundle_list(query: str):
    results = drive_service.files().list(q=query).execute()
    items = results.get('files', [])
    
    # if not items:
    #     print('No folder found.')
    #     raise ValueError(f"Invalid MIME type for document: {item['mimeType']}")
    bundles = []
    for item in items:
        # print(item)
        # print()
        file_type = "Folder" if item['mimeType'] == folderType else "File"
        if file_type == "Folder":
           bundle = bundle_folder(item)
        elif file_type == "File":
            if item['mimeType'] == docsType:
                # bundle_object = bundle_doc
                bundle = bundle_doc(item)
            elif item['mimeType'] == sheetsType:
                # bundle_object = bundle_sheet
                bundle = bundle_sheet(item)
            elif item['mimeType'] == presentationType:
                # bundle_object = bundle_slides
                bundle = bundle_slides(item)
            bundles.append(bundle)
            # parent_folder_bundles = bundle_parent_folders(item)
            # bundles = bundles + parent_folder_bundles
    return bundles

# Example usage
query = f"'1OwnHDuusN9ZiFgUzmttR-cLDbU0sS4z3' in parents"
# query = f"'koi' in parents"
# query = f"mimeType='{folderType}' or mimeType!='{folderType}'"
bundles = bundle_list(query)
# pprint(bundles)
# exit()
bundle_dict = bundles[1].to_json()
bundle_dict['contents'] = 'masked'
# pprint(bundle_dict)
# print(bundle_dict['contents']['path'])
exit()

