
async function getRequest(url='') {
    const response = await fetch(url, {
      method: 'GET', 
      cache: 'no-cache'
    })
    return response.json()
}
  
document.addEventListener('DOMContentLoaded', function() {

let url = document.location
let route = "/flaskwebgui-keep-server-alive"
let interval_request = 3 * 1000 //sec

function keep_alive_server(){
    getRequest(url + route)
    .then(data => console.log(data))
}

setInterval(keep_alive_server, interval_request)()

})

