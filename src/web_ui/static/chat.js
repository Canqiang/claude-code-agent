// Chat Interface JavaScript

class ChatInterface {
    constructor() {
        this.messages = [];
        this.isConfigured = false;
        this.isProcessing = false;
        this.initializeElements();
        this.attachEventListeners();
        this.checkConfiguration();
    }

    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.settingsBtn = document.getElementById('settingsBtn');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.configBanner = document.getElementById('configBanner');
        this.configIcon = document.getElementById('configIcon');
        this.configMessage = document.getElementById('configMessage');
    }

    attachEventListeners() {
        // Send button
        this.sendBtn.addEventListener('click', () => this.sendMessage());

        // Enter key to send (Shift+Enter for new line)
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => {
            this.autoResizeTextarea();
        });

        // Clear button
        this.clearBtn.addEventListener('click', () => this.clearChat());

        // Settings button
        this.settingsBtn.addEventListener('click', () => this.showSettings());
    }

    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
    }

    async checkConfiguration() {
        try {
            const response = await fetch('/health');
            const data = await response.json();

            this.isConfigured = data.configured;

            // Show configuration banner
            this.configBanner.style.display = 'flex';

            if (data.configured) {
                this.configBanner.className = 'config-banner configured';
                this.configIcon.textContent = '✅';
                this.configMessage.textContent = 'Azure OpenAI configured - Full functionality enabled';
            } else {
                this.configBanner.className = 'config-banner demo-mode';
                this.configIcon.textContent = '⚠️';
                this.configMessage.textContent = 'Demo Mode - Configure .env file to enable real agent functionality';
            }
        } catch (error) {
            console.error('Configuration check failed:', error);
            this.configBanner.style.display = 'flex';
            this.configBanner.className = 'config-banner demo-mode';
            this.configIcon.textContent = '❌';
            this.configMessage.textContent = 'Error: Cannot connect to server';
        }
    }

    async sendMessage() {
        const content = this.messageInput.value.trim();

        if (!content || this.isProcessing) {
            return;
        }

        // Clear input
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';

        // Disable send button
        this.isProcessing = true;
        this.sendBtn.disabled = true;

        // Add user message
        this.addMessage('user', content);

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Get assistant response
            await this.getAssistantResponse(content);
        } catch (error) {
            this.addMessage('assistant', `❌ Error: ${error.message}`);
        } finally {
            // Hide typing indicator
            this.hideTypingIndicator();

            // Re-enable send button
            this.isProcessing = false;
            this.sendBtn.disabled = false;
            this.messageInput.focus();
        }
    }

    addMessage(role, content, status = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;

        const timestamp = new Date().toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });

        const avatar = role === 'user' ? '👤' : '🤖';

        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <div class="message-bubble">${this.formatMessage(content)}</div>
                <div class="message-time">${timestamp}</div>
                ${status ? this.createStatusHTML(status) : ''}
            </div>
        `;

        // Remove welcome message if exists
        const welcomeMessage = this.chatMessages.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();

        // Store message
        this.messages.push({ role, content, timestamp });

        return messageDiv;
    }

    formatMessage(content) {
        // Basic markdown-like formatting
        content = this.escapeHtml(content);

        // Code blocks
        content = content.replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>');

        // Inline code
        content = content.replace(/`([^`]+)`/g, '<code>$1</code>');

        // Bold
        content = content.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

        // Italic
        content = content.replace(/\*([^*]+)\*/g, '<em>$1</em>');

        // Line breaks
        content = content.replace(/\n/g, '<br>');

        return content;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    createStatusHTML(status) {
        return `
            <div class="message-status">
                <span class="status-icon">${status.icon || '📊'}</span>
                <span>${status.text}</span>
                ${status.progress !== undefined ? `
                    <div class="status-progress">
                        <div class="status-progress-bar" style="width: ${status.progress}%"></div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    showTypingIndicator() {
        this.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
    }

    async getAssistantResponse(userMessage) {
        // Build context from recent messages
        const context = this.buildContext();

        if (!this.isConfigured) {
            // Demo mode
            await this.getDemoResponse(userMessage);
        } else {
            // Real mode - use streaming
            await this.getStreamingResponse(userMessage, context);
        }
    }

    async getDemoResponse(userMessage) {
        // Simulate thinking time
        await this.sleep(1000);

        const demoResponse = `I understand you're asking about: "${userMessage}"

⚠️ **Demo Mode Active**: I'm running in demonstration mode because Azure OpenAI credentials are not configured.

To enable full functionality:
1. Copy \`.env.example\` to \`.env\`
2. Add your Azure OpenAI credentials:
   - AZURE_OPENAI_API_KEY
   - AZURE_OPENAI_ENDPOINT
   - AZURE_OPENAI_DEPLOYMENT_NAME
3. Restart the server

**What I can do when configured:**
- 🎯 Plan and execute complex tasks
- 💡 Break down problems into steps
- 🔧 Use tools (file operations, code execution, web search)
- 📊 Evaluate results and learn from experience

Would you like to know more about my capabilities?`;

        this.addMessage('assistant', demoResponse, {
            icon: '✅',
            text: 'Demo response completed'
        });
    }

    async getStreamingResponse(userMessage, context) {
        const assistantMessageDiv = this.addMessage('assistant', '');
        const messageContent = assistantMessageDiv.querySelector('.message-bubble');
        const messageStatusContainer = assistantMessageDiv.querySelector('.message-content');

        let currentStatus = null;
        let fullResponse = '';

        try {
            // Use SSE for streaming
            const encodedGoal = encodeURIComponent(userMessage);
            const eventSource = new EventSource(`/api/stream/${encodedGoal}`);

            eventSource.onmessage = (event) => {
                const data = JSON.parse(event.data);

                if (data.type === 'START') {
                    this.updateStatus(messageStatusContainer, {
                        icon: '🚀',
                        text: 'Starting task...',
                        progress: 0
                    });
                } else if (data.type === 'PLANNING') {
                    this.updateStatus(messageStatusContainer, {
                        icon: '🎯',
                        text: 'Planning approach...',
                        progress: 20
                    });
                } else if (data.type === 'THINKING') {
                    this.updateStatus(messageStatusContainer, {
                        icon: '🤔',
                        text: 'Thinking...',
                        progress: 40
                    });
                } else if (data.type === 'EXECUTION') {
                    this.updateStatus(messageStatusContainer, {
                        icon: '⚙️',
                        text: 'Executing task...',
                        progress: 60
                    });
                } else if (data.type === 'PROGRESS') {
                    this.updateStatus(messageStatusContainer, {
                        icon: '📈',
                        text: data.data.message || 'Processing...',
                        progress: data.data.percentage || 50
                    });
                } else if (data.type === 'COMPLETE') {
                    // Build final response
                    fullResponse = data.data.summary || 'Task completed';

                    if (data.data.demo_mode) {
                        fullResponse = '⚠️ **Demo Mode**: ' + fullResponse;
                    }

                    messageContent.innerHTML = this.formatMessage(fullResponse);

                    this.updateStatus(messageStatusContainer, {
                        icon: '✅',
                        text: `Completed (Score: ${(data.data.score * 100).toFixed(0)}%)`,
                        progress: 100
                    });

                    eventSource.close();
                    this.scrollToBottom();
                } else if (data.type === 'ERROR') {
                    messageContent.innerHTML = this.formatMessage('❌ Error: ' + (data.data.error || 'Unknown error'));
                    this.updateStatus(messageStatusContainer, {
                        icon: '❌',
                        text: 'Task failed'
                    });
                    eventSource.close();
                }

                this.scrollToBottom();
            };

            eventSource.onerror = (error) => {
                console.error('SSE Error:', error);
                if (fullResponse === '') {
                    messageContent.innerHTML = this.formatMessage('❌ Connection error. Please try again.');
                }
                eventSource.close();
            };

        } catch (error) {
            messageContent.innerHTML = this.formatMessage('❌ Error: ' + error.message);
        }
    }

    updateStatus(container, status) {
        let statusDiv = container.querySelector('.message-status');

        if (!statusDiv) {
            statusDiv = document.createElement('div');
            statusDiv.className = 'message-status';
            container.appendChild(statusDiv);
        }

        statusDiv.innerHTML = `
            <span class="status-icon">${status.icon}</span>
            <span>${status.text}</span>
            ${status.progress !== undefined ? `
                <div class="status-progress">
                    <div class="status-progress-bar" style="width: ${status.progress}%"></div>
                </div>
            ` : ''}
        `;
    }

    buildContext() {
        // Get last 5 messages for context
        const recentMessages = this.messages.slice(-5);
        return recentMessages.map(msg => `${msg.role}: ${msg.content}`).join('\n');
    }

    clearChat() {
        if (!confirm('Are you sure you want to clear the chat history?')) {
            return;
        }

        this.messages = [];
        this.chatMessages.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-icon">👋</div>
                <h2>Chat Cleared!</h2>
                <p>Ready to start a new conversation.</p>
                <p class="welcome-prompt">What can I help you with?</p>
            </div>
        `;
    }

    showSettings() {
        alert('Settings panel coming soon!\n\nFor now, configure settings in the .env file.');
    }

    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize chat when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new ChatInterface();
});
