import logging
# from datetime import datetime, timedelta
from koi_net.processor.handler import HandlerType, STOP_CHAIN
from koi_net.processor.knowledge_object import KnowledgeSource, KnowledgeObject
from koi_net.processor.interface import ProcessorInterface
from koi_net.protocol.event import EventType
from koi_net.protocol.edge import EdgeType
from koi_net.protocol.node import NodeProfile
from koi_net.protocol.helpers import generate_edge_bundle
from rid_lib.ext import Bundle
from rid_lib.types import KoiNetNode

from .utils.types import GoogleDriveFolder, GoogleDoc, GoogleSlides, GoogleSheets
from .utils.types import folderType, docsType, sheetsType, presentationType
from .utils.connection import drive_service, doc_service, sheet_service, slides_service
from .utils.functions.events import get_FUN_event_type, is_file_deleted
from .utils.functions.api import get_change_results
from .core import node

logger = logging.getLogger(__name__)


@node.processor.register_handler(HandlerType.Network, rid_types=[KoiNetNode])
def coordinator_contact(processor: ProcessorInterface, kobj: KnowledgeObject):
    # when I found out about a new node
    if kobj.normalized_event_type != EventType.NEW: 
        return
    
    node_profile = kobj.bundle.validate_contents(NodeProfile)
    
    # looking for event provider of nodes
    if KoiNetNode not in node_profile.provides.event:
        return
    
    logger.debug("Identified a coordinator!")
    logger.debug("Proposing new edge")
    
    # queued for processing
    processor.handle(bundle=generate_edge_bundle(
        source=kobj.rid,
        target=node.identity.rid,
        edge_type=EdgeType.WEBHOOK,
        rid_types=[KoiNetNode]
    ))
    
    logger.debug("Catching up on network state")
    
    rid_payload = processor.network.request_handler.fetch_rids(kobj.rid, rid_types=[KoiNetNode])
        
    rids = [
        rid for rid in rid_payload.rids 
        if rid != processor.identity.rid and 
        not processor.cache.exists(rid)
    ]
    
    bundle_payload = processor.network.request_handler.fetch_bundles(kobj.rid, rids=rids)
    
    for bundle in bundle_payload.bundles:
        # marked as external since we are handling RIDs from another node
        # will fetch remotely instead of checking local cache
        processor.handle(bundle=bundle, source=KnowledgeSource.External)
    logger.debug("Done")
        

@node.processor.register_handler(HandlerType.Manifest) #, rid_types=[GoogleDoc, GoogleSlides, GoogleSheets])
def custom_manifest_handler(processor: ProcessorInterface, kobj: KnowledgeObject):
    # if type(kobj.rid) in [GoogleDoc, GoogleSlides, GoogleSheets]:
    #     logger.debug("Skipping Google Workspace App manifest handling")
        # return
    
    prev_bundle = processor.cache.read(kobj.rid)

    if prev_bundle:
        if kobj.manifest.sha256_hash == prev_bundle.manifest.sha256_hash:
            logger.debug("Hash of incoming manifest is same as existing knowledge, ignoring")
            return STOP_CHAIN
        if kobj.manifest.timestamp <= prev_bundle.manifest.timestamp:
            logger.debug("Timestamp of incoming manifest is the same or older than existing knowledge, ignoring")
            return STOP_CHAIN
        
        logger.debug("RID previously known to me, labeling as 'UPDATE'")
        kobj.normalized_event_type = EventType.UPDATE

    else:
        logger.debug("RID previously unknown to me, labeling as 'NEW'")
        kobj.normalized_event_type = EventType.NEW
        
    return kobj

# def get change

