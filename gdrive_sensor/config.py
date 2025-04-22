import os, json
from dotenv import load_dotenv

load_dotenv()

HOST = "127.0.0.1"
# PORT = 8002
PORT = 5000
URL = f"http://{HOST}:{PORT}/koi-net"

FIRST_CONTACT = "http://127.0.0.1:8000/koi-net"

GDRIVE_API_TOKEN = os.environ["GDRIVE_API_TOKEN"]

try:
    with open("state.json", "r") as f:
        LAST_PROCESSED_TS = json.load(f).get("last_processed_ts", 0)
except FileNotFoundError:
    LAST_PROCESSED_TS = 0