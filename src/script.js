function createList(div) {
  const reasons = {
    exits: "Number of Exits",
    angular: "Angular Distance between Exits",
    pedestrian: "Pedestrian Flows",
    transport: "Transport Flows",
    visibility: "Visibility",
    decisions: "Number of Dicision Points",
    landmarks: "Number of Landmarks",
    orientation: "Self Orientation Skills",
    context: "Personal Context",
    turns: "Number of Turning Points",
    complexity: "City/Small Scale Complexity",
    amap: "Access to Reliable Map",
    familiarity: "Familiaraty",
    names: "Name Similarity"
  };
  var ul = document.createElement("ul");
  for (const [key, value] of Object.entries(reasons)) {
    //  generate id
    const id = key;

    // create a label
    const label = document.createElement("label");
    label.setAttribute("for", id);

    // create a checkbox
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.name = "reason";
    checkbox.value = key;
    checkbox.id = id;

    // place the checkbox inside a label
    label.appendChild(checkbox);
    // create text node
    label.appendChild(document.createTextNode(value));
    // add the label to the root
    li = document.createElement("li");
    li.appendChild(label);
    ul.appendChild(li);
  }
  var target = document.querySelector("#" + div);
  target.appendChild(ul);

  ta = document.createElement("TEXTAREA");

  ta.cols = 100;
  ta.rows = 10;
  ta.placeholder = "Any other information";
  target.appendChild(ta);
}

function createButtons(div) {
  var target = document.querySelector("#" + div);
  var start = document.createElement("button");
  start.innerHTML = "start";
  start.class = "button";
  start.onclick = clicked;
  target.appendChild(start);
  var lost = document.createElement("button");
  lost.innerHTML = "lost";
  lost.class = "button";
  lost.onclick = clicked;
  target.appendChild(lost);
  var end = document.createElement("button");
  end.innerHTML = "end";
  end.class = "button";
  end.onclick = clicked;
  target.appendChild(end);
}

function clicked(e) {
  addMarker(e.target.innerHTML);
}
var map = L.map("map").setView([51.505, -0.09], 13);
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution:
    '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

createList("checks");
createButtons("mapbox");
createSubmit("right");
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

  if (!positions[name]) {
    var point = map.getCenter();

    var icon = L.icon({
      iconUrl: colors[name],
      iconSize: [30, 30]
    });
    var marker = new L.marker(point, {
      icon: icon,
      title: name,
      draggable: true,
      autoPan: true
    }).addTo(map);
    positions[name] = marker;
  } else {
    console.log("moving to ", positions[name].getLatLng());
    map.panTo(positions[name].getLatLng());
  }
}

function submit() {
  var start = positions["start"] ? positions["start"].getLatLng() : "";
  var end = positions["end"] ? positions["end"].getLatLng() : "";
  var lost = positions["lost"] ? positions["lost"].getLatLng() : "";
  res = {
    start: start,
    end: end,
    lost: lost
  };
  boxes = getCheckedBoxes("reason");
  var reasons = [];
  if (boxes) {
    for (const box of boxes) {
      reasons.append(box.value);
    }
  }
  res["reasons"] = reasons;
  if (ta.value) {
    res["text"] = ta.value;
  }
  alert(JSON.stringify(res));
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
  var start = document.createElement("button");
  start.innerHTML = "submit";
  start.class = "button";
  start.onclick = submit;
  target.appendChild(start);
}
