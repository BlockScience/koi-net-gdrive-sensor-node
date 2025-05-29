import logging
import asyncio
from .utils.functions import bundle_list, get_FUN_event_type, is_file_deleted
from .core import node
from .utils.connection import drive_service
# from gdrive_sensor.utils.functions import get_new_start_page_token, fetch_start_page_token, fetch_changes
from koi_net.processor.knowledge_object import KnowledgeSource, KnowledgeObject
from koi_net.protocol.event import EventType, Event
from gdrive_sensor.utils.types import GoogleWorkspaceApp
from gdrive_sensor import START_PAGE_TOKEN, NEXT_PAGE_TOKEN
from pprint import pprint

# ToDo: trim down bundle list to GoogleDrive File such that handler derefs specific file types

logger = logging.getLogger(__name__)

# async def backfill(driveId=node.config.gdrive.drive_id, start_token='67'):    
#     results = drive_service.changes().list(
#         driveId=node.config.gdrive.drive_id, 
#         includeItemsFromAllDrives=True, 
#         supportsAllDrives=True,
#         pageToken=node.config.gdrive.start_page_token,
#         includeRemoved=True,
#         spaces='drive'
#     ).execute()
#     changes = results.get('changes')
#     change_dict = {}
#     # pprint(changes)
#     # exit()
#     for change in changes:
#         if change['changeType'] == 'file':
#             change_dict[change['fileId']] = change
    
#     bundles = bundle_list(driveId=driveId)
#     logger.debug(f"Found {len(bundles)} in {driveId}")
#     for bundle in bundles:
#         event_type=None
#         if is_file_deleted(bundle.manifest.rid):
#             event_type=EventType.FORGET
#         else:
#             if bundle.manifest.rid.reference in change_dict.keys(): # changes might include deleted file 
#                 event_type=get_FUN_event_type(change_dict, bundle.manifest.rid)
#         # print(event_type)
#         kobj = KnowledgeObject.from_bundle(bundle, event_type, source=KnowledgeSource.Internal)
#         node.processor.handle(kobj=kobj)
#     # for bundle in bundles:
#     #     # rid_str = str(bundle.manifest.rid)
#     #     if is_file_deleted(bundle.manifest.rid):
#     #         node.processor.handle(bundle=bundle, event_type=EventType.FORGET)
#     #     else:
#     #         if bundle.manifest.rid in change_dict.keys():
#     #             change = change_dict[bundle.manifest.rid]
#     #             if change['removed'] is False:
#     #                 node.processor.handle(bundle=bundle, event_type=EventType.UPDATE)
#     #             else:
#     #                 node.processor.handle(bundle=bundle, event_type=EventType.FORGET)
#     #         else:
#     #             node.processor.handle(bundle=bundle, event_type=EventType.NEW)

# import contextvars
# start_page_token_var = contextvars.ContextVar('start_page_token')
# next_page_token_var = contextvars.ContextVar('next_page_token')
# start_page_token_var.set(node.config.gdrive.start_page_token)
# next_page_token_var.set(node.config.gdrive.next_page_token)
# ctx = contextvars.copy_context()

async def backfill(
        driveId: str = node.config.gdrive.drive_id, 
        start_page_token: str = node.config.gdrive.start_page_token, 
        next_page_token: str = node.config.gdrive.next_page_token
    ):
    bundles = bundle_list(driveId=driveId)
    logger.debug(f"Found {len(bundles)} in {driveId}")

    for bundle in bundles:
        bundle.contents['page_token'] = start_page_token
        node.processor.handle(bundle=bundle)
    
    results = drive_service.changes().list(
        driveId=driveId, 
        includeItemsFromAllDrives=True, 
        supportsAllDrives=True,
        pageToken=start_page_token,
        includeRemoved=True,
        spaces='drive'
    ).execute()

    start_page_token = results.get('newStartPageToken')
    next_page_token = results.get('nextPageToken')

    return start_page_token, next_page_token
           
# if __name__ == "__main__":
    # node.start()
    # with asyncio.Runner() as runner:
    #     # node.config.gdrive.start_page_token, node.config.gdrive.next_page_token = runner.run(coro=backfill(), context=ctx)
    #     # start_page_token_var.set(node.config.gdrive.start_page_token)
    #     # next_page_token_var.set(node.config.gdrive.next_page_token)
    #     # runner.run(coro=backfill(), context=ctx)
    #     # runner.run(coro=backfill(), context=ctx)

    #     runner.run(coro=lambda: print('hello'))
    #     runner.run(coro=lambda: print('hello'))
    #     exit()
    #     # runner.run(coro=backfill(), context=ctx)
    # node.stop()