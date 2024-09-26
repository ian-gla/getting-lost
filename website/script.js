
var labels = {};
var names = {};
labels["start"] = "Last known pos";
labels["lost"] = "got lost";
labels["end"] = "Next known pos";
for (key in labels) {
  names[labels[key]] = key;
}
function createButtons(div) {
  var target = document.querySelector("#" + div);
  var startB = document.createElement("button");
  startB.innerHTML = labels["start"];
  startB.class = "button";
  startB.onclick = clicked;
  target.appendChild(startB);
  var lostB = document.createElement("button");
  lostB.innerHTML = labels["lost"];
  lostB.class = "button";
  lostB.onclick = clicked;
  target.appendChild(lostB);
  var endB = document.createElement("button");
  endB.innerHTML = labels["end"];
  endB.class = "button";
  endB.onclick = clicked;
  target.appendChild(endB);
}

function clicked(e) {
  addMarker(e.target.innerHTML);
}
var info = document.querySelector("#info");
var data_entry = document.querySelector('#data-entry-panel');
var data2_entry = document.querySelector('#more-data');
data_entry.style.visibility = 'hidden';
data2_entry.style.visibility = 'hidden';
var map = L.map("map").setView([51.505, -0.09], 13);
tiles = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
tiles = "https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png"
L.tileLayer(tiles, {
  maxZoom: 19,
  attribution:
    '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);
const search = new GeoSearch.GeoSearchControl({
  provider: new GeoSearch.OpenStreetMapProvider()
});

map.addControl(search);
if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(function(position) {
    latit = position.coords.latitude;
    longit = position.coords.longitude;
    // move the map to have the location in its center
    map.panTo(new L.LatLng(latit, longit));
});
}
createButtons("buttonBar");
createSubmit("checks");
var positions = {};
function addMarker(name) {
  const colors = {
    start:
      "https://raw.githubusercontent.com/planetfederal/geosilk/master/silk/flag_green.png",
    end:
      "https://raw.githubusercontent.com/planetfederal/geosilk/master/silk/flag_red.png",
    lost:
      "https://raw.githubusercontent.com/planetfederal/geosilk/master/silk/flag_blue.png"
  };

  if (!positions[names[name]]) {
    var point = map.getCenter();

    var icon = L.icon({
      iconUrl: colors[names[name]],
      iconSize: [30, 30]
    });
    var marker = new L.marker(point, {
      icon: icon,
      title: labels[names[name]],
      draggable: true,
      autoPan: true
    }).addTo(map);
    positions[names[name]] = marker;
  } else {
    map.panTo(positions[names[name]].getLatLng());
  }
  if(Object.values(positions).length == 3){
    displayChecks();
  }
}

function reset(){ 
    info.style.visibility='visible';
    checks.style.visibility='hidden';
    data_entry.style.visibility='hidden';
  var n = ['start', 'lost', 'end'];
  for(const m of n){
    console.log(m)
    console.log(positions[m])
    map.removeLayer(positions[m]);
  }
  positions = {};

}
function displayChecks(){
    info.style.visibility='hidden';
    data_entry.style.visibility='visible';
}
function changeView(){
    data2_entry.style.visibility='visible';
    data_entry.style.visibility='hidden';
}

function submit() {
  var startPos = positions["start"] ? positions["start"].getLatLng() : "";
  var endPos = positions["end"] ? positions["end"].getLatLng() : "";
  var lostPos = positions["lost"] ? positions["lost"].getLatLng() : "";
  res = {
    start: startPos,
    end: endPos,
    lost: lostPos
  };
  s= data_entry.getElementsByTagName('select');
  for(var i=0;i<s.length;i++){
    res[s[i].id] = s[i].options[s[i].selectedIndex].value;
  }
  boxes = getCheckedBoxes("reason");
  var reasons = [];
  if (boxes) {
    for (const box of boxes) {
      reasons.push(box.value);
    }
  }
  res["reasons"] = reasons;
  if (ta.value) {
    res["text"] = ta.value;
  }
  alert(JSON.stringify(res));
  reset();
}

function getCheckedBoxes(chkboxName) {
  var checkboxes = document.getElementsByName(chkboxName);
  var checkboxesChecked = [];
  // loop over them all
  for (var i = 0; i < checkboxes.length; i++) {
    // And stick the checked ones onto an array...
    if (checkboxes[i].checked) {
      checkboxesChecked.push(checkboxes[i]);
    }
  }
  // Return the array if it is non-empty, or null
  return checkboxesChecked.length > 0 ? checkboxesChecked : null;
}

function createSubmit(div) {
  var target = document.querySelector("#" + div);
  var startEl = document.createElement("button");
  startEl.innerHTML = "submit";
  startEl.class = "button";
  startEl.onclick = submit;
  target.appendChild(startEl);
}

