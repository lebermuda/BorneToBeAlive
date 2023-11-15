let canvasElem = document.getElementById("distrib_canvas");
let input = document.getElementById("repartition_voiture");
let chart;
let formated_input = document.getElementById("repartition_voiture_formated");

function plotHistogram(canvasID, inputID) {
    let canvasElem = document.getElementById(canvasID);
    let input = document.getElementById(inputID);

    let datainput = input.value.replace('[', '').replace(']', '').split(/[;:, -]/).filter(str => str !== '');

    let formated_input = document.getElementById(inputID + "_formated");
    formated_input.value = datainput.toString();

    const ctx = canvasElem.getContext('2d');
    ctx.clearRect(0, 0, canvasElem.width, canvasElem.height);

    const maxValue = Math.max(...datainput);

    const barWidth = (canvasElem.width / datainput.length) - 10;

    let x = 10;
    console.log(datainput);
    for (let i = 0; i < datainput.length; i++) {
        const barHeight = (datainput[i] / maxValue) * canvasElem.height;

        ctx.fillStyle = 'rgba(150,150,150, 1)';
        ctx.fillRect(x, canvasElem.height - barHeight, barWidth, barHeight);
        x += barWidth + 10;
    }
}


function plotDistrib(canvasID, inputID) {
    let canvasElem = document.getElementById(canvasID);
    let input = document.getElementById(inputID);

    let datainput = input.value.split(/[;:, -]/).filter(str => str !== '');
    formated_input.value = datainput.toString();
    if (chart != null) {
        chart.destroy();
    }
    const length = datainput.length;
    const backgroundColor = Array.from({length}, (_, i) => `hsl(${i * (360 / length)}, 100%, 40%, 0.3)`)
    const borderColor = Array.from({length}, (_, i) => `hsl(${i * (360 / length)}, 100%, 40%, 1)`)

    console.log(backgroundColor)
    const ctx = canvasElem.getContext('2d');
    chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Array.from({length}, (_, i) => Math.round((i * 100 / length)).toString() + '%'),
            datasets: [{
                label: "Proportion de voiture de voiture",
                data: datainput.map(str => parseInt(str)),
                backgroundColor: backgroundColor,
                borderColor: borderColor,
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                },
                xAxes: [{
                    gridLines: {
                        display: false
                    },
                    ticks: {
                        display: false
                    }
                }],
                yAxes: [{
                    gridLines: {
                        display: false
                    },
                    ticks: {
                        display: false
                    }
                }]
            },
            legend: {
                display: false
            },
            tooltips: {
                enabled: false
            },
            responsive: false
        }
    });
}

let nTrajetInput = document.getElementById("n_trajets");
let pastValue = nTrajetInput.value;
let inputRows = document.getElementById("trajets");
let divs = Array.from(inputRows.children);

let inputDistribRows = document.getElementById("trajets_distrib");
let divs2 = Array.from(inputDistribRows.children);

function drawTrajetInput() {
    let newValue = nTrajetInput.value;
    console.log(pastValue, newValue);
    if (newValue > pastValue) {
        for (let i = pastValue; i < newValue; i++) {
            let newDiv = document.createElement('div');
            newDiv.id = 'trajet_' + i;
            newDiv.className = 'row';
            newDiv.innerHTML =
                "                        <div class='col col-2'>Trajet " + i + ": </div>" +
                "                        <label for=\"km_entree_" + i + "\" class=\"form-label col col-2 col-form-label\">km d'entrée</label>\n" +
                "                        <div class=\"col col-2\">\n" +
                "                            <input type=\"number\" class=\"form-control form-control-sm\" name=\"km_entree_" + i + "\" id=\"km_entree_" + i + "\" value=\"0\" required>\n" +
                "                        </div>\n" +
                "                        <label for=\"km_sortie_" + i + "\" class=\"form-label col col-2 col-form-label\">km de sortie</label>\n" +
                "                        <div class=\"col col-2\">\n" +
                "                            <input type=\"number\" class=\"form-control form-control-sm\" name=\"km_sortie_" + i + "\" id=\"km_sortie_" + i + "\" value=\"0\" required>\n" +
                "                        </div>"
            inputRows.appendChild(newDiv);
            divs.push(newDiv);

            let newDiv2 = document.createElement('div');
            newDiv2.id = 't_distrib_' + i;
            newDiv2.className = 'row';
            newDiv2.innerHTML = "<div class='col col-sm-4'>" +
                "                   <input type=\"text\" class=\"form-control\" name=\"repartition_voiture\" id=\"distrib_trajet_" + i + "\"\n" +
                "                           oninput=\"plotHistogram('distrib_canvas_trajet_" + i + "', this.id)\"\n" +
                "                           required>\n" +
                "                    <input type=\"text\" name=\"distrib_trajet_" + i + "_formated\" id=\"distrib_trajet_" + i + "_formated\"\n" +
                "                           class=\"d-none\">" +
                "                </div>" +
                "                <div class='col col-2'>aperçu: </div>" +
                "                <div class='col col-6'>" +
                "                   <canvas height=\"40px\" width=\"400px\" id=\"distrib_canvas_trajet_" + i + "\" class=\"border-bottom\"></canvas>" +
                "                </div>";
            inputDistribRows.appendChild(newDiv2);
            divs.push(newDiv2);
        }
    } else {
        for (let i = pastValue; i > newValue; i--) {
            divs.pop().remove();
            divs2.pop().remove();
        }
    }

    pastValue = newValue;

}

plotHistogram('distrib_canvas', "repartition_voiture");

for (let i = 0; i < pastValue; i++) {
    plotHistogram('distrib_canvas_trajet_'+i, 'distrib_trajet_'+i);
}

