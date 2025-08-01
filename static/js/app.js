// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('devint Web Interface initializing...');

    // Initialize WebSocket connection
    window.wsManager.connect();

    // Setup navigation
    setupNavigation();

    // Setup scan functionality
    setupScanForm();

    // Initialize tooltips, modals, etc.
    initializeUI();
});

function setupNavigation() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            // Update active nav
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            this.classList.add('active');

            // Show corresponding view
            const viewId = this.getAttribute('href').substring(1) + '-view';
            document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
            const view = document.getElementById(viewId);
            if (view) {
                view.classList.add('active');
            }
        });
    });
}

function showDashboard() {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.getElementById('dashboard-view').classList.add('active');

    // Update active nav
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    document.querySelector('.nav-link[href="#dashboard"]').classList.add('active');
}

function setupScanForm() {
    // Auto-fill ports if available
    fetch('/api/serial/ports')
        .then(response => response.json())
        .then(data => {
            if (data.ports && data.ports.length > 0) {
                document.getElementById('scan-ports').value = data.ports.join(',');
            }
        })
        .catch(error => console.error('Error fetching ports:', error));
}

function startScan() {
    const ports = document.getElementById('scan-ports').value;
    const baudrates = document.getElementById('scan-baudrates').value;

    if (!ports) {
        showNotification('warning', 'Proszę podać porty do skanowania');
        return;
    }

    const resultsContainer = document.getElementById('scan-results');
    resultsContainer.innerHTML = '<div class="scan-progress">Skanowanie w toku...</div>';

    // Send scan request
    window.wsManager.send('scan_devices', {
        ports: ports.split(',').map(p => p.trim()),
        baudrates: baudrates.split(',').map(b => parseInt(b.trim()))
    });

    // Listen for scan results
    window.wsManager.on('scan_result', (data) => {
        updateScanResults(data);
    });

    window.wsManager.on('scan_complete', (data) => {
        showNotification('success', 'Skanowanie zakończone');
    });
}

function updateScanResults(results) {
    const container = document.getElementById('scan-results');

    if (results.length === 0) {
        container.innerHTML = '<p>Nie znaleziono żadnych urządzeń</p>';
        return;
    }

    const html = results.map(result => `
        <div class="scan-result">
            <div class="scan-result-header">
                <i class="fas fa-check-circle"></i>
                Znaleziono urządzenie
            </div>
            <div class="scan-result-details">
                <div>Port: <strong>${result.port}</strong></div>
                <div>Prędkość: <strong>${result.baudrate} baud</strong></div>
                <div>Unit ID: <strong>${result.unit_id}</strong></div>
            </div>
            <button class="btn btn-primary" onclick="addScannedDevice('${result.port}', ${result.baudrate}, ${result.unit_id})">
                Dodaj urządzenie
            </button>
        </div>
    `).join('');

    container.innerHTML = html;
}

function addScannedDevice(port, baudrate, unitId) {
    window.wsManager.send('add_device', {
        port: port,
        baudrate: baudrate,
        unit_id: unitId,
        type: 'auto_detect'
    });
}

function showNotification(type, message) {
    // Simple notification implementation
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check' : type === 'error' ? 'times' : 'info'}-circle"></i>
        ${message}
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('show');
    }, 10);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

function initializeUI() {
    // Add any additional UI initialization here
    console.log('UI initialized');
}

// Export functions for global use
window.showDashboard = showDashboard;
window.startScan = startScan;
window.addScannedDevice = addScannedDevice;
window.showNotification = showNotification;