// Agent Dashboard JavaScript

class AgentDashboard {
    constructor() {
        this.ws = null;
        this.eventSource = null;
        this.isConfigured = false;
        this.initializeElements();
        this.attachEventListeners();
        this.checkConfiguration();
    }

    initializeElements() {
        // Input elements
        this.goalInput = document.getElementById('goalInput');
        this.runButton = document.getElementById('runButton');
        this.streamButton = document.getElementById('streamButton');
        this.collaborateButton = document.getElementById('collaborateButton');
        this.verboseMode = document.getElementById('verboseMode');

        // Status elements
        this.statusSection = document.getElementById('statusSection');
        this.statusMessage = document.getElementById('statusMessage');
        this.progressFill = document.getElementById('progressFill');

        // Stream elements
        this.streamSection = document.getElementById('streamSection');
        this.streamContent = document.getElementById('streamContent');

        // Results elements
        this.resultsSection = document.getElementById('resultsSection');
        this.resultsContent = document.getElementById('resultsContent');

        // Collaboration elements
        this.collaborationSection = document.getElementById('collaborationSection');
        this.collaborationLog = document.getElementById('collaborationLog');
        this.plannerAgent = document.getElementById('plannerAgent');
        this.executorAgent = document.getElementById('executorAgent');
        this.reviewerAgent = document.getElementById('reviewerAgent');

        // Error elements
        this.errorSection = document.getElementById('errorSection');
        this.errorContent = document.getElementById('errorContent');

        // Config banner elements
        this.configBanner = document.getElementById('configBanner');
        this.configIcon = document.getElementById('configIcon');
        this.configMessage = document.getElementById('configMessage');
    }

    attachEventListeners() {
        this.runButton.addEventListener('click', () => this.runTask());
        this.streamButton.addEventListener('click', () => this.streamTask());
        this.collaborateButton.addEventListener('click', () => this.collaborateTask());
    }

    async checkConfiguration() {
        try {
            const response = await fetch('/health');
            const data = await response.json();

            this.isConfigured = data.configured;

            // Show configuration banner
            this.configBanner.style.display = 'block';

            if (data.configured) {
                this.configBanner.className = 'config-banner configured';
                this.configIcon.textContent = '✅';
                this.configMessage.textContent = 'Azure OpenAI configured - Full functionality enabled';
            } else {
                this.configBanner.className = 'config-banner demo-mode';
                this.configIcon.textContent = '⚠️';
                this.configMessage.textContent = 'Demo Mode - Azure OpenAI not configured. Configure .env file to enable real agent functionality.';
            }
        } catch (error) {
            console.error('Configuration check failed:', error);
            this.configBanner.style.display = 'block';
            this.configBanner.className = 'config-banner demo-mode';
            this.configIcon.textContent = '❌';
            this.configMessage.textContent = 'Error checking configuration. Server may not be running.';
        }
    }

    hideAllSections() {
        this.statusSection.style.display = 'none';
        this.streamSection.style.display = 'none';
        this.resultsSection.style.display = 'none';
        this.collaborationSection.style.display = 'none';
        this.errorSection.style.display = 'none';
    }

    showError(errorMessage) {
        this.hideAllSections();
        this.errorSection.style.display = 'block';
        this.errorContent.textContent = errorMessage;
    }

    disableButtons() {
        this.runButton.disabled = true;
        this.streamButton.disabled = true;
        this.collaborateButton.disabled = true;
    }

    enableButtons() {
        this.runButton.disabled = false;
        this.streamButton.disabled = false;
        this.collaborateButton.disabled = false;
    }

