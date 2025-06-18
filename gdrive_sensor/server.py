import logging, asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, Request

from koi_net.protocol.event import EventType
from koi_net.processor.knowledge_object import KnowledgeSource
from koi_net.protocol.api_models import (
    PollEvents,
    FetchRids,
    FetchManifests,
    FetchBundles,
    EventsPayload,
    RidsPayload,
    ManifestsPayload,
    BundlesPayload
)
from koi_net.protocol.consts import (
    BROADCAST_EVENTS_PATH,
    POLL_EVENTS_PATH,
    FETCH_RIDS_PATH,
    FETCH_MANIFESTS_PATH,
    FETCH_BUNDLES_PATH
)
from .core import node
from .backfill import backfill
from .utils.types import GoogleWorkspaceApp
from .utils.connection import drive_service
from .utils.functions.bundle import bundle_item
from pprint import pprint


logger = logging.getLogger(__name__)


async def backfill_loop():
    while True:
        node.config.gdrive.start_page_token, node.config.gdrive.next_page_token = await backfill(
            driveId = node.config.gdrive.drive_id, 
            start_page_token = node.config.gdrive.start_page_token, 
            next_page_token = node.config.gdrive.next_page_token
        )
        # await asyncio.sleep(30)
        # await asyncio.sleep(600)
        await asyncio.sleep(node.config.gdrive.subscription_window)
        
@asynccontextmanager
async def lifespan(app: FastAPI):    
    node.start()
    asyncio.create_task(
        backfill_loop()
    )
    
    yield
    node.stop()

app = FastAPI(
    lifespan=lifespan, 
    root_path="/koi-net",
    title="KOI-net Protocol API",
    version="1.0.0"
)

listener = FastAPI(
    title="gdrive_listener",
    version="1.0.0"
)


koi_net_router = APIRouter(
    prefix="/koi-net"
)

@listener.post('/google-drive-listener')
async def notifications(request: Request):
    # Handle the notification
    fileId = request.headers['X-Goog-Resource-Uri'].split('?')[0].rsplit('/', 1)[-1]
    print("Subscribed to fileId:", fileId)
    print("Received notification:")
    pprint(dict(request.headers))
    
    state = request.headers['X-Goog-Resource-State']
    if state != 'sync':
        file = drive_service.files().get(fileId=fileId, supportsAllDrives=True).execute()
        mimeType = file.get('mimeType')
        rid_obj = GoogleWorkspaceApp.from_reference(fileId).google_object(mimeType)
        if state in ['remove', 'trash']:
            print(f"{state}: from source FORGET")
            node.processor.handle(rid=rid_obj, event_type=EventType.FORGET)
        elif state == 'update':
            if node.cache.exists(rid_obj) == False:
                print(f"{state}: from source UPDATE & NOT cached")
                bundle = bundle_item(file)
                bundle.contents['page_token'] = node.config.gdrive.start_page_token
                node.processor.handle(bundle=bundle)
            else:
                print(f"{state}: from source UPDATE & Cached")
                bundle = node.cache.read(rid_obj)
                node.config.gdrive.start_page_token = bundle.contents['page_token']
        elif state in ['add', 'untrash']:
            bundle = None
            if not node.cache.exists(rid_obj):
                print(f"{state}: External")
                bundle = bundle_item(file)
            else:
                print(f"{state}: Internal")
                bundle = node.cache.read(rid_obj)
            node.processor.handle(bundle=bundle)
    
    if request.body:
        print("Received data:", await request.body())
    else:
        print("No data received.")
    if request.headers.get('content-type') == 'application/json':
        json_data = await request.json()
        print("Received json:", json_data)
    else:
        print("Received non-JSON data.")
    
    return {"message": "No content"}, 204  # Respond with no content

@koi_net_router.post(BROADCAST_EVENTS_PATH)
def broadcast_events(req: EventsPayload):
    logger.info(f"Request to {BROADCAST_EVENTS_PATH}, received {len(req.events)} event(s)")
    for event in req.events:
        logger.info(f"{event!r}")
        node.processor.handle(event=event, source=KnowledgeSource.External)

@koi_net_router.post(POLL_EVENTS_PATH)
def poll_events(req: PollEvents) -> EventsPayload:
    logger.info(f"Request to {POLL_EVENTS_PATH}")
    events = node.network.flush_poll_queue(req.rid)
    return EventsPayload(events=events)

@koi_net_router.post(FETCH_RIDS_PATH)
def fetch_rids(req: FetchRids) -> RidsPayload:
    return node.network.response_handler.fetch_rids(req)

@koi_net_router.post(FETCH_MANIFESTS_PATH)
def fetch_manifests(req: FetchManifests) -> ManifestsPayload:
    return node.network.response_handler.fetch_manifests(req)

@koi_net_router.post(FETCH_BUNDLES_PATH)
def fetch_bundles(req: FetchBundles) -> BundlesPayload:
    return node.network.response_handler.fetch_bundles(req)


app.include_router(koi_net_router)