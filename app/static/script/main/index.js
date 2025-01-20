document.getElementById('toggleBalance').addEventListener('click', function () {
    const balanceValue = document.getElementById('balanceValue');
    const gastosValue = document.getElementById('gastosValue');
    const ganhosValue = document.getElementById('ganhosValue');
    const isHidden = balanceValue.style.visibility === 'hidden';

    balanceValue.style.visibility = isHidden ? 'visible' : 'hidden';
    gastosValue.style.visibility = isHidden ? 'visible' : 'hidden';
    ganhosValue.style.visibility = isHidden ? 'visible' : 'hidden';
});

document.addEventListener('DOMContentLoaded', function () {
    let currentChart = null;
    const ctx = document.getElementById('miniChart').getContext('2d');

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'right',
                labels: {
                    font: {
                        size: 11
                    },
                    padding: 10
                }
            }
        },
        cutout: '60%'
    };

    const expenseData = {
        labels: ['Alimentação', 'Transporte', 'Moradia', 'Saúde', 'Outros'],
        datasets: [{
            data: [
                gastosPorCategoria['Alimentação'] || 0,
                gastosPorCategoria['Transporte'] || 0,
                gastosPorCategoria['Moradia'] || 0,
                gastosPorCategoria['Saúde'] || 0,
                Object.values(gastosPorCategoria).reduce((a, b) => a + b, 0) -
                (gastosPorCategoria['Alimentação'] || 0) -
                (gastosPorCategoria['Transporte'] || 0) -
                (gastosPorCategoria['Moradia'] || 0) -
                (gastosPorCategoria['Saúde'] || 0)
            ],
            backgroundColor: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD']
        }]
    };

    const incomeData = {
        labels: ['Salário', 'Freelance', 'Investimentos', 'Outros'],
        datasets: [{
            data: [
                ganhosPorCategoria['Salário'] || 0,
                ganhosPorCategoria['Freelance'] || 0,
                ganhosPorCategoria['Investimentos'] || 0,
                Object.values(ganhosPorCategoria).reduce((a, b) => a + b, 0) -
                (ganhosPorCategoria['Salário'] || 0) -
                (ganhosPorCategoria['Freelance'] || 0) -
                (ganhosPorCategoria['Investimentos'] || 0)
            ],
            backgroundColor: ['#4CAF50', '#2196F3', '#3F51B5', '#607D8B']
        }]
    };

    function updateChart(type) {
        if (currentChart) {
            currentChart.destroy();
        }

        currentChart = new Chart(ctx, {
            type: 'doughnut',
            data: type === 'expenses' ? expenseData : incomeData,
            options: chartOptions
        });
    }

    document.querySelectorAll('.toggle-btn').forEach(button => {
        button.addEventListener('click', function () {
            document.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            updateChart(this.dataset.chart);
        });
    });

    updateChart('expenses');
});