    // Regular API call (no streaming)
    async runTask() {
        const goal = this.goalInput.value.trim();
        if (!goal) {
            alert('Please enter a task goal');
            return;
        }

        this.hideAllSections();
        this.statusSection.style.display = 'block';
        this.disableButtons();

        try {
            this.updateStatus('Initializing agent...', 10);

            const response = await fetch('/api/run', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    goal: goal,
                    config: null,
                    use_collaboration: false
                })
            });

            const data = await response.json();

            this.updateStatus('Task completed', 100);

            setTimeout(() => {
                this.displayResults(data);
            }, 500);

        } catch (error) {
            this.showError(`Error: ${error.message}`);
        } finally {
            this.enableButtons();
        }
    }

    // Server-Sent Events streaming
    async streamTask() {
        const goal = this.goalInput.value.trim();
        if (!goal) {
            alert('Please enter a task goal');
            return;
        }

        this.hideAllSections();
        this.streamSection.style.display = 'block';
        this.statusSection.style.display = 'block';
        this.disableButtons();

        // Clear previous stream content
        this.streamContent.innerHTML = '';

        try {
            // Close existing EventSource if any
            if (this.eventSource) {
                this.eventSource.close();
            }

            // Create new EventSource for SSE
            const encodedGoal = encodeURIComponent(goal);
            this.eventSource = new EventSource(`/api/stream/${encodedGoal}`);

            this.eventSource.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleStreamEvent(data);
            };

            this.eventSource.onerror = (error) => {
                console.error('SSE Error:', error);
                this.eventSource.close();
                this.showError('Streaming connection error');
                this.enableButtons();
            };

        } catch (error) {
            this.showError(`Error: ${error.message}`);
            this.enableButtons();
        }
    }

    handleStreamEvent(data) {
        const { type, data: eventData, timestamp } = data;

        // Update progress bar
        if (eventData.percentage !== undefined) {
            this.updateProgress(eventData.percentage);
        }

        // Create stream event element
        const eventElement = document.createElement('div');
        eventElement.className = `stream-event ${type.toLowerCase()}`;

        const typeLabel = document.createElement('div');
        typeLabel.className = 'stream-event-type';
        typeLabel.textContent = type;

        const content = document.createElement('div');
        content.textContent = this.formatEventData(eventData);

        eventElement.appendChild(typeLabel);
        eventElement.appendChild(content);

        this.streamContent.appendChild(eventElement);
        this.streamContent.scrollTop = this.streamContent.scrollHeight;

        // Update status message
        if (eventData.message) {
            this.updateStatus(eventData.message, eventData.percentage || 0);
        }

        // Handle completion
        if (type === 'COMPLETE') {
            this.eventSource.close();
            this.enableButtons();
            setTimeout(() => {
                this.displayResults(eventData);
            }, 500);
        }

        // Handle errors
        if (type === 'ERROR') {
            this.eventSource.close();
            this.showError(eventData.error || 'Unknown error occurred');
            this.enableButtons();
        }
    }

    formatEventData(data) {
        if (typeof data === 'string') {
            return data;
        }

        if (data.message) {
            return data.message;
        }

        return JSON.stringify(data, null, 2);
    }

    // WebSocket for multi-agent collaboration
    async collaborateTask() {
        const goal = this.goalInput.value.trim();
        if (!goal) {
            alert('Please enter a task goal');
            return;
        }

        this.hideAllSections();
        this.collaborationSection.style.display = 'block';
        this.statusSection.style.display = 'block';
        this.disableButtons();

        // Clear previous collaboration log
        this.collaborationLog.innerHTML = '';
        this.resetAgentStatus();

        try {
            // Use REST API for collaboration
            this.updateStatus('Starting multi-agent collaboration...', 10);

            const response = await fetch(`/api/collaboration/run?goal=${encodeURIComponent(goal)}`);
            const data = await response.json();

            if (data.success) {
                this.updateStatus('Collaboration completed', 100);
                this.displayCollaborationResults(data.result);
            } else {
                this.showError(data.error || 'Collaboration failed');
            }

        } catch (error) {
            this.showError(`Error: ${error.message}`);
        } finally {
            this.enableButtons();
        }
    }

    resetAgentStatus() {
        this.plannerAgent.classList.remove('active');
        this.executorAgent.classList.remove('active');
        this.reviewerAgent.classList.remove('active');

        this.plannerAgent.querySelector('.agent-status-text').textContent = 'Idle';
        this.executorAgent.querySelector('.agent-status-text').textContent = 'Idle';
        this.reviewerAgent.querySelector('.agent-status-text').textContent = 'Idle';
    }

    updateAgentStatus(agentName, status, active = false) {
        const agentMap = {
            'planner': this.plannerAgent,
            'executor': this.executorAgent,
            'reviewer': this.reviewerAgent
        };

        const agentElement = agentMap[agentName];
        if (!agentElement) return;

        // Reset all agents first
        Object.values(agentMap).forEach(agent => agent.classList.remove('active'));

        // Set active agent
        if (active) {
            agentElement.classList.add('active');
        }

        // Update status text
        agentElement.querySelector('.agent-status-text').textContent = status;
    }

    addCollaborationMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'collaboration-message';

        const senderElement = document.createElement('div');
        senderElement.className = 'message-sender';
        senderElement.textContent = sender;

        const contentElement = document.createElement('div');
        contentElement.className = 'message-content';
        contentElement.textContent = message;

        messageElement.appendChild(senderElement);
        messageElement.appendChild(contentElement);

        this.collaborationLog.appendChild(messageElement);
        this.collaborationLog.scrollTop = this.collaborationLog.scrollHeight;
    }

    displayCollaborationResults(result) {
        // Update final agent statuses
        this.updateAgentStatus('planner', 'Completed');
        this.updateAgentStatus('executor', 'Completed');
        this.updateAgentStatus('reviewer', 'Completed');

        // Add final result message
        this.addCollaborationMessage('System', 'Collaboration completed successfully');
        this.addCollaborationMessage('Result', JSON.stringify(result, null, 2));
    }

    updateStatus(message, percentage) {
        this.statusMessage.textContent = message;
        this.updateProgress(percentage);
    }

    updateProgress(percentage) {
        this.progressFill.style.width = `${percentage}%`;
    }

    displayResults(data) {
        this.hideAllSections();
        this.resultsSection.style.display = 'block';

        let html = '';

        // Demo mode indicator
        if (data.demo_mode) {
            html += `<div class="result-item" style="background-color: #fef3c7; border-left-color: #f59e0b;">`;
            html += `<div class="result-label">⚠️ Demo Mode</div>`;
            html += `<div class="result-value">This is a simulated response. Configure Azure OpenAI in .env file for real functionality.</div>`;
            html += `</div>`;
        }

        // Success status
        html += `<div class="result-item ${data.success ? '' : 'failed'}">`;
        html += `<div class="result-label">Status</div>`;
        html += `<div class="result-value">${data.success ? '✅ Success' : '❌ Failed'}</div>`;
        html += `</div>`;

        // Score
        if (data.score !== undefined) {
            const scoreClass = data.score >= 0.8 ? 'high' : data.score >= 0.5 ? 'medium' : 'low';
            html += `<div class="result-item">`;
            html += `<div class="result-label">Score</div>`;
            html += `<div class="result-value"><span class="score ${scoreClass}">${(data.score * 100).toFixed(1)}%</span></div>`;
            html += `</div>`;
        }

        // Summary
        if (data.summary) {
            html += `<div class="result-item">`;
            html += `<div class="result-label">Summary</div>`;
            html += `<div class="result-value">${data.summary}</div>`;
            html += `</div>`;
        }

        // Evaluation details
        if (data.evaluation) {
            const eval = data.evaluation;

            if (eval.strengths && eval.strengths.length > 0) {
                html += `<div class="result-item">`;
                html += `<div class="result-label">Strengths</div>`;
                html += `<ul>`;
                eval.strengths.forEach(strength => {
                    html += `<li>${strength}</li>`;
                });
                html += `</ul>`;
                html += `</div>`;
            }

            if (eval.weaknesses && eval.weaknesses.length > 0) {
                html += `<div class="result-item">`;
                html += `<div class="result-label">Weaknesses</div>`;
                html += `<ul>`;
                eval.weaknesses.forEach(weakness => {
                    html += `<li>${weakness}</li>`;
                });
                html += `</ul>`;
                html += `</div>`;
            }

            if (eval.lessons_learned && eval.lessons_learned.length > 0) {
                html += `<div class="result-item">`;
                html += `<div class="result-label">Lessons Learned</div>`;
                html += `<ul>`;
                eval.lessons_learned.forEach(lesson => {
                    html += `<li>${lesson}</li>`;
                });
                html += `</ul>`;
                html += `</div>`;
            }
        }

        this.resultsContent.innerHTML = html;
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new AgentDashboard();
});
