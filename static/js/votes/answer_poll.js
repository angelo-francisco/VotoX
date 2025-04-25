function openTab(tabName) {
    var tabcontent = document.getElementsByClassName('tab-pane')
    for (var i = 0; i < tabcontent.length; i++) {
        tabcontent[i].classList.remove('active')
    }

    var tablinks = document.getElementsByClassName('tab-btn')
    for (var i = 0; i < tablinks.length; i++) {
        tablinks[i].classList.remove('active')
    }

    document.getElementById(tabName).classList.add('active')

    event.currentTarget.classList.add('active')
}

function selectOption(element) {
    var options = document.getElementsByClassName('poll-option')
    for (var i = 0; i < options.length; i++) {
        options[i].classList.remove('selected')
    }

    element.classList.add('selected')
}

const ws = new WebSocket(`ws://${window.location.host}/vote/${pollCode}/`)

ws.onopen = event => {
    console.log("Connected!", event)
}

ws.onmessage = event => {
    console.log("Got a message")
    console.log(event)

    const data = JSON.parse(event.data)

    if (data.type === "user_status" && data.status === "online") {
        console.log(`Usuário ${data.user_id} está online`)
    }

    if (data.type === "user_count") {
        document.getElementById("js-voting-user-count").textContent = data.count
    }
}

ws.onclose = (event) => {
    console.log("Connection Closed")
}

ws.onerror = (event) => {
    console.warn("Error on Websockets: " + event.code, event.reason)
}