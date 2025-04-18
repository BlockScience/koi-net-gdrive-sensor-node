from pprint import pprint
from .utils.functions import bundle_list
from koi_net.protocol.event import Event, EventType

# Example usage
query = f"'1OwnHDuusN9ZiFgUzmttR-cLDbU0sS4z3' in parents"
# query = f"'koi' in parents"
# query = f"mimeType='{folderType}' or mimeType!='{folderType}'"
bundles = bundle_list(query)
bundle_manifest = dict(bundles[1].manifest)
rid_obj = bundles[1].manifest.rid
bundle_contents = dict(bundles[1].contents)
print()
pprint(bundle_manifest)
print()
print(rid_obj)
print()
event = Event(rid=rid_obj, event_type=EventType.NEW, manifest=bundle_manifest)
print(event)
print()
# print()
# pprint(bundle_contents)



# bundle_dict = bundles[1].to_json()
# bundle_dict['contents'] = 'masked'
exit()