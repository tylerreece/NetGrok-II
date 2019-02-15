/*
	network.js
	XE401/XE402 - NetGrok II
	Tyler Reece, Dan Young, Matt Kim, Josh Balba
	United States Military Academy
*/


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
	},
	interaction: {
		hover: true,
	},
	physics: {
		enabled: true,
		stabilization: true,
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
       	nodes.add({label: msg, image: 'https://' + msg + '/favicon.ico', shape: 'image'});
	network.fit();
});

/* Print information to console for debuging */
socket.on('debug', function(msg) {
       	console.log(msg);
});

