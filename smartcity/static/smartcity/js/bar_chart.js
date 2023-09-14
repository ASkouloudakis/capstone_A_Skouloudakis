// var data_split_row = {{ split_row|safe }};
var element = document.getElementById("barChart");
var dataset = document.getElementById("divBarChart").getAttribute("data-value");
var dataset = JSON.parse(dataset);

console.log(dataset)

if (element !== null){
    var barCtx = document.getElementById('barChart').getContext('2d');
    var barChart = new Chart(barCtx, {
        type: 'bar',
        data: {
            labels: ['2019', '2020', '2021', '2022', '2023'],
            datasets:dataset
        },
        options: {
            scales: {
                xAxes: [{
                    scaleLabel: {
                        display: true,
                        fontSize: 14,
                        labelString: 'Μέσος Αριθμός Περαστικών ανά ώρα σε κάθε Περιοχή',
                    },
                    ticks: {
                        fontSize: 14,
                        fontColor: 'black'
                    }
                    }],
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: 'Αριθμός Περαστικών'
                    },
                    ticks: {
                        fontSize: 14,
                        fontColor: 'black'
                    }
                }]
            }
        }
    });
    
    function clickHandler(evt) {
        const activeElements = barChart.getElementsAtEventForMode(evt, 'nearest', { intersect: true }, true);
        if (activeElements.length) {
            const firstBar = activeElements[0];
            const label = barChart.data.labels[firstBar._index];
            const value = barChart.data.datasets[firstBar._datasetIndex].data[firstBar._index];
            alert("Bar label: " + label + "\nBar value: " + value);
        }
    }
    document.getElementById("barChart").onclick = clickHandler;
}
