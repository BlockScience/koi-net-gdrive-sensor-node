import json
from dotenv import load_dotenv
from pydantic import BaseModel, Field #, ServerConfig
from koi_net.protocol.node import NodeProfile, NodeType, NodeProvides
from koi_net.config import NodeConfig, EnvConfig, KoiNetConfig
from .utils.types import GoogleDoc, GoogleSlides, GoogleSheets, GoogleDriveFolder
from . import ROOT, CREDENTIALS, SHARED_DRIVE_ID, START_PAGE_TOKEN, NEXT_PAGE_TOKEN, SUBSCRIPTION_WINDOW

load_dotenv()

# FIRST_CONTACT = "http://127.0.0.1:8000/koi-net"

class GDriveConfig(BaseModel):
    drive_id: str | None = SHARED_DRIVE_ID
    start_page_token: str | None = START_PAGE_TOKEN
    next_page_token: str | None = NEXT_PAGE_TOKEN
    subscription_host: str | None = 'koi-net.block.science'
    listener_host: str | None = '0.0.0.0'
    listener_port: int | None = 8003
    subscription_window: int | None = SUBSCRIPTION_WINDOW
    last_processed_ts: float | None = 0.0

class GDriveEnvConfig(EnvConfig):
    api_credentials: str | None = CREDENTIALS

# class GDriveServerConfig(BaseModel):
#     host: str | None = "127.0.0.1"
#     port: int | None = 9002
#     path: str | None = "/koi-net"
    
#     @property
#     def url(self) -> str:
#         return f"http://{self.host}:{self.port}{self.path or ''}"

class GDriveSensorNodeConfig(NodeConfig):
    koi_net: KoiNetConfig | None = Field(default_factory = lambda: 
        KoiNetConfig(
            node_name="gdrive-sensor",
            first_contact="http://127.0.0.1:8000/koi-net",
            node_profile=NodeProfile(
                # base_url=URL,
                node_type=NodeType.FULL,
                provides=NodeProvides(
                    event=[GoogleDoc, GoogleSlides, GoogleSheets, GoogleDriveFolder],
                    state=[GoogleDoc, GoogleSlides, GoogleSheets, GoogleDriveFolder]
                )
            ),
            cache_directory_path=f"{ROOT}/net/metadata/gdrive_sensor_node_rid_cache"
        )
    )
    # server: GDriveServerConfig | None = Field(default_factory=GDriveServerConfig)
    env: GDriveEnvConfig | None = Field(default_factory=GDriveEnvConfig)
    gdrive: GDriveConfig | None = Field(default_factory=GDriveConfig)