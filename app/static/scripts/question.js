const revealBtn = document.getElementById('reveal-btn')
const answer = document.getElementById('answer')

revealBtn.addEventListener('click', () => showAnswer(revealBtn, answer))

function showAnswer (revealBtn, answer) {
    revealBtn.style.display = 'none'
    answer.style.display = 'inline'
}