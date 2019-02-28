var nodesSeen = new Set();

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
		zoomView: false,
		dragView: false,
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


/* Network Functions */
function addNode(json_string) {
    var json_obj = JSON.parse(json_string);
	if(!nodesSeen.has(json_obj.host)) {
    	nodesSeen.add(json_obj.host);
		nodes.add({
        	label: '<b>' + json_obj.host + '</b>',
			src_ip: json_obj.src_ip,
			src_port: json_obj.src_port,
			dst_ip: json_obj.dst_ip,
			dst_port: json_obj.dst_port,
			time_start: json_obj.time_start,
			time_end: json_obj.time_end,
			download: json_obj.download,
			upload: json_obj.upload,
			protocol: json_obj.protocol,
        	image: 'https://' + json_obj.host + '/favicon.ico',
        	shape: 'image'
    	});
	}
    network.fit();
}

function addNodes(json_strings) {
    var j_strings = json_strings.split('}');
    //console.log(j_strings);
    for (var i = 0; i < j_strings.length - 1; i++) {
        var newString = (j_strings[i] + '}').split("'").join('"');
        addNode(newString);
    }

}

/* Connect to socket */
var socket = io.connect('http://' + document.domain + ':' + location.port);

/* On connect message to console */
socket.on('connect', function() {
    socket.emit('send whole graph', {
        userAgent: navigator.userAgent
    });
});

/* On receipt of current state */
socket.on('whole graph', function(msg) {
	addNodes(msg);
});

/* Handle creation of new node */
socket.on('new node', function(msg) {
    addNode(msg);
});

/* Print information to console for debuging */
socket.on('debug', function(msg) {
    console.log(msg);
});

/* User Events */

network.on('hoverNode', function(properties) {
	var hoveredNodes = nodes.get(properties.node);
	var info = document.getElementById('info').innerHTML = 
			JSON.stringify(hoveredNodes);
});

network.on('blurNode', function(properties) {
	var hoveredNodes = nodes.get(properties.node);
	document.getElementById('info').innerHTML = '';
});
