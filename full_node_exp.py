import requests
from koi_net.protocol.consts import (
    BROADCAST_EVENTS_PATH,
    POLL_EVENTS_PATH,
    FETCH_RIDS_PATH,
    FETCH_MANIFESTS_PATH,
    FETCH_BUNDLES_PATH
)
from koi_net.protocol.api_models import EventsPayload
from koi_net.network.request_handler import RequestHandler
from gdrive_sensor.utils.functions import bundle_list, event_filter
from pprint import pprint

url = lambda ep: f'http://127.0.0.1:5000/{ep}'

driveId = '0AJflT9JpikpnUk9PVA'
query = f"\'{driveId}\' in parents"
# bundles = bundle_list(query=query, driveId=driveId)
# events = event_filter(bundles)
# bundle_contents = dict(bundles[1].contents)


# events_payload = EventsPayload(events = event_filter(bundles))
events_payload = EventsPayload(events = [])
req_handler = RequestHandler()
req_handler.broadcast_events(
    url = url(BROADCAST_EVENTS_PATH), 
    req = events_payload
)

# response = requests.post(
#     url = url(BROADCAST_EVENTS_PATH),
#     data=None,
#     json=None 
#     # json = events_payload.model_dump_json()
# )
# pprint(response)


# pprint(events)
# print()
# filtered_events = [events[2]]
# events_payload = EventsPayload
# events_payload.events = filtered_events

# print(events_payload.__dict__)
# pprint(filtered_events)

# response = requests.post(
#     url = url(FETCH_RIDS_PATH), 
#     json = events_payload
# )
# pprint(response)