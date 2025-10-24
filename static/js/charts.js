// Chart.js configuration and utilities for the parking management system

// Global chart configuration
Chart.defaults.color = '#fff';
Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
Chart.defaults.backgroundColor = 'rgba(255, 255, 255, 0.1)';

// Chart color palette
const chartColors = {
    primary: '#0d6efd',
    secondary: '#6c757d',
    success: '#198754',
    danger: '#dc3545',
    warning: '#ffc107',
    info: '#0dcaf0',
    light: '#f8f9fa',
    dark: '#212529'
};

// Load admin dashboard charts
function loadAdminCharts() {
    // Fetch parking statistics
    fetch('/api/parking-stats', {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json',
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data && data.overview && data.lots) {
                createOverallChart(data.overview);
                createLotsChart(data.lots);
            } else {
                console.error('Invalid data format received:', data);
                showChartError();
            }
        })
        .catch(error => {
            console.error('Error loading admin charts:', error);
            showChartError();
        });
}

// Load user dashboard charts
function loadUserCharts() {
    // Fetch user statistics
    fetch('/api/parking-stats', {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json',
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data && data.overview) {
                createBookingChart(data.overview);
                createSpendingChart(data.monthly_spending || {});
            } else {
                console.error('Invalid data format received:', data);
                showChartError();
            }
        })
        .catch(error => {
            console.error('Error loading user charts:', error);
            showChartError();
        });
}

