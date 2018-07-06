import {connectionErrorToast} from './modules/uiElements.js';
import * as jsonApi from './modules/jsonApi.js';
import {formatToUnits} from './modules/dataUtils.js';

let leaderboard = (function(){
   let ids = {
      buttons: {
         beta: 'beta-bt',
         current: 'current-bt'
      }
   }
   function init(){
      //add buttons click listener
      let button = document.getElementById(ids.buttons.beta);
      button.addEventListener('click', e=> loadBeta() );
      button = document.getElementById(ids.buttons.current);
      button.addEventListener('click', e=> loadCurrent() );
      // check if url contains ?s=
      let url = new URL(window.location.href);
      let season = url.searchParams.get("s");
      if (season === 'beta'{
         loadBeta();
      }
      else{
         loadCurrent();
      }

   }
})();

(function(){
   document.addEventListener('DOMContentLoaded', function(){
      
   });
})();