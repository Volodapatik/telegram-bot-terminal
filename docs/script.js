class BotTerminal {
    constructor() {
        this.isConnected = false;
        this.botRunning = false;
        this.startTime = null;
        this.requestCount = 0;
        this.initializeTerminal();
    }

    initializeTerminal() {
        this.updateTime();
        setInterval(() => this.updateTime(), 1000);
        this.setupEventListeners();
        this.log('System initialized successfully');
    }

    updateTime() {
        const now = new Date();
        document.getElementById('currentTime').textContent = 
            now.toLocaleTimeString();
        document.getElementById('lastUpdate').textContent = 
            `Last update: ${now.toLocaleTimeString()}`;
        
        if (this.startTime && this.botRunning) {
            this.updateUptime();
        }
    }

    updateUptime() {
        const now = new Date();
        const diff = now - this.startTime;
        const hours = Math.floor(diff / 3600000);
        const minutes = Math.floor((diff % 3600000) / 60000);
        const seconds = Math.floor((diff % 60000) / 1000);
        
        document.getElementById('uptime').textContent = 
            `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    setupEventListeners() {
        document.getElementById('startBtn').addEventListener('click', () => this.startBot());
        document.getElementById('stopBtn').addEventListener('click', () => this.stopBot());
        document.getElementById('refreshBtn').addEventListener('click', () => this.refreshStatus());
        document.getElementById('clearBtn').addEventListener('click', () => this.clearLog());
    }

    async startBot() {
        this.log('🚀 Starting bot...');
        this.setStatus('CONNECTING', 'yellow');
        
        try {
            // Тут буде запит до Firebase
            await this.simulateRequest('start');
            this.botRunning = true;
            this.startTime = new Date();
            this.setStatus('ONLINE', 'green');
            this.log('✅ Bot started successfully');
            this.updateBotStatus('RUNNING');
        } catch (error) {
            this.setStatus('ERROR', 'red');
            this.log('❌ Failed to start bot: ' + error.message);
        }
    }

    async stopBot() {
        this.log('🛑 Stopping bot...');
        
        try {
            // Тут буде запит до Firebase
            await this.simulateRequest('stop');
            this.botRunning = false;
            this.setStatus('OFFLINE', 'red');
            this.log('✅ Bot stopped successfully');
            this.updateBotStatus('STOPPED');
        } catch (error) {
            this.log('❌ Failed to stop bot: ' + error.message);
        }
    }

    refreshStatus() {
        this.requestCount++;
        document.getElementById('requestCount').textContent = this.requestCount;
        this.log('🔄 Status refreshed');
        
        // Симуляція даних моніторингу
        document.getElementById('memoryUsage').textContent = 
            Math.floor(Math.random() * 100 + 50) + ' MB';
    }

    clearLog() {
        document.getElementById('console').innerHTML = `
            <div class="log-entry">
                <span class="timestamp" id="currentTime"></span>
                <span class="log-message">🟢 Log cleared</span>
            </div>
        `;
        this.updateTime();
    }

    setStatus(status, color) {
        const indicator = document.getElementById('statusIndicator');
        const text = document.getElementById('statusText');
        
        text.textContent = status;
        text.style.color = color;
        indicator.style.color = color;
    }

    updateBotStatus(status) {
        const element = document.getElementById('botStatus');
        element.textContent = status;
        element.style.color = status === 'RUNNING' ? '#00ff00' : '#ff4444';
    }

    log(message) {
        const console = document.getElementById('console');
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';
        
        const timestamp = document.createElement('span');
        timestamp.className = 'timestamp';
        timestamp.textContent = new Date().toLocaleTimeString();
        
        const logMessage = document.createElement('span');
        logMessage.className = 'log-message';
        logMessage.textContent = message;
        
        logEntry.appendChild(timestamp);
        logEntry.appendChild(logMessage);
        console.appendChild(logEntry);
        console.scrollTop = console.scrollHeight;
    }

    // Тимчасова симуляція запитів
    async simulateRequest(action) {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                if (Math.random() > 0.1) { // 90% success rate
                    resolve();
                } else {
                    reject(new Error('Server timeout'));
                }
            }, 2000);
        });
    }
}

// Ініціалізація термінала
document.addEventListener('DOMContentLoaded', () => {
    new BotTerminal();
});
