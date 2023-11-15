let values = [100.0, 0.0, 0.0, 0.0];

function change(x) {
    let newVal = document.getElementById("type" + x).value;
    let oldVal = values[x];
    values[x] = newVal;
    let delta = newVal - oldVal;
    let zCount = 3;
    if (delta > 0) {
        zCount = 3 - values.filter(v => v === 0).length;
    }
    console.log(delta);

    for (let i = 0; i < 4; i++) {
        if (i === x || (values[i] <= 0 && delta > 0) || (values[i] >= 100 && delta < 0)) continue;

        let inputElem = document.getElementById("type" + i);
        inputElem.value -= delta / zCount;
        values[i] -= delta / zCount;
    }

    for (let i = 0; i < 4; i++) {
        document.getElementById('value' + i).innerHTML = Math.round(values[i]) + ' %';

    }

    console.log(values[0], values[1], values[2], values[3]);
}