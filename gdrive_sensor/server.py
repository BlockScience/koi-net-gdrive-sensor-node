import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
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
from gdrive_sensor import START_PAGE_TOKEN, NEXT_PAGE_TOKEN


logger = logging.getLogger(__name__)

def reset_backfill_parameters():
    global START_PAGE_TOKEN, NEXT_PAGE_TOKEN
    node.config.gdrive.start_page_token = START_PAGE_TOKEN
    node.config.gdrive.next_page_token = NEXT_PAGE_TOKEN

async def backfill_loop():
    global START_PAGE_TOKEN, NEXT_PAGE_TOKEN
    while True:
        START_PAGE_TOKEN, NEXT_PAGE_TOKEN = await backfill()
        # await asyncio.sleep(20)
        await asyncio.sleep(600)
        reset_backfill_parameters()
        

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


koi_net_router = APIRouter(
    prefix="/koi-net"
)

@koi_net_router.post(BROADCAST_EVENTS_PATH)
def broadcast_events(req: EventsPayload):
    logger.info(f"Request to {BROADCAST_EVENTS_PATH}, received {len(req.events)} event(s)")
    for event in req.events:
        logger.info(f"{event!r}")
        node.processor.handle(event=event, source=KnowledgeSource.External)
        # node.processor.handle(event=event, source=KnowledgeSource.Internal)
    

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