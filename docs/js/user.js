import {connectionErrorToast} from './modules/uiElements.js';
import * as jsonApi from './modules/jsonApi.js';
import {Scheduler} from './modules/scheduler.js';

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


let investments = (function(){
   //init ids and stuff. create own update scheduler
   function init(){
      
   }
   return {
      init: init
   }
})();


let activeInvestments = (function(){
   //init ids and stuff. create own update scheduler
   function init(){
      
   }
   return {
      init: init
   }
})();

(function(){
   document.addEventListener('DOMContentLoaded', function(){
      getUser.init();
      pageManager.init();
      overview.init();
   });
})();