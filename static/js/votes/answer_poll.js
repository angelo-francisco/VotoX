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

ws.onopen = (event) => {
    console.log("Connected")
}

ws.onmessage = (event) => {
    const data = JSON.parse(event.data)

    if ((data.type) == 'user_update') {
        const userCountSpan = document.querySelector('#js-voting-user-count')
        const userCount = parseInt(userCountSpan.textContent)

        userCountSpan.innerText = data.updated_voting_users_count

    }
}