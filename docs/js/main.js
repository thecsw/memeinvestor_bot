"use strict";
let jsonApi = (function(){
   let options = {
      method: "GET",
      url: "https://memes.market/api",
      //url: "http://localhost/memeinvestor_bot/docs/testApiData.json",
   }
   function makeRequest (param, options) {
      
     return new Promise(function (resolve, reject) {
       var xhr = new XMLHttpRequest();
       let url = options.url+param;
       xhr.open(options.method, url);
       xhr.onload = function () {
         if (this.status >= 200 && this.status < 300) {
           resolve(JSON.parse(xhr.response));
         } else {
           reject({
             status: this.status,
             statusText: xhr.statusText
           });
         }
       };
       xhr.onerror = function () {
         reject({
           status: this.status,
           statusText: xhr.statusText
         });
       };
       xhr.send();
     });
   }
   
   function getAll(){
      return makeRequest("?per_page=5", options);
   }

   function get(param){
      return makeRequest(param, options);
   }
   
   return {
      getAll: getAll,
      get: get
   }
})();



let overview = (function(){
   
   let counters = {
      coinsInvested: undefined,
      coinsTotal: undefined,
      investmentsActive: undefined
      //investmentsTotal: undefined  
   }
   function init(){
      counters = {
         coinsInvested: new CountUp("detained-memecoins", 0, 1.5),
         coinsTotal: new CountUp("existing-memecoins", 100000000, 0, 1.5),
         investmentsActive: new CountUp("active-investments", 0, 1.5)
         //investmentsTotal: new CountUp("total-investments", 24.02, 99.99)      
      }
   }
   function update(coins,investments){
      counters.coinsInvested.update(coins.invested.coins)
      counters.coinsTotal.update(coins.total.coins)
      counters.investmentsActive.update(investments.active.investments)
      //counters.investmentsTotal.update(investments.total.investments)
   }
   
   return {
      init:init,
      update: update
   }
   
})();


let overviewChart = (function(){
   let desktopRatio = true;
   let ch1;
   let graphData = {
     labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri','sat','sun'],
     series: [
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0]
       
     ]
   };

   function getScreenSize(){
      let w = window,
      d = document,
      e = d.documentElement,
      g = d.getElementsByTagName('body')[0],
      x = w.innerWidth || e.clientWidth || g.clientWidth,
      y = w.innerHeight|| e.clientHeight|| g.clientHeight;
      return {x,y};
   }
   function update(graph, index, value){
       graphData.series[graph][index] = value;
       ch1.update();
   }
   function resize(){
      let x = getScreenSize().x;
      if(x<=800 && desktopRatio){
         desktopRatio = false;
         document.getElementById("homepage-graph").className = "ct-chart ct-perfect-fourth";
         ch1.update()
      }else if(x>800 && !desktopRatio){
         desktopRatio = true;
         document.getElementById("homepage-graph").className = "ct-chart ct-major-tenth";
         ch1.update()
      }      
   }
   function init(){
      let x = getScreenSize().x;
      if(x<=800){
         desktopRatio = false;
         //set the chart ratio to a less horizontal ratio, to make it fit on mobile
         document.getElementById("homepage-graph").className = "ct-chart ct-perfect-fourth";
      }else{
         desktopRatio = true;
      }

       iterateDays(7, function(index, from, to) {
           graphData.labels[index] = to.getDate() + '/' + to.getMonth();
       })
      
      let options = {
        showPoint: false,
        lineSmooth: false,
        fullWidth: true,
        chartPadding: 0,
        /*axisX: {
          showGrid: false,
          showLabel: false
        },*/
        axisY: {
          offset: 60,
          // The label interpolation function enables you to modify the values
          // used for the labels on each axis. Here we are converting the
          // values into million pound.
          labelInterpolationFnc: function(value) {
            return formatToUnits(value);
          }
        }
      };
      let responsiveOptions = [

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
      ch1 = new Chartist.Line('.ct-chart', graphData, options, responsiveOptions);
   }
   return{
      init: init,
      resize: resize,
      update: update
   }
})();


