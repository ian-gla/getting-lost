document.getElementById('map').style.cursor = '' //(reset)

const dialogM = document.querySelector("#markers");
const closeButtonM = document.querySelector("#markers > button:nth-child(2)");
const proceedButtonM = document.querySelector("#markers > button:nth-child(3)");
const dialogS = document.querySelector("#submit");
const closeButtonS = document.querySelector("#submit > button:nth-child(2)");
const proceedButtonS = document.querySelector("#submit > button:nth-child(3)");
var max_dist = 1; // distance in kn points must be within
var min_dist = 0; // distance in kn points must be beyond
var min_angle = 130; // max angle between segments
var pointsGood = false;
var center = [55.872505281511444, -4.290044317503135]
var labels = {};
var names = {};
var name;
labels["start"] = "Last known pos";
labels["lost"] = "got lost";
labels["end"] = "Next known pos";
for (key in labels) {
  names[labels[key]] = key;
}
closeButtonM.addEventListener("click", () => {
  pointsGood = false;
  dialogM.close();
});
proceedButtonM.addEventListener("click", () => {
  pointsGood = true;
  dialogM.close();
  displayChecks();
});
closeButtonS.addEventListener("click", () => {
  dialogS.close();
  //continue to allow edits to the info pages!
});
proceedButtonS.addEventListener("click", () => {
  dialogS.close();
  //submit the data!
  cleanup();
});
function createButtons(div) {
  var target = document.querySelector("#" + div);
  var startB = document.createElement("button");
  startB.innerHTML = labels["start"];
  startB.class = "button";
  startB.id = 'start';
  startB.onclick = clicked;
  target.appendChild(startB);
  var lostB = document.createElement("button");
  lostB.innerHTML = labels["lost"];
  lostB.class = "button";
  lostB.id = "lost";
  lostB.onclick = clicked;
  target.appendChild(lostB);
  var endB = document.createElement("button");
  endB.innerHTML = labels["end"];
  endB.class = "button";
  endB.id = "end";
  endB.onclick = clicked;
  target.appendChild(endB);
}

function clicked(e) {
  addMarker(e.target.innerHTML);
}
var buttons = document.querySelector("#buttonBar");
var info = document.querySelector("#info");
var data_entry = document.querySelector('#data-entry-panel');
var data2_entry = document.querySelector('#more-data');

data_entry.style.display = 'none';
data2_entry.style.display = 'none';
var osm = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
});

var osmHOT = L.tileLayer('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors, Tiles style by Humanitarian OpenStreetMap Team hosted by OpenStreetMap France'});

var osmTopo = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
	maxZoom: 17,
	attribution: 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
});

var osmCAT = L.tileLayer('https://tile.openstreetmap.bzh/ca/{z}/{x}/{y}.png', {
	maxZoom: 19,
	attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Tiles courtesy of <a href="https://www.openstreetmap.cat" target="_blank">Breton OpenStreetMap Team</a>'
});

var osmBright = L.tileLayer('https://tiles.stadiamaps.com/tiles/osm_bright/{z}/{x}/{y}{r}.{ext}', {
	minZoom: 0,
	maxZoom: 20,
	attribution: '&copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
	ext: 'png'
});

var CartoDB_Positron = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
	attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
	subdomains: 'abcd',
	maxZoom: 20
});

var CartoDB_Voyager = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
	attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
	subdomains: 'abcd',
	maxZoom: 20
});


var baseMaps = {
    "OpenStreetMap": osm,
    "OpenStreetMap.HOT": osmHOT,
    "OpenTopo": osmTopo,
    "OSM CAT": osmCAT,
    "OSM Bright": osmBright,
    "Carto Positron": CartoDB_Positron,
    "Carto Voyager": CartoDB_Voyager,
};

var map = L.map("map",{
  center: center,
  zoom: 17,
  layers: osm, 
});

var layerControl = L.control.layers(baseMaps, "", {position:'topleft'}).addTo(map);

var geocoder = L.Control.geocoder({
  defaultMarkGeocode: false,
  position: 'topleft',
}).on('markgeocode', function(e) {
    var ll = e.geocode.center;
    map.panTo(ll);
  });
geocoder.addTo(map)._expand();
// move to users location
if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(function(position) {
    latit = position.coords.latitude;
    longit = position.coords.longitude;
    // move the map to have the location in its center
    center = [latit, longit];
    map.panTo(new L.LatLng(latit, longit));
    positions = {};
  });
}

L.control.scale({"position":"bottomright"}).addTo(map);

createButtons("buttonBar");

var positions = {};
function addMarker(n) {
  name = n;
  if (!positions[names[name]]) {
    L.DomUtil.addClass(map._container,`${names[name]}-flag-cursor-enabled`);
    map.on('click', setMarker)
  } else {
    map.panTo(positions[names[name]].getLatLng());
  }
  if(Object.values(positions).length == 3){
      pointsValid();
      if(pointsGood){
      displayChecks();
    }
  }
}

  function mapClickListen(e){
    console.log("Before click: "+e.target.dragging.enabled())
    e.target.dragging.enable();
    console.log("After click: "+e.target.dragging.enabled())
  }

