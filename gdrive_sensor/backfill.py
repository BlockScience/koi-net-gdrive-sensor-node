import logging
import asyncio
from .utils.functions import bundle_list
from .core import node

# ToDo: trim down bundle list to GoogleDrive File such that handler derefs specific file types

logger = logging.getLogger(__name__)

async def backfill(driveId='0AJflT9JpikpnUk9PVA'):
    query = f"\'{driveId}\' in parents"
    bundles = bundle_list(query=query, driveId=driveId)
    
    logger.debug(f"Found {len(bundles)} in {driveId}")

    for bundle in bundles:
        node.processor.handle(bundle=bundle)
        
if __name__ == "__main__":
    node.start()
    asyncio.run(
        backfill()
    )
    node.stop()