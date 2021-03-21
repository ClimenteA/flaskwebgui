// Custom js


document.addEventListener('DOMContentLoaded', function() {
  
    const port = 5001
    const interval_request = 1 * 1000 //sec
    const ws = new WebSocket(`ws://localhost:${port}`)

    function keep_alive_server(){
        let timestamp = parseInt(new Date().getTime() / 1000)
        ws.send(JSON.stringify({timestamp}))
        document.getElementById("ping").innerHTML = timestamp
    }

    setInterval(keep_alive_server, interval_request)()

})

