import { DashboardAPI } from './api.js';

// DOM Elements
const views = document.querySelectorAll('.view-section');
const navItems = document.querySelectorAll('.nav-item');
const refreshBtn = document.getElementById('refresh-btn');
const manualTaskBtn = document.getElementById('manual-task-btn');
const modal = document.getElementById('task-modal');
const closeModal = document.querySelector('.close-modal');
const taskForm = document.getElementById('task-form');

// State
let pollingInterval = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    loadOverview();
    startPolling();
});

// Navigation Logic
function initNavigation() {
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const viewId = item.dataset.view;

            // UI Updates
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');

            views.forEach(v => v.classList.remove('active'));
            document.getElementById(`view-${viewId}`).classList.add('active');

            // Header Update
            document.getElementById('page-title').innerText = item.innerText;

            // Load Data
            if (viewId === 'overview') loadOverview();
            if (viewId === 'agents') loadAgents();
            if (viewId === 'logs') loadLogs();
            if (viewId === 'settings') loadSettings();
        });
    });

    // Modal Logic
    manualTaskBtn.addEventListener('click', () => modal.style.display = 'flex');
    closeModal.addEventListener('click', () => modal.style.display = 'none');
    window.addEventListener('click', (e) => {
        if (e.target === modal) modal.style.display = 'none';
    });

    taskForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const type = document.getElementById('task-type').value;
        const topic = document.getElementById('task-topic').value;

        const result = await DashboardAPI.triggerTask(type, topic);
        if (result) {
            alert('Task Started Successfully!');
            modal.style.display = 'none';
        } else {
            alert('Task Failed to Start');
        }
    });

    refreshBtn.addEventListener('click', () => {
        const activeView = document.querySelector('.view-section.active').id;
        if (activeView === 'view-overview') loadOverview();
        if (activeView === 'view-agents') loadAgents();
        if (activeView === 'view-logs') loadLogs();
    });
}

// Data Loading Functions
async function loadOverview() {
    const data = await DashboardAPI.getOverview();
    if (!data) return;

    document.getElementById('stat-content-count').innerText = data.content?.total_content_created || 0;
    document.getElementById('stat-active-agents').innerText = data.active_agents || 0;
    // document.getElementById('stat-uptime').innerText = data.system_uptime_hours + 'h';

    // Activity List
    const list = document.getElementById('recent-activity-list');
    list.innerHTML = '';
    // Mock activity usage for now
    [
        { text: "System Initialized", time: "Just now" },
        { text: "Checking Trends...", time: "2m ago" }
    ].forEach(item => {
        const li = document.createElement('li');
        li.innerHTML = `<strong>${item.text}</strong> <span style="font-size:0.8rem; color:#888;">${item.time}</span>`;
        list.appendChild(li);
    });
}

async function loadAgents() {
    const data = await DashboardAPI.getAgentStatus();
    const container = document.getElementById('agents-list');
    container.innerHTML = '';

    if (!data || !data.agents) {
        container.innerHTML = '<p>No agents found or orchestrator offline.</p>';
        return;
    }

    // Fallback/Mock agents if list empty (for demo UI)
    const agents = data.agents.length > 0 ? data.agents : [
        { name: "SupervisorAgent", id: "supervisor_001", status: "idle" },
        { name: "TrendFetcherAgent", id: "trend_fetcher_001", status: "working" },
        { name: "ScriptWriterAgent", id: "script_writer_001", status: "error" }
    ];

    agents.forEach(agent => {
        const card = document.createElement('div');
        card.className = 'glass-panel agent-card';
        card.innerHTML = `
            <div class="agent-header">
                <h3>${agent.name}</h3>
                <span class="agent-status status-${agent.status.toLowerCase()}">${agent.status}</span>
            </div>
            <p style="font-size: 0.85rem; color: #aaa; margin-bottom: 15px;">ID: ${agent.id}</p>
            <div class="agent-controls">
                <button onclick="controlAgent('${agent.id}', 'start')" class="btn-small success"><i class="fa fa-play"></i></button>
                <button onclick="controlAgent('${agent.id}', 'pause')" class="btn-small warning"><i class="fa fa-pause"></i></button>
                <button onclick="controlAgent('${agent.id}', 'stop')" class="btn-small danger"><i class="fa fa-stop"></i></button>
            </div>
        `;
        container.appendChild(card);
    });
}

async function loadLogs() {
    const data = await DashboardAPI.getLogs();
    const container = document.getElementById('logs-container');

    if (data && data.logs) {
        container.innerHTML = data.logs.map(log => `
            <div class="log-entry">
                <span class="log-timestamp">[${new Date(log.timestamp).toLocaleTimeString()}]</span>
                <span class="log-${log.level.toLowerCase()}">${log.level}</span>
                <span class="log-source">${log.source}:</span>
                <span class="log-message">${log.message}</span>
            </div>
        `).join('');
        container.scrollTop = container.scrollHeight;
    }
}

async function loadSettings() {
    const data = await DashboardAPI.getConfig();
    if (data) {
        document.getElementById('config-display').innerText = JSON.stringify(data, null, 2);
    }
}

// Global functions for inline HTML events
window.controlAgent = async (id, action) => {
    if (confirm(`Are you sure you want to ${action} agent ${id}?`)) {
        await DashboardAPI.controlAgent(id, action);
        loadAgents(); // Refresh UI
    }
};

function startPolling() {
    if (pollingInterval) clearInterval(pollingInterval);
    pollingInterval = setInterval(() => {
        const activeView = document.querySelector('.view-section.active').id;
        if (activeView === 'view-logs') loadLogs();
        if (activeView === 'view-agents') loadAgents();
        if (activeView === 'view-overview') loadOverview();
    }, 5000);
}
