//a simple script testing all the plugins -
// probably the materialize.js dependency won't be necessary (used only for the sidebar at the moment) 
   
 document.addEventListener('DOMContentLoaded', function() {
    
    //initialize graphs based on screenSize
   var w = window,
   d = document,
   e = d.documentElement,
   g = d.getElementsByTagName('body')[0],
   x = w.innerWidth || e.clientWidth || g.clientWidth,
   y = w.innerHeight|| e.clientHeight|| g.clientHeight;
   if(x<=640){
      desktopRatio = false;
      document.getElementById("homepage-graph").className = "ct-chart ct-perfect-fourth";
   }else{
      desktopRatio = true;
   }
   
    var elems = document.querySelectorAll('.sidenav');
    var instances = M.Sidenav.init(elems);
    
    
var data = {
  // A labels array that can contain any sort of values
  labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri','sat','sun'],
  // Our series array that contains series objects or in this case series data arrays
  series: [
    [0.4, 0.6, 1, 0.9, 0.8,1,1.3],
    [0, 0.4, 0.3, 0.6, 1,1.1,2]
    
  ]
};
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
      return value + 'm';
    }
  }
};


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
// Create a new line chart object where as first parameter we pass in a selector
// that is resolving to our chart container element. The Second parameter
// is the actual data object.
ch1 = new Chartist.Line('.ct-chart', data, options, responsiveOptions);
  });
  
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
    if(x<=640 && desktopRatio){
      desktopRatio = false;
      document.getElementById("homepage-graph").className = "ct-chart ct-perfect-fourth";
      ch1.update()
    }else if(x>640 && !desktopRatio){
       desktopRatio = true;
       document.getElementById("homepage-graph").className = "ct-chart ct-major-tenth";
       ch1.update()      
    }

});


  