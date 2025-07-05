// Analytics Dashboard JavaScript
class EmotionAnalytics {
    constructor() {
        this.charts = {};
        this.emotionColors = {
            'joy': '#28a745',
            'sadness': '#6c757d', 
            'anger': '#dc3545',
            'fear': '#ffc107',
            'surprise': '#17a2b8',
            'love': '#e91e63',
            'neutral': '#6f42c1'
        };
        this.currentTimeRange = 30;
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadAnalytics();
        this.initializeCharts();
    }

    setupEventListeners() {
        // Time range selector
        const timeRangeSelect = document.getElementById('timeRange');
        if (timeRangeSelect) {
            timeRangeSelect.addEventListener('change', async (e) => {
                this.currentTimeRange = parseInt(e.target.value);
                this.showLoading();
                await this.loadAnalytics();
                this.updateAllCharts();
                this.hideLoading();
            });
        }

        // Window resize handler for responsive charts
        window.addEventListener('resize', () => {
            Object.values(this.charts).forEach(chart => {
                if (chart && typeof chart.resize === 'function') {
                    chart.resize();
                }
            });
        });
    }

    showLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.remove('d-none');
            overlay.classList.add('d-flex');
        }
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.add('d-none');
            overlay.classList.remove('d-flex');
        }
    }

    async loadAnalytics() {
        try {
            // Load all analytics data
            const [
                emotionDistribution,
                dailyMood,
                emotionTrends,
                emotionFrequency,
                emotionalBalance,
                sentimentTrends,
                summary
            ] = await Promise.all([
                this.fetchData('/api/analytics/emotion-distribution'),
                this.fetchData('/api/analytics/daily-mood'),
                this.fetchData('/api/analytics/emotion-trends'),
                this.fetchData('/api/analytics/emotion-frequency'),
                this.fetchData('/api/analytics/emotional-balance'),
                this.fetchData('/api/analytics/sentiment-trends'),
                this.fetchData('/api/analytics/summary')
            ]);

            // Store data
            this.data = {
                emotionDistribution,
                dailyMood,
                emotionTrends,
                emotionFrequency,
                emotionalBalance,
                sentimentTrends,
                summary
            };

            // Update summary cards
            this.updateSummaryCards(summary);

        } catch (error) {
            console.error('Error loading analytics:', error);
            this.showError('Failed to load analytics data. Please try again.');
        }
    }

    async fetchData(endpoint) {
        const url = `${endpoint}?days=${this.currentTimeRange}`;
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }

    updateSummaryCards(summary) {
        const elements = {
            'total-entries': summary.total_entries || 0,
            'dominant-emotion': (summary.most_common_emotion || 'N/A').charAt(0).toUpperCase() + (summary.most_common_emotion || 'N/A').slice(1),
            'avg-sentiment': parseFloat(summary.average_sentiment || 0).toFixed(2),
            'days-tracked': summary.days_tracked || 0
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    initializeCharts() {
        this.createEmotionPieChart();
        this.createEmotionBarChart();
        this.createEmotionTrendChart();
        this.createEmotionalBalanceChart();
        this.createSentimentTrendChart();
        this.createMoodHeatmap();
    }

    updateAllCharts() {
        this.updateEmotionPieChart();
        this.updateEmotionBarChart();
        this.updateEmotionTrendChart();
        this.updateEmotionalBalanceChart();
        this.updateSentimentTrendChart();
        this.updateMoodHeatmap();
    }

    createEmotionPieChart() {
        const ctx = document.getElementById('emotionPieChart');
        if (!ctx) return;

        const data = this.data.emotionDistribution || {};
        const labels = Object.keys(data);
        const values = Object.values(data);
        const colors = labels.map(emotion => this.emotionColors[emotion] || '#6c757d');

        this.charts.emotionPie = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels.map(l => l.charAt(0).toUpperCase() + l.slice(1)),
                datasets: [{
                    data: values,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.label}: ${context.parsed.toFixed(1)}%`;
                            }
                        }
                    }
                }
            }
        });
    }

    updateEmotionPieChart() {
        if (!this.charts.emotionPie) return;

        const data = this.data.emotionDistribution || {};
        const labels = Object.keys(data);
        const values = Object.values(data);
        const colors = labels.map(emotion => this.emotionColors[emotion] || '#6c757d');

        this.charts.emotionPie.data.labels = labels.map(l => l.charAt(0).toUpperCase() + l.slice(1));
        this.charts.emotionPie.data.datasets[0].data = values;
        this.charts.emotionPie.data.datasets[0].backgroundColor = colors;
        this.charts.emotionPie.update();
    }

    createEmotionBarChart() {
        const ctx = document.getElementById('emotionBarChart');
        if (!ctx) return;

        const data = this.data.emotionFrequency || {};
        const labels = Object.keys(data);
        const values = Object.values(data);
        const colors = labels.map(emotion => this.emotionColors[emotion] || '#6c757d');

        this.charts.emotionBar = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels.map(l => l.charAt(0).toUpperCase() + l.slice(1)),
                datasets: [{
                    label: 'Frequency',
                    data: values,
                    backgroundColor: colors,
                    borderColor: colors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }

    updateEmotionBarChart() {
        if (!this.charts.emotionBar) return;

        const data = this.data.emotionFrequency || {};
        const labels = Object.keys(data);
        const values = Object.values(data);
        const colors = labels.map(emotion => this.emotionColors[emotion] || '#6c757d');

        this.charts.emotionBar.data.labels = labels.map(l => l.charAt(0).toUpperCase() + l.slice(1));
        this.charts.emotionBar.data.datasets[0].data = values;
        this.charts.emotionBar.data.datasets[0].backgroundColor = colors;
        this.charts.emotionBar.data.datasets[0].borderColor = colors;
        this.charts.emotionBar.update();
    }

    createEmotionTrendChart() {
        const ctx = document.getElementById('emotionTrendChart');
        if (!ctx) return;

        const trendData = this.data.emotionTrends || {};
        const datasets = Object.entries(trendData).map(([emotion, data]) => ({
            label: emotion.charAt(0).toUpperCase() + emotion.slice(1),
            data: data,
            borderColor: this.emotionColors[emotion] || '#6c757d',
            backgroundColor: (this.emotionColors[emotion] || '#6c757d') + '20',
            tension: 0.4,
            fill: false
        }));

        this.charts.emotionTrend = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            parser: 'YYYY-MM-DD',
                            displayFormats: {
                                day: 'MMM DD'
                            }
                        },
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Frequency'
                        }
                    }
                }
            }
        });
    }

    updateEmotionTrendChart() {
        if (!this.charts.emotionTrend) return;

        const trendData = this.data.emotionTrends || {};
        const datasets = Object.entries(trendData).map(([emotion, data]) => ({
            label: emotion.charAt(0).toUpperCase() + emotion.slice(1),
            data: data,
            borderColor: this.emotionColors[emotion] || '#6c757d',
            backgroundColor: (this.emotionColors[emotion] || '#6c757d') + '20',
            tension: 0.4,
            fill: false
        }));

        this.charts.emotionTrend.data.datasets = datasets;
        this.charts.emotionTrend.update();
    }

    createEmotionalBalanceChart() {
        const ctx = document.getElementById('emotionalBalanceChart');
        if (!ctx) return;

        const balanceData = this.data.emotionalBalance || {};
        const labels = Object.keys(balanceData);
        const values = Object.values(balanceData);

        this.charts.emotionalBalance = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Emotional Balance',
                    data: values,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 1,
                        ticks: {
                            stepSize: 0.2
                        }
                    }
                }
            }
        });
    }

    updateEmotionalBalanceChart() {
        if (!this.charts.emotionalBalance) return;

        const balanceData = this.data.emotionalBalance || {};
        const labels = Object.keys(balanceData);
        const values = Object.values(balanceData);

        this.charts.emotionalBalance.data.labels = labels;
        this.charts.emotionalBalance.data.datasets[0].data = values;
        this.charts.emotionalBalance.update();
    }

    createSentimentTrendChart() {
        const ctx = document.getElementById('sentimentTrendChart');
        if (!ctx) return;

        const trendData = this.data.sentimentTrends || [];

        this.charts.sentimentTrend = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: 'Sentiment Score',
                    data: trendData,
                    borderColor: '#17a2b8',
                    backgroundColor: 'rgba(23, 162, 184, 0.2)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            parser: 'YYYY-MM-DD',
                            displayFormats: {
                                day: 'MMM DD'
                            }
                        },
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        min: -1,
                        max: 1,
                        title: {
                            display: true,
                            text: 'Sentiment Score'
                        }
                    }
                }
            }
        });
    }

    updateSentimentTrendChart() {
        if (!this.charts.sentimentTrend) return;

        const trendData = this.data.sentimentTrends || [];
        this.charts.sentimentTrend.data.datasets[0].data = trendData;
        this.charts.sentimentTrend.update();
    }

    createMoodHeatmap() {
        const heatmapData = this.data.dailyMood || [];
        
        if (!heatmapData.length) {
            document.getElementById('moodHeatmap').innerHTML = '<p class="text-muted text-center">No mood data available</p>';
            return;
        }

        // Prepare data for Plotly heatmap
        const dates = heatmapData.map(d => d.date);
        const values = heatmapData.map(d => d.value);
        
        // Create a calendar-style heatmap
        const startDate = new Date(Math.min(...dates.map(d => new Date(d))));
        const endDate = new Date(Math.max(...dates.map(d => new Date(d))));
        
        const data = [{
            x: dates,
            y: dates.map(() => 'Mood'),
            z: values,
            type: 'heatmap',
            colorscale: [
                [0, '#dc3545'],
                [0.5, '#ffc107'],
                [1, '#28a745']
            ],
            showscale: true,
            colorbar: {
                title: 'Mood Score',
                titleside: 'right'
            }
        }];

        const layout = {
            title: false,
            xaxis: {
                title: 'Date',
                type: 'date'
            },
            yaxis: {
                title: '',
                showticklabels: false
            },
            height: 300,
            margin: { l: 50, r: 50, t: 20, b: 50 }
        };

        Plotly.newPlot('moodHeatmap', data, layout, {responsive: true});
    }

    updateMoodHeatmap() {
        this.createMoodHeatmap();
    }

    showError(message) {
        const errorAlert = document.createElement('div');
        errorAlert.className = 'alert alert-danger alert-dismissible fade show';
        errorAlert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container-fluid');
        if (container) {
            container.insertBefore(errorAlert, container.firstChild);
        }
    }
}

// Export functions for chart export functionality
function exportCharts() {
    // Create a new window with all charts for printing/saving
    const printWindow = window.open('', '_blank');
    const chartsHTML = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>Emotion Analytics Export</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .chart-container { margin-bottom: 30px; page-break-inside: avoid; }
                h2 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
                @media print { .chart-container { page-break-inside: avoid; } }
            </style>
        </head>
        <body>
            <h1>Mental Wellness - Emotion Analytics Report</h1>
            <p>Generated on: ${new Date().toLocaleDateString()}</p>
        </body>
        </html>
    `;
    
    printWindow.document.write(chartsHTML);
    printWindow.document.close();
    
    // Copy canvas elements to the new window
    setTimeout(() => {
        const canvases = document.querySelectorAll('canvas');
        canvases.forEach((canvas, index) => {
            if (canvas.getContext) {
                const img = new Image();
                img.src = canvas.toDataURL();
                img.style.maxWidth = '100%';
                img.style.height = 'auto';
                
                const container = printWindow.document.createElement('div');
                container.className = 'chart-container';
                container.appendChild(img);
                printWindow.document.body.appendChild(container);
            }
        });
        
        printWindow.print();
    }, 1000);
}

function exportData() {
    // Export analytics data as JSON
    if (window.emotionAnalytics && window.emotionAnalytics.data) {
        const data = JSON.stringify(window.emotionAnalytics.data, null, 2);
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `emotion-analytics-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    } else {
        alert('No data available to export');
    }
}

// Initialize analytics when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.emotionAnalytics = new EmotionAnalytics();
});
