/*
timeline.js
XE401/XE402 - NetGrok II
Tyler Reece, Dan Young, Matt Kim, Josh Balba
United States Military Academy
*/

var container = document.getElementById('timeline');


var items = new vis.DataSet([
	{id: 1, content: '<b>Session Start</b>', start: new Date()},
]);


var options = {};

  
var timeline = new vis.Timeline(container, items, options);

var socket = io.connect('http://' + document.domain + ':' + location.port);

/* On connect message to console */
socket.on('connect', function() {
        console.log("Client connected successfully!");
        console.log(navigator.userAgent);
        socket.emit('client connected', {userAgent: navigator.userAgent});
});

/* Handle creation of new node */
socket.on('new node', function(msg) {

        var json_obj = JSON.parse(msg);
	var url = json_obj.host;
        var cont = document.createElement('div');
	var favicon = document.createElement('img');
	favicon.src = 'https://' + url + '/favicon.ico';
	favicon.style.width = '35px';
	favicon.style.height='35px';
	cont.appendChild(favicon);
	cont.appendChild(document.createElement('br'));
	var boldText = document.createElement('b');
        boldText.innerHTML = url;
        cont.appendChild(boldText);
	time = json_obj['time_start'];
	var request = {content: cont, start: time};
	items.add(request);
});

/* Print information to console for debuging */
socket.on('debug', function(msg) {
        console.log(msg);
});
