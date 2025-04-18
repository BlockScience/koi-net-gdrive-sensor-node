import time, logging
from rich.logging import RichHandler
from koi_net import NodeInterface
from koi_net.processor.knowledge_object import KnowledgeSource
from koi_net.protocol.node import NodeProfile, NodeType
from pprint import pprint

from ..utils.functions import bundle_list


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
    first_contact=coordinator_url
)


if __name__ == "__main__":
    node.start()

    query = f"'1OwnHDuusN9ZiFgUzmttR-cLDbU0sS4z3' in parents"
    for bundle in bundle_list(query):
        node.processor.handle(bundle=bundle, source=KnowledgeSource.Internal)
    # for event in event_filter(bundles):
    #     # node.processor.handle(event=event, source=KnowledgeSource.Internal)
    #     node.processor.handle(event=event, source=KnowledgeSource.Internal)

    try:
        while True:
            for event in node.network.poll_neighbors():
                node.processor.handle(event=event, source=KnowledgeSource.External)
            node.processor.flush_kobj_queue()
            
            time.sleep(5)
            
    finally:
        node.stop()