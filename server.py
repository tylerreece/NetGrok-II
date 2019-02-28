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
import sqlite3
from multiprocessing import Process, Lock

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
DATABASE = 'database/netgrok.db'
mutex = Lock()

# Bookkeeping for connections
primary_connections_seen = set()

# Debug flag
debug = False

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
	json_string = json_string.strip('{}\x00')
		
	# Format json_string correctly for json.loads()
	json_string = '[{' + json_string + '}]'
	json_obj = json.loads(json_string)
	
	# Primary connections
	if 'host' in json_obj[0]:
		host = json_obj[0]['host']
		host = host.split('www.')[-1]
		global primary_connections_seen
		if host not in primary_connections_seen:
			primary_connections_seen.add(host)
			print(str(primary_connections_seen))
			return json_obj[0]

	# Secondary connections
	else:
		# TODO: add in secondary connection handling
		pass
			
@sio.on('send whole graph')
def send_whole_graph(userAgent):
	with mutex:
		conn = create_connection(DATABASE)
		info = query_database(conn)
		msg = ''
		for row in info:
			entry = dict()
			entry['src_ip'] = row[1]
			entry['src_port'] = row[2]
			entry['dst_ip'] = row[3]
			entry['dst_port'] = row[4]
			entry['time_start'] = row[5]
			entry['time_end'] = row[6]
			entry['download'] = row[7]
			entry['upload'] = row[8]
			entry['protocol'] = row[9]
			entry['host'] = row[10] 
			msg += str(entry)
		sio.emit('whole graph', msg)

def create_connection(db_file):
	try:
		conn = sqlite3.connect(db_file)
		return conn
	except Error as e:
		print(e)
	return None

def create_entry(conn, entry):
	sql = ''' INSERT INTO NETGROK(ID, SRC_IP, SRC_PORT, DST_IP, DST_PORT, TIME_START, TIME_END, DOWNLOAD, UPLOAD, PROTOCOL, HOST) VALUES(?,?,?,?,?,?,?,?,?,?,?)'''
	cur = conn.cursor()
	cur.execute(sql, entry)
	return cur.lastrowid

def query_database(conn):
	sql = ''' SELECT * FROM NETGROK'''
	cur = conn.cursor()
	cur.execute(sql)
	return cur.fetchall()

def remove_duplicates(conn):
	sql = '''DELETE FROM NETGROK 
		WHERE ID NOT IN (SELECT MAX(ID) FROM NETGROK
				GROUP BY host); '''
	cur = conn.cursor()
	cur.execute(sql)
	

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

		json_obj = parse_json(received_message)
		msg = json.dumps(json_obj)
		
		# The only reason this type check is here is because the else statement is not yet filled out in parse_json to handle secondary connections
		if type(msg) is str and json_obj is not None:
			
			with mutex: # Lock during modications to db
				conn = create_connection(DATABASE)
				with conn:
					entry = (None,
						json_obj['src_ip'], 
						json_obj['src_port'], 
						json_obj['dst_ip'], 
						json_obj['dst_port'], 
						json_obj['time_start'], 
						json_obj['time_end'], 
						json_obj['download'], 
						json_obj['upload'], 
						json_obj['protocol'], 
						json_obj['host'])
					create_entry(conn, entry)
					remove_duplicates(conn)			
					sio.emit('new node', msg, broadcast=True)


# Setup and start thread
thread = threading.Thread(target=listen)
thread.start()

# Run server with debug mode enabled
if __name__ == '__main__':
	sio.run(app, host=HOST_MASK, port=APP_PORT, debug=True)
