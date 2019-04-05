# server.py
# XE401/XE402 - NetGrok II
# Tyler Reece, Dan Young, Matt Kim, Josh Balba
# United States Military Academy

# Import necessary modules
import time
from flask_socketio import SocketIO
import threading, zmq, json, sqlite3, sched, time, datetime
from flask import Flask, render_template
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
AGE_OFF_WINDOW = 5.0
AGE_OFF_BYTES = 1000
USE_AGE_OFF = False

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

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = threading.Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

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
    json_string = json_string.strip('{}\x00')
    json_string = '[{' + json_string + '}]'
    json_obj = json.loads(json_string)
    if 'host' in json_obj[0]:
        return json_obj[0]

@sio.on('flush db')
@db_session
def flush_database():
    delete(e for e in Entry)
    sio.emit('database flushed')

@sio.on('send whole graph')
@db_session
def send_whole_graph(userAgent):
        entries = select(e for e in Entry)
        #query_database()
        msg = ''
        for e in entries:
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
def update_entry(entry):
    query = select(e for e in Entry if e.host == entry[9]).for_update()
    for e in query:
        e.time_end = entry[5]
        e.download = str(int(e.download) + int(entry[6]))
        e.upload = str(int(e.upload) + int(entry[7]))

@db_session
def query_database():
    query = select(e for e in Entry)
    for entry in query[:]:
        print(entry.host + '\n')

@db_session
def exists_in_db(host):
    query = select(e for e in Entry if e.host == host)
    if query:
        return True
    else:
        return False

@sio.on('age off')
@db_session
def delete_entry(msg):
    host = msg['host']
    query = select(e for e in Entry if e.host == host).for_update()
    for e in query:
        e.delete()

@db_session
def age_off():
    time_now = datetime.datetime.now()
    age_off_window = time_now - datetime.timedelta(seconds=AGE_OFF_WINDOW)
    state = select(e for e in Entry)
    connection_times = []
    rows_to_age_off = []
    for e in state:
        datetime_obj = datetime.datetime.strptime(e.time_end,
            "%Y-%m-%d %H:%M:%S")
        connection_times.append((e.id, e.host, datetime_obj))
    for (ID, host, date) in connection_times:
        if date < age_off_window:
            query = select(e for e in Entry if e.host == host).for_update()
            sio.emit('reduce node', [host, AGE_OFF_BYTES])

def listen():
    subscriber = context.socket(zmq.SUB)
    subscriber.connect('tcp://127.0.0.1:' + ZMQ_SUBSCRIPTION_PORT)
    subscriber.setsockopt(zmq.SUBSCRIBE, b'')
    while True:
        received_message = subscriber.recv().decode("utf-8")
        json_obj = parse_json(received_message)
        msg = json.dumps(json_obj)
        if type(msg) is str and json_obj is not None:
            newHost = json_obj['host'].split('www.')[-1]
            entry = (json_obj['src_ip'], json_obj['src_port'],
                json_obj['dst_ip'], json_obj['dst_port'],
                json_obj['time_start'], json_obj['time_end'],
                json_obj['download'], json_obj['upload'],
                json_obj['protocol'], newHost)
            if exists_in_db(newHost):
                update_entry(entry)
                sio.emit('update node', msg, broadcast=True)
            else:
                create_entry(entry)
                sio.emit('new node', msg, broadcast=True)

# Setup and start thread
thread = threading.Thread(target=listen)
thread.start()

# Run server with debug mode enabled
if __name__ == '__main__':
    if USE_AGE_OFF:
        rt = RepeatedTimer(AGE_OFF_WINDOW, age_off)
    sio.run(app, host=HOST_MASK, port=APP_PORT, debug=True)