function setMarker(e){
  map.removeEventListener("click", setMarker , false);
  if (!positions[names[name]]) {
  const colors = {
    start:
    "https://raw.githubusercontent.com/planetfederal/geosilk/master/silk/flag_green.png",
    end:
    "https://raw.githubusercontent.com/planetfederal/geosilk/master/silk/flag_red.png",
    lost:
    "https://raw.githubusercontent.com/planetfederal/geosilk/master/silk/flag_blue.png"
  };
    var icon = L.icon({
      iconUrl: colors[names[name]],
      iconSize: [30, 30]
    });
  lat = e.latlng.lat;
  lon = e.latlng.lng;

  //Add a marker to show where you clicked.
  var marker = new L.marker([lat,lon], {
    icon: icon,
    title: labels[names[name]],
    draggable: false,
    clickable: true,
    autoPan: true,
  }).addTo(map);
  marker.on('click', mapClickListen);
  /* this is all to work around dragend triggering a click
   * see https://gis.stackexchange.com/questions/190049/leaflet-map-draggable-marker-events
   */
  marker.on('dragstart', function(e) {
    console.log('marker dragstart event');
    marker.off('click', mapClickListen);
  });
  marker.on('dragend', (e) => {
    console.log("Before end "+e.target.dragging.enabled())
    e.target.dragging.disable();
    console.log("After end "+e.target.dragging.enabled())
    pointsValid();
    marker.on('click', mapClickListen);
  });
  positions[names[name]] = marker;

  } else {
    map.panTo(positions[names[name]].getLatLng());
  }
  //document.getElementById('map').style.cursor = '' //(reset)
  L.DomUtil.removeClass(map._container,`${names[name]}-flag-cursor-enabled`);
  pointsValid()
}

function cleanup(){ 
  if(data_form!=null)
    clearForm(data_form);
  if(data2_form!=null)
    clearForm(data2_form);
  info.style.display='block';
  buttons.style.display = 'block';
  data_entry.style.display='none';
  data2_entry.style.display='none';
  var n = ['start', 'lost', 'end'];
  for(const m of n){
    console.log("got marker: ",m)
    console.log(positions[m])
    map.removeLayer(positions[m]);
  }
  positions = {};

}
function displayChecks(){
    console.log("info off, data 1 on")
    buttons.style.display = 'none';
    info.style.display='none';
    data_entry.style.display='block';
    data_form = document.querySelector("#data-entry-form");
    data2_entry.style.display='none';
  }
  var data_form, data2_form;
function changeView(){
  s= data_entry.getElementsByTagName('select');
  res=false;
  for(var i=0;i<s.length;i++){
    res |= s[i].options[s[i].selectedIndex].value == "";
  }
  if(res){
    alert("Please select values for all the boxes");
  } else {
    data2_entry.style.display='block';
    data2_form = document.querySelector("#more-data-entry-form");
    data_entry.style.display='none';
  }
}

function pointsValid() {
  console.log("points check")

  if(Object.values(positions).length != 3){
    console.log("not enough points in check")
    return;
  }
  var startPos = positions["start"] ? positions["start"].getLatLng() : "";
  var endPos = positions["end"] ? positions["end"].getLatLng() : "";
  var lostPos = positions["lost"] ? positions["lost"].getLatLng() : "";
  var from = turf.point([startPos.lng, startPos.lat]);
  var to = turf.point([endPos.lng, endPos.lat]);
  var lost = turf.point([lostPos.lng, lostPos.lat]);
  var options = {units: "kilometers"}

  var distance1 = turf.distance(from, lost, options);
  var distance2 = turf.distance(to, lost, options);
  var angle = turf.angle(from, lost, to);
  console.log("before: ",angle);
  if(angle > 180){
    angle=360 - angle;
  }
  console.log(angle);
  var too_short = true;
  var too_long = true;
  var too_wide = true;
  var message = "The points you have selected seem to be a little odd, are you sure they are correct?<br>";
  if (distance1 < max_dist && distance2 < max_dist){
    too_long = false;
  } else {
    message += "Your points are too far apart ("+Math.max(distance1, distance2).toFixed(2)+"km)<br>\n";
  }
  if (distance1 > min_dist && distance2 > min_dist){
    too_short = false;
  } else {
    message += "Your points are too close together ("+Math.max(distance1, distance2).toFixed(2)+"km)<br>\n";
  }
  if (angle < min_angle){
    too_wide = false;
  } else {
    message += "The angle "+angle.toFixed(2)+": between your points is too wide<br>\n";
  }


  if (too_long || too_short || too_wide){
    pointsGood = false;
    document.querySelector("#message").innerHTML = message;
    dialogM.showModal();
  } else {
    pointsGood = true;
    displayChecks();
  }

}
function collectData() {
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
  s= data2_entry.getElementsByTagName('select');
  for(var i=0;i<s.length;i++){
    res[s[i].id] = s[i].options[s[i].selectedIndex].value;
  }
  s= data2_entry.getElementsByTagName('textarea');
  for(var i=0;i<s.length;i++){
    res[s[i].id] = s[i].value;
  }
  //set res data nicely!

  let html = `<ul>`;
  for (const [key, value] of Object.entries(res)) {
    html += `<li>${key} = ${value}</li>`;
  }

  html += `</ul>`;
  document.querySelector("#submessage").innerHTML = html;
  dialogS.showModal();
}


function checkData(){
  s= data2_entry.getElementsByTagName('select');
  res=false;
  for(var i=0;i<s.length;i++){
    res |= s[i].options[s[i].selectedIndex].value == "";
  }
  if(res){
    alert("Please select values for all the boxes");
  } else {
    collectData();
  }
}

function clearForm(myFormElement) {

  var elements = myFormElement.elements;

  myFormElement.reset();

  for(i=0; i<elements.length; i++) {

  field_type = elements[i].type.toLowerCase();

  switch(field_type) {

    case "text":
    case "password":
    case "textarea":
          case "hidden":

      elements[i].value = "";
      break;

    case "radio":
    case "checkbox":
        if (elements[i].checked) {
          elements[i].checked = false;
      }
      break;

    case "select-one":
    case "select-multi":
                elements[i].selectedIndex = -1;
      break;

    default:
      break;
  }
}
}

