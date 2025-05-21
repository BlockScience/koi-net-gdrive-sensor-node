from pprint import pprint
from rid_lib.ext import Cache, Effector, Bundle
from koi_net.protocol.event import Event, EventType

from . import get_parent_ids
from .connection import drive_service, doc_service, sheet_service, slides_service
from .types import GoogleWorkspaceApp, docsType, folderType, sheetsType, presentationType
from googleapiclient.errors import HttpError

from gdrive_sensor import SENSOR


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
def fetch_start_page_token(service, drive_id=None):
  """Retrieve page token for the current state of the account or a specific drive.
  Returns & prints : start page token

  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """
  try:
    # pylint: disable=maybe-no-member
    if drive_id:
      response = service.changes().getStartPageToken(
        driveId=drive_id,
        supportsAllDrives=True
      ).execute()
    else:
      response = service.changes().getStartPageToken().execute()
    
    # print(f'Start token: {response.get("startPageToken")}')
    # print(response)
    return response.get("startPageToken")

  except HttpError as error:
    print(f"An error occurred: {error}")
    response = None

  return response.get("startPageToken")

def handle_bundle_changes(id: str, driveId: str = None, change_token: str = None):
    results = None
    results = drive_service.changes().list(
        q=f"id='{id}'", 
        driveId=driveId, 
        includeItemsFromAllDrives=True, 
        supportsAllDrives=True,
        pageToken=change_token,
        spaces='drive'
    ).execute()
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

def fetch_files(drive_service, driveId, pageToken=None):
    original_files = []
    changed_files = []
    
    while True:
        # Prepare the request with the page token if it exists
        response = drive_service.files().list(
            driveId=driveId, 
            includeItemsFromAllDrives=True, 
            supportsAllDrives=True,
            pageToken=pageToken,
            corpora='drive'
        ).execute() # Use await here
        
        # Process the files in the response
        original_files.extend(response.get('files', []))  # Collect original files
        changed_files.extend(response.get('changedFiles', []))  # Collect changed files (if applicable)

        # Get the next page token
        page_token = response.get('nextPageToken')
        if not page_token:  # Exit the loop if there are no more pages
            break

    return original_files, changed_files

def filter_by_ids(files: list, ids: list):
   filtered_files = [file for file in files if file['id'] in ids]

def filter_by_changes(original_files, changed_files):
   changed_ids = [file['id'] for file in changed_files]
   unchanged_files = [file for file in original_files if file['id'] not in changed_ids]
   changed_files = filter_by_ids(changed_files, original_ids)
   

def bundle_list(query: str = None, driveId: str = None, pageToken: str = None):
    results = None
    
    if driveId is None and pageToken is None:
        results = drive_service.files().list(q=query).execute()
    elif driveId is None and pageToken is not None:
        results = drive_service.changes().list(q=query, pageToken=pageToken).execute()
    elif driveId is not None and pageToken is not None:
        results = drive_service.changes().list(
            # q=query, 
            driveId=driveId, 
            includeItemsFromAllDrives=True, 
            supportsAllDrives=True,
            pageToken=pageToken,
            spaces='drive'
        ).execute()
    elif driveId is not None and pageToken is None:
        results = drive_service.files().list(
            # q=query, 
            driveId=driveId, 
            includeItemsFromAllDrives=True, 
            supportsAllDrives=True,
            corpora='drive'
        ).execute()
    page_token = results.get('nextPageToken')
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
            bundle.contents['nextPageToken'] = page_token
            bundles.append(bundle)
            # parent_folder_bundles = bundle_parent_folders(item)
            # bundles = bundles + parent_folder_bundles
    return bundles


def fetch_changes(service, saved_start_page_token, drive_id=None):
  """Retrieve the list of changes for the currently authenticated user or a specific drive.
      prints changed file's ID
  Args:
      saved_start_page_token : StartPageToken for the current state of the
      account.
      drive_id : Optional ID of the specific drive to retrieve changes from.
  Returns: saved start page token.

  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """
  try:
    # Begin with our last saved start token for this user or the
    # current token from getStartPageToken()
    page_token = saved_start_page_token
    # pylint: disable=maybe-no-member

    while page_token is not None:
      if drive_id:
        response = (
            service.changes().list(
               driveId=drive_id,
               supportsAllDrives=True, 
               includeItemsFromAllDrives=True, 
               pageToken=page_token, 
               spaces="drive"
            ).execute()
        )
      else:
        response = (
            service.changes().list(pageToken=page_token, spaces="drive").execute()
        )
        
      for change in response.get("changes"):
        # Process change
        print(f'Change found for file: {change.get("fileId")}')
      if "newStartPageToken" in response:
        # Last page, save this token for the next polling interval
        saved_start_page_token = response.get("newStartPageToken")
      page_token = response.get("nextPageToken")

  except HttpError as error:
    print(f"An error occurred: {error}")
    saved_start_page_token = None

    return saved_start_page_token

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