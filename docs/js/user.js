import {connectionErrorToast} from './modules/uiElements.js';
import * as jsonApi from './modules/jsonApi.js';
import {Scheduler} from './modules/scheduler.js';
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
      username: 'username'
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
      `<h5>User not found</h5>`
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
      let nameEl = document.getElementById(ids.username);
      nameEl.innerText = 'u/'+data.name
      nameEl.setAttribute('href','https://www.reddit.com/u/'+data.name)
      //update badges
      badges.set(data.badges)
      //update investments
      investments.set(data.name);
      
      //kill old overview updater
      if(overviewUpdater)overviewUpdater.stop();
      //create a new one, for the new username
      overviewUpdater = new Scheduler(
      function(){
         jsonApi.get('/investor/'+data.name)
         .then(overview.update)
         .catch(connectionErrorToast)
      },
      10000 //every 10 seconds
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
      goneBroke: undefined
   }
   function init(data){
      counters = {
         netWorth: new CountUp("net-worth", 10, 1.5),
         balance: new CountUp("balance", 10, 0, 1.5),
         completedInvestments: new CountUp("completed-investments", 3, 1.5),
         goneBroke: new CountUp("gone-broke", 12, 99.99)
      }
      if(data)update(data);
   }
   function update(data){
      //TODO: replace with data.netWorth when added to apis
      counters.netWorth.update(9876544321)
      counters.balance.update(data.balance)
      counters.completedInvestments.update(data.completed)
      counters.goneBroke.update(data.broke)
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
      if(!html)html='<p class="grey-text">This account doesn\'t have any badge.</p>'
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
      table: 'investments-table'
   }
   let toggleBt = undefined;
   let filtersOpen = false;
   
   let perPage = 10;
   let page = 0;
   function toggleFilters(){
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
   function init(){
      toggleBt = document.getElementById(ids.toggleFilters);
      toggleBt.addEventListener('click',toggleFilters);
   }
   function set(name){

      let options = `?per_page=${perPage}&page=${page}`
      jsonApi.get(`/investor/${name}/investments${options}`)
      .then(render)
      .catch(er=>{
         if(er.status === 404)noInvestments();
         else connectionErrorToast(er);
      })
       
   }
   function noInvestments(){
      document.getElementById(ids.table).innerHTML = 
      `<h5 class="grey-text">No investments found</h5>`
   }
   function render(data){
      console.log(data)
      let html = `
      <thead>
        <tr>
            <th>Post url</th>
            <th>date</th>
            <th>In</th>
            <th>out</th>
        </tr>
      </thead>
      <tbody>
      `
      for(let inv of data){
         html += `
         <tr>
            <td><a href="https://redd.it/${inv.post}">${inv.post}</a></td>
            <td><span class="grey-text">23:22<br>19/jan</span></td>
            <td>${inv.amount} Mc<br>${inv.upvotes} upvotes</td>
            <td><span class="green-text">+340 Mc</span><br>423 upvotes</td>
         </tr>`
      }
      html += `</tbody>`
      document.getElementById(ids.table).innerHTML = html
   }
   function update(){
      
   }
   return {
      init: init,
      set: set,
      update: update
   }
})();



(function(){
   document.addEventListener('DOMContentLoaded', function(){
      getUser.init();
      pageManager.init();
      overview.init();
      investments.init();
   });
})();