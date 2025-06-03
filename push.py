from flask import Flask, request

app = Flask(__name__)

@app.route('/google-drive-listener', methods=['POST'])
def notifications():
    # Handle the notification
    print("Received notification:", request.headers)
    print("Received data:", request.data)
    print("Received json:", request.json_module)
    return '', 204  # Respond with no content

if __name__ == '__main__':
    app.run(port=8003)