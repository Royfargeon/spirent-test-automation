// Initialize charts
let resultChart = null;
let trendChart = null;

document.addEventListener('DOMContentLoaded', () => {
    initializeCharts();
    setupEventListeners();
});

function initializeCharts() {
    const resultCtx = document.getElementById('resultChart').getContext('2d');
    const trendCtx = document.getElementById('trendChart').getContext('2d');

    resultChart = new Chart(resultCtx, {
        type: 'bar',
        data: {
            labels: ['Success', 'Failed'],
            datasets: [{
                label: 'Test Results',
                data: [0, 0],
                backgroundColor: ['rgba(75, 192, 192, 0.2)', 'rgba(255, 99, 132, 0.2)'],
                borderColor: ['rgb(75, 192, 192)', 'rgb(255, 99, 132)'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Test Results Summary'
                }
            }
        }
    });

    trendChart = new Chart(trendCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Test Duration Trend',
                data: [],
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Test Duration Trend'
                }
            }
        }
    });
}

function setupEventListeners() {
    // File Upload Handler
    document.getElementById('uploadForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData();
        const fileInput = document.getElementById('tccFile');
        formData.append('file', fileInput.files[0]);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            if (result.success) {
                alert('File uploaded successfully');
                location.reload(); // Refresh to update test list
            } else {
                alert(result.error);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Upload failed');
        }
    });

    // Test Execution Handler
    document.getElementById('runTest').addEventListener('click', async () => {
        const testSelect = document.getElementById('testSelect');
        const selectedTest = testSelect.value;
        
        if (!selectedTest) {
            alert('Please select a test configuration');
            return;
        }

        const statusDiv = document.getElementById('testStatus');
        statusDiv.textContent = 'Running test...';
        statusDiv.className = 'alert alert-info';
        statusDiv.style.display = 'block';

        try {
            const response = await fetch('/run-test', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ test_file: selectedTest })
            });
            const result = await response.json();
            
            if (result.status === 'success') {
                updateResults(result.data);
                statusDiv.textContent = 'Test completed successfully';
                statusDiv.className = 'alert alert-success';
            } else {
                statusDiv.textContent = `Test failed: ${result.error}`;
                statusDiv.className = 'alert alert-danger';
            }
        } catch (error) {
            console.error('Error:', error);
            statusDiv.textContent = 'Test execution failed';
            statusDiv.className = 'alert alert-danger';
        }
    });
}

function updateResults(result) {
    // Update table
    const tbody = document.querySelector('#resultsTable tbody');
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>${new Date(result.timestamp).toLocaleString()}</td>
        <td>${result.test_file}</td>
        <td>${result.status}</td>
        <td>${result.return_code}</td>
        <td>
            <button class="btn btn-sm btn-info" onclick="viewDetails('${result.timestamp}')">Details</button>
        </td>
    `;
    tbody.insertBefore(row, tbody.firstChild);

    // Update charts
    updateCharts(result);
}

function updateCharts(result) {
    // Update result chart
    const successCount = parseInt(resultChart.data.datasets[0].data[0]);
    const failCount = parseInt(resultChart.data.datasets[0].data[1]);
    
    if (result.status === 'completed') {
        resultChart.data.datasets[0].data[0] = successCount + 1;
    } else {
        resultChart.data.datasets[0].data[1] = failCount + 1;
    }
    resultChart.update();

    // Update trend chart
    const timestamp = new Date(result.timestamp).toLocaleTimeString();
    trendChart.data.labels.push(timestamp);
    trendChart.data.datasets[0].data.push(result.duration || 0);
    if (trendChart.data.labels.length > 10) {
        trendChart.data.labels.shift();
        trendChart.data.datasets[0].data.shift();
    }
    trendChart.update();
}

function viewDetails(timestamp) {
    // Implement detailed view of test results
    alert('Details view to be implemented');
}