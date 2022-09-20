document.addEventListener('DOMContentLoaded', function () {

  function keep_alive_server() {
    fetch(document.location + "flaskwebgui-dumb-request-for-middleware-keeping-the-server-online", {
      method: 'GET',
      cache: 'no-cache'
    })
      .then(res => { })
      .catch(err => { })
  }

  try {
    setInterval(keep_alive_server, 3 * 1000)()
  } catch (error) {
    // doesn't matter handled by middleware
  }

})

