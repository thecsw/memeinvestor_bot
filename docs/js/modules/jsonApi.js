
let options = {
   method: "GET",
   //url: "/api",
   url: "https://memes.market/api",
   //url: "http://localhost/memeinvestor_bot/docs/testApiData.json",
}
function makeRequest (param = '', options) {
  return new Promise(function (resolve, reject) {
    var xhr = new XMLHttpRequest();
    let url = options.url+param;
    xhr.open(options.method, url);
    xhr.onload = function () {
      if (this.status >= 200 && this.status < 300) {
        resolve(JSON.parse(xhr.response));
      } else {
        reject({
          status: this.status,
          statusText: xhr.statusText
        });
      }
    };
    xhr.onerror = function () {
      reject({
        status: this.status,
        statusText: xhr.statusText
      });
    };
    xhr.send();
  });
}

export function getAll(){
   return makeRequest("/summary?per_page=5", options);
}

export function get(param, newOptions = options){
   return makeRequest(param, newOptions);
}

