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

        const sentimentData = this.data.sentimentTrends || [];
        const data = sentimentData.map(item => ({
            x: item.date,
            y: item.sentiment
        }));

        this.charts.sentimentTrend = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: 'Sentiment Score',
                    data: data,
                    borderColor: '#17a2b8',
                    backgroundColor: 'rgba(23, 162, 184, 0.1)',
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
                        },
                        ticks: {
                            callback: function(value) {
                                if (value > 0.1) return 'Positive';
                                if (value < -0.1) return 'Negative';
                                return 'Neutral';
                            }
                        }
                    }
                }
            }
        });
    }

    updateSentimentTrendChart() {
        if (!this.charts.sentimentTrend) return;

        const sentimentData = this.data.sentimentTrends || [];
        const data = sentimentData.map(item => ({
            x: item.date,
            y: item.sentiment
        }));

        this.charts.sentimentTrend.data.datasets[0].data = data;
        this.charts.sentimentTrend.update();
    }

    createMoodHeatmap() {
        const element = document.getElementById('moodHeatmap');
        if (!element) return;

        const moodData = this.data.dailyMood || [];
        
        if (moodData.length === 0) {
            element.innerHTML = '<div class="text-center text-muted py-5"><p>No mood data available for the selected time period.</p></div>';
            return;
        }

        // Prepare data for Plotly heatmap
        const dates = moodData.map(item => item.date);
        const intensities = moodData.map(item => item.intensity);
        const counts = moodData.map(item => item.count);

        // Create calendar grid data
        const startDate = new Date(Math.min(...dates.map(d => new Date(d))));
        const endDate = new Date(Math.max(...dates.map(d => new Date(d))));
        
        // Group by weeks for heatmap
        const heatmapData = this.prepareHeatmapData(moodData);

        const trace = {
            z: heatmapData.z,
            x: heatmapData.x,
            y: heatmapData.y,
            type: 'heatmap',
            colorscale: [
                [0, '#f8f9fa'],
                [0.2, '#e9ecef'],
                [0.4, '#dee2e6'],
                [0.6, '#adb5bd'],
                [0.8, '#6c757d'],
                [1, '#495057']
            ],
            showscale: true,
            colorbar: {
                title: 'Mood Intensity',
                titleside: 'right'
            },
            hovertemplate: 'Date: %{x}<br>Intensity: %{z:.2f}<extra></extra>'
        };

        const layout = {
            title: {
                text: 'Daily Mood Intensity',
                font: { size: 16 }
            },
            xaxis: {
                title: 'Date',
                type: 'category'
            },
            yaxis: {
                title: 'Day of Week',
                type: 'category'
            },
            margin: { t: 50, r: 50, b: 50, l: 80 },
            height: 300,
            plot_bgcolor: 'transparent',
            paper_bgcolor: 'transparent',
            font: {
                color: '#6c757d'
            }
        };

        const config = {
            responsive: true,
            displayModeBar: false
        };

        Plotly.newPlot(element, [trace], layout, config);
        this.charts.moodHeatmap = element;
    }

    prepareHeatmapData(moodData) {
        const data = {};
        const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
        
        // Group data by date
        moodData.forEach(item => {
            const date = new Date(item.date);
            const dayOfWeek = dayNames[date.getDay()];
            const dateStr = item.date;
            
            if (!data[dateStr]) {
                data[dateStr] = { dayOfWeek, intensity: item.intensity };
            }
        });

        // Convert to arrays for Plotly
        const dates = Object.keys(data).sort();
        const z = []; // intensity values
        const x = []; // dates
        const y = []; // days of week

        dates.forEach(date => {
            x.push(date);
            y.push(data[date].dayOfWeek);
            z.push(data[date].intensity);
        });

        return { x, y, z: [z] }; // z needs to be 2D for heatmap
    }

    updateMoodHeatmap() {
        const element = document.getElementById('moodHeatmap');
        if (!element) return;

        // Clear and recreate heatmap
        Plotly.purge(element);
        this.createMoodHeatmap();
    }

    showError(message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show position-fixed top-50 start-50 translate-middle';
        alertDiv.style.zIndex = '9999';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alertDiv);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 5000);
    }
}

// Export functions
function exportCharts() {
    const charts = document.querySelectorAll('canvas');
    const zip = new JSZip();
    
    charts.forEach((canvas, index) => {
        const chartName = canvas.id || `chart_${index}`;
        const dataURL = canvas.toDataURL('image/png');
        const base64Data = dataURL.replace(/^data:image\/png;base64,/, '');
        zip.file(`${chartName}.png`, base64Data, { base64: true });
    });

    // Export heatmap if exists
    const heatmapElement = document.getElementById('moodHeatmap');
    if (heatmapElement) {
        Plotly.toImage(heatmapElement, { format: 'png' }).then(function(dataURL) {
            const base64Data = dataURL.replace(/^data:image\/png;base64,/, '');
            zip.file('mood_heatmap.png', base64Data, { base64: true });
            
            // Generate and download zip
            zip.generateAsync({ type: 'blob' }).then(function(content) {
                const link = document.createElement('a');
                link.href = URL.createObjectURL(content);
                link.download = `emotion_analytics_charts_${new Date().toISOString().split('T')[0]}.zip`;
                link.click();
            });
        });
    } else {
        // Generate and download zip without heatmap
        zip.generateAsync({ type: 'blob' }).then(function(content) {
            const link = document.createElement('a');
            link.href = URL.createObjectURL(content);
            link.download = `emotion_analytics_charts_${new Date().toISOString().split('T')[0]}.zip`;
            link.click();
        });
    }
}

async function exportData() {
    try {
        const analytics = window.emotionAnalytics;
        if (!analytics || !analytics.data) {
            throw new Error('No analytics data available');
        }

        const exportData = {
            export_date: new Date().toISOString(),
            time_range_days: analytics.currentTimeRange,
            summary: analytics.data.summary,
            emotion_distribution: analytics.data.emotionDistribution,
            emotion_frequency: analytics.data.emotionFrequency,
            emotional_balance: analytics.data.emotionalBalance,
            daily_mood_data: analytics.data.dailyMood,
            sentiment_trends: analytics.data.sentimentTrends,
            emotion_trends: analytics.data.emotionTrends
        };

        const jsonString = JSON.stringify(exportData, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `emotion_analytics_data_${new Date().toISOString().split('T')[0]}.json`;
        link.click();

    } catch (error) {
        console.error('Error exporting data:', error);
        alert('Failed to export data. Please try again.');
    }
}

// Initialize analytics when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if we're on the analytics page
    if (document.getElementById('emotionPieChart')) {
        window.emotionAnalytics = new EmotionAnalytics();
    }
});

// Add JSZip library for chart export (if not already included)
if (typeof JSZip === 'undefined') {
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js';
    document.head.appendChild(script);
}
