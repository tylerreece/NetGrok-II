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
	interaction: {
		hover: true,
	},
	physics: {
		stabilization: true,
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
       	console.log("Client connected successfully!")
});

/* Handle creation of new node */
socket.on('new node', function(msg) {
       	nodes.add({label: msg});
	network.fit();
	var div = document.getElementById('stream');
       	div.innerHTML += '<p>' + msg + '</p>';
});

/* Print information to console for debuging */
socket.on('debug', function(msg) {
       	console.log(msg);
});

