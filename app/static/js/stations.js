async function getJSON(path) {
    return fetch(path, {method: 'GET'})
        .then(response => {
            return response.json()
        });
}

let eventListeners = [];

function new_station_v2(index) {
    let el = document.createElement('div');
    el.id = 'station_' + index;
    el.className = 'col col-3 custom-box2 p-1 mb-2';
    el.innerHTML =
        "           <button class='btn btn-sm btn-outline-danger position-absolute btn-square-xs offset-p1' title='Supprimer cette station' onclick='deleteStation(" + (index - 1) + ")' type='button'>" +
        "               ✕" +
        "           </button>" +
        "           <div class='row mb-1'>\n" +
        "               <label title='Emplacement de la station " + index + "' for='emplacement" + index + "' class='col-sm-6 col-form-label col-form-label-sm'>Emplacement</label>\n" +
        "               <div class='col-sm-4'>\n" +
        "                   <input type='number' class='form-control form-control-sm simu_form' id='emplacement" + index + "' name='emplacement" + index + "' required value='0' min='0'>\n" +
        "                   <div class='invalid-feedback'>Veuillez spécifier un emplacement pour la station.</div>\n" +
        "               </div>\n" +
        "           </div>\n" +
        "           <div class='row mb-1'>\n" +
        "               <label title='Nombre de bornes de type A' for='station0' class='col-sm-6 col-form-label col-form-label-sm'>Bornes Types A</label>\n" +
        "               <div class='col-sm-4'>\n" +
        "                   <input type='number' class='form-control form-control-sm simu_form' id='station" + index + "_typeA' name='station" + index + "_typeA' required value='0' min='0'>\n" +
        "                   <div class='invalid-feedback'>Veuillez spécifier une quantité de bornes de type A.</div>\n" +
        "               </div>\n" +
        "           </div>\n" +
        "           <div class='row mb-1'>\n" +
        "               <label title='Nombre de bornes de type B' for='station0' class='col-sm-6 col-form-label col-form-label-sm'>Bornes Types B</label>\n" +
        "               <div class='col-sm-4'>\n" +
        "                   <input type='number' class='form-control form-control-sm simu_form' id='station" + index + "_typeB' name='station" + index + "_typeB' required value='0' min='0'>\n" +
        "                   <div class='invalid-feedback'>Veuillez spécifier une quantité de bornes de type B.</div>\n" +
        "               </div>\n" +
        "           </div>"
    ;

    return el;
}

let route = [ // A6
    44, 42,
    44, 71,
    67, 96,
    67, 123,
    180, 236,
    223, 236,
    306, 318,
    306, 517
];

const scale = 1.35;
let canvasElem = document.getElementById('map_canvas');

// stations de recharges
const nStationsElem = document.getElementById('n_stations'); // input
const stationsElem = document.getElementById('stations');
let cur_stations = Array.from(stationsElem.children);
eventListeners.length = cur_stations.length;
// console.log(cur_stations);

/*
async function set_stations() {
    stations_json = await getJSON('/stations/get/' + configStationElem.value);
    let bornes = stations_json["stations"];
    nStationsElem.value = bornes.length;
    console.log(bornes);
    await updateStationsElem2();
    for (let i = 0; i < bornes.length; i++) {
        document.getElementById("station" + (i + 1) + "_typeA").value = bornes[i]["station_typeA"];
        document.getElementById("station" + (i + 1) + "_typeB").value = bornes[i]["station_typeB"];
        document.getElementById("emplacement" + (i + 1)).value = bornes[i]["emplacement"];
        placePointOnMap(i + 1);
    }
}*/

// points
let stationPoints = [];

function updateStationsElem2() {
    const n_stations = nStationsElem.value;
    eventListeners.length = n_stations;
    // console.log(n_stations, cur_stations.length);
    if (n_stations > cur_stations.length) {
        for (let i = cur_stations.length; i < n_stations; i++) {
            let el = new_station_v2(i + 1);
            cur_stations.push(el);
            stationsElem.appendChild(el);
            eventListeners[i] = () => placePointOnMap(i + 1);
            el.addEventListener('input', eventListeners[i]);
            stationPoints.push({x: route[0], y: route[1], v: -1, nbA: 0, nbB: 0});
        }
    } else {
        for (let i = cur_stations.length; i > n_stations; i--) {
            cur_stations.pop().remove();
            stationPoints.pop();
        }
    }
    clearCanvas();
    drawPoints();
}

