document.getElementById('map').style.cursor = '' //(reset)

const dialogM = document.querySelector("#markers");
const closeButtonM = document.querySelector("#markers > button:nth-child(2)");
const proceedButtonM = document.querySelector("#markers > button:nth-child(3)");
const dialogS = document.querySelector("#submit");
const closeButtonS = document.querySelector("#submit > button:nth-child(2)");
const proceedButtonS = document.querySelector("#submit > button:nth-child(3)");
const icons = {
    start: "assets/flag_green.png",
    end: "assets/flag_red.png",
    lost: "assets/flag_blue.png"
};
const colors = {
    start: '#3A6152',
    end: '#ff6057',
    lost: '#81cdff',
}
var max_dist = 1; // distance in kn points must be within
var min_dist = 0; // distance in kn points must be beyond
var min_angle = 130; // max angle between segments
var pointsGood = false;
var center = [55.872505281511444, -4.290044317503135]
var labels = {};
var names = {};
var circles = {};
var name;
var lastClick = "";
labels["start"] = "Last known position";
labels["lost"] = "Where you got lost";
labels["end"] = "Next known position";
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
    displayButton();
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
    attribution: '© OpenStreetMap contributors, Tiles style by Humanitarian OpenStreetMap Team hosted by OpenStreetMap France'
});

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

var map = L.map("map", {
    center: center,
    zoom: 17,
    layers: osm,
});

var layerControl = L.control.layers(baseMaps, "", {
    position: 'topleft'
}).addTo(map);

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

L.control.scale({
    "position": "bottomright"
}).addTo(map);

createButtons("buttonBar");

var positions = {};
var lat_lngs = {};

function addMarker(n) {
    name = n;

    if (lastClick) {
        L.DomUtil.removeClass(map._container, `${lastClick}-flag-cursor-enabled`);
    }


    lastClick = names[name];
    if (!positions[names[name]]) {
        L.DomUtil.addClass(map._container, `${names[name]}-flag-cursor-enabled`);
        map.on('click', setMarker)
    } else {
        map.panTo(positions[names[name]].getLatLng());
    }
    if (Object.values(positions).length == 3) {
        pointsValid();
        if (pointsGood) {
            displayButton();
        }
    }
}

function mapClickListen(e) {
    console.log("Before click: " + e.target.dragging.enabled())
    e.target.dragging.enable();
    console.log("After click: " + e.target.dragging.enabled())
}


function addCircle(marker) {
    name = names[marker.options.title];
    if (!circles[name]) {
        const popup = document.createElement("div");
        popup.innerHTML = 'adjust radius: ';
        
        const up = document.createElement("button");
        up.id = name+"_up_button";
        up.innerHTML = `<i id='${name}_up' class="arrow up"></i>`;
        up.addEventListener('click', function(e) {
          id = e.target.id.substring(0,e.target.id.indexOf('_'));
          circles[id].setRadius(circles[id].getRadius()+10);
        });
        popup.appendChild(up);
        const down = document.createElement("button");
        down.id = name+"_down_button";
        down.innerHTML = `<i id='${name}_down' class="arrow down"></i>`;
        down.addEventListener('click', function(e) {
          id = e.target.id.substring(0,e.target.id.indexOf('_'));
          radius = circles[id].getRadius();
          if(radius > 10){
            circles[id].setRadius(radius - 10);
          }
        });
        popup.appendChild(down);
        circle = L.circle(marker.getLatLng(), 100, {
            color: colors[name],
            fillcolor: colors[name],
            fillopacity: 0.5,

        }).bindPopup(popup).addTo(map);
        circles[name] = circle;

        marker.on('drag', (e) => {
            circles[names[e.target.options.title]].setLatLng(e.latlng);
        });
    }
}

function setMarker(e) {
    map.removeEventListener("click", setMarker, false);
    if (!positions[names[name]]) {
        var icon = L.icon({
            iconUrl: icons[names[name]],
            iconSize: [30, 30],
            iconAnchor: [20, 27],
        });
        lat = e.latlng.lat;
        lon = e.latlng.lng;

        //Add a marker to show where you clicked.
        var latlng = L.latLng(lat, lon);
        var marker = new L.marker(latlng, {
            icon: icon,
            title: labels[names[name]],
            draggable: true,
            clickable: true,
            autoPan: true,
        }).addTo(map);
        marker.on('dblclick', (e) => {
            addCircle(e.target);
        });
        marker.on('click', mapClickListen);
        /* this is all to work around dragend triggering a click
         * see https://gis.stackexchange.com/questions/190049/leaflet-map-draggable-marker-events
         */
        marker.on('dragstart', function(e) {
            console.log('marker dragstart event');
            marker.off('click', mapClickListen);
        });
        marker.on('dragend', (e) => {
            console.log("Before end " + e.target.dragging.enabled())
            e.target.dragging.disable();
            console.log("After end " + e.target.dragging.enabled())
            pointsValid();
            marker.on('click', mapClickListen);
        });
        positions[names[name]] = marker;

    } else {
        map.panTo(positions[names[name]].getLatLng());
    }
    //document.getElementById('map').style.cursor = '' //(reset)
    L.DomUtil.removeClass(map._container, `${names[name]}-flag-cursor-enabled`);
    pointsValid()
}

