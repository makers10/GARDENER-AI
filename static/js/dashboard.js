document.addEventListener('DOMContentLoaded', function() {
    let forecastChart = null;
    let currentData = null;
    let currentChartType = 'temp'; // 'temp' or 'rain'
    let testMode = true; // Default to true since user doesn't have an API key yet

    async function fetchDashboardData() {
        const container = document.getElementById('recommendations-container');
        try {
            // Get user location if possible (optional)
            const response = await fetch(`/api/forecast?test=${testMode}`);
            if (!response.ok) throw new Error('API Error');
            
            const data = await response.json();
            currentData = data;
            
            updateUI(data);
            initChart(data);
            
            // Hide error if test mode is on OR if we have real data
            if (testMode || data.current) {
                document.getElementById('api-error').classList.add('hidden');
            } else {
                document.getElementById('api-error').classList.remove('hidden');
            }
        } catch (error) {
            console.error('Fetch error:', error);
            if (!testMode) document.getElementById('api-error').classList.remove('hidden');
        }
    }

    function updateUI(data) {
        // 1. Current Stats Cards
        if (data.current) {
            document.querySelector('#card-temp .value').textContent = `${Math.round(data.current.temp)}°C`;
            document.querySelector('#card-humidity .value').textContent = `${data.current.humidity}%`;
            document.querySelector('#card-vpd .value').textContent = `${data.current.vpd} kPa`;
            document.querySelector('#card-rain .value').textContent = `${Math.round(data.forecast.rain_prob[0] * 100)}%`;
            
            document.getElementById('location-text').textContent = 'Micro-Locale: GARDEN_01';
            
            // Sub-values
            document.getElementById('avg-temp').textContent = Math.round(data.forecast.temp.reduce((a, b) => a + b) / 24);
            document.getElementById('humidity-status').textContent = data.current.humidity > 70 ? 'High' : (data.current.humidity > 40 ? 'Optimal' : 'Dry');
            document.getElementById('vpd-status').textContent = data.current.vpd > 1.5 ? 'High' : 'Optimal';
            document.getElementById('rain-window').textContent = Math.max(...data.forecast.rain_prob) > 0.4 ? 'Rainy' : 'Clear';
        }

        // 1.1 Local Sensor Overlay (If available)
        if (data.local_sensor && data.local_sensor.temp !== null) {
            const statusBadge = document.querySelector('.status-indicator');
            statusBadge.innerHTML = `<div class="pulse" style="background:#38bdf8"></div><span>📡 Local Sensor Active (${data.local_sensor.soil_moisture}% Soil)</span>`;
            statusBadge.style.background = 'rgba(56, 189, 248, 0.1)';
            statusBadge.style.color = '#38bdf8';
            statusBadge.style.border = '1px solid rgba(56, 189, 248, 0.2)';
            
            // Optionally update card values with local data for higher accuracy
            document.querySelector('#card-temp .value').innerHTML = `${Math.round(data.local_sensor.temp)}°C <small style="font-size:12px;opacity:0.6">(Local)</small>`;
            document.querySelector('#card-humidity .value').innerHTML = `${Math.round(data.local_sensor.humidity)}% <small style="font-size:12px;opacity:0.6">(Local)</small>`;
        }

        // 2. Recommendations
        const recsContainer = document.getElementById('recommendations-container');
        recsContainer.innerHTML = '';
        data.recommendations.forEach(rec => {
            const item = document.createElement('div');
            item.className = 'rec-item';
            if (rec.type === 'watering') item.style.borderLeftColor = '#4ade80';
            if (rec.type === 'fertilizing') item.style.borderLeftColor = '#38bdf8';
            
            item.innerHTML = `
                <div class="rec-item-title">
                    <span>${rec.status}</span>
                    <small style="color:${rec.impact === 'Critical' ? '#ef4444' : 'inherit'}">${rec.impact} Priority</small>
                </div>
                <p class="rec-item-msg">${rec.msg}</p>
            `;
            recsContainer.appendChild(item);
        });
    }

    function initChart(data) {
        const ctx = document.getElementById('forecastChart').getContext('2d');
        
        if (forecastChart) {
            forecastChart.destroy();
        }

        const chartConfig = {
            type: 'line',
            data: {
                labels: data.forecast.times,
                datasets: []
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                elements: {
                    point: { radius: 0, hoverRadius: 5 },
                    line: { tension: 0.4 }
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { color: '#94a3b8', font: { family: 'Outfit' } }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        titleColor: '#f8fafc',
                        bodyColor: '#cbd5e1',
                        borderColor: 'rgba(255,255,255,0.1)',
                        borderWidth: 1,
                        padding: 12,
                        cornerRadius: 10
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#64748b' },
                        grid: { display: false }
                    },
                    y: {
                        ticks: { color: '#64748b' },
                        grid: { color: 'rgba(255,255,255,0.05)' }
                    }
                }
            }
        };

        if (currentChartType === 'temp') {
            chartConfig.data.datasets = [
                {
                    label: 'Temperature (°C)',
                    data: data.forecast.temp,
                    borderColor: '#4ade80',
                    backgroundColor: 'rgba(74, 222, 128, 0.1)',
                    fill: true,
                    yAxisID: 'y'
                },
                {
                    label: 'Humidity (%)',
                    data: data.forecast.humidity,
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.1)',
                    fill: false,
                    yAxisID: 'y1'
                }
            ];
            chartConfig.options.scales.y1 = {
                position: 'right',
                min: 0,
                max: 100,
                grid: { display: false },
                ticks: { color: '#38bdf8' }
            };
        } else if (currentChartType === 'rain') {
            chartConfig.data.datasets = [
                {
                    label: 'Rain Probability (%)',
                    data: data.forecast.rain_prob.map(p => p * 100),
                    borderColor: '#fb923c',
                    backgroundColor: 'rgba(251, 146, 60, 0.2)',
                    fill: true,
                    type: 'bar'
                }
            ];
            chartConfig.options.scales.y.max = 100;
        } else if (currentChartType === 'daily') {
            const days = data.daily_trend.map(d => new Date(d.dt * 1000).toLocaleDateString(undefined, {weekday: 'short'}));
            chartConfig.data.labels = days;
            chartConfig.data.datasets = [
                {
                    label: '7-Day Avg Temp (°C)',
                    data: data.daily_trend.map(d => d.temp.day),
                    borderColor: '#4ade80',
                    backgroundColor: 'rgba(74, 222, 128, 0.4)',
                    type: 'bar'
                }
            ];
            chartConfig.options.scales.y.min = 0;
            chartConfig.options.scales.y.max = undefined;
        }

        forecastChart = new Chart(ctx, chartConfig);
    }

    // New: Plant Advisor Integration
    document.getElementById('get-advice-btn').addEventListener('click', async () => {
        const plant = document.getElementById('plant-select').value;
        const country = document.getElementById('country-input').value || 'US';
        const content = document.getElementById('plant-advice-content');
        
        content.classList.remove('hidden');
        content.innerHTML = '<div class="loading-spinner">Consulting Expert Database...</div>';
        
        try {
            const r = await fetch(`/api/plant-advice?plant=${plant}&country=${country}`);
            const advice = await r.json();
            
            content.innerHTML = `
                <div class="advice-card">
                    <h4>${advice.season_context}</h4>
                    <p><strong>Conditions:</strong> ${advice.ideal_params}</p>
                    <div class="advice-tips">
                        ${advice.tips.map(t => `<div class="tip-tag">${t}</div>`).join('')}
                    </div>
                    <p class="warning">⚠️ ${advice.warnings[0] || 'No immediate climate threats detected.'}</p>
                </div>
            `;
        } catch (e) {
            content.innerHTML = '<p>Expert temporarily unavailable.</p>';
        }
    });

    // Toggle logic
    document.getElementById('test-mode-btn').addEventListener('click', function() {
        testMode = !testMode;
        this.innerHTML = testMode ? '🚀 Disable Test Mode' : '🧪 Enable Test Mode';
        this.classList.toggle('active', testMode);
        fetchDashboardData();
    });

    document.querySelectorAll('.btn-toggle').forEach(btn => {
        // Skip the test mode button as it has its own listener
        if (btn.id === 'test-mode-btn') return;
        
        btn.addEventListener('click', function() {
            document.querySelectorAll('.btn-toggle').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentChartType = this.dataset.type;
            if (currentData) initChart(currentData);
        });
    });

    // Run
    fetchDashboardData();
    // Refresh every 30 mins
    setInterval(fetchDashboardData, 30 * 60 * 1000);
});
