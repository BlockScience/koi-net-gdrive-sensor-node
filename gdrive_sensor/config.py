import os, json
from dotenv import load_dotenv

load_dotenv()

ROOT = os.getcwd()
SENSOR = f'{ROOT}/gdrive_sensor'
CREDENTIALS = f'{ROOT}/creds/service_account/gdrive-sensor-cred.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SHARED_DRIVE_ID = os.environ["SHARED_DRIVE_ID"]

# HOST = "127.0.0.1"
# PORT = 8002
# URL = f"http://{HOST}:{PORT}/koi-net"

FIRST_CONTACT = "http://127.0.0.1:8000/koi-net"

try:
    with open("state.json", "r") as f:
        LAST_PROCESSED_TS = json.load(f).get("last_processed_ts", 0)
except FileNotFoundError:
    LAST_PROCESSED_TS = 0


from pydantic import BaseModel, Field
from koi_net.protocol.node import NodeProfile, NodeType, NodeProvides
from koi_net.config import NodeConfig, EnvConfig, KoiNetConfig
from gdrive_sensor.utils.types import GoogleWorkspaceApp


class GDriveConfig(BaseModel):
    drive_id: str | None = SHARED_DRIVE_ID

class GDriveEnvConfig(EnvConfig):
    gdrive_api_token: str | None = CREDENTIALS

class GDriveServerConfig(BaseModel):
    host: str | None = "127.0.0.1"
    port: int | None = 8002
    path: str | None = "/koi-net"
    
    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}{self.path or ''}"


class GDriveSensorNodeConfig(NodeConfig):
    koi_net: KoiNetConfig | None = Field(default_factory = lambda: 
        KoiNetConfig(
            node_name="gdrive-sensor",
            first_contact=FIRST_CONTACT,
            node_profile=NodeProfile(
                # base_url=URL,
                node_type=NodeType.FULL,
                provides=NodeProvides(
                    event=[GoogleWorkspaceApp],
                    state=[GoogleWorkspaceApp]
                )
            ),
            cache_directory_path=f"{ROOT}/net/metadata/gdrive_sensor_node_rid_cache"
        )
    )
    server: GDriveServerConfig | None = Field(default_factory=GDriveServerConfig)
    env: GDriveEnvConfig | None = Field(default_factory=GDriveEnvConfig)
    gdrive: GDriveConfig | None = Field(default_factory=GDriveConfig)