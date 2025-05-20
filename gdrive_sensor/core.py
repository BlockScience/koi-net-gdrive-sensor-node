import logging
from .utils.types import GoogleWorkspaceApp
from koi_net import NodeInterface
from koi_net.protocol.node import NodeProfile, NodeType, NodeProvides
from koi_net.processor.default_handlers import (
    basic_rid_handler,
    edge_negotiation_handler,
    basic_network_output_filter
)
from .config import URL, FIRST_CONTACT, ROOT, GDriveSensorNodeConfig

logger = logging.getLogger(__name__)


# node = NodeInterface(
#     name="gdrive-sensor",
#     profile=NodeProfile(
#         base_url=URL,
#         node_type=NodeType.FULL,
#         provides=NodeProvides(
#             event=[GoogleWorkspaceApp],
#             state=[GoogleWorkspaceApp]
#         )
#     ),
#     use_kobj_processor_thread=True,
#     first_contact=FIRST_CONTACT,
#     cache_directory_path=f"{ROOT}/net/metadata/gdrive_sensor_node_rid_cache",
#     identity_file_path=f"{ROOT}/net/metadata/gdrive_sensor_node_identity.json",
#     handlers=[
#         basic_rid_handler,
#         edge_negotiation_handler,
#         basic_network_output_filter
#     ]
# )

node = NodeInterface(
    config=GDriveSensorNodeConfig.load_from_yaml(f"{ROOT}/net/metadata/gdrive_sensor_config.yaml"),
    use_kobj_processor_thread=True,
    # cache_directory_path=f"{ROOT}/net/metadata/gdrive_sensor_node_rid_cache",
    # identity_file_path=f"{ROOT}/net/metadata/gdrive_sensor_node_identity.json",
    handlers=[
        basic_rid_handler,
        edge_negotiation_handler,
        basic_network_output_filter
    ]
)

from . import handlers