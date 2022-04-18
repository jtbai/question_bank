const revealBtn = document.getElementById('reveal-btn')
const nextBtn = document.getElementById('next-btn')
const answer = document.getElementById('answer')
const nextContainer = document.getElementById('next')

revealBtn.addEventListener('click', () => showAnswer(revealBtn, answer))
nextBtn.addEventListener('click', () => { window.location.reload() })

function showAnswer (revealBtn, answer) {
    revealBtn.style.display = 'none'
    answer.style.display = 'inline'
    nextContainer.style.display = 'block'
}