@node.processor.register_handler(HandlerType.Bundle, rid_types=[GoogleDoc, GoogleSlides, GoogleSheets])
def custom_bundle_handler(processor: ProcessorInterface, kobj: KnowledgeObject):
    assert type(kobj.rid) in [GoogleDoc, GoogleSlides, GoogleSheets]
    # logger.debug(kobj.rid)
    # logger.debug(kobj.rid.namespace)
    # logger.debug(kobj.rid.reference)
    prev_bundle = processor.cache.read(kobj.rid)
    print(node.config.gdrive.start_page_token)
    print(node.config.gdrive.next_page_token)
    print()
    
    # change_ids = []
    results = get_change_results(node.config.gdrive.drive_id, node.config.gdrive.start_page_token)
    changes = results.get('changes')
    change_dict = {}
    for change in changes:
        if change['changeType'] == 'file':
            change_dict[change['fileId']] = change
    
    change_ids = change_dict.keys()
    new_start_page_token = results.get('newStartPageToken')
    # change = None
    if is_file_deleted(kobj.rid):
        kobj.normalized_event_type = EventType.FORGET
    else:
        if prev_bundle:
            # prev_bundle.manifest.timestamp
            if prev_bundle.rid.reference in change_ids:
                logger.debug("Incoming note has been changed more recently!")
                logger.debug(f"Page Token Changed from {node.config.gdrive.start_page_token} to {new_start_page_token}")
                # kobj.normalized_event_type = get_FUN_event_type(change_dict, kobj)
                kobj.normalized_event_type = get_FUN_event_type(change_dict, kobj.rid)
            else:
                logger.debug("Incoming note is not newer")
                return STOP_CHAIN
        else:
            logger.debug("Incoming note is previously unknown to me")
            if kobj.rid.reference in change_ids:
                # kobj.normalized_event_type = get_FUN_event_type(change_dict, kobj)
                kobj.normalized_event_type = get_FUN_event_type(change_dict, kobj.rid)
        
    namespace = kobj.rid.namespace
    reference = kobj.rid.reference

    logger.debug("Retrieving full content...")
    if namespace == GoogleDriveFolder.namespace:
        logger.debug(f"Retrieving: {folderType}")
        data = drive_service.files().get(fileId=reference, supportsAllDrives=True).google_object(folderType).execute()
    elif namespace == GoogleDoc.namespace:
        logger.debug(f"Retrieving: {docsType}")
        data = doc_service.documents().get(documentId=reference).execute()
    elif namespace == GoogleSheets.namespace:
        logger.debug(f"Retrieving: {sheetsType}")
        data = sheet_service.spreadsheets().get(spreadsheetId=reference).execute()
    elif namespace == GoogleSlides.namespace:
        logger.debug(f"Retrieving: {presentationType}")
        data = slides_service.presentations().get(presentationId=reference).execute()
    else:
        data = drive_service.files().get(fileId=reference, supportsAllDrives=True).execute()

    if not data:
        logger.debug("Failed.")
        return STOP_CHAIN

    logger.debug("Done.")
    
    full_note_bundle = Bundle.generate(
        rid=kobj.rid,
        contents=data
    )

    full_note_bundle.contents['page_token'] = new_start_page_token
    
    kobj.manifest = full_note_bundle.manifest
    kobj.contents = full_note_bundle.contents
    
    return kobj

# @node.processor.register_handler(HandlerType.Network, rid_types=[GoogleDoc, GoogleSlides, GoogleSheets])
# def pagination(processor: ProcessorInterface, kobj: KnowledgeObject):
#     if kobj.normalized_event_type != EventType.NEW: 
#         results = drive_service.changes().list(
#             driveId=node.config.gdrive.drive_id, 
#             includeItemsFromAllDrives=True, 
#             supportsAllDrives=True,
#             pageToken=node.config.gdrive.start_page_token,
#             includeRemoved=True,
#             spaces='drive'
#         ).execute()
#         # node.config.gdrive.start_page_token = results.get('newStartPageToken')
#     logger.debug("Done")


# @node.processor.register_handler(HandlerType.RID, rid_types=[GoogleDoc, GoogleSlides, GoogleSheets])
# def update_last_processed_ts(processor: ProcessorInterface, kobj: KnowledgeObject):
#     # rid = kobj.rid
#     dt = kobj.bundle.manifest.timestamp
#     ts = dt.timestamp()
    
#     global LAST_PROCESSED_TS
#     print(ts < LAST_PROCESSED_TS.timestamp())

#     if ts < LAST_PROCESSED_TS: 
#         return
    
#     LAST_PROCESSED_TS = ts
    
#     with open("state.json", "w") as f:
#         json.dump({"last_processed_ts": LAST_PROCESSED_TS}, f)

# @node.processor.register_handler(HandlerType.RID, rid_types=[GoogleDoc, GoogleSlides, GoogleSheets])
# def update_last_processed_ts(processor: ProcessorInterface, kobj: KnowledgeObject):
#     file_id = kobj.rid.reference
#     file = drive_service.files().get(fileId=file_id, fields='modifiedTime', supportsAllDrives=True).execute()
#     modified_time_str = file.get('modifiedTime')
#     modified_time_dt = datetime.fromisoformat(modified_time_str[:-1]) if modified_time_str.endswith('Z') else datetime.fromisoformat(modified_time_str)
#     # formated_modified_time_str = str(modified_time_dt)

#     if modified_time_dt.timestamp() < float(node.config.gdrive.last_processed_ts):
#         return
    
#     node.config.gdrive.last_processed_ts = modified_time_dt.timestamp()
#     node.config.save_to_yaml()