import {connectionErrorToast} from './modules/uiElements.js';
import * as jsonApi from './modules/jsonApi.js';
import {formatToUnits, getSuffix} from './modules/dataUtils.js';

let leaderboard = (function(){
   let ids = {
      buttons: {
         beta: 'beta-bt',
         current: 'current-bt'
      },
      cards: {
         prefix: ['top','left','right'],
         name: 'name',
         netWorth: 'net-worth',
         netWorthSuffix: 'net-worth-suffix',
         profile: 'profile'
      }
   }
   let cardElements = {};
   let currentBlob = undefined;
   //["id","name","balance","completed","broke"]
   let betaBlob = [["3418","genericusername123","2000000000000000000","97","0"],["2992","ex_ex_parrot","500833736958591552","214","0"],["6646","ometrist","987188306261","54","0"],["8479","squid718","588137816312","119","0"],["5586","magicm8ball","328849356207","105","0"],["9690","twinproduction","205140420337","80","0"],["11238","q_fd","128926009852","99","0"],["4008","hyt_larry","35865715671","166","0"],["1367","bstefan236","32005393827","30","0"],["6699","organic_crystal_meth","28406704437","80","0"],["9655","tsansome","18501151353","55","0"],["6989","pjmarbaugh","10764250772","121","0"],["12063","nopedope33","10580599517","28","0"],["7895","scout_b","10561469593","63","0"],["3354","gameguy32","6371886294","69","0"],["2072","daddysdaddy33","5867864050","112","0"],["12293","AlphaShippai","4467601732","43","0"],["9945","vortuka","4223768236","48","0"],["11472","KungDododo","3795932264","36","0"],["11041","HighRollerNoGoaler","3310015621","20","0"],["318","agentsmithjr","2805468269","225","0"],["1089","billthesmallkitten","2664474907","19","0"],["1410","busy-at-work","2195687609","35","0"],["8092","shrekissexy","2090589352","49","0"],["1425","buyinggirlfriend","1894628104","71","0"],["1543","carbonshock","1516388706","92","0"],["3393","gawndy","1360502930","80","0"],["3152","flankingzen","1334914777","71","0"],["5812","meatballboy","1255613405","255","0"],["6029","mlmlmlmlmlmlmlml","1237706387","93","0"],["2602","dreamlifehunting","1227397594","77","0"],["3887","hivaladeeen","1218727414","78","0"],["111","2thousandand1","1173137948","22","0"],["5030","kittencaretaker","1158133203","139","0"],["1607","cgrabda","1150564859","33","0"],["4507","jaredroe","1095443218","18","0"],["10574","_buff_drinklots_","1000553816","32","0"]];
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
      init: init
   }
})();

(function(){
   document.addEventListener('DOMContentLoaded', function(){
      leaderboard.init();
   });
})();
