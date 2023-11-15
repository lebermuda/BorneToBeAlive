async function getJSON(path) {
    return fetch(path, {method: 'GET'})
        .then(response => {
            return response.json()
        });
}

/*
function set_readonly_simu_form(bool) {
    bool = false;
    let els = document.getElementsByClassName("simu_form")
    Array.from(els).forEach((el) => {
        bool ? el.setAttribute('disabled', "true") : el.removeAttribute('disabled');
    });
}
*/
let scenario = [];

const formElem = document.getElementById('form');
const selectElem = document.getElementById('scenario');

configStationElem = document.getElementById("scenario_stations");

async function get_set_stations() {
    stations_json = await getJSON('/stations/get/' + configStationElem.value);
    let bornes = stations_json["stations"];
    nStationsElem.value = bornes.length;
    //console.log(bornes);
    await updateStationsElem2();
    for (let i = 0; i < bornes.length; i++) {
        document.getElementById("station" + (i + 1) + "_typeA").value = bornes[i]["station_typeA"];
        document.getElementById("station" + (i + 1) + "_typeB").value = bornes[i]["station_typeB"];
        document.getElementById("emplacement" + (i + 1)).value = bornes[i]["emplacement"];
        placePointOnMap(i + 1);
    }
}

configStationElem.addEventListener('change', get_set_stations);
// scenario choice

/*
async function updateReadonly() {
    const index = selectElem.value;
    console.log("selected " + index);
    if (index !== "999") { // != nombre de ligne
        set_readonly_simu_form(true);
        //await get_set_scenario(index);
    } else {
        set_readonly_simu_form(false);
    }
}
*/

selectElem.addEventListener('change', () => {
    //get_set_scenario();
    if (selectElem.value !== "999")
        window.location.href = '/?scenario_id=' + selectElem.value;
    else
        window.location.href = '/';
});
/*
function new_station_v2(index) {
    let el = document.createElement('div');
    el.id = 'station_' + index;
    el.className = 'col col-6 custom-box2 p-1 mb-2';
    el.innerHTML =
        "               <div class='row mb-1'>\n" +
        "                   <label title='Emplacement de la station " + index + "' for='emplacement0' class='col-sm-6 col-form-label col-form-label-sm'>Emplacement</label>\n" +
        "                   <div class='col-sm-4'>\n" +
        "                       <input type='number' class='form-control form-control-sm simu_form' id='emplacement" + index + "' name='emplacement" + index + "' required value='0' min='0'>\n" +
        "                       <div class='invalid-feedback'>Veuillez spécifier un emplacement pour la station.</div>\n" +
        "                   </div>\n" +
        "               </div>\n" +
        "               <div class='row mb-1'>\n" +
        "                   <label title='Nombre de bornes de type A' for='station0' class='col-sm-6 col-form-label col-form-label-sm'>Bornes Types A</label>\n" +
        "                   <div class='col-sm-4'>\n" +
        "                       <input type='number' class='form-control form-control-sm simu_form' id='station" + index + "_typeA' name='station" + index + "_typeA' required value='0' min='0'>\n" +
        "                       <div class='invalid-feedback'>Veuillez spécifier une quantité de bornes de type A.</div>\n" +
        "                   </div>\n" +
        "               </div>\n" +
        "               <div class='row mb-1'>\n" +
        "                   <label title='Nombre de bornes de type B' for='station0' class='col-sm-6 col-form-label col-form-label-sm'>Bornes Types B</label>\n" +
        "                   <div class='col-sm-4'>\n" +
        "                       <input type='number' class='form-control form-control-sm simu_form' id='station" + index + "_typeB' name='station" + index + "_typeB' required value='0' min='0'>\n" +
        "                       <div class='invalid-feedback'>Veuillez spécifier une quantité de bornes de type B.</div>\n" +
        "                   </div>\n" +
        "               </div>"
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
console.log(cur_stations);

// points
let stationPoints = [];

function updateStationsElem2() {
    const n_stations = nStationsElem.value;
    console.log(n_stations, cur_stations.length);
    if (n_stations > cur_stations.length) {
        for (let i = cur_stations.length; i < n_stations; i++) {
            let el = new_station_v2(i + 1);
            cur_stations.push(el);
            stationsElem.appendChild(el);
            el.addEventListener('change', () => placePointOnMap(i + 1));
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

nStationsElem.addEventListener('change', updateStationsElem2);

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

console.log(lengths);

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
    console.log("cur_length:" + cur_length + ", route[i*2]: " + route[i * 2] + ", route[i*2+2]: " + route[i * 2 + 2]);
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
        ctx.fillStyle = "#fff";
        ctx.beginPath();
        ctx.arc(point.x * scale, point.y * scale, 8, 0, Math.PI * 2, true);
        ctx.fill();

        if (point.v === -1) {
            ctx.fillStyle = "#45b645";
        } else {
            ctx.fillStyle = `rgb(${lerp(blue.r, red.r, point.v)}, ${lerp(blue.g, red.g, point.v)}, ${lerp(blue.b, red.b, point.v)})`;
        }
        ctx.beginPath();
        ctx.arc(point.x * scale, point.y * scale, 6, 0, Math.PI * 2, true);
        ctx.fill();

        ctx.strokeStyle = 'white';
        ctx.lineWidth = 4;
        ctx.font = 'bold 14px serif';

        ctx.strokeText(point.nbA + "A, " + point.nbB + "B", point.x * scale + 16, point.y * scale + 7);
        ctx.fillText(point.nbA + "A, " + point.nbB + "B", point.x * scale + 16, point.y * scale + 7);


    }
}

function placePointOnMap(index) {
    clearCanvas();
    // lire emplacement
    let km = document.getElementById('emplacement' + index).value;

    stationPoints[index - 1] = computePointAtKm(km);
    stationPoints[index - 1].nbA = document.getElementById("station" + index + "_typeA").value;
    stationPoints[index - 1].nbB = document.getElementById("station" + index + "_typeB").value;
    drawPoints();
}
*/

