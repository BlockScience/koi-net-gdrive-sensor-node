import logging
import asyncio
from .utils.functions import bundle_list
from .core import node
from .utils.connection import drive_service
from gdrive_sensor.utils.functions import get_new_start_page_token, fetch_start_page_token, fetch_changes
from koi_net.processor.knowledge_object import KnowledgeSource
from koi_net.protocol.event import EventType
from gdrive_sensor.utils.types import GoogleWorkspaceApp
from pprint import pprint

# ToDo: trim down bundle list to GoogleDrive File such that handler derefs specific file types

logger = logging.getLogger(__name__)

# page_token = None
# async def backfill(driveId=node.config.gdrive.drive_id, start_token='67'):
#     query = f"\'{driveId}\' in parents"
    
#     changes, new_start_token = fetch_changes(
#         service=drive_service, drive_id=node.config.gdrive.drive_id, saved_start_page_token=start_token
#     )
#     rid_changes = {}
#     for change in changes:
#         rid_obj = GoogleWorkspaceApp.from_reference(change['fileId']).google_object(change['file']['mimeType'])
#         rid_changes[str(rid_obj)] = change
#     # print()
#     # print(start_token)
#     # print()
#     # print(change_token)
#     # exit()
#     bundles = bundle_list(query=query, driveId=driveId)
#     logger.debug(f"Found {len(bundles)} in {driveId}")

#     for bundle in bundles:
#         bundle.contents['page_token'] = new_start_token
#         rid_str = str(bundle.manifest.rid)
#         if rid_str in rid_changes.keys():
#             change = rid_changes[rid_str]
#             if change['removed'] is False:
#                 node.processor.handle(bundle=bundle, event_type=EventType.UPDATE)
#             else:
#                 node.processor.handle(bundle=bundle, event_type=EventType.FORGET)
#         else:
#             node.processor.handle(bundle=bundle, event_type=EventType.NEW)

async def backfill(driveId=node.config.gdrive.drive_id, start_token='67'):
    query = f"\'{driveId}\' in parents"
    bundles = bundle_list(query=query, driveId=driveId)
    logger.debug(f"Found {len(bundles)} in {driveId}")
    current_token = get_new_start_page_token(driveId, start_token)
    # print(current_token)
    # exit()

    for bundle in bundles:
        bundle.contents['start_token'] = start_token
        bundle.contents['current_token'] = current_token
        node.processor.handle(bundle=bundle)
           
if __name__ == "__main__":
    node.start()
    asyncio.run(
        backfill()
    )
    node.stop()