import time, logging
from rich.logging import RichHandler
from koi_net import NodeInterface
from koi_net.processor.knowledge_object import KnowledgeSource
from koi_net.protocol.node import NodeProfile, NodeType
from koi_net.protocol.api_models import FetchBundles
from koi_net.network.request_handler import RequestHandler
from koi_net.protocol.api_models import EventsPayload
from koi_net.protocol.consts import FETCH_BUNDLES_PATH, BROADCAST_EVENTS_PATH
from pprint import pprint

from ..utils.functions import bundle_list, event_filter, rid_filter

from .. import SENSOR


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[RichHandler()]
)

logger = logging.getLogger(__name__)


coordinator_url = "http://127.0.0.1:8000/koi-net"

node = NodeInterface(
    name="partial",
    profile=NodeProfile(
        node_type=NodeType.PARTIAL,
    ),
    cache_directory_path=f"{SENSOR}/net/metadata/io_partial_node_rid_cache",
    identity_file_path=f"{SENSOR}/net/metadata/io_partial_node_identity.json",
    first_contact=coordinator_url
)

if __name__ == "__main__":
    node.start()

    full_node_url = 'http://127.0.0.1:5000/koi-net'
    driveId = '0AJflT9JpikpnUk9PVA'
    query = f"\'{driveId}\' in parents"
    bundles = bundle_list(query=query, driveId=driveId)
    events_payload = EventsPayload(events = event_filter(bundles))
    req_handler = RequestHandler(cache=node.network.cache, graph=node.network.graph)
    req_handler.broadcast_events(
        url = full_node_url, 
        req = events_payload
    )

    try:
        while True:
            for event in node.network.poll_neighbors():
                node.processor.handle(event=event, source=KnowledgeSource.External)
            node.processor.flush_kobj_queue()
            
            time.sleep(5)
            
    finally:
        node.stop()
