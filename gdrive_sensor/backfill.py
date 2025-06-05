import logging
import asyncio
from .utils.functions.bundle import bundle_list
from .utils.functions.api import get_change_results
from .core import node
from .utils.connection import drive_service
from gdrive_sensor.utils.functions.events import is_file_deleted, get_FUN_event_type#, get_FUN_event_type # get_new_start_page_token, fetch_start_page_token, fetch_changes
from koi_net.processor.knowledge_object import KnowledgeSource, KnowledgeObject
from koi_net.protocol.event import EventType #, Event
# from gdrive_sensor.utils.types import GoogleWorkspaceApp
# from gdrive_sensor import START_PAGE_TOKEN, NEXT_PAGE_TOKEN
# from pprint import pprint

# ToDo: trim down bundle list to GoogleDrive File such that handler derefs specific file types

logger = logging.getLogger(__name__)

# async def backfill(
#         driveId: str = node.config.gdrive.drive_id, 
#         start_page_token: str = node.config.gdrive.start_page_token, 
#         next_page_token: str = node.config.gdrive.next_page_token
#     ):  
#     results = get_change_results(driveId, start_page_token)
#     changes = results.get('changes')

#     # exit()
#     change_dict = {}
#     # pprint(changes)
#     # exit()
#     for change in changes:
#         if change['changeType'] == 'file':
#             change_dict[change['fileId']] = change
    
#     bundles = bundle_list(driveId=driveId)
#     logger.debug(f"Found {len(bundles)} in {driveId}")
#     # for bundle in bundles:
#     #     event_type=None
#     #     if is_file_deleted(bundle.manifest.rid):
#     #         event_type=EventType.FORGET
#     #     else:
#     #         if bundle.manifest.rid.reference in change_dict.keys(): # changes might include deleted file 
#     #             event_type=get_FUN_event_type(change_dict, bundle.manifest.rid)
#     #     # print(event_type)
#     #     # kobj = KnowledgeObject.from_bundle(bundle, event_type, source=KnowledgeSource.Internal)
#     #     node.processor.handle(bundle=bundle, event_type=event_type)

#     for bundle in bundles:
#         # rid_str = str(bundle.manifest.rid)
#         bundle.contents['page_token'] = start_page_token
#         if is_file_deleted(bundle.manifest.rid):
#             event_type=EventType.FORGET
#         else:
#             if bundle.manifest.rid in change_dict.keys():
#                 change = change_dict[bundle.manifest.rid]
#                 if change['removed'] is False:
#                     event_type=EventType.UPDATE
#                 else:
#                     event_type=EventType.FORGET
#             else:
#                 event_type=EventType.NEW
                
#         node.processor.handle(bundle=bundle, event_type=event_type)

#     start_page_token = results.get('newStartPageToken')
#     next_page_token = results.get('nextPageToken')

#     return start_page_token, next_page_token

async def backfill(
        driveId: str = node.config.gdrive.drive_id, 
        start_page_token: str = node.config.gdrive.start_page_token, 
        next_page_token: str = node.config.gdrive.next_page_token
    ):
    bundles = bundle_list(driveId=driveId)
    logger.debug(f"Found {len(bundles)} in {driveId}")

    results = get_change_results(driveId, start_page_token)

    for bundle in bundles:
        bundle.contents['page_token'] = start_page_token
        node.processor.handle(bundle=bundle)

    start_page_token = results.get('newStartPageToken')
    next_page_token = results.get('nextPageToken')

    return start_page_token, next_page_token
           
if __name__ == "__main__":
    node.start()
    asyncio.run(backfill())
    node.stop()