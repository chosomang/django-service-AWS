// const needlePlugin = {
//     id: 'needle',
//     afterDatasetsDraw: function(chart, options) {
//       const minValue = 0;
//       const maxValue = 4;
//       const currentValue = 3; // Change this value according to the current gauge value
//       const needleAngle = -Math.PI + (currentValue - minValue) / (maxValue - minValue) * Math.PI;
//       const centerPoint = chart.chartArea.right / 2;
//       const needleCenterY = chart.chartArea.bottom;
//       const needleLength = (chart.chartArea.right - chart.chartArea.left) / 2;

//       const angle = needleAngle; // Set this to the desired angle of your needle (in radians)
//       const needlePoints = {
//         start: {
//           x: centerPoint,
//           y: needleCenterY,
//         },
//         end: {
//           x: centerPoint + needleLength * Math.cos(angle - Math.PI / 2),
//           y: needleCenterY - needleLength * Math.sin(angle - Math.PI / 2)
//         }
//       };

//       const ctx = chart.ctx;
//       ctx.save();

//       // Set needle color and width
//       ctx.strokeStyle = 'black';
//       ctx.lineWidth = 5;

//       // Draw needle
//       ctx.beginPath();
//       ctx.moveTo(needlePoints.start.x, needlePoints.start.y);
//       ctx.lineTo(needlePoints.end.x, needlePoints.end.y);
//       ctx.stroke();

//       ctx.restore();
//     }
//   };


//   Chart.registerPlugin(needlePlugin);

(function (Chart) {
    Chart.pluginService.register({
        beforeDraw: function (chart) {
            if (chart.config.options.needle) {
                var needleRadius = chart.config.options.needle.radius || 7;
                var centerPoint = {
                    x: chart.chartArea.left + (chart.chartArea.right - chart.chartArea.left) / 2,
                    y: chart.chartArea.bottom - (chart.chartArea.bottom - chart.chartArea.top) / 8 //.top + (chart.chartArea.bottom - chart.chartArea.top) / 2
                };
                var meta = chart.getDatasetMeta(0);
                var currentValue = chart.config.options.needle.currentValue || 0;
                var totalDatasetValues = chart.data.datasets[0].data.reduce((a, b) => a + b);
                var angle = ((currentValue / totalDatasetValues) * Math.PI * 2) - (Math.PI / 2);
                var needleX = centerPoint.x + Math.cos(angle) * meta.controller.outerRadius * 0.8; // needle length
                var needleY = centerPoint.y + Math.sin(angle) * meta.controller.outerRadius * 0.8; // needle length

                // chart.chart.ctx.beginPath();
                // chart.chart.ctx.moveTo(centerPoint.x + needleRadius, centerPoint.y);
                // chart.chart.ctx.arc(centerPoint.x, centerPoint.y, needleRadius, 0, Math.PI * 2);
                // chart.chart.ctx.lineTo(centerPoint.x + needleRadius * 0.3, centerPoint.y);
                // chart.chart.ctx.closePath();
                // chart.chart.ctx.fillStyle = "#1cc88a";
                // chart.chart.ctx.fill();

                // chart.chart.ctx.beginPath();
                // chart.chart.ctx.moveTo(centerPoint.x, centerPoint.y);
                // chart.chart.ctx.lineTo(needleX, needleY);
                // chart.chart.ctx.lineWidth = 3;
                // chart.chart.ctx.stroke();

                // Draw round base
                chart.chart.ctx.beginPath();
                chart.chart.ctx.arc(centerPoint.x, centerPoint.y, needleRadius, 0, Math.PI * 2);
                chart.chart.ctx.closePath();
                chart.chart.ctx.fillStyle = "#f6c23e"; // centerpointer color
                chart.chart.ctx.fill();

                // Calculate additional points for the triangular needle
                var theta = Math.PI / 5; // needle thinkness
                var needleStartLeftX = centerPoint.x + Math.cos(angle + theta) * (needleRadius * 0.6);
                var needleStartLeftY = centerPoint.y + Math.sin(angle + theta) * (needleRadius * 0.6);
                var needleStartRightX = centerPoint.x + Math.cos(angle - theta) * (needleRadius * 0.6);
                var needleStartRightY = centerPoint.y + Math.sin(angle - theta) * (needleRadius * 0.6);

                // Draw triangular needle
                chart.chart.ctx.beginPath();
                chart.chart.ctx.moveTo(needleStartLeftX, needleStartLeftY);
                chart.chart.ctx.lineTo(needleX, needleY);
                chart.chart.ctx.lineTo(needleStartRightX, needleStartRightY);
                chart.chart.ctx.closePath();
                chart.chart.ctx.fillStyle = "#f6c23e"; // needle color
                chart.chart.ctx.fill();
            }
        }
    });
})(Chart);

var ctx = document.getElementById("test");
var myPieChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ['정상', '주의', '경계', '심각'],
        datasets: [{
            data: [1, 1, 1, 1],
            backgroundColor: ['#1cc88a', '#f6c23e', '#fd7e14', '#e74a3b'],
            //hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf'],
            hoverBorderColor: "rgba(234, 236, 244, 1)",
        }],
    },
    options: {
        maintainAspectRatio: false,
        needle: {
            currentValue: 3.75, // 3.15 = 1, 3.75 = 2, 4.30 = 3, 4.85 = 4
        },
        tooltips: {
            backgroundColor: "rgb(255,255,255)",
            bodyFontColor: "#858796",
            borderColor: '#dddfeb',
            borderWidth: 1,
            xPadding: 15,
            yPadding: 15,
            displayColors: false,
            caretPadding: 10,
        },
        legend: {
            display: false
        },
        cutoutPercentage: 80,
        circumference: Math.PI,
        rotation: - Math.PI,
        plugins: {
            datalabels: {
                anchor: 'center',
                align: 'center',
                color: '#fff',
                formatter: function(value, context) {
                    return context.chart.data.labels[context.dataIndex];
                },
                rotation:function(context){
                    const index = context.dataIndex;
                    const chart = context.chart;
                    const meta = chart.getDatasetMeta(0);
                    const angle = (meta.data[index]._model.endAngle + meta.data[index]._model.startAngle) / 2;
                    // Convert radians to degrees and subtract 90 to correctly align the label
                    return (angle * (180 / Math.PI)) - 270; // label rotation
                }
            }
        },
        onAnimationComplete: function() {
          this.options.animation = false;
          this.update();
       }
    },
});