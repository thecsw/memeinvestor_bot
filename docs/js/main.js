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
   let desktopRatio = false;
   let canvas1;
   let ch1;

   function getScreenSize(){
      let w = window,
      d = document,
      e = d.documentElement,
      g = d.getElementsByTagName('body')[0],
      x = w.innerWidth || e.clientWidth || g.clientWidth,
      y = w.innerHeight|| e.clientHeight|| g.clientHeight;
      return {x,y};
   }
   function update(dataSet, index, val){
       let chartDataSet = ch1.data.datasets[dataSet];
       chartDataSet.data[index] = val;
       ch1.update();
   }
   function resize(){
      let x = getScreenSize().x;
      if(x<=800 && desktopRatio){
         desktopRatio = false;
         canvas1.parentNode.style.height = "300px";
         //TODO: manage to remove axys labels on small devices
      }else if(x>800 && !desktopRatio){
         desktopRatio = true;
         //TODO: manage to add axys labels on big devices
         canvas1.parentNode.style.height = "400px";
      }      
   }
   function init(){
      canvas1 = document.getElementById('homepage-graph');
      let x = getScreenSize().x;
      if(x>=800){
         desktopRatio = true;
         //set the chart ratio to a more horizontal ratio, to make it fit on desktop
         canvas1.parentNode.style.height = "400px";
      }
      //display axys labels based on device width
      let displayAxysLabel = desktopRatio;
      let ctx = canvas1.getContext('2d');
      //generate labels for x axys
      let graphLabels = [];
      iterateDays(7, function(index, from, to) {
         //note: months are zero-based
         graphLabels[index] = to.getDate() + '/' + (to.getMonth()+1);
      })
      ch1 = new Chart(ctx, {
         type: 'line',
          // The data for our dataset
         data: {
            labels: graphLabels,
            datasets: [{
               //red dataset
               label: "M¢ invested",
               backgroundColor: 'rgb(240, 91, 79, 0)',
               borderColor: 'rgb(240, 91, 79)',
               data: [10, 20, 22, 40, 89, 100, 150],
               yAxisID: "A",
               lineTension: 0
            },{
               //ORANG dataset
               label: "investments",
               backgroundColor: 'rgba(255, 167, 38, 0)',
               borderColor: 'rgb(255, 167, 38)',
               data: [10, 20, 3, 5, 14, 20, 35],
               yAxisID: "B",
               lineTension: 0
            }]
         },
         // Configuration options go here
         options: {
            responsive: true,
            maintainAspectRatio: false,
            
            legend: {
               //we use our own
               display: false
            },
            scales: {
               yAxes: [{
                  ticks: {
                     display: displayAxysLabel,
                     callback: val => formatToUnits(val)
                  },
                  id: 'A',
                  type: 'linear',
                  position: 'left'
               }, {
                  ticks: {
                     display: displayAxysLabel,
                     callback: val => formatToUnits(val)
                  },
                  id: 'B',
                  type: 'linear',
                  position: 'right'
               }],
               xAxes: [{
                  ticks: {
                     display: true
                  }                  
               }]
            }
         }
      });

      
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
      //init all materialize elements
      let elems = document.querySelectorAll('.sidenav');
      let instances = M.Sidenav.init(elems);
      elems = document.querySelectorAll('.collapsible');
      M.Collapsible.init(elems);
      elems = document.querySelectorAll('.materialboxed');
      M.Materialbox.init(elems);
      //popup code. after the first view, the current popup viewed is stored in localStorage,
      //to avoid showing it on every page reload. increment const popup and refresh cache to show
      //the popup message again
      const POPUP = 1
      //debug
      //localStorage.removeItem('viewed_info')   
      if(localStorage.getItem('viewed_info') != POPUP){
         let domPopup = document.getElementById('modal1');
         M.Modal.init(domPopup);
         setTimeout(
            ()=> M.Modal.getInstance(domPopup).open(),
            2000 );
         localStorage.setItem('viewed_info',POPUP)            
      }

      //init modules
      overview.init()
      overviewChart.init()
      
      //load chart
      iterateDays(7, function(index, dateFrom, to){
          let ufrom = dateFrom.valueOf() / 1000;
          let uto = to.valueOf() / 1000;

          jsonApi.get('/investments/total?from='+ufrom+'&to='+uto)
              .then(function (data) {
                  overviewChart.update(1, index, parseInt(data.investments));
              })
          jsonApi.get('/investments/amount?from='+ufrom+'&to='+uto)
              .then(function (data) {
                  overviewChart.update(0, index, parseInt(data.coins));
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
    var abbrev = ['', 'K', 'M', 'B', 'T', 'Qa', 'Qi', 'S'];
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

function calculateInvestmentResult() {
    let start = parseInt(document.getElementById('investment-start-score').value);
    let end = parseInt(document.getElementById('investment-end-score').value);
    let amount = parseInt(document.getElementById('investment-amount').value);
    const SCALE_FACTOR = 1 / 3.0;
    let relativeChange = 0;
    if (start !== 0) {
        relativeChange = (end - start) / Math.abs(start);
    } else {
        relativeChange = end;
    }
    let multiple = Math.pow(relativeChange + 1, SCALE_FACTOR);
    let investmentSuccess = false, returnMoney = false;
    const WIN_THRESHOLD = 1.2;
    if (multiple > WIN_THRESHOLD) {
        investmentSuccess = returnMoney = true;
    } else if (multiple > 1) {
        returnMoney = true;
    }
    let factor = 0;
    if (investmentSuccess) {
        factor = multiple;
    } else if (returnMoney) {
        factor = (multiple - 1)/(WIN_THRESHOLD - 1);
    }
    let output = (amount * factor).toFixed();
    output = isNaN(output)?"invalid data":output;
    output = (output+[]).length>20?formatToUnits(output):output;
    document.getElementById('investment-result').innerText = output;
}
