const API_BASE = '/api/v1';

export const API = {
    async get(endpoint) {
        try {
            const response = await fetch(`${API_BASE}${endpoint}`);
            if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
            return await response.json();
        } catch (error) {
            console.error("API Get Failed", error);
            return null;
        }
    },

    async post(endpoint, body = {}) {
        try {
            const response = await fetch(`${API_BASE}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
            return await response.json();
        } catch (error) {
            console.error("API Post Failed", error);
            return null;
        }
    }
};

export const DashboardAPI = {
    getOverview: () => API.get('/dashboard/overview'),
    getLogs: () => API.get('/dashboard/logs'),
    getConfig: () => API.get('/dashboard/config'),
    getAgentStatus: () => API.get('/agents/status'),
    controlAgent: (id, action) => API.post(`/dashboard/agents/${id}/control?action=${action}`),
    triggerTask: (type, topic) => API.post(`/dashboard/tasks/manual?task_type=${type}`, { topic })
};