nStationsElem.addEventListener('input', updateStationsElem2);

function deleteStation(index) {
    let prev_n_stations = nStationsElem.value;
    nStationsElem.value = prev_n_stations - 1;
    cur_stations.splice(index, 1)[0].remove();
    stationPoints.splice(index);

    for (let i = index; i < nStationsElem.value; i++) {
        let innerHtml = cur_stations[i].innerHTML;
        let inputs = cur_stations[i].getElementsByTagName('input');
        let values = [];
        values.length = inputs.length;
        for (let j = 0; j < inputs.length; j++) {
            values[j] = inputs[j].value;
        }
        cur_stations[i].removeEventListener('input', eventListeners[i + 1]);
        innerHtml = innerHtml.replaceAll("emplacement" + (i + 2), "emplacement" + (i + 1))
            .replaceAll("station" + (i + 2) + "_typeA", "station" + (i + 1) + "_typeA")
            .replaceAll("station" + (i + 2) + "_typeB", "station" + (i + 1) + "_typeB")
            .replaceAll("deleteStation(" + (i + 1) + ")", "deleteStation(" + i + ")")
            .replaceAll("station " + (i + 2), "station " + (i + 1));
        eventListeners[i] = () => placePointOnMap(i + 1);
        cur_stations[i].addEventListener('input', eventListeners[i]);
        cur_stations[i].innerHTML = innerHtml;
        for (let j = 0; j < inputs.length; j++) {
            inputs[j].value = values[j];
        }
    }
    eventListeners.splice(index);

    placePointOnMap(index + 1);
    clearCanvas();
    drawPoints();
}

const route_length = 445; // TODO: extract it from scenario json

// calcule longueur de chaque segment de route
let lengths = [];
let l = 0;
let total_l = 0;
for (let i = 0; i < route.length - 2; i += 2) {
    l = ((route[i + 2] - route[i]) ** 2 + (route[i + 3] - route[i + 1]) ** 2) ** 0.5;
    total_l += l;
    lengths.push(l);
}

for (let i = 0; i < lengths.length; i++) {
    lengths[i] = lengths[i] * route_length / total_l;
}

// console.log(lengths);

function computePointAtKm(km) { // mauvais resultat a partir de km = 87 - pas encore compris
    if (km < 0) {
        return {x: 0, y: 0, v: -1};
    } else if (km > route_length) {
        return {x: route[route.length - 2], y: route[route.length - 1], v: -1};
    }

    let i = 0;
    let cur_length = 0;
    while (i < lengths.length - 1 && cur_length < km - lengths[i]) {
        cur_length += lengths[i];
        i++;
    }
    let x = route[i * 2] + (route[i * 2 + 2] - route[i * 2]) * (km - cur_length) / lengths[i];
    let y = route[i * 2 + 1] + (route[i * 2 + 3] - route[i * 2 + 1]) * (km - cur_length) / lengths[i];

    return {x: x, y: y, v: -1, nbA: 0, nbB: 0};
}

function drawRoute() {
    // draw a6
    let ctx = canvasElem.getContext('2d');
    ctx.beginPath();
    ctx.lineWidth = "10";
    ctx.strokeStyle = "#555";
    ctx.moveTo(route[0] * scale, route[1] * scale);
    for (let i = 2; i < route.length; i += 2) {
        ctx.lineTo(route[i] * scale, route[i + 1] * scale);
    }
    ctx.stroke();
}

function clearCanvas() {
    let ctx = canvasElem.getContext('2d');
    let map = document.getElementById('map_img');
    ctx.clearRect(0, 0, map.width * scale, map.height * scale);
    ctx.drawImage(map, 0, 0, map.width * scale, map.height * scale);
    drawRoute();
}

const blue = {r: 221, g: 68, b: 68};
const red = {r: 85, g: 204, b: 221};

function lerp(a, b, t) {
    return a * t + b * (1 - t);
}

