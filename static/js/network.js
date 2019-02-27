/*
	network.js
	XE401/XE402 - NetGrok II
	Tyler Reece, Dan Young, Matt Kim, Josh Balba
	United States Military Academy
*/

/* Hash Function */
String.prototype.hashCode = function() {
  var hash = 0, i, chr;
  if (this.length === 0) return hash;
  for (i = 0; i < this.length; i++) {
    chr   = this.charCodeAt(i);
    hash  = ((hash << 5) - hash) + chr;
    hash |= 0; // Convert to 32bit integer
  }
  hash = Math.abs(hash);
  return hash % 25;
  
};


/* Grid Mapping */
var mapping = {
        0: [-200, -250],
        1: [-100, -250],
        2: [0. -250],
        3: [100, -250],
        4: [200, -250],
        5: [-200, -150],
        6: [-100, -150],
        7: [0, -150],
        8: [100, -150],
        9: [200, -150],
        10: [-200, 0],
        11: [-100, 0],
        12: [100, 0],
        13: [200, 0],
        14: [-200, -150],
        15: [-100, -150],
        16: [0, -150],
        17: [100, -150],
        18: [200, -150],
        19: [-200, -250],
        20: [-100, -250],
        21: [0, -250],
        22: [100, -250],
        23: [200, -250]
};

var url = 'google.com';
console.log(mapping[url.hashCode()][1]);

/* VisJS setup */
var nodes = new vis.DataSet();
var edges = new vis.DataSet();

var container = document.getElementById('visualization');
var data = {
	nodes: nodes,
	edges: edges
};

var options = {
	nodes: {
		brokenImage: "https://i.dlpng.com/static/png/6818_preview.png",
		font: {
			multi: 'html',
		},
	},
	interaction: {
		hover: true,
	},
	physics: {
		enabled: true,
		stabilization: false,
		barnesHut: {
			gravitationalConstant: -2000,
			centralGravity: 0.3,
			avoidOverlap: 0.5,
			
		},		
	},
	layout: {
		randomSeed: 2,
	},
};

var network = new vis.Network(container, data, options);


/* Add initial informational node on empty network */
if(!nodes.length) {
	nodes.add({id: 0, label: "<b>Browse around to start Grokking!</b>"});
};

	
/* Connect to socket */
var socket = io.connect('http://' + document.domain + ':' + location.port);

/* On connect message to console */
socket.on('connect', function() {
	console.log("Client connected successfully!");
	console.log(navigator.userAgent);
	socket.emit('client connected', {userAgent: navigator.userAgent});
});

/* Handle creation of new node */
socket.on('new node', function(msg) { 	
	
	/* Remove intro message on browsing start */
	if(nodes.get(0)){
		nodes.remove(0)
	};
	
	var json_obj = JSON.parse(msg);
       	var host = json_obj.host;
	var hash = host.hashCode();
	var x = mapping[hash][0];
	var y = mapping[hash][1];
	
	console.log(x.toString());
	nodes.add({label: '<b>' + host + '</b>', image: 'https://' + host + '/favicon.ico', shape: 'image', x: x, y: y});
	network.fit();
});

/* Print information to console for debuging */
socket.on('debug', function(msg) {
       	console.log(msg);
});

