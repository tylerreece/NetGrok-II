/*
timeline.js
XE401/XE402 - NetGrok II
Tyler Reece, Dan Young, Matt Kim, Josh Balba
United States Military Academy
*/

//'2015-01-23T14:00:00.200Z'

function formatFullDate(year, month, day, hour, min, sec, ms) {
  var formatted = '';
  var newMonth = month + 1;
  var newDay = day;
  var newSec = sec;
  var newMin = min;
  if(newMonth.length < 2) newMonth = '0' + String(newMonth);
  if(newDay.length < 2) newDay = '0' + String(newDay);
  if(newSec.length < 2) newSec = '0' + String(newSec); 
  if(newMin.length < 2) newMin ='0' + String(newMin);
  formatted += year + '-' + newMonth + '-' + newDay + 'T' + hour + ':' + newMin + ':' + newSec + '.' + ms;
  return formatted;
}


var container = document.getElementById('timeline');

var date = new Date();
var year = String(date.getFullYear());
var month = String(date.getMonth());
var day = String(date.getDate());
var hour = String(date.getHours());
var min = String(date.getMinutes());
var sec = String(date.getSeconds());
var mil = String(date.getMilliseconds());


var items = new vis.DataSet([
	{id: 1, content: 'item1', start: '2019-02-14'},
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
socket.on('new item', function(msg) {

        var json_obj = JSON.parse(msg);
	var url = json_obj.host;
        var cont = document.createElement('div');
	cont.appendChild(document.createTextNode(url));
	cont.appendChild(document.createElement('br'));
	var favicon = document.createElement('img');
	favicon.src = 'https://' + url + '/favicon.ico';
	favicon.style.width = '35px';
	favicon.style.height='35px';
	cont.appendChild(favicon);
	var request = {content: cont, fromCache: deets.fromCache, ip: deets.ip, start: time};//, image: 'https://' + url + '/favicon.ico', shape:'image'};
	console.log(request.start);
	items.add(request);
	items.add({label: '<b>' + json_obj.host + '</b>', image: 'https://' + json_obj.host + '/favicon.ico', shape: 'image'});
});

/* Print information to console for debuging */
socket.on('debug', function(msg) {
        console.log(msg);
});
