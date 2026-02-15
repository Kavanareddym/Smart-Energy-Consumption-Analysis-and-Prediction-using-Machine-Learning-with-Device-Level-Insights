let chartInstances = {};

async function fetchStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        document.getElementById('total-consumption').textContent = data.total_consumption + ' kWh';
        document.getElementById('avg-usage').textContent = data.avg_hourly + ' kWh';
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

async function fetchPrediction() {
    try {
        const response = await fetch('/api/predict');
        const data = await response.json();
        if (data.status === 'success') {
            document.getElementById('prediction-value').textContent = data.prediction + ' ' + data.unit;
        }
    } catch (error) {
        console.error('Error fetching prediction:', error);
    }
}

async function fetchSuggestions() {
    try {
        const response = await fetch('/api/suggestions');
        const data = await response.json();
        const container = document.getElementById('suggestions-container');
        container.innerHTML = '';

        data.suggestions.forEach(tip => {
            const div = document.createElement('div');
            div.className = 'suggestion-item';
            div.textContent = tip;
            container.appendChild(div);
        });
    } catch (error) {
        console.error('Error fetching suggestions:', error);
    }
}

async function updateCharts() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();

        // 1. Hourly Chart (Line)
        renderChart('hourlyChart', 'line', data.hourly.labels, data.hourly.values, 'Hourly Consumption (kWh)', '#00d7ff');

        // 2. Device Chart (Doughnut)
        renderChart('deviceChart', 'doughnut', data.devices.labels, data.devices.values, 'Energy Mix', [
            '#00d7ff', '#00af00', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#10b981', '#f97316'
        ]);

        // 3. Daily Chart (Bar)
        renderChart('dailyChart', 'bar', data.daily.labels, data.daily.values, 'Daily Consumption (kWh)', '#00af00');

    } catch (error) {
        console.error('Error updating charts:', error);
    }
}

function renderChart(canvasId, type, labels, values, label, color) {
    if (chartInstances[canvasId]) {
        chartInstances[canvasId].destroy();
    }

    const ctx = document.getElementById(canvasId).getContext('2d');

    const config = {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: values,
                backgroundColor: Array.isArray(color) ? color : color + '33',
                borderColor: Array.isArray(color) ? '#ffffff33' : color,
                borderWidth: 2,
                fill: type === 'line',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: type === 'doughnut',
                    labels: { color: '#94a3b8', font: { family: 'Inter' } }
                },
                tooltip: {
                    backgroundColor: '#1e293b',
                    titleColor: '#f8fafc',
                    bodyColor: '#f8fafc',
                    borderColor: '#00d7ff',
                    borderWidth: 1
                }
            },
            scales: type !== 'doughnut' ? {
                y: {
                    beginAtZero: true,
                    grid: { color: '#ffffff11' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8' }
                }
            } : {}
        }
    };

    chartInstances[canvasId] = new Chart(ctx, config);
}

function refreshDashboard() {
    fetchStats();
    fetchPrediction();
    fetchSuggestions();
    updateCharts();
}

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    refreshDashboard();
});
