from fastapi import FastAPI, Request
from rid_lib.ext import Bundle
from koi_net.protocol.event import EventType

from gdrive_sensor.core import node
from gdrive_sensor.utils.connection import drive_service
from gdrive_sensor.utils.functions.bundle import bundle_item
from gdrive_sensor.utils.functions.api import get_change_results
from gdrive_sensor.utils.types import GoogleWorkspaceApp
from pprint import pprint

app = FastAPI()

@app.post('/google-drive-listener')
async def notifications(request: Request):
    # Handle the notification
    fileId = request.headers['X-Goog-Resource-Uri'].split('?')[0].rsplit('/', 1)[-1]
    
    print("fileId:", fileId)
    print()
    print("Received notification:")
    pprint(dict(request.headers))
    
    state = request.headers['X-Goog-Resource-State']
    if state != 'sync':
        file = drive_service.files().get(fileId=fileId, supportsAllDrives=True).execute()
        mimeType = file.get('mimeType')
        rid_obj = GoogleWorkspaceApp.from_reference(fileId).google_object(mimeType)
        
        event_type = None
        if state in ['remove', 'trash']:
            print(f"{state}: from source FORGET")
            node.processor.handle(rid=rid_obj, event_type=EventType.FORGET)
        elif state == 'update':
            print(f"{state}: from source UPDATE")
            if not node.cache.exists(rid_obj):
                bundle = bundle_item(file)
                bundle.contents['page_token'] = node.config.gdrive.start_page_token
                node.processor.handle(bundle=bundle)
            else:
                bundle = node.cache.read(rid_obj)
            node.config.gdrive.start_page_token = bundle.contents['page_token']
        elif state in ['add', 'untrash']:
            bundle = None
            if not node.cache.exists(rid_obj):
                print(f"{state}: External")
                bundle = bundle_item(file)
            else:
                print(f"{state}: Internal")
                bundle = node.cache.read(rid_obj)
            node.processor.handle(bundle=bundle)
    
    if request.body:
        print("Received data:", await request.body())
    else:
        print("No data received.")
    if request.headers.get('content-type') == 'application/json':
        json_data = await request.json()
        print("Received json:", json_data)
    else:
        print("Received non-JSON data.")
    
    return {"message": "No content"}, 204  # Respond with no content

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)