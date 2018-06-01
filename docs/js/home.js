/* on page size change,
   if screen size is < 640px (max-width:640px)
   change graph ratio and update it */
window.addEventListener('resize', function(event){
    //get screen size
    var w = window,
        d = document,
        e = d.documentElement,
        g = d.getElementsByTagName('body')[0],
        x = w.innerWidth || e.clientWidth || g.clientWidth,
        y = w.innerHeight|| e.clientHeight|| g.clientHeight;

    if (x <= 800 && desktopRatio) {
        desktopRatio = false;
        document.getElementById("homepage-graph").className = "ct-chart ct-perfect-fourth";
        ch1.update()
    } else if(x > 800 && !desktopRatio) {
        desktopRatio = true;
        document.getElementById("homepage-graph").className = "ct-chart ct-major-tenth";
        ch1.update()
    }
});

var responsiveOptions = [

    ['screen and (min-width: 641px) and (max-width: 1024px)', {
        seriesBarDistance: 10
    }],
    ['screen and (max-width: 640px)', {
        seriesBarDistance: 5,
        chartPadding: { left: -59 },
        axisY: {
            showLabel: false
        }
    }]
];

// We are setting a few options for our chart and override the defaults
options = {
    // Don't draw the line chart points
    showPoint: false,
    // Disable line smoothing
    lineSmooth: false,

    fullWidth: true,
    chartPadding: 0,
    // X-Axis specific configuration
    /*axisX: {
    // We can disable the grid for this axis
    showGrid: false,
    // and also don't show the label
    showLabel: false
    },*/
    // Y-Axis specific configuration
    axisY: {
        // Lets offset the chart a bit from the labels
        offset: 60,
        // The label interpolation function enables you to modify the values
        // used for the labels on each axis. Here we are converting the
        // values into million pound.
        labelInterpolationFnc: function(value) {
            return formatToUnits(value);
        }
    }
};


//initialize graphs based on screenSize
var w = window,
    d = document,
    e = d.documentElement,
    g = d.getElementsByTagName('body')[0],
    x = w.innerWidth || e.clientWidth || g.clientWidth,
    y = w.innerHeight|| e.clientHeight|| g.clientHeight;
if (x <= 790) {
    desktopRatio = false;
    document.getElementById("homepage-graph").className = "ct-chart ct-perfect-fourth";
} else {
    desktopRatio = true;
}

var elems = document.querySelectorAll('.sidenav');
var instances = M.Sidenav.init(elems);


var data = {
    // A labels array that can contain any sort of values
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri','Sat','Sun'],
    // Our series array that contains series objects or in this case series data arrays
    series: [
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0]
    ]
};

// Create a new line chart object where as first parameter we pass in a selector
// that is resolving to our chart container element. The Second parameter
// is the actual data object.
ch1 = new Chartist.Line('.ct-chart', data, options, responsiveOptions);

function updateChart(index, graph, field) {
    return function(api) {
        data.series[graph][index] = parseInt(api[field]);
        if (field == "investments")
            data.series[graph][index] *= 10000;
        ch1.update();
    }
}

iterateDays(7, function(day, from, to) {
    var fromto = '?from=' + from.getTime()/1000 + '&to=' + to.getTime()/1000;
    $.getJSON('http://localhost:5000/investments/amount' + fromto,
              updateChart(day, 0, "coins"));
    $.getJSON('http://localhost:5000/investments/total' + fromto,
              updateChart(day, 1, "investments"));
});
