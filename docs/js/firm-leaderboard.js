import {connectionErrorToast} from './modules/uiElements.js';
import * as jsonApi from './modules/jsonApi.js';
import {formatToUnits, getSuffix, commafy} from './modules/dataUtils.js';
import {seasons} from '../resources/leaderboards/seasons.js';

let getLeaderboard = (function(){
   function init() {
      jsonApi.get('/firms/top?per_page=50')
      .then(d => leaderboard.update(d))
      .catch(connectionErrorToast)
   }
   return {
      init: init
   }
})();


let leaderboard = (function() {
   let ids = {
      table: 'leaderboards-table',
      cards: {
         prefix: ['top', 'left', 'right'],
         name: 'name',
         balance: 'balance',
         balanceSuffix: 'balance-suffix',
         profile: 'profile'
      }
   }
   let cardElements = {};

   function init() {
      //init card elements
      for (let prefix of ids.cards.prefix) {
         cardElements[prefix] = {
            name: document.getElementById(`${prefix}-${ids.cards.name}`),
            balance: new CountUp(`${prefix}-${ids.cards.balance}`, 0, 0, 1),
            balanceSuffix: document.getElementById(`${prefix}-${ids.cards.balanceSuffix}`),
            profile: document.getElementById(`${prefix}-${ids.cards.profile}`)
         }
      }
   }
   function update(data) {
      renderCards(data)
      renderTable(data)
   }
   function renderTable(obj){
      let html = ''
      for(let i=3,l=obj.length; i<l;i++){
         let firm = obj[i]
         let badge = ''
         html += `<tr>
                     <td>#${i+1}</td>
                     <td><a href="./firm.html?firm=${firm.id}">${firm.name} ${badge}</a></td>
                     <td title="${commafy(firm.balance)} M&cent;">${formatToUnits(firm.balance)}</td>
                     <td>${firm.rank}</td>
                     <td>${firm.size}</td>
                  </tr>`
      }
      document.getElementById(ids.table).innerHTML = html  
   }
   function renderCards(obj){
      for(let i=0; i<3; i++){
         let data = obj[i]
         let card = cardElements[ids.cards.prefix[i]]
         card.name.classList.add("flip")
         setTimeout(updateName,240);
         function updateName(){
            card.name.innerText = data.name;
            setTimeout(removeClass,500);
         }
         function removeClass(){
            card.name.classList.remove("flip")
         }
         let balance = getSuffix(data.balance)
         card.balance.update(balance.val);
         card.balanceSuffix.innerText = balance.suffix
         card.profile.setAttribute("href", "./firm.html?firm="+data.id);
      }
   }
   return {
      init: init,
      update: update
   }
})();

(function(){
   document.addEventListener('DOMContentLoaded', function(){
      getLeaderboard.init();
      leaderboard.init();
      document.getElementById('scroll-top').addEventListener('click',_=>scroll(0,0))
      
   });
})();
