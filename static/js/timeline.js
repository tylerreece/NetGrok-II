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