let leaderboard = (function(){
   function update(top){
      let tb = document.getElementById("leaderboards-table");
      let html = ""
          for(let i=0; i<top.length;i++){
             //broke badge
             let badge = top[i].broke>0? '<span class="red bankrupt-badge white-text">'+top[i].broke+'</span>':"";
             // all in badge <span class="amber badge white-text">all in 3</span>
             html += "<tr><td>"+top[i].name + badge+"</td>"+
                         "<td>"+formatToUnits(top[i].balance)+"</td>"+
                         "<td>"+top[i].completed+"</td></tr>"
          }
      tb.innerHTML = html
   }
   return{
      update: update
   }
})();


(function(){
   //get session cookie
   
   //dom ready listener
   document.addEventListener('DOMContentLoaded', function(){
      //create sidenav 
      let elems = document.querySelectorAll('.sidenav');
      let instances = M.Sidenav.init(elems);
      //instantiate collapsible
      elems = document.querySelectorAll('.collapsible');
      M.Collapsible.init(elems);

      overview.init()
      overviewChart.init()
      
      //load chart
      iterateDays(7, function(index, dateFrom, to){
          let ufrom = dateFrom.valueOf() / 1000;
          let uto = to.valueOf() / 1000;

          jsonApi.get('/investments/total?from='+ufrom+'&to='+uto)
              .then(function (data) {
                  overviewChart.update(0, index, parseInt(data.investments) * 10000);
              })
          jsonApi.get('/investments/amount?from='+ufrom+'&to='+uto)
              .then(function (data) {
                  overviewChart.update(1, index, parseInt(data.coins));
              })
      })
      
      //start infinite short polling updater with 5s frequency
      setInterval(updater,10000);
      function updater(){
         console.log('updating data..')
         let tempData = jsonApi.getAll()
         .then(function (data) {
            overview.update(data.coins, data.investments);
            leaderboard.update(data.investors.top);
         })
         .catch(function (err) {
            // Get toast DOM Element, get instance, then call dismiss function
            let toastElement = document.querySelector('.toast');
            let toastInstance = M.Toast.getInstance(toastElement);
            toastInstance.dismiss();
            console.error('error while retrieving apis data', err.statusText);
            connectionErrorToast(err)
         });      
      } 
      updater();
   });
   //dom resize listener
   window.addEventListener('resize', function(event){
      overviewChart.resize()
   });   
   
   
}());

//debug part
//TODO: redirect to prefilled github issue/tweet/reddit post
var globalError;
function reportError(){
   alert("debug"+globalError)
}
function connectionErrorToast(error){
   globalError = JSON.stringify(error);
   var toastHTML = '<p>an error occurred while trying to get the bot data. </p><button class="btn-flat toast-action" onclick="reportError()">report</button>';
  M.toast({html: toastHTML,displayLength:6000});
   
}

function createWalletToast(){
   var toastHTML = '<p><a href="#" class="">connect your reddit account first</a> or <a href="#"> create your wallet directly from reddit</a></p>';
  M.toast({html: toastHTML,displayLength:6000});
}


function formatToUnits(val) {
    var number = parseInt(val);
    var abbrev = ['', 'K', 'M', 'B', 'T'];
    var unrangifiedOrder = Math.floor(Math.log10(Math.abs(number)) / 3);
    var order = Math.max(0, Math.min(unrangifiedOrder, abbrev.length -1 ));
    var suffix = abbrev[order];
    var precision = suffix ? 1 : 0;
    var res = (number / Math.pow(10, order * 3)).toFixed(precision) + suffix;

    return res;
}

function iterateDays(days, callback) {
    let to = new Date();
    to.setHours(23);
    to.setMinutes(59);
    to.setSeconds(59);
    to.setMilliseconds(999);
    let dateFrom = new Date();
    dateFrom.setTime(to.getTime());
    dateFrom.setDate(dateFrom.getDate() - 1);

    for (let i = days - 1; i >= 0; i--) {
        callback(i, dateFrom, to);
        dateFrom.setDate(dateFrom.getDate() - 1);
        to.setDate(to.getDate() - 1);
    }
}

