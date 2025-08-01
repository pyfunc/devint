class DigitalIOWidget {
    constructor(containerId, deviceId, channels, type = 'output') {
        this.container = document.getElementById(containerId);
        this.deviceId = deviceId;
        this.channels = channels;
        this.type = type;
        this.render();
    }

    render() {
        const html = `
            <div class="io-widget">
                <div class="io-widget-header">
                    <i class="fas fa-${this.type === 'output' ? 'toggle-on' : 'sign-in-alt'}"></i>
                    <h3 class="io-widget-title">
                        ${this.type === 'output' ? 'Wyjścia cyfrowe' : 'Wejścia cyfrowe'}
                    </h3>
                </div>
                <div class="io-channels">
                    ${this.channels.map((channel, index) => this.renderChannel(channel, index)).join('')}
                </div>
            </div>
        `;
        this.container.innerHTML = html;

        if (this.type === 'output') {
            this.attachEventHandlers();
        }
    }

    renderChannel(value, index) {
        const isOutput = this.type === 'output';
        return `
            <div class="io-channel">
                <div class="io-channel-label">CH${index}</div>
                <button
                    class="io-channel-button ${value ? 'active' : ''}"
                    data-channel="${index}"
                    ${isOutput ? '' : 'disabled'}
                >
                    ${isOutput ? (value ? 'ON' : 'OFF') : (value ? '1' : '0')}
                </button>
            </div>
        `;
    }

    attachEventHandlers() {
        this.container.querySelectorAll('.io-channel-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const channel = parseInt(e.target.dataset.channel);
                this.toggleChannel(channel);
            });
        });
    }

    toggleChannel(channel) {
        const currentValue = this.channels[channel];
        const newValue = !currentValue;

        // Send command via WebSocket
        window.wsManager.send('write_register', {
            device_id: this.deviceId,
            register: `output_${channel}`,
            value: newValue
        });

        // Optimistic UI update
        this.channels[channel] = newValue;
        this.updateChannel(channel, newValue);
    }

    updateChannel(channel, value) {
        const button = this.container.querySelector(`[data-channel="${channel}"]`);
        if (button) {
            button.classList.toggle('active', value);
            button.textContent = this.type === 'output' ? (value ? 'ON' : 'OFF') : (value ? '1' : '0');
        }
    }

    update(channels) {
        this.channels = channels;
        channels.forEach((value, index) => {
            this.updateChannel(index, value);
        });
    }
}

class AnalogInputWidget {
    constructor(containerId, deviceId, channels) {
        this.container = document.getElementById(containerId);
        this.deviceId = deviceId;
        this.channels = channels;
        this.render();
    }

    render() {
        const html = `
            <div class="analog-widget">
                <div class="io-widget-header">
                    <i class="fas fa-wave-square"></i>
                    <h3 class="io-widget-title">Wejścia analogowe</h3>
                </div>
                <div class="analog-channels">
                    ${this.channels.map((channel, index) => this.renderChannel(channel, index)).join('')}
                </div>
            </div>
        `;
        this.container.innerHTML = html;
    }

    renderChannel(channel, index) {
        const percentage = (channel.value / channel.max_value) * 100;
        return `
            <div class="analog-channel">
                <div class="analog-channel-header">
                    <span class="analog-channel-name">AI${index}</span>
                    <span class="analog-channel-type">${channel.type}</span>
                </div>
                <div class="analog-channel-value">
                    ${channel.value.toFixed(2)}
                    <span class="analog-channel-unit">${channel.unit}</span>
                </div>
                <div class="analog-channel-bar">
                    <div class="analog-channel-bar-fill" style="width: ${percentage}%"></div>
                </div>
            </div>
        `;
    }

    update(channels) {
        this.channels = channels;
        channels.forEach((channel, index) => {
            this.updateChannel(channel, index);
        });
    }

    updateChannel(channel, index) {
        const channelEl = this.container.querySelectorAll('.analog-channel')[index];
        if (channelEl) {
            const valueEl = channelEl.querySelector('.analog-channel-value');
            const barEl = channelEl.querySelector('.analog-channel-bar-fill');

            valueEl.innerHTML = `${channel.value.toFixed(2)}<span class="analog-channel-unit">${channel.unit}</span>`;
            barEl.style.width = `${(channel.value / channel.max_value) * 100}%`;
        }
    }
}

class RegisterTableWidget {
    constructor(containerId, deviceId, registers) {
        this.container = document.getElementById(containerId);
        this.deviceId = deviceId;
        this.registers = registers;
        this.render();
    }

    render() {
        const html = `
            <table class="register-table">
                <thead>
                    <tr>
                        <th>Nazwa</th>
                        <th>Adres</th>
                        <th>Wartość</th>
                        <th>Typ</th>
                        <th>Akcje</th>
                    </tr>
                </thead>
                <tbody>
                    ${Object.entries(this.registers).map(([name, reg]) => this.renderRow(name, reg)).join('')}
                </tbody>
            </table>
        `;
        this.container.innerHTML = html;
        this.attachEventHandlers();
    }

    renderRow(name, register) {
        const isWritable = register.access.includes('w');
        return `
            <tr>
                <td>${register.description || name}</td>
                <td>0x${register.address.toString(16).padStart(4, '0')}</td>
                <td class="register-value" id="reg-${name}">${this.formatValue(register.value, register.data_type)}</td>
                <td>${register.data_type}</td>
                <td class="register-actions">
                    <button class="btn btn-small btn-primary" onclick="readRegister('${this.deviceId}', '${name}')">
                        <i class="fas fa-sync"></i>
                    </button>
                    ${isWritable ? `
                        <button class="btn btn-small btn-success" onclick="writeRegister('${this.deviceId}', '${name}')">
                            <i class="fas fa-edit"></i>
                        </button>
                    ` : ''}
                </td>
            </tr>
        `;
    }

    formatValue(value, dataType) {
        if (value === null || value === undefined) return '-';

        switch (dataType) {
            case 'bool':
                return value ? 'TRUE' : 'FALSE';
            case 'uint16':
            case 'int16':
                return `${value} (0x${value.toString(16).padStart(4, '0')})`;
            case 'float32':
                return value.toFixed(3);
            default:
                return value.toString();
        }
    }

    updateRegister(name, value) {
        const element = document.getElementById(`reg-${name}`);
        if (element && this.registers[name]) {
            element.textContent = this.formatValue(value, this.registers[name].data_type);
            element.classList.add('updated');
            setTimeout(() => element.classList.remove('updated'), 1000);
        }
    }

    attachEventHandlers() {
        // Event handlers są inline w HTML dla uproszczenia
    }
}

// Global widget functions
window.readRegister = function(deviceId, registerName) {
    window.wsManager.send('read_register', {
        device_id: deviceId,
        register: registerName
    });
};

window.writeRegister = function(deviceId, registerName) {
    const value = prompt(`Wprowadź nową wartość dla ${registerName}:`);
    if (value !== null) {
        window.wsManager.send('write_register', {
            device_id: deviceId,
            register: registerName,
            value: parseFloat(value) || value
        });
    }
};