let resultsElem = document.getElementById("simu_results");
let chart;
let current_station = 0;
let simu_stationAmount;

function changeStation(index) {
    if (current_station + index > 0 && current_station + index <= simu_stationAmount) {
        //console.log("changing station:" + index);
        current_station += index;
        chart.destroy();
        updateInfo();
    }
}

let selectStationInput = document.getElementById('station_index');

function changeStationInput() {
    if (selectStationInput.value > 0 && selectStationInput.value <= simu_stationAmount) {
        current_station = selectStationInput.value;
    } else if (selectStationInput.value <= 0) {
        // console.log("aa");
        selectStationInput.value = 1;
        current_station = 1;
    } else {
        // console.log("bb");

        selectStationInput.value = simu_stationAmount;
        current_station = simu_stationAmount;
    }
    chart.destroy();
    updateInfo();
}

selectStationInput.addEventListener('change', changeStationInput);

function formatDuration(duration) {
    if (duration === 0) {
        return 'None'
    }
    if (duration === '0:00:00') {
        return '0sec'
    }

    let [hours, minutes, seconds] = duration.split(':').map(x => parseInt(x));

    let result = '';
    if (hours > 0) {
        result += `${hours}h `;
    }
    if (minutes > 0) {
        result += `${minutes}min `;
    }
    if (seconds > 0) {
        result += `${seconds}sec`;
    }
    return result.trim();
}

function normalizeDurations(durations) {
    let maxDuration = 0;
    let durationList = [];
    for (let duration of durations) {
        if (duration === 0) {
            durationList.push(null);
        }
        else {
            let [hours, minutes, seconds] = duration.split(':').map(x => parseInt(x));
            let totalSeconds = hours * 60 * 60 + minutes * 60 + seconds;
            maxDuration = Math.max(maxDuration, totalSeconds);
            durationList.push(totalSeconds);
        }
    }
    if (maxDuration > 0){
        durationList=durationList.map(x => (x === null)  ? x : x / maxDuration);
    }
    return durationList;
}

let simu_results = {};

