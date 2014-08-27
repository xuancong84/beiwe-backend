function steve (){
  var plot1 = $.jqplot ('chart1', [[3,7,9,1,4,6,8,2,5]], {
// Give the plot a title.
      title: 'Graph Of a question',
      animate: true,
      series:[{
            // Don't show a line, just show markers.
            // Make the markers 7 pixels with an 'x' style
            // showLine:false,
            markerOptions: { size: 7, style:"x" },
          }],
      // You can specify options for all axes on the plot at once with
      // the axesDefaults object.  Here, we're using a canvas renderer
      // to draw the axis label which allows rotated text.
      axesDefaults: {
        labelRenderer: $.jqplot.CanvasAxisLabelRenderer
      },
      // An axes object holds options for all axes.
      // Allowable axes are xaxis, x2axis, yaxis, y2axis, y3axis, ...
      // Up to 9 y axes are supported.
      axes: {
        // options for each axis are specified in seperate option objects.
        xaxis: {
          show: false,
          label: "X Axis",
          // Turn off "padding".  This will allow data point to lie on the
          // edges of the grid.  Default padding is 1.2 and will keep all
          // points inside the bounds of the grid.
          pad: 0
        },
        yaxis: {
            // showTicks : false,
            label: "Y Axis",
        },
        labelRenderer: $.jqplot.CanvasAxisLabelRenderer,
        tickRenderer: $.jqplot.CanvasAxisTickRenderer
      },
      seriesColors: ["#7BB661", "#E03C31"]
    });
}

window.onload( steve() );