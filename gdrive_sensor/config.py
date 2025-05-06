import os, json
from dotenv import load_dotenv

load_dotenv()

ROOT = os.getcwd()
SENSOR = f'{ROOT}/gdrive_sensor'
CREDENTIALS = f'{ROOT}/creds/service_account/gdrive-sensor-cred.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SHARED_DRIVE_ID = os.environ["SHARED_DRIVE_ID"]

HOST = "127.0.0.1"
PORT = 8002
URL = f"http://{HOST}:{PORT}/koi-net"

FIRST_CONTACT = "http://127.0.0.1:8000/koi-net"

try:
    with open("state.json", "r") as f:
        LAST_PROCESSED_TS = json.load(f).get("last_processed_ts", 0)
except FileNotFoundError:
    LAST_PROCESSED_TS = 0