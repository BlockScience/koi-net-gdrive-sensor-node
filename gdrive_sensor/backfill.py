import logging, asyncio
from gdrive_sensor.core import node
from gdrive_sensor.utils.functions.bundle import bundle_list
from gdrive_sensor.utils.functions.api import get_change_results
from gdrive_sensor.utils.functions.events import is_file_deleted
from gdrive_sensor.utils.types import GoogleDriveFolder, GoogleDoc, GoogleSlides, GoogleSheets
from gdrive_sensor.utils.types import folderType, docsType, sheetsType, presentationType
from gdrive_sensor.utils.connection import drive_service, doc_service, sheet_service, slides_service
from koi_net.protocol.event import EventType #, Event
from rid_lib.ext import Bundle
# from gdrive_sensor.utils.types import GoogleWorkspaceApp
# from gdrive_sensor import START_PAGE_TOKEN, NEXT_PAGE_TOKEN
# from pprint import pprint

# ToDo: trim down bundle list to GoogleDrive File such that handler derefs specific file types

logger = logging.getLogger(__name__)

async def backfill(
        driveId: str = node.config.gdrive.drive_id, 
        start_page_token: str = node.config.gdrive.start_page_token, 
        next_page_token: str = node.config.gdrive.next_page_token
    ):

    bundles = bundle_list(driveId=driveId)
    logger.debug(f"Found {len(bundles)} in {driveId}")

    print(start_page_token)
    print(next_page_token)

    results = get_change_results(driveId, start_page_token)
    changes = results.get('changes')
    new_start_page_token = results.get('newStartPageToken')
    next_page_token = results.get('nextPageToken')
    change_dict = {}
    for change in changes:
        if change['changeType'] == 'file':
            change_dict[change['fileId']] = change
    change_ids = change_dict.keys()

    for bundle in bundles:
        rid_obj = bundle.manifest.rid
        prev_bundle = node.processor.cache.read(rid_obj)
        # NOTE: try to handle is_file_deleted in bundling process
        if is_file_deleted(rid_obj): # bundle is cached but trashed in gdrive
            node.processor.handle(rid=rid_obj, event_type=EventType.FORGET)
        else:
            if prev_bundle:
                logger.debug("Bundle is cached:")
                if prev_bundle.rid.reference in change_ids: # bundle is cached but changed
                    logger.debug("Incoming item has been changed more recently!")
                    logger.debug(f"Page Token Changed from {node.config.gdrive.start_page_token} to {new_start_page_token}: Retrieving full content...")
                    if type(rid_obj) == GoogleDriveFolder:
                        logger.debug(f"Retrieving: {folderType}")
                        data = drive_service.files().get(fileId=rid_obj.reference, supportsAllDrives=True).google_object(folderType).execute()
                    elif type(rid_obj) == GoogleDoc:
                        logger.debug(f"Retrieving: {docsType}")
                        data = doc_service.documents().get(documentId=rid_obj.reference).execute()
                    elif type(rid_obj) == GoogleSheets:
                        logger.debug(f"Retrieving: {sheetsType}")
                        data = sheet_service.spreadsheets().get(spreadsheetId=rid_obj.reference).execute()
                    elif type(rid_obj) == GoogleSlides:
                        logger.debug(f"Retrieving: {presentationType}")
                        data = slides_service.presentations().get(presentationId=rid_obj.reference).execute()
                    else:
                        data = drive_service.files().get(fileId=rid_obj.reference, supportsAllDrives=True).execute()

                    full_bundle = Bundle.generate(
                        rid=rid_obj,
                        contents=data
                    )
                    full_bundle.contents['page_token'] = start_page_token
                    node.processor.handle(bundle=full_bundle)
                else:
                    logger.debug("Incoming note is not newer")
            else:
                logger.debug("Bundle is NEW / not cached")
                bundle.contents['page_token'] = start_page_token
                node.processor.handle(bundle=bundle)

    return new_start_page_token, next_page_token
           
if __name__ == "__main__":
    node.start()
    asyncio.run(backfill())
    node.stop()