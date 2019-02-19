# server.py
# XE401/XE402 - NetGrok II
# Tyler Reece, Dan Young, Matt Kim, Josh Balba
# United States Military Academy

# Import necessary modules
from flask_socketio import SocketIO
import threading
from flask import Flask, render_template
import zmq
import json

# Setup ZMQ and Flask
context = zmq.Context()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'TeamNetGrok'

# Do not cache static assets. Annoying during development
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 

# Utilize threading mode to allow utilization of .recv() blocking call
sio = SocketIO(app, async_mode='threading')

# Server parameter constants
HOST_MASK = '0.0.0.0'
APP_PORT = 5000
ZMQ_SUBSCRIPTION_PORT = '7188'

# Bookkeeping for connections
primary_connections_seen = set()

# Debug flag
debug = True

# Server routing logic

@app.route('/')
def index():
	"""Returns NetGrok's index page."""
	return render_template('index.html')

@app.route('/index.html')
def index2():
	"""Returns NetGrok's index page (secondary route)."""
	return render_template('index.html')

@app.route('/timeline.html')
def timeline():
	"""Returns NetGrok's timeline page."""
	return render_template('timeline.html')

@app.route('/table.html')
def table():
	"""Returns NetGrok's table page."""
	return render_template('table.html')

@app.route('/about.html')
def about():
	"""Returns NetGrok's about page."""
	return render_template('about.html')

def parse_json(json_string):
	"""
	Parses JSON and outputs message to be broadcasted.

	Parameters
	----------
	json_string: str
		A string in JSON format sent from SSLSplit.

	Returns
	----------
	message: str
		A string of the necessary information for the 
		visualization. Add fields here as necessary.
	"""
	
	# Clean up json_string
	json_string = json_string.strip('{').strip('}').strip('\x00').strip('}')
	
	# Format json_string correctly for json.loads()
	json_string = '[{' + json_string + '}]'
	json_obj = json.loads(json_string)
	
	# Primary connections
	if 'host' in json_obj[0]:
		message = json_obj[0]['host']
		message = message.split('www.')[-1]
		if message not in primary_connections_seen:
			primary_connections_seen.add(message)
			return message

	# Secondary connections
	else:
		# TODO: add in secondary connection handling
		pass
			

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
		received_message = subscriber.recv().decode("utf-8")

		if(debug):
			sio.emit('debug', received_message, broadcast=True)

		message_to_emit = parse_json(received_message)
		# The only reason this type check is here is because the else statement is not yet filled out in parse_json to handle secondary connections
		if type(message_to_emit) is str:
			sio.emit('new node', message_to_emit, broadcast=True)


# Setup and start thread
thread = threading.Thread(target=listen)
thread.start()

# Run server with debug mode enabled
if __name__ == '__main__':
	sio.run(app, host=HOST_MASK, port=APP_PORT, debug=True)
