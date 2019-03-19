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
from pony.orm import *

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

# Database information
DATABASE = 'database/netgrok.db'
db = Database()
class Entry(db.Entity):
    host = Required(str)
    protocol = Required(str)
    src_ip = Required(str)
    src_port = Required(str)
    dst_ip = Required(str)
    dst_port = Required(str)
    time_start = Required(str)
    time_end = Required(str)
    download = Required(str)
    upload = Required(str)
db.bind(provider='sqlite', filename=DATABASE, create_db=True)
db.generate_mapping(create_tables=True)
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

# Helper Functions

def parse_json(json_string):
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

@sio.on('flush db')
@db_session
def flush_database():
    delete(e for e in Entry)
    primary_connections_seen.clear()
    sio.emit('database flushed')

@sio.on('send whole graph')
@db_session
def send_whole_graph(userAgent):
        entries = select(e for e in Entry)
        #query_database()
        msg = ''
        for e in entries:
            print(e.host)
            entry = dict()
            entry['src_ip'] = e.src_ip
            entry['src_port'] = e.src_port
            entry['dst_ip'] = e.dst_ip
            entry['dst_port'] = e.dst_port
            entry['time_start'] = e.time_start
            entry['time_end'] = e.time_end
            entry['download'] = e.download
            entry['upload'] = e.upload
            entry['protocol'] = e.protocol
            entry['host'] = e.host
            msg += str(entry)
        sio.emit('whole graph', msg)

@db_session
def create_entry(entry):
    Entry(src_ip=entry[0], src_port=entry[1], dst_ip=entry[2],
        dst_port=entry[3], time_start=entry[4], time_end=entry[5],
        download=entry[6], upload=entry[7], protocol=entry[8],
        host=entry[9])

@db_session
def query_database():
    query = select(e for e in Entry)
    for entry in query[:]:
        print(entry.host + '\n')

def listen():
    subscriber = context.socket(zmq.SUB)
    subscriber.connect('tcp://127.0.0.1:' + ZMQ_SUBSCRIPTION_PORT)
    subscriber.setsockopt(zmq.SUBSCRIBE, b'')
    while True:
        received_message = subscriber.recv().decode("utf-8")

        if (debug):
            sio.emit('debug', received_message, broadcast=True)

        json_obj = parse_json(received_message)
        msg = json.dumps(json_obj)

        # The only reason this type check is here is because the else 
        # statement is not yet filled out in parse_json to handle 
        # secondary connections
        if type(msg) is str and json_obj is not None:

            with mutex:  # Lock during modications to db
                entry = (json_obj['src_ip'], json_obj['src_port'],
                         json_obj['dst_ip'], json_obj['dst_port'],
                         json_obj['time_start'], json_obj['time_end'],
                         json_obj['download'], json_obj['upload'],
                         json_obj['protocol'], json_obj['host'])
                create_entry(entry)
                query_database()
                sio.emit('new node', msg, broadcast=True)

# Setup and start thread
thread = threading.Thread(target=listen)
thread.start()

# Run server with debug mode enabled
if __name__ == '__main__':
    sio.run(app, host=HOST_MASK, port=APP_PORT, debug=True)
