
const radioOptions = document.querySelectorAll('.radio-option');
const submitBtn = document.querySelector('.submit-btn');
const categoriasGanho = document.getElementById('categoriasGanho');
const categoriasGasto = document.getElementById('categoriasGasto');

function updateFormStyle(transactionType) {
// Remove previous classes
submitBtn.classList.remove('income', 'expense');

// Update submit button style and text
if (transactionType === 'ganho') {
    submitBtn.classList.add('income');
    categoriasGanho.style.display = 'block';
    categoriasGasto.style.display = 'none';
    // Adiciona/remove o atributo name
    categoriasGanho.setAttribute('name', 'categoria');
    categoriasGasto.removeAttribute('name');
    submitBtn.innerHTML = '<i class="fi fi-rr-plus"></i><span>Adicionar Ganho</span>';
} else {
    submitBtn.classList.add('expense');
    categoriasGanho.style.display = 'none';
    categoriasGasto.style.display = 'block';
    // Adiciona/remove o atributo name
    categoriasGasto.setAttribute('name', 'categoria');
    categoriasGanho.removeAttribute('name');
    submitBtn.innerHTML = '<i class="fi fi-rr-minus"></i><span>Adicionar Gasto</span>';
}
}

// Adiciona selected apenas se clicado
radioOptions.forEach(option => {
option.addEventListener('click', () => {
    radioOptions.forEach(opt => opt.classList.remove('selected'));
    option.classList.add('selected');
    const transactionType = option.querySelector('input[type="radio"]').value;
    updateFormStyle(transactionType);
});
});


// Set today's date as default
document.addEventListener('DOMContentLoaded', () => {
const today = new Date().toISOString().split('T')[0];
document.getElementById('data').value = today;

// Show gastos categories by default
categoriasGasto.style.display = 'block';
categoriasGanho.style.display = 'none';
submitBtn.classList.add('expense');

// Garante que apenas o select visível tenha o atributo name
categoriasGasto.setAttribute('name', 'categoria');
categoriasGanho.removeAttribute('name');
});