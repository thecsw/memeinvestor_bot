export function formatToUnits(val) {
   let res = getSuffix(val)
   return res.val + res.suffix;
}

export function getSuffix(val){
   let number = parseInt(val);
   let abbrev = ['', 'k', 'M', 'B', 'T', 'q', 'Q', 's', 'S'];
   let unrangifiedOrder = Math.floor(Math.log10(Math.abs(number)) / 3);
   let order = Math.max(0, Math.min(unrangifiedOrder, abbrev.length - 1));
   let toDisplay = number / Math.pow(10, order * 3);
   return {
      val: unrangifiedOrder > 0 && unrangifiedOrder < abbrev.length ? toDisplay.toPrecision(3) : toDisplay.toFixed(0),
      suffix: abbrev[order]
   }  
}

export function commafy(val) {
   if (Number.isSafeInteger(val)) {
     //transform the number into a language-sensitive format
     return val.toLocaleString()
   } else {
      // switch to scientific notation
      return val.toExponential(4).replace(/e\+?/, ' &times;10^')
   }
}

export function iterateDays(days, callback) {
    let to = new Date();
    to.setHours(0);
    to.setMinutes(0);
    to.setSeconds(0);
    to.setMilliseconds(0);
    let dateFrom = new Date();
    dateFrom.setTime(to.getTime());
    dateFrom.setDate(dateFrom.getDate() - 1);

    for (let i = days + 15; i >= 0; i--) {
        callback(i, dateFrom, to);
        dateFrom.setDate(dateFrom.getDate() - 1);
        to.setDate(to.getDate() - 1);
    }
}

/* export formatToUnits;
export iterateDays; */
