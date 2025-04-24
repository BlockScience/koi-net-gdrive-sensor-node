from pprint import pprint
from rid_lib.ext import Cache, Effector, Bundle
from koi_net.protocol.event import Event, EventType

from . import get_parent_ids
from .connection import drive_service, doc_service, sheet_service, slides_service
from .types import GoogleWorkspaceApp, docsType, folderType, sheetsType, presentationType

from ..config import SENSOR

cache = Cache(f"{SENSOR}/my_cache")
effector = Effector(cache)

def bundle_dir(item: dict):
    if not item['mimeType'] == folderType:
        print(f"Required MIME type for document: {folderType}")
        raise ValueError(f"Invalid MIME type for document: {item['mimeType']}")

# def publish(rid_obj, manifest, event_type):
#     publish_event = None
#     if event_type is EventType.NEW:
#         publish_event = Event(rid=rid_obj, event_type=EventType.NEW, manifest=manifest)
#     elif event_type is EventType.UPDATE:
#         publish_event = Event(rid=rid_obj, event_type=EventType.UPDATE, manifest=manifest)

def bundle_obj(item: dict, content: dict):
    rid_obj = GoogleWorkspaceApp.from_reference(item['id']).google_object(item['mimeType'])
    if cache.exists(rid_obj) == False:
        bundle = Bundle.generate(rid=rid_obj, contents=dict(content))
        cache.write(bundle)
        # cache.bundle_and_write(rid=rid_obj, data=dict(content))
    rid = rid_obj.__str__()
    print(rid)
    # bundle: CacheBundle = cache.read(rid)
    bundle: Bundle = cache.read(rid)
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


def bundle_list(query: str, driveId: str = None):
    results = None
    if driveId is None:
        results = drive_service.files().list(q=query).execute()
    else:
        results = drive_service.files().list(
            q=query, 
            driveId=driveId, 
            includeItemsFromAllDrives=True, 
            supportsAllDrives=True, 
            corpora='drive').execute()
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


def event_filter(bundles):
    events = []
    for bundle in bundles:
        manifest = bundle.manifest
        rid_obj = manifest.rid
        event = Event(rid=rid_obj, event_type=EventType.NEW, manifest=manifest)
        events.append(event)
    return events

def rid_filter(bundles):
    rids = []
    for bundle in bundles:
        manifest = bundle.manifest
        rid_obj = manifest.rid
        rids.append(rid_obj)
    return rids

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