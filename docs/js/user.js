import {connectionErrorToast} from './modules/uiElements.js';
import * as jsonApi from './modules/jsonApi.js';
import {Scheduler} from './modules/scheduler.js';
import {formatToUnits, commafy} from './modules/dataUtils.js';
import {getFileName, getDescription} from './modules/badges.js';

var getUser = (function(){
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
   function show(device,pushState=true) {
      let username = document.getElementById(ids.searchBar[device]).value;
      if(username.length > 0){
         if(device === 'mobile'){
            //close sidenav
            let elem = document.getElementById('mobile-sidebar');
            let instance = M.Sidenav.getInstance(elem);
            instance.close();
         }
         if(pushState)history.pushState(null, '', '?account='+username);
         pageManager.search(username);
      }
   }
   function checkUrl(){
      // check if url contains ?account=
      let url = new URL(window.location.href);
      let username = url.searchParams.get("account");
      const reg = /^[a-zA-Z0-9\-\_]+$/;
      if (reg.test(username)) {
         document.getElementById('investor-username').value = username;
         show('desktop',false);
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
      //add history back listener
      window.addEventListener('popstate', function(e) {
         checkUrl();
      });
      checkUrl();

   }
   return {
      init: init,
      show: show
   }
})();

let pageManager = (function(){
   let ids = {
      overlay: 'overlay',
      overlayContent: 'overlay-content',
      username: 'username',
      firm: 'user-firm'
   }
   let overviewUpdater = undefined;
   function init(){
      //nothing to init
   }
   function search(username){
      //set overlay to loading 
      document.body.style.overflowY = 'hidden'
      document.getElementById(ids.overlay).style.display = 'block'
      document.getElementById(ids.overlayContent).innerHTML = 
      `<h4>Searching. </h4>
      <div class="preloader-wrapper big active">
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
      //search user
      jsonApi.get('/investor/'+username)
      .then(d => {
         jsonApi.get('/firm/'+d.firm)
         .then(df => {display(d,df)})
         .catch(er=>{
            if(er.status == 404){
               notFound();
            }else{
               connectionErrorToast(er)
            }
         })
      })
      .catch(er=>{
         if(er.status == 404){
            notFound();
         }else{
            connectionErrorToast(er)
         }
      })
   }
   function notFound(){
      document.body.style.overflowY = 'hidden'
      document.getElementById(ids.overlay).style.display = 'block'
      document.getElementById(ids.overlayContent).innerHTML = 
      `<h5>User not found</h5>`
      //kill old overview updater
      if(overviewUpdater)overviewUpdater.stop();
      overviewUpdater = undefined;
   }
   function display(data, firmData){
      //remove overlay with animation
      let overlay = document.getElementById(ids.overlay);
      overlay.classList.add('fade-out')
      setTimeout(_=>{
      document.body.style.overflowY = 'auto'
         overlay.style.display = 'none'
         overlay.classList.remove('fade-out')
      },900)
      
      //update name
      let nameEl = document.getElementById(ids.username)
      let firmEl = document.getElementById(ids.firm)
      nameEl.innerText = 'u/'+data.name
      nameEl.setAttribute('href','https://www.reddit.com/u/'+data.name)
      firmEl.innerText = firmData.name
      firmEl.setAttribute('href','./firm.html?firm='+firmData.id)
      //update badges
      badges.set(data.badges)
      //update investments
      investments.setUser(data.name,data.completed);
      //kill old overview updater
      if(overviewUpdater)overviewUpdater.stop();
      //create a new one, for the new username
      overviewUpdater = new Scheduler(
      function(){
         jsonApi.get('/investor/'+data.name)
         .then(overview.update)
         .catch(connectionErrorToast)
      },
      60000 //every 60 seconds
      )    

      //call investments.init()
      //call activeInvestments.init()
   }

   return {
      init: init,
      search: search
   }
})();


let overview = (function(){
   let counters = {
      netWorth: undefined,
      balance: undefined,
      investmentsActive: undefined,
      goneBroke: undefined,
      rank: undefined
   }
   function init(data){
      counters = {
         netWorth: new CountUp("net-worth", 0, 0),
         balance: new CountUp("balance", 0, 0),
         completedInvestments: new CountUp("completed-investments", 0, 0),
         goneBroke: new CountUp("gone-broke", 0, 0),
         rank: new CountUp("rank", 0, 0)
      }
      if(data)update(data);
   }
   function update(data){
      counters.netWorth.update(data.networth)
      counters.balance.update(data.balance)
      counters.completedInvestments.update(data.completed)
      counters.goneBroke.update(data.broke)
      counters.rank.update(data.rank)
   }
   return {
      init:init,
      update: update
   }
   
})();

let badges = (function(){
   let ids = {
      container: 'badges-container'
   }
   let amount = 0;
   function set(badges){
      render(badges);
   }
   function render(badges){
      let html = '';
      for(let badge of badges){
         html += `
         <img class="badge z-depth-2 tooltipped" 
         data-position="top" 
         data-tooltip="${getDescription(badge)}" 
         src="./resources/badges/${getFileName(badge)}"/>
         `
      }
      if(!html)html='<p class="grey-text">This account doesn\'t have any badges.</p>'
      let container = document.getElementById(ids.container);
      container.innerHTML = html;
      let elems = container.querySelectorAll('.tooltipped');
      M.Tooltip.init(elems);
   }
   return {
      set: set
   }
})();


let investments = (function(){
   let ids = {
      toggleFilters: 'filters-show',
      tableControls: 'table-controls',
      dateFrom : 'date-from',
      dateTo : 'date-to',
      applyFilters: 'filters-apply',
      clearFilters: 'filters-clear',
      table: 'investments-table',
      tableOverlay: 'investments-table-overlay',
      page: {
         previous: 'page-previous',
         indicator: 'page-indicator',
         next: 'page-next'
      }
   }
   let filtersOpen = false;
   let loading = false;
   
   let showOverlayTimer;
   let showingOverlay = false;
   
   let name = '';
   
   let perPage = 15;
   let pages = 0;
   let page = 0;
   let tFrom = '';
   let tTo = '';
   const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
   
   function init(){
      document.getElementById(ids.toggleFilters).addEventListener('click',toggleFilters);
      document.getElementById(ids.applyFilters).addEventListener('click',applyFilters);
      document.getElementById(ids.clearFilters).addEventListener('click',clearFilters);
      document.getElementById(ids.page.previous).addEventListener('click',previous);
      document.getElementById(ids.page.next).addEventListener('click',next);
      setInterval(60000, updateTable);
   }
   //initialize the table for a specific user
   function setUser(userName,amount){
      name = userName;
      pages = Math.ceil(amount/perPage);
      page = 0;
      tFrom = '';
      tTo = '';
      updatePageNumber();
      updateTable();
   }
   function toggleFilters(){
      let toggleBt = document.getElementById(ids.toggleFilters);
      let tableControls = document.getElementById(ids.tableControls);
      if(filtersOpen){
         filtersOpen = false;
         toggleBt.firstChild.innerText = 'expand_more';
         tableControls.classList.remove('f-scale');
      }else{
         filtersOpen = true;
         toggleBt.firstChild.innerText = 'expand_less';
         tableControls.classList.add('f-scale');
      }
   }
   function applyFilters(){
      if(!loading){
         let dateFrom = document.getElementById(ids.dateFrom)
         let dateTo = document.getElementById(ids.dateTo)
         if(dateFrom.value && dateTo.value){
            tFrom = Date.parse(dateFrom.value)/1000
            tTo = Date.parse(dateTo.value)/1000
            page = 0;
            updatePageNumber();
            updateTable();
         }else{
            let toastHTML = 'invalid data'
            M.toast({html: toastHTML,displayLength:2000, classes:"dark-toast"}); 
         }
      }
   }
   function clearFilters(){
      if(!loading){
         document.getElementById(ids.dateFrom).value = '';
         document.getElementById(ids.dateTo).value = '';
         page = 0;
         tFrom = '';
         tTo = '';
         updatePageNumber();
         updateTable();
      }
   }
   function previous(){
      if(!loading){
         page--
         updatePageNumber();
         updateTable()
      }
   }
   function updatePageNumber(){
      let previousBt = document.getElementById(ids.page.previous).classList;
      let nextBt = document.getElementById(ids.page.next).classList;
      //increment by one the page number. keep it to zero if there are zero pages
      let pageNonZeroIndexed = pages>0 ? page+1 : page
      document.getElementById(ids.page.indicator).innerText = (pageNonZeroIndexed)+'/'+pages
      
      if(page>0) previousBt.remove('disabled')
      else previousBt.add('disabled')
   
      if((page+1)<pages) nextBt.remove('disabled')
      else nextBt.add('disabled')
   }
   function next(){
      if(!loading){
         page++
         updatePageNumber();
         updateTable()
      }
   }
   function updateTable(){
      showOverlay()
      let options = `?per_page=${perPage}&page=${page}&from=${tFrom}&to=${tTo}`
      jsonApi.get(`/investor/${name}/investments${options}`)
      .then(d=>{
         if(d.length>0)render(d)
         else noInvestments()
         removeOverlay()
         profitChart.updateDataSet(d)
      })
      .catch(er=>{
         removeOverlay()
         connectionErrorToast(er);
      })      
   }
   function showOverlay(){
      //console.log(9)
      loading = true;
      //set a timer that displays the loading overlay after x milliseconds
      showOverlayTimer = setTimeout(function(){
         //console.log(10)
         showingOverlay = true;
         document.getElementById(ids.table).style.opacity = 0.4
         document.getElementById(ids.tableOverlay).style.opacity = 1      
      },200//the max millis of time allowed to api calls before the loader overlay is shown
      )
   }
   function removeOverlay(){
      //remove the overlay if it is being shown
      //console.log(11)
      if(showingOverlay){
         //console.log(12)
         let overlay = document.getElementById(ids.tableOverlay)
         document.getElementById(ids.table).style.opacity = 1
         overlay.classList.add('pulse-out')
         setTimeout(_=>{
         showingOverlay = false;
            loading = false;
            overlay.style.opacity = 0
            overlay.classList.remove('pulse-out')
         },400)
      }else{
         loading = false;
         //if the overlay is not not being shown (there is a timer that is about to show it)
         //stop the timer 
         clearTimeout(showOverlayTimer)
      }
   }
   function noInvestments(){
      document.getElementById(ids.table).innerHTML = 
      `<h5 class="grey-text">No investments found</h5>`
      document.getElementById(ids.page.next).classList.add('disabled')
   }
   function render(data){
      //console.log(data)
      let html = `
      <thead>
        <tr>
            <th>post</th>
            <th>date</th>
            <th class="invest-values">in</th>
            <th class="invest-values">result</th>
        </tr>
      </thead>
      <tbody>
      `
      for(let inv of data){
         let invTime = new Date(inv.time*1000)
         let time = invTime.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', hour12: false})
         let date = invTime.getDate()+'/'+monthNames[invTime.getMonth()]
         html += `
         <tr>
            <td><a href="https://redd.it/${inv.post}">${inv.post}</a></td>
            <td><span class="grey-text">${time}<br>${date}</span></td>
            <td class="invest-values"><span title="${commafy(inv.amount)} MemeCoins">${formatToUnits(inv.amount)} M&cent;</span><br><span title="${commafy(inv.upvotes)} upvotes">${formatToUnits(inv.upvotes)} &uarr;</span></td>
            <td class="invest-values">`
         if(inv.done){
            let color = inv.success? 'green-text' : 'red-text text-lighten-1'
            let sign = inv.success? '<i class="material-icons">arrow_drop_up</i>' : '<i class="material-icons">arrow_drop_down</i>'
            let profit = sign+formatToUnits(Math.abs(inv.profit))
            let finalUpvotes = inv.final_upvotes? formatToUnits(inv.final_upvotes) : '--';
            html += `<span class="${color}" title="${commafy(inv.profit)} MemeCoins">${profit} M&cent;</span><br><span title="${commafy(inv.final_upvotes)} upvotes">${finalUpvotes} &uarr;</span>`
         }else{
            let currentTime = new Date();
            //14400000 == 4h
            let millisecondsLeft = 14400000 - ( currentTime.getTime() - invTime.getTime() );
            if(millisecondsLeft >= 0 ){
               let hoursLeftString = Math.floor(millisecondsLeft / 3600000).toString()
               let minutesLeftString = Math.floor((millisecondsLeft % 3600000) / 60000).toString()
               if(minutesLeftString.length < 2) minutesLeftString = "0" + minutesLeftString;
               let timeLeftString = hoursLeftString+':'+minutesLeftString;
               html += `<span><i class="material-icons">access_time</i> ${timeLeftString} left</span>`
            }else{
               html += '<span><i class="material-icons">layers</i> processing&hellip;</span>'
            }
         }
         html += '</td></tr>'

      }
      html += `</tbody>`
      document.getElementById(ids.table).innerHTML = html
   }
   return {
      init: init,
      setUser: setUser
   }
})();


let profitChart = (function(){
   let desktop = false;
   const fields = ['profit','amount','upvotes','final_upvotes']
   let field = fields[0]
   let tempData;
   let canvas1;
   let ch1;
   //the points displayed in the chart
   let points = 15;
   
   let ids = {
      chart: 'profit-graph',
      dropdown: 'dataset-select'
   }

   function getScreenSize(){
      let w = window,
      d = document,
      e = d.documentElement,
      g = d.getElementsByTagName('body')[0],
      x = w.innerWidth || e.clientWidth || g.clientWidth,
      y = w.innerHeight|| e.clientHeight|| g.clientHeight;
      return {x,y};
   }
   function update(){
      if(desktop){
         let chartDataSet = ch1.data.datasets[0];
         let data = tempData;
         for(let i=0; i<points; i++){
            let inv = data[i] || {};
            chartDataSet.data[points-i-1] = inv[field];
         }
         ch1.update();
      }
   }
   function updateDataSet(data = []){
      if(desktop){
         tempData = data;
         update();
      }
   }
   function updateField(){
      field = document.getElementById(ids.dropdown).value;
      update();
   }
   function init(){
      let x = getScreenSize().x;
      //if on desktop
      if(x>=800){
      canvas1 = document.getElementById(ids.chart)
      desktop = true
      //init dropdown listener
      let dropDown = document.getElementById(ids.dropdown);
      dropDown.addEventListener('change',updateField)
      field = dropDown.value
      
      let graphLabels = []
      for(let i=0;i<points;i++){
         graphLabels.push('')
      }
      let ctx = canvas1.getContext('2d');
      ch1 = new Chart(ctx, {
         type: 'line',
         data: {
            labels: graphLabels,
            datasets: [{
               //red dataset
               data: [],
               label: "amount",
               yAxisID: "A",
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
                     display: true,
                     callback: val => formatToUnits(val)
                  }
               },],
               xAxes: [{
                  gridLines: {
                     display: true,
                     color: 'rgba(255,255,255,0.1)',
                     zeroLineColor: 'rgba(255,255,255,0.0)'
                  },                  
                  ticks: {
                     display: false,
                     fontColor: 'rgba(255,255,255,0.4)',
                  }                  
               }]
            }
         }
      });
      
      }
   
   }
   return{
      init: init,
      update: update,
      updateDataSet: updateDataSet
   }
})();


(function(){
   document.addEventListener('DOMContentLoaded', function(){
      getUser.init();
      pageManager.init();
      overview.init();
      investments.init();
      profitChart.init();
   });
})();
