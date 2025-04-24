from pprint import pprint
from gdrive_sensor.utils.functions import bundle_list, list_shared_drives
from gdrive_sensor.utils.connection import drive_service
from koi_net.protocol.event import Event, EventType
from rid_lib.ext import Bundle

# Example usage
# query = f"'1OwnHDuusN9ZiFgUzmttR-cLDbU0sS4z3' in parents"
driveId = '0AJflT9JpikpnUk9PVA'
query = f"\'{driveId}\' in parents"

# query = f"'koi' in parents"
# query = f"mimeType='{folderType}' or mimeType!='{folderType}'"
bundles = bundle_list(query=query, driveId=driveId)
bundle: Bundle = bundles[0]
bundle_manifest = dict(bundle.manifest)
rid_obj = bundle.manifest.rid
bundle_contents = dict(bundle.contents)
print("Examples:")
print()
print("Manifest:")
pprint(bundle_manifest)
print()
print("Contents:")
pprint(bundle_contents)
print()
print("RID Obj:")
print(rid_obj)
print()
print("Event:")
event = Event(rid=rid_obj, event_type=EventType.NEW, manifest=bundle_manifest)
print(event)
print()
print()

# list_shared_drives(drive_service)



# bundle_dict = bundles[1].to_json()
# bundle_dict['contents'] = 'masked'
exit()