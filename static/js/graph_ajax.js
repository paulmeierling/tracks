function draw_graph(labels, values){
    var context = $('#canvas').get(0).getContext('2d');
    var chart = new Chart(context);
    var chartData = {
                labels : labels,
                datasets : 
                [{
                        fillColor : "rgba(151,187,205,0.5)",
                        strokeColor : "rgba(151,187,205,1)",
                        pointColor : "rgba(151,187,205,1)",
                        pointStrokeColor : "#fff",
                        data : values
                    }]
    }
    
    options = {
        scaleShowGridLines : false,
    }

    chart.Line(chartData, options);
}








