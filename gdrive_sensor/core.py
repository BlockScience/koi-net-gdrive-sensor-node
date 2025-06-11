import logging
from koi_net import NodeInterface
from .config import ROOT, GDriveSensorNodeConfig
from pprint import pprint

logger = logging.getLogger(__name__)

node = NodeInterface(
    config=GDriveSensorNodeConfig.load_from_yaml(f"{ROOT}/net/metadata/gdrive_sensor_config.yaml"),
    use_kobj_processor_thread=True,
    # cache_directory_path=f"{ROOT}/net/metadata/gdrive_sensor_node_rid_cache",
    # identity_file_path=f"{ROOT}/net/metadata/gdrive_sensor_node_identity.json",
)

from . import handlers
pprint(node.processor.handlers)