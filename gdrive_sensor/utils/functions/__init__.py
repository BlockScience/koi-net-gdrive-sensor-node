from ..connection import drive_service, doc_service
from koi_net.protocol.event import EventType, Event

def filter_by_ids(files: list, ids: list):
   filtered_files = [file for file in files if file['id'] in ids]

def filter_by_changes(original_files, changed_files):
   changed_ids = [file['id'] for file in changed_files]
   unchanged_files = [file for file in original_files if file['id'] not in changed_ids]
   changed_files = filter_by_ids(changed_files, original_ids)

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

def get_parent_ids(item: dict):
    file_metadata = drive_service.files().get(fileId=item['id'], fields='parents').execute()
    parent_ids = file_metadata.get('parents', [])
    return parent_ids

def get_doc_paths(item: dict):
    parent_ids = get_parent_ids(item)
    path_parts = []
    path_part_kvs = {}
    while parent_ids:
        for parent_id in parent_ids:
            parent_metadata = drive_service.files().get(fileId=parent_id, fields='id, name, parents').execute()
            path_parts.append(parent_metadata['name'])
            path_part_kvs[parent_metadata['name']] = parent_metadata['id']
            parent_ids = parent_metadata.get('parents', [])
            break
        if not parent_ids:
            pass
    path_parts.reverse()
    document = doc_service.documents().get(documentId=item['id']).execute()
    document_name = document.get('title', 'Untitled Document')
    path_part_kvs[document_name] = item['id']
    item_names = path_parts + [document_name]
    full_path = str('/'.join(item_names))
    item_ids = [path_part_kvs[name] for name in item_names]
    full_id_path = str('/'.join(item_ids))
    return (full_path, full_id_path)