import {connectionErrorToast} from './modules/uiElements.js';
import * as jsonApi from './modules/jsonApi.js';
import {formatToUnits, iterateDays} from './modules/dataUtils.js';

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
               data: [10, 20, 22, 40, 89, 100, 150],
               label: "M¢ invested",
               yAxisID: "A",
               backgroundColor: 'rgba(240, 91, 79, 0.0)',
               borderColor: 'rgb(240, 91, 79)',
               lineTension: 0,
               borderWidth: 2,
            },{
               //ORANG dataset
               data: [10, 20, 3, 5, 14, 20, 35],
               label: "investments",
               yAxisID: "B",
               backgroundColor: 'rgba(255, 167, 38, 0.0)',
               borderColor: 'rgb(255, 167, 38)',
               lineTension: 0,
               borderWidth: 2,
               
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
             html += "<tr><td>"+top[i].name + badge+"</td>"+
                         "<td>"+formatToUnits(top[i].networth)+"</td>"+
                         "<td>"+top[i].completed+"</td></tr>"
          }
      tb.innerHTML = html
   }
   return{
      update: update
   }
})();

//TODO: move all this to a custom page
let userAccount = (function(){
   let ids = {
      searchBar: {
         desktop: 'investor-username',
         mobile: 'investor-username-mobile'         
      },
      searchButton: {
         desktop: 'investor-username-search',
         mobile: undefined
      }
   }
   function show(device) {
      let username = document.getElementById(ids.searchBar[device]).value;
      if(username.length > 0){
         let domPopup = document.getElementById('investor-info'); 
         M.Modal.init(domPopup);
         M.Modal.getInstance(domPopup).open()
         jsonApi.get('/investor/'+username).then(function(data) {
         document.getElementById('investor-account-data').innerHTML = `
              <h5>${username}'s profile</h5>
              <p><a target="_blank" href="https://reddit.com/u/${username}">visit reddit profile</a></p>
              <table>
                 <tr><th>Balance</th><td>${data.balance}</td></tr>
                 <tr><th>Gone broke</th><td>${data.broke} times</td></tr>
                 <tr><th>Investments</th><td>${data.completed}</td></tr>
              </table>`;
         })
         .catch(function(er){
            if (er.status === 404){
               document.getElementById('investor-account-data').innerHTML = `<h5>There is no investor with that username!</h5>`
            }
         });
      }
   }
   function init(){
      //add ENTER key listener
      let searchEl = document.getElementById(ids.searchBar['desktop']);
      searchEl.addEventListener('keypress', e=> {if((e.which || e.keyCode) === 13)show('desktop')} );     
      searchEl = document.getElementById(ids.searchBar['mobile']);
      searchEl.addEventListener('keypress', e=> {if((e.which || e.keyCode) === 13)show('mobile')} );
      //add SEARCH button click listener
      let searchButton = document.getElementById(ids.searchButton['desktop']);
      searchButton.addEventListener('click', e=> show('desktop') );  
      // check if url contains ?account=
      let url = new URL(window.location.href);
      let username = url.searchParams.get("account");
      const reg = /^[a-zA-Z0-9\-\_]+$/;
      if (reg.test(username)) {
         document.getElementById('investor-username').value = username;
         show('desktop');
         history.pushState(null, '', window.location.href.split('?')[0]);
      }

   }
   return {
      init: init,
      show: show
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
   function calc(){
      let start = parseInt(document.getElementById('investment-start-score').value);
      let end = parseInt(document.getElementById('investment-end-score').value);
      let amount = parseInt(document.getElementById('investment-amount').value);
      if(start>0 && end>0 && amount > 100){
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
         jsonApi.get('/calculate?old='+start+'&new='+end).then(function(data) {
            let factor = data.factor.valueOf()
            let output = (amount * factor).toFixed();
            output = isNaN(output)?"invalid data":output;
            output = (output+[]).length>20?formatToUnits(output):output;
            //replaces the spinning loader with the calculated result
            document.getElementById('investment-result').innerText = output;
         }).catch(function(er){
            connectionErrorToast(er,'connection error');
            //removes the spinnign loader
            document.getElementById('investment-result').innerText = '000';
         });
      }else{
         document.getElementById('investment-result').innerText = 'invalid data';
      }
   }
   return {
      init: init
   }
})();

let updater = (function(){
   let hidden, visibilityChange; 
   let updateInterval = 10000;
   let interval = false;
   function init(){
      //start the updater
      start();
      // Set the name of the hidden property and the change event for visibility
      if (typeof document.hidden !== "undefined") {
        hidden = "hidden";
        visibilityChange = "visibilitychange";
      } else if (typeof document.msHidden !== "undefined") {
        hidden = "msHidden";
        visibilityChange = "msvisibilitychange";
      } else if (typeof document.webkitHidden !== "undefined") {
        hidden = "webkitHidden";
        visibilityChange = "webkitvisibilitychange";
      }
      document.addEventListener(visibilityChange, handleVisibilityChange, false);
   }
   //pause the updater when the window lose its focus
   function handleVisibilityChange() {
      if (document[hidden]) {
         stop();
      } else {
         start();
      }
   }
   function update(){
      console.log('updating data..')
      let tempData = jsonApi.getAll()
      .then(function (data) {
         overview.update(data.coins, data.investments);
         leaderboard.update(data.investors.top);
      })
      .catch(function (err) {
         console.error('error while retrieving apis data', err.statusText);
         connectionErrorToast(err)
      }); 
      //beep(500, 2);//used for debugging on mobile
   }
   function stop(){
      if(interval){
         clearInterval(interval);
         interval = false;
      }
   }
   function start(){
      if(!interval){
         update()
         interval = setInterval(update,updateInterval);
      }
   }
   
   return {
      init: init,
      update: update,
      pause: stop,
      resume: start
   }
})();


(function(){
   document.addEventListener('DOMContentLoaded', function(){
      //init local modules
      overview.init()
      overviewChart.init()
      userAccount.init()
      updater.init()
      investmentsCalculator.init()
      
      
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
      
   });
   
}());





