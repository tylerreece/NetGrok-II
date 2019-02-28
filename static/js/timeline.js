/*
timeline.js
XE401/XE402 - NetGrok II
Tyler Reece, Dan Young, Matt Kim, Josh Balba
United States Military Academy
*/

var container = document.getElementById('timeline');


var options = {};

var items = new vis.DataSet([{id: 0, content: '<b>Server Start</b>', start: new Date()}]);
  
var timeline = new vis.Timeline(container, items, options);


/* Timeline Functions */
function addItem(json_string) {
	var json_obj = JSON.parse(json_string);
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
}

function addItems(json_strings) {
        var j_strings = json_strings.split('}');
        //console.log(j_strings);
        for(var i = 0; i < j_strings.length-1; i++) {
                var newString = (j_strings[i] + '}').split("'").join('"');
                console.log(newString);
                addItem(newString);
        }
}




var socket = io.connect('http://' + document.domain + ':' + location.port);

/* On connect message to console */
socket.on('connect', function() {
        console.log("Client connected successfully!");
        console.log(navigator.userAgent);
        socket.emit('send whole graph', {userAgent: navigator.userAgent});
});

socket.on('whole graph', function (msg) {
	addItems(msg);
});

/* Handle creation of new node */
socket.on('new node', function(msg) {
	addItem(msg);
});

/* Print information to console for debuging */
socket.on('debug', function(msg) {
        console.log(msg);
});