// Create overall parking status pie chart for admin
function createOverallChart(stats) {
    const ctx = document.getElementById('overallChart');
    if (!ctx) return;

    // Clear any existing chart
    const existingChart = Chart.getChart(ctx);
    if (existingChart) {
        existingChart.destroy();
    }

    const availableSpots = stats.available_spots || 0;
    const occupiedSpots = stats.occupied_spots || 0;
    const total = availableSpots + occupiedSpots;

    if (total === 0) {
        ctx.parentElement.innerHTML = `
            <div class="alert alert-info text-center">
                <i class="fas fa-info-circle"></i>
                No parking spots available yet. Create some parking lots first!
            </div>
        `;
        return;
    }

    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Available Spots', 'Occupied Spots'],
            datasets: [{
                data: [availableSpots, occupiedSpots],
                backgroundColor: [chartColors.success, chartColors.danger],
                borderColor: [chartColors.success, chartColors.danger],
                borderWidth: 2
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
                            const percentage = total > 0 ? ((context.parsed / total) * 100).toFixed(1) : 0;
                            return `${context.label}: ${context.parsed} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Create lots occupancy bar chart for admin
function createLotsChart(lots) {
    const ctx = document.getElementById('lotsChart');
    if (!ctx) return;

    // Clear any existing chart
    const existingChart = Chart.getChart(ctx);
    if (existingChart) {
        existingChart.destroy();
    }

    if (!lots || lots.length === 0) {
        ctx.parentElement.innerHTML = `
            <div class="alert alert-info text-center">
                <i class="fas fa-info-circle"></i>
                No parking lots created yet. Add some parking lots to see occupancy data!
            </div>
        `;
        return;
    }

    const labels = lots.map(lot => lot.name.length > 15 ? 
        lot.name.substring(0, 15) + '...' : lot.name);
    const availableData = lots.map(lot => lot.available);
    const occupiedData = lots.map(lot => lot.occupied);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Available',
                    data: availableData,
                    backgroundColor: chartColors.success,
                    borderColor: chartColors.success,
                    borderWidth: 1
                },
                {
                    label: 'Occupied',
                    data: occupiedData,
                    backgroundColor: chartColors.danger,
                    borderColor: chartColors.danger,
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 0
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            const lotIndex = context.dataIndex;
                            const lot = lots[lotIndex];
                            return `Total spots: ${lot.total}`;
                        }
                    }
                }
            }
        }
    });
}

// Create booking summary donut chart for user
function createBookingChart(stats) {
    const ctx = document.getElementById('bookingChart');
    if (!ctx) return;

    // Clear any existing chart
    const existingChart = Chart.getChart(ctx);
    if (existingChart) {
        existingChart.destroy();
    }

    const activeReservations = stats.active_reservations || 0;
    const completedReservations = stats.completed_reservations || 0;
    const total = activeReservations + completedReservations;

    if (total === 0) {
        ctx.parentElement.innerHTML = `
            <div class="alert alert-info text-center">
                <i class="fas fa-info-circle"></i>
                No bookings yet. Start by booking your first parking spot!
            </div>
        `;
        return;
    }

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Active Bookings', 'Completed Bookings'],
            datasets: [{
                data: [activeReservations, completedReservations],
                backgroundColor: [chartColors.warning, chartColors.success],
                borderColor: [chartColors.warning, chartColors.success],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
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
                            const percentage = total > 0 ? ((context.parsed / total) * 100).toFixed(1) : 0;
                            return `${context.label}: ${context.parsed} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Create monthly spending line chart for user
function createSpendingChart(monthlyData) {
    const ctx = document.getElementById('spendingChart');
    if (!ctx) return;

    // Clear any existing chart
    const existingChart = Chart.getChart(ctx);
    if (existingChart) {
        existingChart.destroy();
    }

    // Check if there's any data
    if (!monthlyData || Object.keys(monthlyData).length === 0) {
        ctx.parentElement.innerHTML = `
            <div class="alert alert-info text-center">
                <i class="fas fa-info-circle"></i>
                No spending data yet. Complete some bookings to see your spending trends!
            </div>
        `;
        return;
    }

    // Sort months and prepare data
    const sortedMonths = Object.keys(monthlyData).sort();
    const labels = sortedMonths.map(month => {
        const date = new Date(month + '-01');
        return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
    });
    const data = sortedMonths.map(month => monthlyData[month]);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Amount Spent (₹)',
                data: data,
                borderColor: chartColors.primary,
                backgroundColor: chartColors.primary + '20',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: chartColors.primary,
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + value.toFixed(0);
                        }
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 0
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Amount: ₹${context.parsed.y.toFixed(2)}`;
                        }
                    }
                }
            }
        }
    });
}

// Show error message when charts fail to load
function showChartError() {
    const chartContainers = document.querySelectorAll('canvas[id$="Chart"]');
    chartContainers.forEach(canvas => {
        const container = canvas.parentElement;
        container.innerHTML = `
            <div class="alert alert-warning text-center">
                <i class="fas fa-exclamation-triangle"></i>
                Charts are loading... Please wait or refresh the page.
                <br><small>If this persists, ensure you are logged in.</small>
            </div>
        `;
    });
}

// Utility function to format duration
function formatDuration(hours) {
    if (hours < 1) {
        const minutes = Math.floor(hours * 60);
        return `${minutes}m`;
    } else if (hours < 24) {
        const h = Math.floor(hours);
        const m = Math.floor((hours - h) * 60);
        return m > 0 ? `${h}h ${m}m` : `${h}h`;
    } else {
        const days = Math.floor(hours / 24);
        const h = Math.floor(hours % 24);
        return h > 0 ? `${days}d ${h}h` : `${days}d`;
    }
}

// Auto-refresh charts every 30 seconds for real-time updates
function startAutoRefresh() {
    setInterval(() => {
        const currentPath = window.location.pathname;
        if (currentPath.includes('admin/dashboard')) {
            loadAdminCharts();
        } else if (currentPath.includes('user/dashboard')) {
            loadUserCharts();
        }
    }, 30000); // 30 seconds
}

// Initialize auto-refresh when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Start auto-refresh for dashboard pages
    if (window.location.pathname.includes('dashboard')) {
        startAutoRefresh();
    }
});

// Export functions for global access
window.chartUtils = {
    loadAdminCharts,
    loadUserCharts,
    createOverallChart,
    createLotsChart,
    createBookingChart,
    createSpendingChart,
    formatDuration
};
