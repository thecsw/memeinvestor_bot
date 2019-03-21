import {connectionErrorToast} from './modules/uiElements.js';
import * as jsonApi from './modules/jsonApi.js';
import {formatToUnits, iterateDays} from './modules/dataUtils.js';
import {Scheduler} from './modules/scheduler.js';

let ticker = (function(){
   function init() {
      jsonApi.get('/investors/last24').then(function (top5) {
         var tickerElements = document.getElementsByClassName("last24-item");
         for (var i = tickerElements.length - 1; i >= 0; i--) {
             tickerElements[i].innerHTML = `
               <span class="last24-name">${top5[i].name}:</span>
               <span class="last24-profit">${top5[i].profit}</span>
             `
             tickerElements[i].className += " last24-position-" + (i+1)
          } 
      });
   }

   return {
      init: init,
      update: function() {} // there isn't any real reason to update this, it's cached by the hour.
      // update: init
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
         coinsInvested: new CountUp("detained-memecoins", 0, 0),
         coinsTotal: new CountUp("existing-memecoins", 0, 0),
         investmentsActive: new CountUp("active-investments", 0, 0)
         //investmentsTotal: new CountUp("total-investments", 0)
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
      //dom resize listener
      window.addEventListener('resize', e=> resize() );
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
      const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
      iterateDays(7, function(index, from, to) {
         //note: months are zero-based
         graphLabels[index] = to.getDate() + ' ' + monthNames[to.getMonth()];
      })
      ch1 = new Chart(ctx, {
         type: 'line',
         data: {
            labels: graphLabels,
            datasets: [{
               //red dataset
               data: [],
               label: "M¢ invested",
               yAxisID: "A",
               backgroundColor: 'rgba(240, 91, 79, 0.0)',
               borderColor: 'rgb(240, 91, 79)',
               lineTension: 0,
               borderWidth: 2,
               pointRadius: 2,
               pointHoverRadius: 3
            },{
               //ORANG dataset
               data: [],
               label: "investments",
               yAxisID: "B",
               backgroundColor: 'rgba(255, 167, 38, 0.0)',
               borderColor: 'rgb(255, 167, 38)',
               lineTension: 0,
               borderWidth: 2,
               pointRadius: 2,
               pointHoverRadius: 3
            }]
         },
         options: {
            responsive: true,
            maintainAspectRatio: false,
            
            legend: {
               //we use our own
               display: false
            },
            tooltips: {
               cornerRadius: 2,
               backgroundColor: 'rgba(233, 164, 53, 0.8)',
               displayColors: false
              
            },
            scales: {
               yAxes: [{
                  id: 'A',
                  type: 'linear',
                  position: 'left',
                  gridLines: {
                     display: true,
                     color: 'rgba(255,255,255,0.1)',
                     zeroLineColor: 'rgba(255,255,255,0.0)'                     
                  },
                  ticks: {
                     fontColor: 'rgba(255,255,255,0.4)',
                     display: displayAxysLabel,
                     callback: val => formatToUnits(val)
                  }
               }, {
                  id: 'B',
                  type: 'linear',
                  position: 'right',
                  gridLines: {
                     display: false,
                     drawBorder: false,
                     color: 'rgba(255,255,255,0.1)',
                     zeroLineColor: 'rgba(255,255,255,0.0)'
                  },
                  ticks: {
                     fontColor: 'rgba(255,255,255,0.4)',
                     display: displayAxysLabel,
                     callback: val => formatToUnits(val)
                  }
               }],
               xAxes: [{
                  gridLines: {
                     display: true,
                     color: 'rgba(255,255,255,0.1)',
                     zeroLineColor: 'rgba(255,255,255,0.0)'
                  },                  
                  ticks: {
                     display: true,
                     fontColor: 'rgba(255,255,255,0.4)',
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
             html += '<tr><td><a href="./user.html?account='+top[i].name+'">'+top[i].name+"</a>"+badge+"</td>"+
                         "<td>"+formatToUnits(top[i].networth)+"</td>"+
                         "<td>"+top[i].completed+"</td></tr>"
          }
      tb.innerHTML = html
   }
   return{
      update: update
   }
})();

let investmentsCalculator = (function() {
   let startEl, endEl, amountEl;
   let ids = {
/*    input: {
         start: 'investment-start-score',
         end: 'investment-end-score',
         amount: 'investment-amount'
      },
      output: 'investment-result', */
      button: 'investment-calc'
   }
   function init(){
      let calcButton = document.getElementById(ids.button);
      calcButton.addEventListener('click', e=> calc() );
   }
   // formula functions are converted to JS from formula.py
   // the function names follow the paper on memes.market
   // parameter names also follow the paper, except for start and end, which replace v0 and vf for consistency with other parts of this code
   function linear_interpolate(x, x_0, x_1, y_0, y_1){
     let m = (y_1 - y_0) / x_1 - x_0;
     let c = y_0;
     let y = (m * x) + c;
     return y;
   }
   function S(x, max, mid, stp){
      let arg = -(stp * (x - mid));
      let y = max / (1 + Math.exp(arg));
      return y;
   }
   function gain(start, end) {
      if(end < start) {
        // treat negative gain as no gain
        return 0;
      }
      else {
        return end - start;
      }
   }
   function max(start) {
      return 1.2 + 0.6 / ((start / 10) + 1);
   }
   function mid(start) {
      let sig_mp_0 = 50;
      let sig_mp_1 = 500;
      return linear_interpolate(start, 0, 25000, sig_mp_0, sig_mp_1);
   }
   function stp(start){
      return 0.06 / ((start / 100) + 1);
   }
   function C(start, end) {
     return S(gain(start, end), max(start), mid(start), stp(start));
   }
   function calc(){
      let start = parseInt(document.getElementById('investment-start-score').value);
      let end = parseInt(document.getElementById('investment-end-score').value);
      let amount = parseInt(document.getElementById('investment-amount').value);
      if(start>=0 && end>=0 && amount >= 100){
         //creates a spinning loader
         document.getElementById('investment-result').innerHTML =
         `<div class="preloader-wrapper small active custom-preloader-wrapper">
          <div class="spinner-layer spinner-yellow-only">
            <div class="circle-clipper left">
              <div class="circle"></div>
            </div><div class="gap-patch">
              <div class="circle"></div>
            </div><div class="circle-clipper right">
              <div class="circle"></div>
            </div>
          </div>
         </div>`
         let factor = C(start, end);
         let output = (amount * factor).toFixed();
         output = isNaN(output)?"invalid data":output;
         output = (output+[]).length>20?formatToUnits(output):output;
         //replaces the spinning loader with the calculated result
         document.getElementById('investment-result').innerText = output;
      }else{
         document.getElementById('investment-result').innerText = 'invalid data';
         let toastHTML = 'you have to fill all the fields with a valid number'
         if(amount<100){
            toastHTML = 'you can\'t invest less than 100 M¢'
         }
         M.toast({html: toastHTML,displayLength:2000, classes:"dark-toast"}); 
      }
   }
   return {
      init: init
   }
})();



(function(){
   document.addEventListener('DOMContentLoaded', function(){
      //init local modules
      overview.init()
      overviewChart.init()
      investmentsCalculator.init()
      ticker.init()
      //init short polling update schedulers
      let dataUpdater = new Scheduler(
         function(){
            console.log('updating data..')
            jsonApi.getAll()
            .then(function (data) {
               overview.update(data.coins, data.investments);
               leaderboard.update(data.investors.top);
            })
            .catch(function (err) {
               console.error('error while retrieving apis data', err.statusText);
               connectionErrorToast(err)
            }); 
         },
         //every 10 seconds
         10000
      )

      iterateDays(7, function(index, dateFrom, to){
         console.log("updating chart---")
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

      
   });
   
}());





