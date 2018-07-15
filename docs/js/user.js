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
      overlay: 'loading-overlay'
   }
   function init(){
      //init ids
   }
   function search(username){
      //make ajax to investor/username
      //if good, call display(data)
      //else call displaynotfound()
   }
   function displayNotFound(){
      //change overlay text with "username not found"
   }
   function display(data){
      //init overview(data)
      //create scheduler for overview update (executeOnCreation = false)
      
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
      let overviewUpdater = new Scheduler(
         function(){
            console.log('updating overview..')
            jsonApi.get('user/')
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
   }  
   return {
      init:init,
      update: update
   }
   
})();


let investments = (function(){
   //init ids and stuff. create own update scheduler
   return {
      init: init
   }
})();


let activeInvestments = (function(){
   //init ids and stuff. create own update scheduler
   return {
      init: init
   }
})();

(function(){
   document.addEventListener('DOMContentLoaded', function(){
      getUser.init();
      pageManager.init();
   });
})();