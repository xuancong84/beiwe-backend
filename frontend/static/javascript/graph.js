function graph(graphtitle, input){
var title = graphtitle;
plot1 = $.jqplot ('chart1', input, {
        // Give the plot a title.
      title: title,
      animate: true,
      series:[{
            // Don't show a line, just show markers.
            // Make the markers 7 pixels with an 'x' style
            // showLine:false,
            markerOptions: { size: 10, style:"filledCircle" },
            pointLabels: {show: true},
            rendererOptions: {animation:{speed: 2000}},
            showLine: false
          }],
      seriesDefaults: {
        breakOnNull: true,
      },
      // You can specify options for all axes on the plot at once with
      // the axesDefaults object.  Here, we're using a canvas renderer
      // to draw the axis label which allows rotated text.
      axesDefaults: {
        tickRenderer: $.jqplot.CanvasAxisTickRenderer,
        labelRenderer: $.jqplot.CanvasAxisLabelRenderer,
        tickOptions: {
          angle: -20,
        },
      },
      // An axes object holds options for all axes.
      // Allowable axes are xaxis, x2axis, yaxis, y2axis, y3axis, ...
      // Up to 9 y axes are supported.
      axes: {
        // options for each axis are specified in seperate option objects.
        xaxis: {
          show: false,
          label: "Day in the week",
          // Turn off "padding".  This will allow data point to lie on the
          // edges of the grid.  Default padding is 1.2 and will keep all
          // points inside the bounds of the grid.
          pad:2,
          min:0,
          max: input.length + 1,
          tickInterval:1
        },
        yaxis: {
            // showTicks : false,
            label: "Answer",
            labelOptions: {angle: 0},
            min:0,
            max:input.max() + 1,
            tickInterval: 1,
            pad:2
        },
      },
      seriesColors: ["#7BB661", "#E03C31"],
      highlighter: {
            show: true,
            showLabel: true,
            yvalues: 3,
            tooltipAxes: 'y',
            formatString: "%d",
            sizeAdjust: 7.5 , tooltipLocation : 'ne'
        }
    });

}

function replot_user_results(title, data) {
    $('#chart1').empty();
    // TODO: Need to grab information specific to that question in the last X days.
    // For now, the question_number variable is useless
    graph(title, data);
}

// $(document).ready(function() {
// graph(['', 6.5, null ,9 ,8.2]);
// });

// Used in this JS to make the graph look better..
Array.prototype.max = function() {
  var max = this[0];
  var len = this.length;
  for (var i = 1; i < len; i++) if (this[i] > max) max = this[i];
  return max;
}