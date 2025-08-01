class WebSocketManager {
    constructor() {
        this.ws = null;
        this.reconnectInterval = 5000;
        this.reconnectTimer = null;
        this.messageHandlers = new Map();
        this.isConnected = false;
        this.url = `ws://${window.location.host}/ws`;
    }

    connect() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            return;
        }

        try {
            this.ws = new WebSocket(this.url);

            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.isConnected = true;
                this.updateConnectionStatus(true);
                this.clearReconnectTimer();

                // Request initial data
                this.send('get_devices', {});
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };

            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.isConnected = false;
                this.updateConnectionStatus(false);
                this.scheduleReconnect();
            };
        } catch (error) {
            console.error('Error creating WebSocket:', error);
            this.scheduleReconnect();
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.clearReconnectTimer();
    }

    send(type, data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            const message = JSON.stringify({
                type: type,
                data: data,
                timestamp: new Date().toISOString()
            });
            this.ws.send(message);
        } else {
            console.warn('WebSocket not connected');
        }
    }

    handleMessage(message) {
        const { type, data } = message;

        // Handle system messages
        switch (type) {
            case 'devices_list':
                this.updateDevicesList(data);
                break;
            case 'device_update':
                this.updateDevice(data);
                break;
            case 'register_update':
                this.updateRegister(data);
                break;
            case 'error':
                this.handleError(data);
                break;
        }

        // Call custom handlers
        const handlers = this.messageHandlers.get(type) || [];
        handlers.forEach(handler => handler(data));
    }

    on(type, handler) {
        if (!this.messageHandlers.has(type)) {
            this.messageHandlers.set(type, []);
        }
        this.messageHandlers.get(type).push(handler);
    }

    off(type, handler) {
        const handlers = this.messageHandlers.get(type);
        if (handlers) {
            const index = handlers.indexOf(handler);
            if (index !== -1) {
                handlers.splice(index, 1);
            }
        }
    }

    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('ws-status');
        if (statusElement) {
            statusElement.className = `status-indicator ${connected ? 'online' : 'offline'}`;
            statusElement.innerHTML = `<i class="fas fa-circle"></i> ${connected ? 'Połączony' : 'Rozłączony'}`;
        }
    }

    updateDevicesList(devices) {
        if (window.DeviceManager) {
            window.DeviceManager.updateDevices(devices);
        }
    }

    updateDevice(deviceData) {
        if (window.DeviceManager) {
            window.DeviceManager.updateDevice(deviceData);
        }
    }

    updateRegister(data) {
        if (window.DeviceManager) {
            window.DeviceManager.updateRegister(data.device_id, data.register, data.value);
        }
    }

    handleError(error) {
        console.error('WebSocket error:', error);
        // Show error notification
        if (window.showNotification) {
            window.showNotification('error', error.message || 'Wystąpił błąd');
        }
    }

    scheduleReconnect() {
        this.clearReconnectTimer();
        this.reconnectTimer = setTimeout(() => {
            console.log('Attempting to reconnect...');
            this.connect();
        }, this.reconnectInterval);
    }

    clearReconnectTimer() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
    }
}

// Create global WebSocket manager instance
window.wsManager = new WebSocketManager();