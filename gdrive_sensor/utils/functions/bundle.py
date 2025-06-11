from gdrive_sensor import SENSOR
from . import get_parent_ids
from ...core import node
from ..connection import drive_service, doc_service, sheet_service, slides_service
from ..types import GoogleWorkspaceApp, docsType, folderType, sheetsType, presentationType
from rid_lib import RID
from rid_lib.ext import Cache, Effector, Bundle


# cache = Cache(f"{SENSOR}/my_cache")
cache = node.cache
effector = Effector(cache)

def bundle_dir(item: dict):
    if not item['mimeType'] == folderType:
        print(f"Required MIME type for document: {folderType}")
        raise ValueError(f"Invalid MIME type for document: {item['mimeType']}")

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
        parent_item = drive_service.files().get(fileId=parent_folder_id, supportsAllDrives=True).execute()
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

def bundle_item(item):
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
    return bundle


def bundle_list(query: str = None, driveId: str = None, pageToken: str = None):
    results = None
    results = drive_service.files().list(
        q=query, 
        driveId=driveId, 
        includeItemsFromAllDrives=True, 
        supportsAllDrives=True,
        corpora='drive'
    ).execute()
    items = results.get('files', [])
    
    # if not items:
    #     print('No folder found.')
    #     raise ValueError(f"Invalid MIME type for document: {item['mimeType']}")
    bundles = []
    for item in items:
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
            # bundle.contents['page_token'] = page_token
            bundles.append(bundle)
            # parent_folder_bundles = bundle_parent_folders(item)
            # bundles = bundles + parent_folder_bundles
    return bundles


# def handle_bundle_change(id: str):
#     item = drive_service.files().get(fileId=id).execute()
    
#     # if not items:
#     #     print('No folder found.')
#     #     raise ValueError(f"Invalid MIME type for document: {item['mimeType']}")
   
#     file_type = "Folder" if item['mimeType'] == folderType else "File"
#     if file_type == "Folder":
#         bundle = bundle_folder(item)
#     elif file_type == "File":
#         if item['mimeType'] == docsType:
#             # bundle_object = bundle_doc
#             bundle = bundle_doc(item)
#         elif item['mimeType'] == sheetsType:
#             # bundle_object = bundle_sheet
#             bundle = bundle_sheet(item)
#         elif item['mimeType'] == presentationType:
#             # bundle_object = bundle_slides
#             bundle = bundle_slides(item)
#         # parent_folder_bundles = bundle_parent_folders(item)
#         # bundles = bundles + parent_folder_bundles
#     return bundle


# def handle_bundle_changes(driveId: str = None, pageToken: str = None):
#     results = None
#     results = drive_service.changes().list(
#         driveId=driveId, 
#         includeItemsFromAllDrives=True, 
#         supportsAllDrives=True,
#         pageToken=pageToken,
#         spaces='drive'
#     ).execute()
#     items = results.get('changes', [])
    
#     # if not items:
#     #     print('No folder found.')
#     #     raise ValueError(f"Invalid MIME type for document: {item['mimeType']}")
#     bundles = []
#     for item in items:
#         # print(item)
#         # print()
#         file_type = "Folder" if item['mimeType'] == folderType else "File"
#         if file_type == "Folder":
#            bundle = bundle_folder(item)
#         elif file_type == "File":
#             if item['mimeType'] == docsType:
#                 # bundle_object = bundle_doc
#                 bundle = bundle_doc(item)
#             elif item['mimeType'] == sheetsType:
#                 # bundle_object = bundle_sheet
#                 bundle = bundle_sheet(item)
#             elif item['mimeType'] == presentationType:
#                 # bundle_object = bundle_slides
#                 bundle = bundle_slides(item)
#             bundles.append(bundle)
#             # parent_folder_bundles = bundle_parent_folders(item)
#             # bundles = bundles + parent_folder_bundles
#     return bundles