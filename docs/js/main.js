"use strict";
let jsonApi = (function(){
   let options = {
      method: "GET",
      //url: "/api",
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


let userAccount = (function(){
   let searchBarIds = {
      desktop: 'investor-username',
      mobile:'investor-username-mobile'      
   }
   function show(device) {
      let username = document.getElementById(searchBarIds[device]).value;
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
      let searchEl = document.getElementById(searchBarIds['desktop']);
      searchEl.addEventListener('keypress', e=> {if((e.which || e.keyCode) === 13)show('desktop')} );     
      searchEl = document.getElementById(searchBarIds['mobile']);
      searchEl.addEventListener('keypress', e=> {if((e.which || e.keyCode) === 13)show('mobile')} );
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
      const POPUP = 2
      const SHOWPOPUP = false
      //debug
      //localStorage.removeItem('viewed_info')   
      if(SHOWPOPUP && localStorage.getItem('viewed_info') != POPUP){
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
      userAccount.init()
      
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
            console.error('error while retrieving apis data', err.statusText);
            connectionErrorToast(err)
         });      
      } 
      updater();
   });
   
}());


function connectionErrorToast(error){
   let toastHTML = '';
   //simple connection error
   if(error.status === 0 || error.statusText === ""){
      toastHTML = '<p>We couldn\'t get the latest data. Please check your connection</p>';
   }//more serious problem, that is worth reporting
   else{
      globalError = error;
      toastHTML = '<p>an error occurred while trying to get the latest data. </p><button class="btn-flat toast-action" onclick="reportError()">report</button>';   
   }
   M.toast({html: toastHTML,displayLength:2000}); 
}

var globalError;
function reportError(){
   let responsable = "robalborb";
   let subject = "BRUH%20YOU%20MESSED%20UP!!1!";
   let message = "error: "+JSON.stringify(globalError);
   let url = "https://www.reddit.com/message/compose/?to="+responsable+"&subject="+subject+"&message="+message;
   let win = window.open(url, '_blank');
   win.focus();
}


function formatToUnits(val) {
    let number = parseInt(val);
    let abbrev = ['', 'K', 'M', 'B', 'T', 'q', 'Q', 's', 'S'];
    //, 'Sx', 'Sp', 'Oc', 'No', 'Dc', 'Ud', 'Dd', 'Td', 'Qad', 'Qid', 'Sxd', 'Spd', 'Ocd', 'Nod', 'Vg', 'Uvg','Dvg'];
    //after the Dvg (duovigintillion) use scientific notation
    let unrangifiedOrder = Math.floor(Math.log10(Math.abs(number)) / 3);
    let order = Math.max(0, Math.min(unrangifiedOrder, abbrev.length -1 ));
    let suffix = abbrev[order];
    let precision = suffix ? 1 : 0;
    let res = (number / Math.pow(10, order * 3)).toFixed(precision) + suffix;
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
    //creates a spinning loader
    document.getElementById('investment-result').innerHTML =
     `<div class="preloader-wrapper small active custom-preloader-wrapper">
       <div class="spinner-layer spinner-green-only">
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
        let errorString = '<p>'+er.status+' connection error</p>';
        //removes the spinnign loader
        document.getElementById('investment-result').innerText = '000';
        M.toast({html: errorString,displayLength:2000});
    });
}
