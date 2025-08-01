class DeviceManager {
    constructor() {
        this.devices = new Map();
        this.activeDeviceId = null;
        this.widgets = new Map();
    }

    updateDevices(devicesData) {
        // Update devices map
        devicesData.forEach(device => {
            this.devices.set(device.device_id, device);
        });

        // Update UI
        this.renderDevicesList();
        this.updateStats();
    }

    updateDevice(deviceData) {
        this.devices.set(deviceData.device_id, deviceData);

        // Update device card
        this.updateDeviceCard(deviceData.device_id);

        // Update device details if active
        if (this.activeDeviceId === deviceData.device_id) {
            this.renderDeviceDetails(deviceData);
        }

        this.updateStats();
    }

    updateRegister(deviceId, registerName, value) {
        const device = this.devices.get(deviceId);
        if (device && device.registers[registerName]) {
            device.registers[registerName].value = value;

            // Update widgets
            const widget = this.widgets.get(`${deviceId}_registers`);
            if (widget) {
                widget.updateRegister(registerName, value);
            }

            // Update IO widgets if needed
            if (registerName.startsWith('output_')) {
                const outputWidget = this.widgets.get(`${deviceId}_outputs`);
                if (outputWidget) {
                    const outputs = this.getOutputStates(device);
                    outputWidget.update(outputs);
                }
            } else if (registerName.startsWith('input_')) {
                const inputWidget = this.widgets.get(`${deviceId}_inputs`);
                if (inputWidget) {
                    const inputs = this.getInputStates(device);
                    inputWidget.update(inputs);
                }
            }
        }
    }

    renderDevicesList() {
        const container = document.getElementById('devices-list');
        if (!container) return;

        const html = Array.from(this.devices.values()).map(device => `
            <div class="device-card ${device.is_online ? '' : 'offline'}"
                 onclick="DeviceManager.showDevice('${device.device_id}')">
                <div class="device-header">
                    <h3 class="device-title">${device.name}</h3>
                    <div class="device-status ${device.is_online ? 'online' : ''}"></div>
                </div>
                <div class="device-info">
                    <div class="device-info-row">
                        <span class="device-info-label">Model:</span>
                        <span class="device-info-value">${device.identity.model}</span>
                    </div>
                    <div class="device-info-row">
                        <span class="device-info-label">Port:</span>
                        <span class="device-info-value">${this.getDevicePort(device)}</span>
                    </div>
                    <div class="device-info-row">
                        <span class="device-info-label">Status:</span>
                        <span class="device-info-value">${device.is_online ? 'Online' : 'Offline'}</span>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = html || '<p>Brak urządzeń</p>';
    }

    updateDeviceCard(deviceId) {
        // Implementation for updating single device card
    }

    showDevice(deviceId) {
        const device = this.devices.get(deviceId);
        if (!device) return;

        this.activeDeviceId = deviceId;

        // Switch to device view
        document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
        document.getElementById('device-view').classList.add('active');

        // Update device name
        document.getElementById('device-name').textContent = device.name;

        // Render device details
        this.renderDeviceDetails(device);
    }

    renderDeviceDetails(device) {
        const container = document.getElementById('device-content');

        // Clear existing widgets
        this.widgets.forEach(widget => {
            if (widget.deviceId === device.device_id) {
                this.widgets.delete(widget);
            }
        });

        let html = `
            <div class="device-details">
                <div class="device-info-card">
                    <h3>Informacje o urządzeniu</h3>
                    <div class="device-info">
                        <div class="device-info-row">
                            <span class="device-info-label">Producent:</span>
                            <span class="device-info-value">${device.identity.manufacturer}</span>
                        </div>
                        <div class="device-info-row">
                            <span class="device-info-label">Model:</span>
                            <span class="device-info-value">${device.identity.model}</span>
                        </div>
                        <div class="device-info-row">
                            <span class="device-info-label">Port:</span>
                            <span class="device-info-value">${this.getDevicePort(device)}</span>
                        </div>
                        <div class="device-info-row">
                            <span class="device-info-label">Protokół:</span>
                            <span class="device-info-value">${this.getDeviceProtocol(device)}</span>
                        </div>
                    </div>
                </div>
        `;

        // Add capability-specific widgets
        if (device.capabilities.digital_outputs) {
            html += '<div id="outputs-widget"></div>';
        }

        if (device.capabilities.digital_inputs) {
            html += '<div id="inputs-widget"></div>';
        }

        if (device.capabilities.analog_inputs) {
            html += '<div id="analog-widget"></div>';
        }

        // Add registers table
        html += '<div id="registers-widget"></div>';

        html += '</div>';

        container.innerHTML = html;

        // Create widgets
        if (device.capabilities.digital_outputs) {
            const outputs = this.getOutputStates(device);
            const widget = new DigitalIOWidget('outputs-widget', device.device_id, outputs, 'output');
            this.widgets.set(`${device.device_id}_outputs`, widget);
        }

        if (device.capabilities.digital_inputs) {
            const inputs = this.getInputStates(device);
            const widget = new DigitalIOWidget('inputs-widget', device.device_id, inputs, 'input');
            this.widgets.set(`${device.device_id}_inputs`, widget);
        }

        if (device.capabilities.analog_inputs) {
            const channels = this.getAnalogChannels(device);
            const widget = new AnalogInputWidget('analog-widget', device.device_id, channels);
            this.widgets.set(`${device.device_id}_analog`, widget);
        }

        // Create registers table
        const registersWidget = new RegisterTableWidget('registers-widget', device.device_id, device.registers);
        this.widgets.set(`${device.device_id}_registers`, registersWidget);
    }

    getDevicePort(device) {
        const primaryInterface = device.interfaces.primary;
        return primaryInterface ? primaryInterface.port : 'N/A';
    }

    getDeviceProtocol(device) {
        const primaryInterface = device.interfaces.primary;
        return primaryInterface ? primaryInterface.protocol : 'N/A';
    }

    getOutputStates(device) {
        const states = [];
        for (let i = 0; i < 8; i++) {
            const reg = device.registers[`output_${i}`];
            states.push(reg ? reg.value : false);
        }
        return states;
    }

    getInputStates(device) {
        const states = [];
        for (let i = 0; i < 8; i++) {
            const reg = device.registers[`input_${i}`];
            states.push(reg ? reg.value : false);
        }
        return states;
    }

    getAnalogChannels(device) {
        const channels = [];
        for (let i = 0; i < 8; i++) {
            const reg = device.registers[`analog_${i}`];
            if (reg) {
                channels.push({
                    value: reg.value || 0,
                    unit: reg.unit || 'V',
                    type: '0-10V',
                    max_value: 10
                });
            }
        }
        return channels;
    }

    updateStats() {
        const onlineCount = Array.from(this.devices.values()).filter(d => d.is_online).length;
        const outputsActive = Array.from(this.devices.values()).reduce((count, device) => {
            return count + this.getOutputStates(device).filter(state => state).length;
        }, 0);
        const inputsActive = Array.from(this.devices.values()).reduce((count, device) => {
            return count + this.getInputStates(device).filter(state => state).length;
        }, 0);

        document.getElementById('devices-online').textContent = onlineCount;
        document.getElementById('outputs-active').textContent = outputsActive;
        document.getElementById('inputs-active').textContent = inputsActive;
    }

    static showDevice(deviceId) {
        window.DeviceManager.showDevice(deviceId);
    }
}

// Create global instance
window.DeviceManager = new DeviceManager();