function drawPoints() {
    let ctx = canvasElem.getContext('2d');
    for (let i = 0; i < stationPoints.length; i++) {
        const point = stationPoints[i];
        // console.log(point);

        ctx.fillStyle = "#fff";
        ctx.beginPath();
        ctx.arc(point.x * scale, point.y * scale, 10, 0, Math.PI * 2, true);
        ctx.fill();

        if (point.v === -1) {
            ctx.fillStyle = "#45b645";
        } else if (point.v === null) {
            ctx.fillStyle = "rgba(0, 0, 0, 0.2)";
        } else {
            ctx.fillStyle = `rgb(${lerp(blue.r, red.r, point.v)}, ${lerp(blue.g, red.g, point.v)}, ${lerp(blue.b, red.b, point.v)})`;
        }
        ctx.beginPath();
        ctx.arc(point.x * scale, point.y * scale, 8, 0, Math.PI * 2, true);
        ctx.fill();

        ctx.font = 'bold 14px serif';

        ctx.strokeStyle = 'white';
        ctx.lineWidth = 4;

        ctx.strokeText(point.nbA + "A, " + point.nbB + "B", point.x * scale + 16, point.y * scale + 7);
        ctx.fillText(point.nbA + "A, " + point.nbB + "B", point.x * scale + 16, point.y * scale + 7);
    }

    if(current_station !== 0){
        const point = stationPoints[current_station-1];

        ctx.fillStyle = "#333";
        ctx.beginPath();
        ctx.arc(point.x * scale, point.y * scale, 12, 0, Math.PI * 2, true);
        ctx.fill();

        ctx.fillStyle = "#fff";
        ctx.beginPath();
        ctx.arc(point.x * scale, point.y * scale, 10, 0, Math.PI * 2, true);
        ctx.fill();

        if (point.v === -1) {
            ctx.fillStyle = "#45b645";
        } else {
            ctx.fillStyle = `rgb(${lerp(blue.r, red.r, point.v)}, ${lerp(blue.g, red.g, point.v)}, ${lerp(blue.b, red.b, point.v)})`;
        }
        ctx.beginPath();
        ctx.arc(point.x * scale, point.y * scale, 8, 0, Math.PI * 2, true);
        ctx.fill();

        ctx.font = 'bold 14px serif';

        ctx.strokeStyle = '#333';
        ctx.lineWidth = 8;

        ctx.strokeText(point.nbA + "A, " + point.nbB + "B", point.x * scale + 16, point.y * scale + 7);

        ctx.strokeStyle = 'white';
        ctx.lineWidth = 4;

        ctx.strokeText(point.nbA + "A, " + point.nbB + "B", point.x * scale + 16, point.y * scale + 7);
        ctx.fillText(point.nbA + "A, " + point.nbB + "B", point.x * scale + 16, point.y * scale + 7);
    }
}

function placePointOnMap(index) {
    clearCanvas();
    // lire emplacement
    //console.log("index: ", index);
    let km = document.getElementById('emplacement' + index).value;

    stationPoints[index - 1] = computePointAtKm(km);
    stationPoints[index - 1].nbA = document.getElementById("station" + index + "_typeA").value;
    stationPoints[index - 1].nbB = document.getElementById("station" + index + "_typeB").value;
    drawPoints();
}

//let cart;

async function init() {
    //await get_set_scenario();
    // init stationPoints
    for (let i = 0; i < cur_stations.length; i++) {
        stationPoints.push(computePointAtKm(document.getElementById('emplacement' + (i + 1)).value));
        stationPoints[i].nbA = document.getElementById('station' + (i + 1) + '_typeA').value;
        stationPoints[i].nbB = document.getElementById('station' + (i + 1) + '_typeB').value;
        eventListeners[i] = () => placePointOnMap(i + 1);
        cur_stations[i].addEventListener('input', eventListeners[i]);
    }
    //await set_stations();
    updateStationsElem2();
}

// CANVAS
window.onload = function () {
    let ctx = canvasElem.getContext('2d');

    // draw map
    let map = document.getElementById('map_img');
    canvasElem.height = map.height * scale;
    canvasElem.width = map.width * scale;
    map.classList.add("d-none");
    // console.log("oui");
    ctx.drawImage(map, 0, 0, map.width * scale, map.height * scale);

    init();
    drawRoute();
    drawPoints();
}
let stop = 0;

