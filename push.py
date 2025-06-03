from flask import Flask, request
from koi_net.protocol.event import Event, EventType
from koi_net.processor.knowledge_object import KnowledgeSource
from gdrive_sensor.core import node
from gdrive_sensor.utils.connection import drive_service
from gdrive_sensor.utils.functions.bundle import bundle_item
from gdrive_sensor.utils.types import GoogleWorkspaceApp

app = Flask(__name__)

@app.route('/google-drive-listener', methods=['POST'])
def notifications():
    # Handle the notification
    fileId = request.headers['X-Goog-Resource-Uri'].split('?')[0].rsplit('/', 1)[-1]
    # changed = request.headers['X-Goog-Changed']
    
    print("fileId:", fileId)
    print()
    print("Received notification:", request.headers)
    
    state = request.headers['X-Goog-Resource-State']
    if state != 'sync':
        file = drive_service.files().get(fileId=fileId, supportsAllDrives=True).execute()
        mimeType = file.get('mimeType')
        rid_obj = GoogleWorkspaceApp.from_reference(fileId).google_object(mimeType)
        if state == 'untrash':
            bundle = None
            knowledge_source = None
            if node.cache.exists(rid_obj) == False:
                print("untrash: External")
                bundle = bundle_item(file)
                knowledge_source = KnowledgeSource.External
            else:
                print("untrash: Internal")
                bundle = node.cache.read(rid_obj)
                knowledge_source = KnowledgeSource.Internal
            node.processor.handle(bundle=bundle, source=knowledge_source)
        else:
            event_type = None
            if state in ['remove', 'trash']:
                print("remove OR trash: External FORGET")
                event_type = EventType.FORGET
            elif state == 'update':
                print("         update: External UPDATE")
                event_type = EventType.UPDATE
            elif state == 'add':
                print("            add: External NEW")
                event_type = EventType.NEW
            event = Event(rid=rid_obj, event_type=event_type)
            node.processor.handle(event=event, source=KnowledgeSource.External)
    
    if request.data:
        print("Received data:", request.data)
    else:
        print("No data received.")
    if request.is_json:
        print("Received json:", request.json)
    else:
        print("Received non-JSON data.")
    return '', 204  # Respond with no content

if __name__ == '__main__':
    app.run(port=8003)