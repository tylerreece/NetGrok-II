var rowsSeen = new Set();

/* Create table header */
var header = "<table><tr>" +
    "<th>Host</th>" +
    "<th>Protocol</th>" +
    "<th>Source IP</th>" +
    "<th>Source Port</th>" +
    "<th>Destination IP</th>" +
    "<th>Destination Port</th>" +
    "<th>Time Start</th>" +
    "<th>Time End</th>" +
    "<th>Download</th>" +
    "<th>Upload</th>" +
    "</tr></table>";

document.getElementById('table').innerHTML = header;

/* Table Functions */
function addRow(json_string) {
    var json_obj = JSON.parse(json_string);
    if(!rowsSeen.has(json_obj.host)) {
		rowsSeen.add(json_obj.host);	
		var newRow = "<table><tr>" +
        	"<td>" + json_obj.host + "</td>" +
        	"<td>" + json_obj.protocol + "</td>" +
        	"<td>" + json_obj.src_ip + "</td>" +
        	"<td>" + json_obj.src_port + "</td>" +
        	"<td>" + json_obj.dst_ip + "</td>" +
        	"<td>" + json_obj.dst_port + "</td>" +
        	"<td>" + json_obj.time_start + "</td>" +
        	"<td>" + json_obj.time_end + "</td>" +
        	"<td>" + json_obj.download + "</td>" +
        	"<td>" + json_obj.upload + "</td>" +
        	"</tr></table>";
    	document.getElementById('table').innerHTML += newRow;
	}
}

function addRows(json_strings) {
    var j_strings = json_strings.split('}');
    for (var i = 0; i < j_strings.length - 1; i++) {
        var newString = (j_strings[i] + '}').split("'").join('"');
        addRow(newString);
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

/* Populate table on receipt of current state */
socket.on('whole graph', function(msg) {
    addRows(msg);
});

/* Update table */
socket.on('new node', function(msg) {
    addRow(msg);
});
