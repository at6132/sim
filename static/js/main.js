// Global variables
let worldMap = null;
let selectedAgent = null;
let simulationRunning = false;
let timeScale = 1;

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    initializeMap();
    setupEventListeners();
    startSimulation();
});

// Initialize the world map
function initializeMap() {
    const canvas = document.getElementById('worldMap');
    const ctx = canvas.getContext('2d');
    
    // Set canvas size
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    
    // Initialize map
    worldMap = {
        canvas: canvas,
        ctx: ctx,
        width: canvas.width,
        height: canvas.height,
        scale: 1,
        offsetX: 0,
        offsetY: 0
    };
    
    // Draw initial map
    drawMap();
}

// Set up event listeners
function setupEventListeners() {
    // Simulation controls
    document.getElementById('startSim').addEventListener('click', startSimulation);
    document.getElementById('pauseSim').addEventListener('click', pauseSimulation);
    document.getElementById('resetSim').addEventListener('click', resetSimulation);
    
    // Time scale control
    document.getElementById('timeScale').addEventListener('input', (e) => {
        timeScale = parseInt(e.target.value);
        updateTimeScale(timeScale);
    });
    
    // Map interaction
    worldMap.canvas.addEventListener('mousedown', handleMapMouseDown);
    worldMap.canvas.addEventListener('mousemove', handleMapMouseMove);
    worldMap.canvas.addEventListener('mouseup', handleMapMouseUp);
    worldMap.canvas.addEventListener('wheel', handleMapZoom);
}

// Start the simulation
function startSimulation() {
    if (!simulationRunning) {
        simulationRunning = true;
        fetch('/api/world')
            .then(response => response.json())
            .then(data => {
                updateWorldState(data);
                requestAnimationFrame(updateLoop);
            });
    }
}

// Pause the simulation
function pauseSimulation() {
    simulationRunning = false;
}

// Reset the simulation
function resetSimulation() {
    fetch('/api/world/reset', { method: 'POST' })
        .then(() => {
            pauseSimulation();
            startSimulation();
        });
}

// Update time scale
function updateTimeScale(scale) {
    fetch('/api/world/timescale', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scale })
    });
}

// Main update loop
function updateLoop() {
    if (simulationRunning) {
        fetch('/api/world')
            .then(response => response.json())
            .then(data => {
                updateWorldState(data);
                requestAnimationFrame(updateLoop);
            });
    }
}

// Update world state
function updateWorldState(state) {
    // Update map
    drawMap(state);
    
    // Update agent panel if agent is selected
    if (selectedAgent) {
        updateAgentPanel(selectedAgent);
    }
    
    // Update civilization tracker
    updateCivilizationTracker(state);
    
    // Update family trees
    updateFamilyTrees(state);
}

// Draw the world map
function drawMap(state) {
    const ctx = worldMap.ctx;
    ctx.clearRect(0, 0, worldMap.width, worldMap.height);
    
    if (!state) return;
    
    // Draw terrain
    state.world.terrain.forEach(tile => {
        const x = (tile.longitude + 180) * worldMap.width / 360;
        const y = (90 - tile.latitude) * worldMap.height / 180;
        
        ctx.fillStyle = getTerrainColor(tile.type);
        ctx.fillRect(x, y, 1, 1);
    });
    
    // Draw agents
    Object.values(state.world.agents).forEach(agent => {
        const x = (agent.longitude + 180) * worldMap.width / 360;
        const y = (90 - agent.latitude) * worldMap.height / 180;
        
        ctx.fillStyle = '#007bff';
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, Math.PI * 2);
        ctx.fill();
    });
    
    // Draw animals
    Object.values(state.world.animals).forEach(animal => {
        const x = (animal.longitude + 180) * worldMap.width / 360;
        const y = (90 - animal.latitude) * worldMap.height / 180;
        
        ctx.fillStyle = '#28a745';
        ctx.beginPath();
        ctx.arc(x, y, 2, 0, Math.PI * 2);
        ctx.fill();
    });
}

// Get terrain color
function getTerrainColor(type) {
    const colors = {
        'water': '#0077be',
        'land': '#90EE90',
        'mountain': '#808080',
        'forest': '#228B22',
        'desert': '#F4A460'
    };
    return colors[type] || '#90EE90';
}

// Update agent panel
function updateAgentPanel(agent) {
    const panel = document.getElementById('agentPanel');
    panel.innerHTML = `
        <div class="stat-card">
            <div class="stat-value">${agent.name}</div>
            <div class="stat-label">${agent.gender}, Age: ${agent.age.toFixed(1)}</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${agent.health.toFixed(2)}</div>
            <div class="stat-label">Health</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${agent.needs.food.toFixed(2)}</div>
            <div class="stat-label">Food</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${agent.needs.water.toFixed(2)}</div>
            <div class="stat-label">Water</div>
        </div>
    `;
}

// Update civilization tracker
function updateCivilizationTracker(state) {
    const inventions = document.getElementById('inventions');
    const religions = document.getElementById('religions');
    const languages = document.getElementById('languages');
    
    // Update inventions
    inventions.innerHTML = '<h4>Inventions</h4>' + 
        Object.entries(state.world.technology.discoveries)
            .map(([id, tech]) => `<div class="timeline-event">${tech.name}</div>`)
            .join('');
    
    // Update religions
    religions.innerHTML = '<h4>Religions</h4>' +
        Object.entries(state.world.society.religions)
            .map(([id, religion]) => `<div class="timeline-event">${religion.name}</div>`)
            .join('');
    
    // Update languages
    languages.innerHTML = '<h4>Languages</h4>' +
        Object.entries(state.world.society.languages)
            .map(([id, language]) => `<div class="timeline-event">${language.name}</div>`)
            .join('');
}

// Update family trees
function updateFamilyTrees(state) {
    const container = document.getElementById('familyTree');
    
    // Create SVG for family tree
    const svg = d3.select(container)
        .append('svg')
        .attr('width', '100%')
        .attr('height', '100%');
    
    // Create tree layout
    const tree = d3.tree()
        .size([container.clientWidth, container.clientHeight]);
    
    // Create hierarchy
    const root = d3.hierarchy(state.world.society.familyTrees);
    
    // Calculate tree layout
    const nodes = tree(root);
    
    // Draw links
    svg.selectAll('.link')
        .data(nodes.links())
        .enter()
        .append('path')
        .attr('class', 'link')
        .attr('d', d3.linkVertical()
            .x(d => d.x)
            .y(d => d.y));
    
    // Draw nodes
    svg.selectAll('.node')
        .data(nodes.descendants())
        .enter()
        .append('circle')
        .attr('class', 'node')
        .attr('cx', d => d.x)
        .attr('cy', d => d.y)
        .attr('r', 5);
}

// Map interaction handlers
function handleMapMouseDown(e) {
    // Handle map panning
}

function handleMapMouseMove(e) {
    // Handle map panning
}

function handleMapMouseUp(e) {
    // Handle map panning
}

function handleMapZoom(e) {
    // Handle map zooming
}

// Socket event handlers
socket.on('simulation_state', (data) => {
    updateWorldState(data);
}); 