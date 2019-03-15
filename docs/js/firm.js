import {connectionErrorToast} from './modules/uiElements.js';
import * as jsonApi from './modules/jsonApi.js?c=2';
import {Scheduler} from './modules/scheduler.js';
import {formatToUnits} from './modules/dataUtils.js';
import {getFileName, getDescription} from './modules/badges.js';

var getFirm = (function(){
   function show(device,pushState=true) {
      let url = new URL(window.location.href);
      let firm = url.searchParams.get("firm");
      if(firm.length > 0){
         if(device === 'mobile'){
            //close sidenav
            let elem = document.getElementById('mobile-sidebar');
            let instance = M.Sidenav.getInstance(elem);
            instance.close();
         }
         if(pushState)history.pushState(null, '', '?firm='+firm);
         pageManager.search(firm);
      }
   }
   return {
      show: show
   }
})();

let pageManager = (function(){
   let ids = {
      overlay: 'overlay',
      overlayContent: 'overlay-content',
      firm: 'firm-name',
      ceo: 'firm-ceo',
      level: 'firm-level',
      image: 'firm-image'
   }
   let overviewUpdater = undefined;
   function init(){
      //nothing to init
   }
   function search(firm){
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
      //search firm
      //TODO: update api call
      jsonApi.get('/investor/'+username)
      .then(display)
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
      `<h5>Firm not found</h5>`
      //kill old overview updater
      if(overviewUpdater)overviewUpdater.stop();
      overviewUpdater = undefined;
   }
   function display(data){
      //remove overlay with animation
      let overlay = document.getElementById(ids.overlay);
      overlay.classList.add('fade-out')
      setTimeout(_=>{
      document.body.style.overflowY = 'auto'
         overlay.style.display = 'none'
         overlay.classList.remove('fade-out')
      },900)
      
      //update name
      let nameEl = document.getElementById(ids.firm);
      let ceoEl = document.getElementById(ids.ceo);
      let levelEl = document.getElementById(ids.level);
      let imageEl = document.getElementById(ids.image);
      nameEl.innerText = data.name
      ceoEl.InnerText = data.ceo
      levelEl.InnerText = data.level
      imageEl.setAttribute('src',data.logo)
      //update badges
      upgrades.set(data.upgrades)
      //update firm members
      firmMembers.setFirm(data.name,data.firm-members);
      //update firm value
      firmValue.setFirm(data.firm,data.firm-members);
   }
   return {
      init: init,
      search: search
   }
})();

let overview = (function(){
   let counters = {
      firmValue: undefined,
   }
   function init(data){
      counters = {
         firmValue: new CountUp("firmvalue", 0, 0),
      }
      if(data)update(data);
   }
   function update(data){
      counters.firmValue.update(data.firmvalue)
   }
   return {
      init:init,
      update: update
   }
   
})();

let upgrades = (function(){
   let ids = {
      container: 'upgrades-container'
   }
   let amount = 0;
   function set(upgrades){
      render(upgrades);
   }
   function render(upgrades){
      let html = '';
      for(let upgrade of upgrades){
         html += `
         <img class="badge z-depth-2 tooltipped" 
         data-position="top" 
         data-tooltip="${getDescription(upgrade)}" 
         src="./resources/badges/${getFileName(upgrade)}"/>
         `
      }
      if(!html)html='<p class="grey-text">This firm doesn\'t have any upgrades.</p>'
      let container = document.getElementById(ids.container);
      container.innerHTML = html;
      let elems = container.querySelectorAll('.tooltipped');
      M.Tooltip.init(elems);
   }
   return {
      set: set
   }
})();


let firmMembers = (function(){
   let ids = {
      table: 'investments-table',
      tableOverlay: 'investments-table-overlay',
      page: {
         previous: 'page-previous',
         indicator: 'page-indicator',
         next: 'page-next'
      }
   }
   let loading = false;
   
   let name = '';
   
   let perPage = 15;
   let pages = 0;
   let page = 0;
   
   function init(){
      document.getElementById(ids.page.previous).addEventListener('click',previous);
      document.getElementById(ids.page.next).addEventListener('click',next);
   }
   //initialize the table for a specific user
   function setFirm(firmName,firmMembers){
      name = firmName;
      members = firmMembers
      pages = Math.ceil(members.length/perPage);
      page = 0;
      updatePageNumber();
      render(members);
   }
   function previous(){
      if(!loading){
         page--
         updatePageNumber();
         render(members);
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
         render(members);
      }
   }
   function render(data){
      console.log(data)
      let html = `
      <thead>
        <tr>
            <th>name</th>
            <th>position</th>
        </tr>
      </thead>
      <tbody>
      `
      for(let member of data){
         html += `
         <tr>
            <td>${member.name}</td>
            <td>${member.position}</td>
            <td>`
         html += '</td></tr>'
      }
      html += `</tbody>`
      document.getElementById(ids.table).innerHTML = html
   }
   return {
      init: init,
      setFirm: setFirm
   }
})();

//TODO: update when we have the firm value API endpoint
let firmValue = (function(){
   
   let name = '';
   let members = '';

   function setFirm(firmName,firmMembers){
      name = firmName;
      members = firmMembers
      updateGraph();
   }

   function updateGraph(){
      //TODO: update to firm value API call
      let options = `?per_page=${perPage}&page=${page}&from=${tFrom}&to=${tTo}`
      jsonApi.get(`/investor/${name}/investments${options}`)
      .then(d=>{
         if(d.length>0)profitChart.updateDataSet(d)
         else noInvestments()
         removeOverlay()
      })
      .catch(er=>{
         removeOverlay()
         connectionErrorToast(er);
      })      
   }
   return {
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
