# server.py
# XE401/XE402 - NetGrok II
# Tyler Reece, Dan Young, Matt Kim, Josh Balba
# United States Military Academy

# Import necessary modules
from flask_socketio import SocketIO
import threading
from flask import Flask, render_template
import zmq

# Setup ZMQ and Flask
context = zmq.Context()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'teamNetGrok'

# Utilize threading mode to allow utilization of .recv() blocking call
sio = SocketIO(app, async_mode='threading')

# Server parameter constants
HOST_MASK = '0.0.0.0'
APP_PORT = 5000
ZMQ_SUBSCRIPTION_PORT = '7188'


# Server routing logic

@app.route('/')
def index():
	"""Returns NetGrok's index page."""
	return render_template('index.html')

def listen():
	"""
	Listens for messages on ZMQ_SUBSCRIPTION_PORT and emits them 
	on APP_PORT under the title 'updates'. Utilizes the broadcast
	parameter to send to all listening hosts.
	"""
	subscriber = context.socket(zmq.SUB)
	subscriber.connect('tcp://127.0.0.1:' + ZMQ_SUBSCRIPTION_PORT)
	subscriber.setsockopt(zmq.SUBSCRIBE, b'')
	while True:
		message = subscriber.recv() 
		sio.emit('updates', message.decode("utf-8"), broadcast=True)


# Setup and start thread
thread = threading.Thread(target=listen)
thread.start()

# Run server with debug mode enabled
if __name__ == '__main__':
	sio.run(app, host=HOST_MASK, port=APP_PORT, debug=True)
