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
   constructor(callback,updateInterval) {
      this.callback = callback;
      this.updateInterval = updateInterval;
      this.interval = false;
      document.addEventListener(this.visibilityChange, this.handleVisibilityChange.bind(this), false);
      this.start();
   }
   handleVisibilityChange(){     
      if(document[this.hidden]){
         this.pause()
      }else{
         this.start()
      }
   }
   execute(){
      //beep(500,880)//debugging on mobile
      this.callback();
   }
   pause(){
      if(this.interval){
         clearInterval(this.interval);
         this.interval = false;         
      }
   }
   start(){
      if(!this.interval){
         this.interval = setInterval(this.execute.bind(this),this.updateInterval);
         this.execute();
      }
   }
}

(function(){
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