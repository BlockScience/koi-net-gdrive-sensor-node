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
    cache_directory_path=f"{SENSOR}/node/egress_partial_node_rid_cache",
    identity_file_path=f"{SENSOR}/node/egress_partial_node_identity.json",
    first_contact=coordinator_url
)
node.network.graph




if __name__ == "__main__":
    node.start()

    # remote_bundle = node.network.fetch_remote_bundle("orn:koi-net.node:partial+a3bf5d9e-6b16-454b-bdf4-e67490d4ce94")
    # print(remote_bundle)

    # try:
    #     while True:
    #         for event in node.network.poll_neighbors():
    #             node.processor.handle(event=event, source=KnowledgeSource.External)
    #         node.processor.flush_kobj_queue()
            
    #         time.sleep(5)
            
    # finally:
    #     node.stop()

    # url = lambda ep: f'http://127.0.0.1:5000/{ep}'
    url = 'http://127.0.0.1:5000/'
    driveId = '0AJflT9JpikpnUk9PVA'
    query = f"\'{driveId}\' in parents"
    bundles = bundle_list(query=query, driveId=driveId)
    events_payload = EventsPayload(events = event_filter(bundles))
    req_handler = RequestHandler(cache=node.network.cache, graph=node.network.graph)
    req_handler.broadcast_events(
        url = url, 
        req = events_payload
    )
    node.stop()

    # try:
    #     while True:
    #         # query = f"'1OwnHDuusN9ZiFgUzmttR-cLDbU0sS4z3' in parents"
    #         driveId = '0AJflT9JpikpnUk9PVA'
    #         query = f"\'{driveId}\' in parents"
    #         bundles = bundle_list(query=query, driveId=driveId)
    #         # bundles = bundle_list(query)
    #         # rid_obj: GoogleDoc = GoogleDrive.from_reference(item['id']).google_object(item['mimeType'])
    #         fetch_bundles = FetchBundles(rids = rid_filter(bundles))
    #         req_handler = RequestHandler(cache=node.network.cache, graph=node.network.graph)
    #         url = lambda ep: f'http://127.0.0.1:5000/{ep}'
    #         # print(fetch_bundles)
    #         # print(type(fetch_bundles))
    #         # exit()
    #         req_handler.fetch_bundles(
    #             # rid = "orn:koi-net.node:partial+a3bf5d9e-6b16-454b-bdf4-e67490d4ce94",
    #             url = url(FETCH_BUNDLES_PATH),
    #             req = fetch_bundles
    #         )
    #         node.processor.flush_kobj_queue()
    #         time.sleep(5)
    # finally:
    #     node.stop()
