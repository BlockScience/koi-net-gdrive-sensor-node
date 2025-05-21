import logging, os
from rich.logging import RichHandler

ROOT = os.getcwd()
SENSOR = f'{ROOT}/gdrive_sensor'
CREDENTIALS = f'{ROOT}/creds/service_account/gdrive-sensor-cred.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SHARED_DRIVE_ID = os.environ["SHARED_DRIVE_ID"]

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

rich_handler = RichHandler()
rich_handler.setLevel(logging.INFO)
rich_handler.setFormatter(logging.Formatter(
    "%(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))

file_handler = logging.FileHandler("node-log.txt")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))

# Add both
logger.addHandler(rich_handler)
logger.addHandler(file_handler)