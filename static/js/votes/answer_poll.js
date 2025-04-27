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

function timeAgo(timestamp) {
    const now = new Date();
    const then = new Date(timestamp);
    const secondsAgo = Math.floor((now - then) / 1000);

    const intervals = {
        year: 31536000,
        month: 2592000,
        day: 86400,
        hour: 3600,
        minute: 60,
        second: 1,
    };

    for (let [nome, segundos] of Object.entries(intervals)) {
        const quantidade = Math.floor(secondsAgo / segundos);
        if (quantidade > 0) {
            return `${quantidade} ${nome}${quantidade > 1 ? 's' : ''} ago`;
        }
    }

    return 'just now';
}

function updateAllTimes() {
    document.querySelectorAll('.comment-time')
        .forEach(element => {
            element.textContent = timeAgo(element.dataset.time);
        });
}

updateAllTimes();
setInterval(updateAllTimes, 30000);

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

        document.querySelector("#total_votes_number").innerText = data.total_votes
    }

    if (data.type === "questioning") {
        let message = ''
        const usernames = data.usernames
        const total = usernames.length

        message = `${usernames.join(', ')} ${total === 1 ? 'is' : 'are'} typing...`

        if (total > 3) {
            message = `${usernames.slice(0, 3).join(', ')}, and +${total - 3} are typing…`;
        }

        const spanHTML = document.getElementById('question_information')

        spanHTML.classList.add('typing');
        spanHTML.classList.remove('hide');

        spanHTML.textContent = message
    }

    if (data.type === 'stop_questioning') {
        const spanHTML = document.getElementById('question_information')
        spanHTML.textContent = ''

        spanHTML.classList.add('hide');
        spanHTML.classList.remove('typing');
    }

    if (data.type === "questioned") {
        const noQuests = document.querySelector('.no-quests')

        if (noQuests) {
            noQuests.remove()
        }

        const commentEl = document.createElement('div');
        commentEl.classList.add('comment');

        commentEl.innerHTML = `
            <div class="comment-header">
                <span class="user-name"></span>
                <span class="comment-time"></span>
            </div>
            <p class="comment-text"></p>
        `

        commentEl.querySelector('.user-name').textContent = data.author

        const timeSpan = commentEl.querySelector('.comment-time');
        timeSpan.textContent = timeAgo(data.created_at);

        commentEl.querySelector('.comment-text').textContent = data.body

        const commentList = document.querySelector('.comments-list')
        commentList.prepend(commentEl)
    }

    if (data.type === 'countdown_update') {
        const countdownElement = document.getElementById('countdown');
        countdownElement.innerHTML = data.remaining_time;

        if (data.remaining_time.includes('m') &&
            !data.remaining_time.includes('h') &&
            !data.remaining_time.includes('d')) {
            const minutes = parseInt(data.remaining_time);
            if (minutes < 5) {
                countdownElement.classList.add('countdown-urgent');
            }
        }

        if (data.remaining_time === "Poll has ended") {
            document.querySelector('.submit-vote').disabled = true;
            document.querySelector('.submit-vote').textContent = 'Poll Closed';

            const endedMessage = document.createElement('div');
            endedMessage.className = 'poll-ended-message';
            endedMessage.textContent = 'This poll has ended. Thank you for participating!';
            document.querySelector('.poll-meta').appendChild(endedMessage);
        }
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

const commentInput = document.querySelector('.comment-input')
let typingTimeOut = null
let isTyping = false

commentInput.addEventListener('input', () => {
    if (!isTyping) {
        ws.send(JSON.stringify({
            action: 'questioning',
            username: username
        }))
        isTyping = true
    }

    clearTimeout(typingTimeOut)

    typingTimeOut = setTimeout(() => {
        ws.send(JSON.stringify({
            action: 'stop_questioning',
            username: username
        }));
        isTyping = false
    }, 3000);
})

const submitComment = document.querySelector('.submit-comment')

if (submitComment) {
    submitComment.addEventListener('click', () => {
        const text = commentInput.value.trim()

        if (!text) {
            return
        }

        ws.send(JSON.stringify({
            action: 'questioned',
            body: text,
            userId: userId

        }))
        commentInput.value = ''
    })
}

document.addEventListener('DOMContentLoaded', function () {
    setTimeout(() => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                'action': 'request_countdown'
            }));
        }
    }, 1000);
})