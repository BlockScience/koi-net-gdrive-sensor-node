import uvicorn
# from .config import HOST, PORT
from .core import node

uvicorn.run(
    "gdrive_sensor.server:app", 
    host=node.config.server.host, 
    port=node.config.server.port, 
    log_config=None
)