/*
//temporary beep function for testing the scheduler on mobile devices. will remove soon
//code from https://stackoverflow.com/a/29641185/916979
var audioCtx = new (window.AudioContext || window.webkitAudioContext || window.audioContext);
//All arguments are optional:
//duration of the tone in milliseconds. Default is 500
//frequency of the tone in hertz. default is 440
//volume of the tone. Default is 1, off is 0.
//type of tone. Possible values are sine, square, sawtooth, triangle, and custom. Default is sine.
//callback to use on end of tone
function beep(duration, frequency, volume, type, callback) {
    var oscillator = audioCtx.createOscillator();
    var gainNode = audioCtx.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    if (volume){gainNode.gain.value = volume;};
    if (frequency){oscillator.frequency.value = frequency;}
    if (type){oscillator.type = type;}
    if (callback){oscillator.onended = callback;}

    oscillator.start();
    setTimeout(function(){oscillator.stop()}, (duration ? duration : 500));
};*/

export class Scheduler {
   constructor(task,updateInterval,executeOnCreation = true,executeAfterPauseResume = true) {
      this.task = task;
      this.updateInterval = updateInterval;
      this.interval = false;
      this.executeAfterPauseResume = executeAfterPauseResume;
      this.canExecute = executeOnCreation;
      //this.visibilityChange and this.hidden are injected in the class proto by external code
      this.handler = this.handleVisibilityChange.bind(this);
      document.addEventListener(this.visibilityChange, this.handler, false);
      this.start();
   }
   handleVisibilityChange(){     
      if(document[this.hidden]){
         this.pause()
      }else{
         if(!this.executeAfterPauseResume) this.canExecute = false;
         this.start()
      }
   }
   execute(){
      //beep(500,880)//debugging on mobile
      this.task();
   }
   pause(){
      if(this.interval){
         clearInterval(this.interval);
         this.interval = false;         
      }
   }
   stop(){
      this.pause();
      document.removeEventListener(this.visibilityChange, this.handler, false);
      //will this successfully remove every reference to the object? or will it leak
      //memory in eternity? Who knows.
   }
   start(){
      if(!this.interval){
         this.interval = setInterval(this.execute.bind(this),this.updateInterval);
         if(this.canExecute){
            this.execute();
         }else{
            this.canExecute = true;
         }
      }
   }
}

(function(){
   //inject hidden and visibilityChange into the Scheduler prototype
   let hidden, visibilityChange;
   // Set the name of the hidden property and the change event for visibility
   if (typeof document.hidden !== "undefined") {
     hidden = "hidden";
     visibilityChange = "visibilitychange";
   } else if (typeof document.msHidden !== "undefined") {
     hidden = "msHidden";
     visibilityChange = "msvisibilitychange";
   } else if (typeof document.webkitHidden !== "undefined") {
     hidden = "webkitHidden";
     visibilityChange = "webkitvisibilitychange";
   }
   Scheduler.prototype.hidden = hidden;
   Scheduler.prototype.visibilityChange = visibilityChange;
})();