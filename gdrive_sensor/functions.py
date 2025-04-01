import os, uuid
from pprint import pprint
from rid_lib.ext import Cache, Effector, CacheBundle, Event, EventType

from googleapiclient.errors import HttpError
from utils import get_parent_ids
from utils.connection import drive_service, doc_service, sheet_service, slides_service
from utils.types import GoogleDrive, GoogleDoc, docsType, folderType, sheetsType, presentationType

cache = Cache(f"{os.getcwd()}/my_cache")
effector = Effector(cache)

# the ;path'

# {'contents': {'id': 'masked',
#               'mimeType': 'application/vnd.google-apps.document',
#               'path': 'masked_name/masked_name/masked_name',
#               "id_path": 'masked_id/masked_id/masked_file_id'
#               'text': 'masked',
#               'url': 'https://drive.google.com/file/d/{masked_id}'},
#  'manifest': {'rid': 'orn:google.drive.document:{masked_id}',
#               'sha256_hash': 'e6641bd3e8c9810c1afb940fd49f7596688c3b37461b0fe375a9733fde60a557',
#               'timestamp': '2025-03-01T02:23:04.618580+00:00'}}

#ToDo: Auth consideration - Try accessing provare folder

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


# Next ToDo (done): we want access to raw doc representation
# Next plus (done): URL is a transformation from one RID to Another, HTTPS Type
# Next ToDo (done for docs): content should be the direct json returned from the file / folder
# Next ToDo (done): Remove folder ids and just include file id
# Next ToDo (Done): find schema & endpoint differences online for different types (an aditional type)
# ToDo: Test rid.from_string
# ToDo: Get URL fom api (in returned content)
# ToDo: rename item to metadata
# ToDo: Look up auth is universaly unique or tied to specific account
# ToDo: Auth Scopes [is per account and folder (root)] (read only, etc)
# ToDo: select folder to opperate out off
# ToDo; Processing live file Updates contigent on deployment
# Near: Pull (backfill or catch up (do i have everything)), & cache, then bundle and publish events what hasnt been published

# ToDo: Refactor Processor, set up call with sayer


# Question: if i change a files folder locations does the id change or remain the same
# Question: if i edit does the id change or remain the same

# Future: mimeTypes in manafest
# Future: parsed knowledge object (concatenated text) in the future

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
def bundle_list(folder_name = None):
    # query = f"mimeType='{folderType}' and name='{folder_name}'"
    # query = f"mimeType='{folderType}' and id='{folder_name}'"
    # query = f"id='{folder_name}'"
    {'kind': 'drive#file', 'mimeType': 'application/vnd.google-apps.folder', 'id': '1OwnHDuusN9ZiFgUzmttR-cLDbU0sS4z3', 'name': 'koi'}
    query = f"mimeType='{folderType}' or mimeType!='{folderType}'"
    # if folder_name is not None:
    #    query = folder_query
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
# bundles = bundle_list(folder_name='1OwnHDuusN9ZiFgUzmttR-cLDbU0sS4z3')
bundles = bundle_list()
# pprint(bundles)
# exit()
bundle_dict = bundles[1].to_json()
bundle_dict['contents'] = 'masked'
# pprint(bundle_dict)
# print(bundle_dict['contents']['path'])
exit()

def fetch_start_page_token():
  """Retrieve page token for the current state of the account.
  Returns & prints : start page token

  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """
#   creds, _ = google.auth.default()

  try:
    # create drive api client
    # service = build("drive", "v3", credentials=creds)
    service = drive_service

    # pylint: disable=maybe-no-member
    response = service.changes().getStartPageToken().execute()
    print(f'Start token: {response.get("startPageToken")}')

  except HttpError as error:
    print(f"An error occurred: {error}")
    response = None

  return response.get("startPageToken")


def fetch_changes(saved_start_page_token):
  """Retrieve the list of changes for the currently authenticated user.
      prints changed file's ID
  Args:
      saved_start_page_token : StartPageToken for the current state of the
      account.
  Returns: saved start page token.

  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """
#   creds, _ = google.auth.default()
  try:
    # create drive api client
    # service = build("drive", "v3", credentials=creds)
    service = drive_service

    # Begin with our last saved start token for this user or the
    # current token from getStartPageToken()
    page_token = saved_start_page_token
    # pylint: disable=maybe-no-member

    while page_token is not None:
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


# start_page_token = fetch_start_page_token()
# changes = fetch_changes(saved_start_page_token=start_page_token)
# pprint(changes)

def subscribe_to_drive_changes(start_page_token, host: str = '0.0.0.0'):
    channel_id = str(uuid.uuid4())  # Generate a unique channel ID
    channel_address = f'https://{host}/notifications'  # Your webhook URL
    resource = {
        'id': channel_id,
        'type': 'web_hook',
        'address': channel_address,
        'params': {
            'ttl': 3600  # Time-to-live for the channel in seconds
        }
    }

    try:
        # Call the changes.watch method
        response = drive_service.changes().watch(pageToken=start_page_token, body=resource).execute()
        print(f"Subscribed to Drive changes with channel ID: {response['id']}")
    except HttpError as error:
        print(f"An error occurred: {error}")

# subscribe_to_drive_changes()