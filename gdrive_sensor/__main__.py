import uvicorn
import threading
from .core import node
from .server import app, listener  # Import both FastAPI apps

def run_app(app_instance, host, port):
    uvicorn.run(app_instance, host=host, port=port, log_config=None)

if __name__ == "__main__":
    # Define the host and ports for each application
    app_host = node.config.server.host
    app_port = node.config.server.port
    # listener_host = '0.0.0.0'
    listener_host = 'koi-net.block.science'
    listener_port = 8003
    
    # Create threads for each application
    app_thread = threading.Thread(target=run_app, args=(app, app_host, app_port))
    listener_thread = threading.Thread(target=run_app, args=(listener, listener_host, listener_port))
    
    # Start both threads
    app_thread.start()
    listener_thread.start()
   
    # Optionally, join threads if you want to wait for them to finish
    app_thread.join()
    listener_thread.join()

# import uvicorn
# from .core import node

# print(node.config.server.port)

# uvicorn.run(
#     "gdrive_sensor.server:app", 
#     host=node.config.server.host, 
#     port=node.config.server.port, 
#     log_config=None
# )