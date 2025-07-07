// Banking Chatbot JavaScript
class BankingChatbot {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.clearChatBtn = document.getElementById('clearChatBtn');
        this.loadingSpinner = document.getElementById('loadingSpinner');
        
        this.isLoading = false;
        this.messageQueue = [];
        
        this.initializeEventListeners();
        this.loadChatHistory();
    }
    
    initializeEventListeners() {
        // Send button click
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        
        // Enter key press
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Clear chat button
        this.clearChatBtn.addEventListener('click', () => this.clearChat());
        
        // Auto-resize input
        this.messageInput.addEventListener('input', () => this.adjustInputHeight());
    }
    
    adjustInputHeight() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message || this.isLoading) {
            return;
        }
        
        // Clear input
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            this.isLoading = true;
            this.updateSendButton(false);
            
            // Send message to backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Remove typing indicator and add bot response
                this.hideTypingIndicator();
                this.addMessage(data.response, 'bot', data.timestamp);
            } else {
                throw new Error(data.error || 'Failed to send message');
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.showError('Sorry, I encountered an error. Please try again or contact your bank directly.');
        } finally {
            this.isLoading = false;
            this.updateSendButton(true);
        }
    }
    
    addMessage(text, sender, timestamp = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const headerDiv = document.createElement('div');
        headerDiv.className = 'message-header';
        
        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        
        if (sender === 'user') {
            headerDiv.innerHTML = `
                <i class="fas fa-user me-2"></i>
                <strong>You</strong>
                <small class="text-muted ms-2">${this.formatTimestamp(timestamp)}</small>
            `;
            textDiv.innerHTML = `<p>${this.escapeHtml(text)}</p>`;
        } else {
            headerDiv.innerHTML = `
                <i class="fas fa-robot me-2"></i>
                <strong>Banking Assistant</strong>
                <small class="text-muted ms-2">${this.formatTimestamp(timestamp)}</small>
            `;
            textDiv.innerHTML = this.formatBotMessage(text);
        }
        
        contentDiv.appendChild(headerDiv);
        contentDiv.appendChild(textDiv);
        messageDiv.appendChild(contentDiv);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatBotMessage(text) {
        // Convert markdown-like formatting to HTML
        let formatted = this.escapeHtml(text);
        
        // Bold text
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert bullet points to HTML lists
        const lines = formatted.split('\n');
        let inList = false;
        let result = [];
        
        for (let line of lines) {
            const trimmed = line.trim();
            if (trimmed.startsWith('- ') || trimmed.startsWith('• ')) {
                if (!inList) {
                    result.push('<ul>');
                    inList = true;
                }
                result.push(`<li>${trimmed.substring(2)}</li>`);
            } else if (trimmed.match(/^\d+\.\s/)) {
                if (!inList) {
                    result.push('<ol>');
                    inList = true;
                }
                result.push(`<li>${trimmed.replace(/^\d+\.\s/, '')}</li>`);
            } else {
                if (inList) {
                    result.push(result[result.length - 1] === '<ul>' ? '</ul>' : '</ol>');
                    inList = false;
                }
                if (trimmed) {
                    result.push(`<p>${trimmed}</p>`);
                }
            }
        }
        
        if (inList) {
            result.push(result.some(line => line === '<ul>') ? '</ul>' : '</ol>');
        }
        
        return result.join('');
    }
    
    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message';
        typingDiv.id = 'typing-indicator';
        
        typingDiv.innerHTML = `
            <div class="typing-indicator">
                <i class="fas fa-robot me-2"></i>
                <span class="me-2">Banking Assistant is typing</span>
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${this.escapeHtml(message)}
        `;
        
        this.chatMessages.appendChild(errorDiv);
        this.scrollToBottom();
        
        // Remove error message after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
    
    showSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>
            ${this.escapeHtml(message)}
        `;
        
        this.chatMessages.appendChild(successDiv);
        this.scrollToBottom();
        
        // Remove success message after 3 seconds
        setTimeout(() => {
            successDiv.remove();
        }, 3000);
    }
    
    updateSendButton(enabled) {
        this.sendBtn.disabled = !enabled;
        this.messageInput.disabled = !enabled;
        
        if (enabled) {
            this.sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
        } else {
            this.sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        }
    }
    
    async loadChatHistory() {
        try {
            const response = await fetch('/api/history');
            const data = await response.json();
            
            if (response.ok && data.messages) {
                // Clear existing messages except welcome message
                const welcomeMessage = this.chatMessages.querySelector('.message');
                this.chatMessages.innerHTML = '';
                if (welcomeMessage) {
                    this.chatMessages.appendChild(welcomeMessage);
                }
                
                // Add historical messages
                data.messages.forEach(msg => {
                    this.addMessage(msg.message, 'user', msg.timestamp);
                    this.addMessage(msg.response, 'bot', msg.timestamp);
                });
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }
    
    async clearChat() {
        if (!confirm('Are you sure you want to clear the chat history?')) {
            return;
        }
        
        try {
            const response = await fetch('/api/clear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                // Clear chat messages except welcome message
                const welcomeMessage = this.chatMessages.querySelector('.message');
                this.chatMessages.innerHTML = '';
                if (welcomeMessage) {
                    this.chatMessages.appendChild(welcomeMessage);
                }
                
                this.showSuccess('Chat history cleared successfully');
            } else {
                throw new Error('Failed to clear chat history');
            }
        } catch (error) {
            console.error('Error clearing chat:', error);
            this.showError('Failed to clear chat history. Please try again.');
        }
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    formatTimestamp(timestamp) {
        if (!timestamp) {
            return 'Just now';
        }
        
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        
        if (diffMins < 1) {
            return 'Just now';
        } else if (diffMins < 60) {
            return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
        } else if (diffMins < 1440) {
            const hours = Math.floor(diffMins / 60);
            return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        } else {
            return date.toLocaleDateString();
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the chatbot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new BankingChatbot();
});
