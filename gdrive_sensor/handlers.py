import logging, json
from multiprocessing import process
from koi_net.processor.handler import HandlerType, STOP_CHAIN
from koi_net.processor.knowledge_object import KnowledgeSource, KnowledgeObject
from koi_net.processor.interface import ProcessorInterface
from koi_net.protocol.event import EventType
from koi_net.protocol.edge import EdgeType
from koi_net.protocol.node import NodeProfile
from koi_net.protocol.helpers import generate_edge_bundle
from rid_lib.ext import Bundle
from rid_lib.types import KoiNetNode
from gdrive_sensor.utils.functions import handle_bundle_changes, fetch_changes

from .utils.types import GoogleWorkspaceApp, GoogleDriveFolder, GoogleDoc, GoogleSlides, GoogleSheets
from .utils.types import folderType, docsType, sheetsType, presentationType
from .utils.connection import drive_service, doc_service, sheet_service, slides_service
from .core import node
from pprint import pprint
# from .config import LAST_PROCESSED_TSe

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


@node.processor.register_handler(HandlerType.Manifest)
def custom_manifest_handler(processor: ProcessorInterface, kobj: KnowledgeObject):
    if type(kobj.rid) == GoogleWorkspaceApp:
        logger.debug("Skipping Google Workspace App manifest handling")
        return
    
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


@node.processor.register_handler(HandlerType.Bundle, rid_types=[GoogleWorkspaceApp])
def custom_bundle_handler(processor: ProcessorInterface, kobj: KnowledgeObject):
    assert type(kobj.rid) == GoogleWorkspaceApp
    
    prev_bundle = processor.cache.read(kobj.rid)
    # pprint(prev_bundle)
    start_token = prev_bundle.contents['start_token']
    change_token = prev_bundle.contents['change_token']
    # change_token = prev_bundle.contents['change_token'] = fetch_changes(
    #     service=drive_service, drive_id=SHARED_DRIVE_ID, saved_start_page_token=start_token
    # )
    print()
    print(start_token)
    print()
    print(change_token)
    # exit()


    # print('bye')
    logger.debug("bye")
    # if prev_bundle:
    if change_token != start_token:
        # prevChangedAt = prev_bundle.contents["lastChangedAt"]
        # currChangedAt = kobj.contents["lastChangedAt"]
        logger.debug("Incoming note has been changed more recently!")
        # if currChangedAt > prevChangedAt:
        if change_token > start_token:
            logger.debug(f"Changed at {change_token} -> {start_token}")
            file_id = kobj.rid.reference()
            changed_bundle = handle_bundle_changes(id=file_id, driveId=None, pageToken=change_token)[0]
            kobj.from_bundle(changed_bundle)
            kobj.normalized_event_type = EventType.UPDATE      
        else:
            logger.debug("Incoming note is not newer")
            return STOP_CHAIN
        
    else:
        logger.debug("Incoming note is previously unknown to me")
        kobj.normalized_event_type = EventType.NEW
        
    # logger.debug("Retrieving full note...")
    # data = hackmd_api.request(f"/notes/{kobj.rid.note_id}")
    
    namespace = prev_bundle.rid.namespace
    reference = prev_bundle.rid.reference
    # logger.debug("reference")

    logger.debug("Retrieving full content...")
    if namespace == GoogleDriveFolder.namespace:
        logger.debug(f"Retrieving: {folderType}")
        data = drive_service.files().get(fileId=reference).google_object(folderType).execute()
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
        data = drive_service.files().get(fileId=reference).execute()

    if not data:
        logger.debug("Failed.")
        return STOP_CHAIN

    logger.debug("Done.")
    
    full_note_bundle = Bundle.generate(
        rid=kobj.rid,
        contents=data
    )
    
    kobj.manifest = full_note_bundle.manifest
    kobj.contents = full_note_bundle.contents
    
    return kobj

@node.processor.register_handler(HandlerType.RID, rid_types=[GoogleWorkspaceApp])
def update_last_processed_ts(processor: ProcessorInterface, kobj: KnowledgeObject):
    rid: GoogleWorkspaceApp = kobj.rid
    ts = float(rid.ts)
    
    global LAST_PROCESSED_TS
    if ts < LAST_PROCESSED_TS: 
        return
    
    LAST_PROCESSED_TS = ts
    
    with open("state.json", "w") as f:
        json.dump({"last_processed_ts": LAST_PROCESSED_TS}, f)