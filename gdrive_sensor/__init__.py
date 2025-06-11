import logging, os
from rich.logging import RichHandler
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ROOT = os.getcwd()
SENSOR = f'{ROOT}/gdrive_sensor'
CREDENTIALS = f'{ROOT}/creds/service_account/gdrive-sensor-cred.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SHARED_DRIVE_ID = os.environ["SHARED_DRIVE_ID"]
START_PAGE_TOKEN = '67'
NEXT_PAGE_TOKEN = None
SUBSCRIPTION_WINDOW = 600 # Seconds

LAST_PROCESSED_TS = datetime.now()

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