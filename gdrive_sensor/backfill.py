import logging
import asyncio
from .utils.functions import bundle_list
from .core import node
from .utils.connection import drive_service
from gdrive_sensor.utils.functions import fetch_start_page_token, fetch_changes
from pprint import pprint

# ToDo: trim down bundle list to GoogleDrive File such that handler derefs specific file types

logger = logging.getLogger(__name__)

page_token = None
async def backfill(driveId=node.config.gdrive.drive_id):
    query = f"\'{driveId}\' in parents"
    start_token = '24'
    # start_token = fetch_start_page_token(
    #         service=drive_service, drive_id=SHARED_DRIVE_ID
    # )
    # change_token = fetch_changes(
    #     service=drive_service, drive_id=SHARED_DRIVE_ID, saved_start_page_token=start_token
    # )
    bundles = bundle_list(query=query, driveId=driveId, pageToken=page_token)
    
    # print('hI')
    # bundles = bundle_list(driveId=driveId, pageToken=start_token)
    # pprint(bundles)
    logger.debug(f"Found {len(bundles)} in {driveId}")

    for bundle in bundles:
        bundle.contents['start_token'] = start_token
        bundle.contents['change_token'] = fetch_changes(
            service=drive_service, drive_id=driveId, saved_start_page_token=start_token
        )
        node.processor.handle(bundle=bundle)
        
if __name__ == "__main__":
    node.start()
    asyncio.run(
        backfill()
    )
    node.stop()