async function updateInfo() {
    /*
    let simu_results = await fetch('http://localhost:5000/simulate')
    .then((response) => response.json())
    .catch( function( err ) {
 
        console.error( err );
         
        throw "fetch GET have fail ";
     
    } ) ;*/

    //console.log(simu_results);
    //Temps d'attente Moyen
    document.getElementById("temps_attente_moyen_g").innerHTML = formatDuration(simu_results.t_wait_mean_v);
    //Temps de charge Moyen
    document.getElementById("temps_charge_moyen_g").innerHTML = formatDuration(simu_results.t_use_mean_v);
    //Proportion de temps de route moyen
    document.getElementById("proportion_roule_g").innerHTML = Math.round(simu_results.proportion_route_mean_v * 10000) / 100 + " %";

    // get info of current_station
    let els = document.getElementsByClassName("station_index");
    Array.from(els).forEach((el) => {
        el.innerHTML = current_station;
    });
    let els2 = document.getElementsByClassName("station_amount");
    Array.from(els2).forEach((el) => {
        el.innerHTML = simu_stationAmount;
    });
    //Temps d'attente moyen par Borne
    let els3 = document.getElementsByClassName("temps_moyen_borne");
    Array.from(els3).forEach((el) => {
        el.innerHTML = formatDuration(simu_results.t_wait_mean_b[current_station - 1]);
    });
    //Proportion de temps d'usage par Borne
    let els4 = document.getElementsByClassName("proportion_use_borne");
    Array.from(els4).forEach((el) => {
        el.innerHTML = Math.round(simu_results.proportion_usage_b[current_station - 1] * 10000) / 100 + " %";
    });

    selectStationInput.value = current_station;


    const ctx = document.getElementById('station_chart').getContext('2d');
    chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['0', '10','20', '30', '40', '50','1h00','1h10','1h20','1h30','1h40','1h50','2h00'],
            datasets: [{
                label: "Temps d'attente (min)",
                data: simu_results.repartitions[current_station - 1],

                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)',
                    'rgba(200, 100, 50, 0.2)',
                    'rgba(100, 200, 50, .2)',
                    'rgba(100, 50, 200, .2)',
                    'rgba(50, 100, 25, .2)',
                    'rgba(255, 100, 100, .2)',
                    'rgba(25, 50, 255, .2)',
                    'rgba(0,200 ,155 , .2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',
                    'rgba(200, 100, 50, 1)',
                    'rgba(100, 200, 50, 1)',
                    'rgba(100, 50, 200, 1)',
                    'rgba(50, 100, 25, 1)',
                    'rgba(255, 100, 100, 1)',
                    'rgba(25, 50, 255, 1)',
                    'rgba(0,200 ,155 , 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    let fluidite = normalizeDurations(simu_results.t_wait_mean_b);
    // console.log("fluidité: ",fluidite);
    // put results in points
    for (let i = 0; i < stationPoints.length; i++) {
        stationPoints[i].v = fluidite[i];
    }
    clearCanvas();
    drawPoints();
}

let simBtnElem = document.getElementById("simulate_btn");
let loaderElem = document.getElementById("loader");

let fileInputElem = document.getElementById('file_scenario');

function blockInputs() {
    // console.log("blockInputs called: ", fileInputElem.value);
    let els = document.getElementsByClassName("to_be_blocked_if_file")
    Array.from(els).forEach((el) => {
        if (fileInputElem.value) {
            el.setAttribute('disabled', "");
            el.removeAttribute('required');
        } else {
            el.removeAttribute('disabled');
            el.setAttribute('required', "");
        }
    });
}

async function run_simulation() {
    if (!formElem.reportValidity()) {
        return;
    }
    simBtnElem.setAttribute('disabled', "true");
    loaderElem.classList.remove('d-none');

    if (chart != null) {
        chart.destroy();
        resultsElem.classList.add('d-none');
    }
    simu_stationAmount = nStationsElem.value;

    //let json = await getJSON('/simulate');
    //console.log("result: " + JSON.stringify(json));
    req = new XMLHttpRequest();
    req.open("POST", "/simulate");

    // save result when repsonse is recieved
    req.onload = function (event) {
        current_station = 1;
        simu_results = event.target.response;
        // console.log("result: ", simu_results);
        clearCanvas();
        updateInfo();

        loaderElem.classList.add('d-none');
        simBtnElem.removeAttribute('disabled');
        resultsElem.classList.remove('d-none');
    }

    // send simu parameters
    var formData = new FormData(formElem);
    req.responseType = "json";
    req.send(formData);
}

/*
async function init() {
    //await get_set_scenario();
    // init stationPoints
    for (let i = 0; i < cur_stations.length; i++) {
        stationPoints.push(computePointAtKm(document.getElementById('emplacement'+(i+1)).value));
        stationPoints[i].nbA = document.getElementById('station'+(i+1)+'_typeA').value;
        stationPoints[i].nbB = document.getElementById('station'+(i+1)+'_typeB').value;
        cur_stations[i].addEventListener('change', () => placePointOnMap(i + 1));
    }
    updateStationsElem2();
    await updateReadonly();
}

// CANVAS
window.onload = function () {
    let ctx = canvasElem.getContext('2d');

    // draw map
    let map = document.getElementById('map_img');
    canvasElem.height = map.height * scale;
    canvasElem.width = map.width * scale;
    map.classList.add("d-none");
    ctx.drawImage(map, 0, 0, map.width * scale, map.height * scale);

    init();
    get_set_stations();
    drawRoute();
    drawPoints();
}
let stop = 0;
*/

get_set_stations();

