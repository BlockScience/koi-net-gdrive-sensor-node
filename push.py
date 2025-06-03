from flask import Flask, request
from koi_net.protocol.event import Event

app = Flask(__name__)

@app.route('/google-drive-listener', methods=['POST'])
def notifications():
    # Handle the notification
    print("Received notification:", request.headers)
    fileId = request.headers['X-Goog-Resource-Uri'].split('?')[0].rsplit('/', 1)[-1]
    print("Received fileId:", fileId)
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