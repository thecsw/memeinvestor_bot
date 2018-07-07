import {connectionErrorToast} from './modules/uiElements.js';
import * as jsonApi from './modules/jsonApi.js';


var userAccount = (function(){
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
         history.pushState(null, '', '?account='+username);
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
      }

   }
   return {
      init: init,
      show: show
   }
})();


(function(){
   document.addEventListener('DOMContentLoaded', function(){
      userAccount.init();
   });
})();