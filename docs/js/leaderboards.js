import {connectionErrorToast} from './modules/uiElements.js';
import * as jsonApi from './modules/jsonApi.js?c=1';
import {formatToUnits, getSuffix} from './modules/dataUtils.js';

const seasons = [
   {name:'beta season', id:'beta', dataUrl:'./resources/leaderboards/beta.json'},
   {name:'season 1', id:'s1', dataUrl:'./resources/leaderboards/s1.json'},
   {name:'season 2', id:'s2', dataUrl:'https://memes.market/api/investors/top?per_page=50'},
]

let getSeason = (function(){
   let ids = {
      dropdown: 'dataset-select'
   }
   let cache = {};
   /*seasons are hardcoded here.
   the current season is the last one in the array.*/
   function init(){
      let dropDown = document.getElementById(ids.dropdown);
      let html = seasons.map(s=>`<option value="${s.id}" >${s.name}</option>`).join('')
      /*the line above is the equivalent of 
      let html = '';
      for(let season of seasons){
         html+= `<option value="${season.id}" >${season.name}</option>`
      }
      i'll be using this ugly hack a lot. sorry.
      */
      dropDown.innerHTML = html;
      dropDown.addEventListener('change', _=> search(dropDown.value) )
      window.addEventListener('popstate', function(e){
         checkUrl();
      });
      checkUrl();
   }
   function isValidId(id){
      return seasons.some(a => a.id === id)
   }
   function getLastId(){
      return seasons[seasons.length-1].id
   }
   function checkUrl(){
      // check if url contains ?season=<a valid season>
      let url = new URL(window.location.href);
      let seasonId = url.searchParams.get("season");
      if (!isValidId(seasonId)){
         seasonId = getLastId()
         history.replaceState(null, '', '?season='+seasonId)
      }
      search(seasonId, false)
   }
   function search(seasonId, pushState = true){
      if(pushState)history.pushState(null, '', '?season='+seasonId);
      document.getElementById(ids.dropdown).value = seasonId;
      //download the season data if not in cache. then proceeds to update the leaderboard
      if(!cache[seasonId]){
         let seasonUrl = seasons.find(s=> s.id === seasonId).dataUrl
         let options = {
            method: "GET",
            url: seasonUrl
         }
         jsonApi.get('',options)
            .then(d=>{
               cache[seasonId] = d;
               leaderboard.update(d)
            })
            .catch(connectionErrorToast)
      }else{
         leaderboard.update(cache[seasonId])
      }
   }
   return{
      init: init
   }
})()


let leaderboard = (function(){
   let ids = {
      cards: {
         prefix: ['top','left','right'],
         name: 'name',
         netWorth: 'net-worth',
         netWorthSuffix: 'net-worth-suffix',
         profile: 'profile'
      }
   }
   let cardElements = {};

   function init(){
      //init card elements
      for(let prefix of ids.cards.prefix){
         cardElements[prefix] = {}
         let card = cardElements[prefix];
         card.name = document.getElementById(prefix+'-'+ids.cards.name)
         card.netWorth = new CountUp(prefix+'-'+ids.cards.netWorth,0, 1.5);
         card.netWorthSuffix = document.getElementById(prefix+'-'+ids.cards.netWorthSuffix)
         card.profile = document.getElementById(prefix+'-'+ids.cards.profile)
      } 
      //add buttons click listener
      let button = document.getElementById(ids.buttons.beta);
      button.addEventListener('click', e=> loadBeta() );
      button = document.getElementById(ids.buttons.current);
      button.addEventListener('click', e=> loadCurrent() );
      // check if url contains ?s=
      let url = new URL(window.location.href);
      let season = url.searchParams.get("s");
      if (season === 'current'){
         loadCurrent();
      }
      else{
         loadBeta();
      }
   }
   function update(d){
      console.log('-- update --')
      console.log(d)
      console.log('-- update --')
   }
   function loadBeta(){
      document.getElementById(ids.buttons.beta).classList.add("disabled");
      document.getElementById(ids.buttons.current).classList.remove("disabled");
      //render leaderboard table
      let tb = document.getElementById("leaderboards-table");
      let html = ""
          for(let i=3,l=betaBlob.length; i<l;i++){
             let user = betaBlob[i]
             let badge = user[4]>0? '<span class="red bankrupt-badge white-text">'+user[4]+'</span>':"";
             html += "<tr><td>#"+(i+1)+"</td>"+
                        '<td><a href="./user.html?account='+user[1]+'">'+user[1] + badge+"</a></td>"+
                        "<td>"+formatToUnits(user[2])+"</td>"+
                        "<td>"+user[3]+"</td></tr>"
          }
      tb.innerHTML = html
      //create top 3 object to pass to updatecards
      let firstThree = {}
      for(let i=0; i<3; i++){
         let prefix = ids.cards.prefix[i];
         firstThree[prefix] = {}
         let card = firstThree[prefix];
         card.name = betaBlob[i][1]
         card.netWorth = betaBlob[i][2]
      }
      updateCards(firstThree)
   }
   function loadCurrent(){
      document.getElementById(ids.buttons.beta).classList.remove("disabled");
      document.getElementById(ids.buttons.current).classList.add("disabled");
      if(!currentBlob){
         jsonApi.get('/investors/top?per_page=50')
         .then(function (data) {
            currentBlob = data;
            loadFromObject(data);
         })
         .catch(function (err) {
            console.error('error while retrieving apis data', err);
            connectionErrorToast(err)
         });
      }else{
         loadFromObject(currentBlob);
      } 
   }
   function loadFromObject(obj){
      //create top 3 object to pass to updatecards
      let firstThree = {}
      for(let i=0; i<3; i++){
         let prefix = ids.cards.prefix[i];
         firstThree[prefix] = {}
         let card = firstThree[prefix];
         card.name = obj[i].name
         card.netWorth = obj[i].networth
      }
      updateCards(firstThree)  
      //update table
      let tb = document.getElementById("leaderboards-table");
      let html = ""
          for(let i=3,l=obj.length; i<l;i++){
             let user = obj[i]
             let badge = obj.broke>0? '<span class="red bankrupt-badge white-text">'+obj.broke+'</span>':"";
             html += "<tr><td>#"+(i+1)+"</td>"+
                        '<td><a href="./user.html?account='+user.name+'">'+user.name + badge+"</a></td>"+
                        "<td>"+formatToUnits(user.networth)+"</td>"+
                        "<td>"+user.completed+"</td></tr>"
          }
      tb.innerHTML = html      
   }
   function updateCards(cards){
      for (let el in cards) {
         let data = cards[el]
         let card = cardElements[el]
         card.name.classList.add("flip")
         setTimeout(updateName,240);
         function updateName(){
            card.name.innerText = data.name;
            setTimeout(removeClass,500);
         }
         function removeClass(){
            card.name.classList.remove("flip")
         }
         let netWorth = getSuffix(data.netWorth)
         card.netWorth.update(netWorth.val);
         card.netWorthSuffix.innerText = netWorth.suffix
         card.profile.setAttribute("href", "./user.html?account="+data.name);
      }
   }
   return {
      init: init,
      update: update
   }
})();

(function(){
   document.addEventListener('DOMContentLoaded', function(){
      getSeason.init();
      //leaderboard.init();
      
   });
})();
