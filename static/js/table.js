/* 
table.js
XE401/XE402 - NetGrok II
Tyler Reece, Dan Young, Matt Kim, Josh Balba
United States Military Academy
*/


/* Connect to socket */
var socket = io.connect('http://' + document.domain + ':' + location.port);

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


/* Update table */
socket.on('new node', function(msg) {
	console.log(msg);
	var json_obj = JSON.parse(msg);
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
	console.log(newRow);		
	document.getElementById('table').innerHTML += newRow;
});
