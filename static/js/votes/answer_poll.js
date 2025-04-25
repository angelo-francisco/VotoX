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
    const data = JSON.parse(event.data)

    if (data.type === "user_count") {
        document.getElementById("js-voting-user-count").textContent = data.count
    }

    if (data.type === "voting") {
        data.optionsData.forEach(optionData => {
            const optionId = optionData[0]
            const percentage = `${optionData[1]}%`

            const optionPercentage = document.querySelector(`#percentage-${optionId}`)
            const progressBar = document.querySelector(`#progress-${optionId}`)

            if (optionPercentage) {
                optionPercentage.innerText = percentage
            }

            if (progressBar) {
                progressBar.style.width = percentage
            }
        })

        document.querySelector('#total-votes').innerText = data.total_votes
    }
}

ws.onclose = (event) => {
    console.log("Connection Closed")
}

ws.onerror = (event) => {
    console.warn("Error on Websockets: " + event.code, event.reason)
}

const submitButton = document.querySelector('.submit-vote')

if (submitButton) {
    submitButton.addEventListener('click', () => {
        const optionHTML = document.querySelector('.poll-option.selected')

        if (!optionHTML) {
            return
        }

        const optionId = optionHTML.dataset.optionId

        submitButton.remove()

        ws.send(JSON.stringify({
            action: 'voting',
            optionId: optionId,
        }))
    })
}