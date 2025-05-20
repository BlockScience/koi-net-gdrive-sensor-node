import uvicorn
from .config import HOST, PORT
from .core import node

uvicorn.run("gdrive_sensor.server:app", host=HOST, port=PORT, log_config=None)