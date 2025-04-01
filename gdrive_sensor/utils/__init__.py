from utils.connection import drive_service, doc_service

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