// Connect to WebSocket
const socket = io();

// DOM Elements
const startButton = document.getElementById('start-simulation');
const stopButton = document.getElementById('stop-simulation');
const statusDiv = document.getElementById('simulation-status');
const logContainer = document.getElementById('log-container');

// Socket event handlers
socket.on('connect', () => {
    addLogEntry('Connected to server', 'info');
    updateStatus('connected');
});

socket.on('disconnect', () => {
    addLogEntry('Disconnected from server', 'warning');
    updateStatus('disconnected');
});

socket.on('simulation_state', (state) => {
    updateSimulationState(state);
});

// Button event handlers
startButton.addEventListener('click', () => {
    socket.emit('start_simulation');
    addLogEntry('Starting simulation...', 'info');
});

stopButton.addEventListener('click', () => {
    socket.emit('stop_simulation');
    addLogEntry('Stopping simulation...', 'info');
});

// Helper functions
function updateStatus(status) {
    statusDiv.className = `status ${status}`;
    statusDiv.textContent = `Status: ${status}`;
}

function addLogEntry(message, type) {
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    logContainer.appendChild(entry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

function updateSimulationState(state) {
    // Update UI with simulation state
    // This will be expanded based on what data we want to display
    console.log('Simulation state updated:', state);
} 