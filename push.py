from flask import Flask, request

app = Flask(__name__)

@app.route('/notifications', methods=['POST'])
def notifications():
    # Handle the notification
    print("Received notification:", request.headers)
    return '', 204  # Respond with no content

if __name__ == '__main__':
    app.run(port=5000)