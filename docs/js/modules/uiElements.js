

document.addEventListener('DOMContentLoaded', function(){
      //init all materialize elements
      M.AutoInit();      
      //show modal box
      modal("announcements-modal");
});
//popup code. after the first view, the current popup viewed is stored in localStorage,
//to avoid showing it on every page reload. increment const popup and refresh cache to show
//the popup message again
function modal(id){
   const POPUP = 2
   const SHOWPOPUP = true
   /*
   some icons that can be placed inside the popup title
   <i class="material-icons medium left orange-text">info</i>
   <i class="material-icons medium left orange-text">warning</i>
   <i class="material-icons medium left amber-text">new_releases</i>
   */
   const message = `
   <div class="modal-content" id="message-popup" >
      <h4><i class="material-icons medium left orange-text">info</i> INFO</h4>
      <p>Write your message here</p>
   </div>
   <div class="modal-footer">
      <a href="#!" class="modal-close waves-effect waves-light btn grey darken-3">close</a>
   </div>
   `
   //uncomment this while debugging the popup to show it on every page reload
   localStorage.removeItem('viewed_info')

   let modalEl = document.getElementById(id);
   if(SHOWPOPUP && localStorage.getItem('viewed_info') != POPUP){
      modalEl.innerHTML = message
      M.Modal.init(modalEl);
      setTimeout(
         ()=> M.Modal.getInstance(modalEl).open(),
         2000 );
      localStorage.setItem('viewed_info',POPUP)          
   }
}

export function connectionErrorToast(error, defaultErrorText = 'we couldn\'t get the latest data.'){
   let toastHTML = '';
   //simple connection error
   if(error.status === 0 || error.statusText === ""){
      toastHTML = '<p>We couldn\'t get the latest data. Please check your connection</p>';
   }//more serious problem, that is worth reporting
   else{
      toastHTML = `<p>${defaultErrorText} Error ${error.status}</p>`;   
   }
   M.toast({html: toastHTML,displayLength:2000, classes:"dark-toast"}); 
}
