export function formatToUnits(val) {
   let res = getSuffix(val)
   return res.val + res.suffix;
}

export function getSuffix(val){
   let number = parseInt(val);
   let abbrev = ['', 'K', 'M', 'B', 'T', 'q', 'Q', 's', 'S'];
   let unrangifiedOrder = Math.floor(Math.log10(Math.abs(number)) / 3);
   let order = Math.max(0, Math.min(unrangifiedOrder, abbrev.length -1 ));
   let suffix = abbrev[order];
   let precision = suffix ? 1 : 0;
   return {
      val: (number / Math.pow(10, order * 3)).toFixed(precision),
      suffix: suffix
   }  
}

export function iterateDays(days, callback) {
    let to = new Date();
    to.setHours(23);
    to.setMinutes(59);
    to.setSeconds(59);
    to.setMilliseconds(999);
    let dateFrom = new Date();
    dateFrom.setTime(to.getTime());
    dateFrom.setDate(dateFrom.getDate() - 1);

    for (let i = days - 1; i >= 0; i--) {
        callback(i, dateFrom, to);
        dateFrom.setDate(dateFrom.getDate() - 1);
        to.setDate(to.getDate() - 1);
    }
}

/* export formatToUnits;
export iterateDays; */