function cleanup() {
    if (data_form != null)
        clearForm(data_form);
    if (data2_form != null)
        clearForm(data2_form);
    info.style.display = 'block';
    document.getElementById('continue').remove();
    buttonAdded = false;

    buttons.style.display = 'block';
    data_entry.style.display = 'none';
    data2_entry.style.display = 'none';
    var n = ['start', 'lost', 'end'];
    for (const m of n) {
        map.removeLayer(positions[m]);
        if (circles[m]) {
            map.removeLayer(circles[m]);
        }
    }
    positions = {};
  circles = {};

}

function displayChecks() {
    
    var n = ['start', 'lost', 'end'];
    for (const m of n) {
        positions[m].off("click");
        positions[m].off('dblclick');
        positions[m].off('dragstart');
        positions[m].dragging.disable();
        if (circles[m]) {
          circles[m].off("click");
        }
    }
    buttons.style.display = 'none';
    info.style.display = 'none';
    data_entry.style.display = 'block';
    data_form = document.querySelector("#data-entry-form");
    data2_entry.style.display = 'none';
}
var data_form, data2_form;

function changeView() {
    s = data_entry.getElementsByTagName('select');
    res = false;
    for (var i = 0; i < s.length; i++) {
        res |= s[i].options[s[i].selectedIndex].value == "";
    }
    if (res) {
        alert("Please select values for all the boxes");
    } else {
        data2_entry.style.display = 'block';
        data2_form = document.querySelector("#more-data-entry-form");
        data_entry.style.display = 'none';
    }
}

function pointsValid() {
    if (Object.values(positions).length != 3) {
        console.log("not enough points in check")
        return;
    }
    var startPos = positions["start"] ? positions["start"].getLatLng() : "";
    var endPos = positions["end"] ? positions["end"].getLatLng() : "";
    var lostPos = positions["lost"] ? positions["lost"].getLatLng() : "";
    var from = turf.point([startPos.lng, startPos.lat]);
    var to = turf.point([endPos.lng, endPos.lat]);
    var lost = turf.point([lostPos.lng, lostPos.lat]);
    var options = {
        units: "kilometers"
    }

    var distance1 = turf.distance(from, lost, options);
    var distance2 = turf.distance(to, lost, options);
    var angle = turf.angle(from, lost, to);
    console.log("before: ", angle);
    if (angle > 180) {
        angle = 360 - angle;
    }
    console.log(angle);
    var too_short = true;
    var too_long = true;
    var too_wide = true;
    var message = "The points you have selected seem to be a little odd, are you sure they are correct?<br>";
    if (distance1 < max_dist && distance2 < max_dist) {
        too_long = false;
    } else {
        message += "Your points are too far apart (" + Math.max(distance1, distance2).toFixed(2) + "km)<br>\n";
    }
    if (distance1 > min_dist && distance2 > min_dist) {
        too_short = false;
    } else {
        message += "Your points are too close together (" + Math.max(distance1, distance2).toFixed(2) + "km)<br>\n";
    }
    if (true /*angle < min_angle*/) {
        too_wide = false;
    } else {
        message += "The angle " + angle.toFixed(2) + ": between your points is too wide<br>\n";
    }


    if (too_long || too_short || too_wide) {
        pointsGood = false;
        document.querySelector("#message").innerHTML = message;
        dialogM.showModal();
    } else {
        pointsGood = true;
        displayButton();
    }

}

var buttonAdded = false;
function displayButton() {
    // add a button to display the questions when they are happy with the map locations
    if (!buttonAdded) {
        const div = document.createElement("div");
        div.id = 'continue';
        div.innerHTML = "<hr/><p>If you are happy with the position of the points (and circles) you can go on to the survey about factors that may have contributed to your getting lost.</p>"
        const mvButton = document.createElement("button");
        mvButton.innerHTML = "Continue to survey";
        mvButton.addEventListener("click", displayChecks);
        div.append(mvButton)

        info.append(div);
        buttonAdded = true;
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
    res["start_radius"] = circles['start'] ? circles['start'].getRadius() : 0;
    res["lost_radius"] = circles['lost'] ? circles['lost'].getRadius() : 0;
    res["end_radius"] = circles['end'] ? circles['end'].getRadius() : 0;
    s = data_entry.getElementsByTagName('select');
    for (var i = 0; i < s.length; i++) {
        res[s[i].id] = s[i].options[s[i].selectedIndex].value;
    }
    s = document.getElementById('nav-skill');
    res[s.id] = s.value;

    s = data2_entry.getElementsByTagName('select');
    for (var i = 0; i < s.length; i++) {
        res[s[i].id] = s[i].options[s[i].selectedIndex].value;
    }
    s = document.getElementById('familiarity');
    res[s.id] = s.value;

    s = data2_entry.getElementsByTagName('textarea');
    for (var i = 0; i < s.length; i++) {
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


function checkData() {
    s = data2_entry.getElementsByTagName('select');
    res = false;
    for (var i = 0; i < s.length; i++) {
        res |= s[i].options[s[i].selectedIndex].value == "";
    }
    if (res) {
        alert("Please select values for all the boxes");
    } else {
        collectData();
    }
}

function clearForm(myFormElement) {

    var elements = myFormElement.elements;

    myFormElement.reset();

    for (i = 0; i < elements.length; i++) {

        field_type = elements[i].type.toLowerCase();

        switch (field_type) {

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
