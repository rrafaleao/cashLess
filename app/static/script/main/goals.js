function toggleModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.toggle('active');
}

function deleteGoal(goalId) {
        window.location.href = `/goals/delete/${goalId}`;
}

// Fecha o modal se clicar fora dele
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('active');
    }
}