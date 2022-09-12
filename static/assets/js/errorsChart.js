function generateChart(arrX, arrY) {
    var barColors = [
        "#b91d47",
        "#00aba9",
        "#2b5797",
        "#e8c3b9",
        "#1e7145"
    ];

    new Chart("chart-pie", {
        type: "pie",
        data: {
            labels: arrX,
            datasets: [{
                backgroundColor: barColors,
                data: arrY
            }]
        },
        options: {
            responsive: true,
            aspectRatio: 4 //(width/height)
        }
    });}