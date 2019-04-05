var container = document.getElementById('timeline');

var options = {
	zoomMin: 1,
	horizontalScroll: true,
	orientation: 'top',
	zoomKey: 'ctrlKey',
};

var items = new vis.DataSet([{
    id: 0,
    content: '<b>Server Start</b>',
    start: new Date()
}]);

var timeline = new vis.Timeline(container, items, options);

/* Timeline Functions */
function addItem(json_string) {
    var json_obj = JSON.parse(json_string);
    var url = json_obj.host;
	var cont = document.createElement('div');
    var favicon = document.createElement('img');
    favicon.src = 'https://' + url + '/favicon.ico';
    favicon.onerror="this.src='https://i.dlpng.com/static/png/6818_preview.png';";
	favicon.style.width = '35px';
    favicon.style.height = '35px';
    cont.appendChild(favicon);
    cont.appendChild(document.createElement('br'));
    var boldText = document.createElement('b');
    boldText.innerHTML = url;
    cont.appendChild(boldText);
    time = json_obj['time_start'];
    var request = {
		name: url, 
		content: cont,
       	start: time
    };
	items.add(request);
}

function addItems(json_strings) {
    var j_strings = json_strings.split('}');
    for (var i = 0; i < j_strings.length - 1; i++) {
        var newString = (j_strings[i] + '}').split("'").join('"');
        addItem(newString);
    }
}

var socket = io.connect('http://' + document.domain + ':' + location.port);

/* On connect message to console */
socket.on('connect', function() {
    socket.emit('send whole graph', {
        userAgent: navigator.userAgent
    });
});

/* On receipt of whole graph */
socket.on('whole graph', function(msg) {
    addItems(msg);
});

/* On receipt of age off */
socket.on('age off', function(msg) {
	var item = items.get({
	filter: function (item) {
		return (item.name == msg);
	}
});
	items.remove(item);

});

/* On database flushed message */
socket.on('database flushed', function() {
	location.reload();
});


/* Handle creation of new node */
socket.on('new node', function(msg) {
    addItem(msg);
});

/* Print information to console for debuging */
socket.on('debug', function(msg) {
    console.log(msg);
});
