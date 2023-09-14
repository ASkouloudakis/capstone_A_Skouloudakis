var bubbleChart = document.getElementById("bubbleChart");
if (bubbleChart !== null){
    var bubbleCtx = document.getElementById('bubbleChart').getContext('2d');
    var bubbleChart = new Chart(bubbleCtx, {
        type: 'bubble',
        data: {
            datasets: [{
                label: 'Passers',
                data: [
                    { x: 1, y: 1, r: 213681/100000 },
                    { x: 2, y: 8, r: 161018/100000 },
                    { x: 3, y: 10, r: 2099895/100000 },
                    { x: 4, y: 1, r: 2175/100000 },
                    { x: 5, y: 2, r: 849/100000 },
                    { x: 6, y: 2, r: 34992/100000 },
                    { x: 7, y: 12, r: 850455/100000 },
                    { x: 8, y: 16, r: 11233215/100000 },
                    { x: 9, y: 7, r: 6723689/100000 },
                    { x: 10, y: 6, r: 522533/100000 },
                ],
                backgroundColor: 'rgba(19, 13, 191, 0.2)', 
                borderColor: 'rgba(19, 13, 191, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                xAxes: [{
                    scaleLabel: {
                        display: true,
                        fontSize: 9,
                        labelString: '1:Albert Cuypstraat, 2:Arena, 3:IJ-veren, 4:Plein, 5:Schinkeleiland, 6:Station Zuid, 7:Vondelpark, 8:Wallen, 9:Winkelgebied, 10:Zuidoost',
                    },
                    ticks: {
                        fontSize: 14,
                        fontColor: 'black'
                    }
                    }],
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: 'Num Of Locations'
                    },
                    ticks: {
                        fontSize: 14,
                        fontColor: 'black'
                    }
                }]
            }
        }
    });
}
