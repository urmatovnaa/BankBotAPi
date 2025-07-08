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
        this.enableChatIfAuthorized();
    }

    enableChatIfAuthorized() {
        fetch('/api/history', {credentials: 'include'})
            .then(r => {
                if (r.ok) {
                    this.messageInput.disabled = false;
                    this.sendBtn.disabled = false;
                    this.clearChatBtn.disabled = false;
                    this.messageInput.placeholder = "Банк суроонузду бул жерге жазыңыз...";
                    this.showWelcomeMessage();
                    this.loadChatHistory();
                } else {
                    this.messageInput.disabled = true;
                    this.sendBtn.disabled = true;
                    this.clearChatBtn.disabled = true;
                    this.messageInput.placeholder = "Кирүү же катталуу талап кылынат";
                }
            });
    }

    showWelcomeMessage() {
        const welcomeText = `\
Банк Жардамчысына кош келиңиз! 👋\n\nМен сизге жалпы банк суроолору, биздин кызматтар жана жеке банк эсебиңиз тууралуу маалымат бере алам.\n\nМен төмөнкүлөр боюнча жардам бере алам:\n• Эсептериңиздин тизмеси жана балансы\n• Акыркы транзакцияларыңыз\n• Кимге жана канча акча которгонсуз\n• Банк кызматтары жана процедуралары\n• Каржы сабаттуулугу жана коопсуздук\n• Акча которуу ассистенти катары иштейм (мисалы, \"100 сомду Бакытка котор\" ж.б.)\n\nЖеке суроолорду да бере аласыз: мисалы, \"Канча акча бар?\", \"Акыркы транзакцияларымды көрсөт\", \"Кимге акыркы жолу котордум?\" ж.б.\n\nЭскертүү: Купуя маалыматты (сыр сөз, PIN) эч качан бөлүшпөңүз!`;
        this.addMessage(welcomeText, 'bot');
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
        
        // Setup analytics modal
        this.setupAnalyticsModal();
        
        // Add event listeners for login and register buttons
        const loginBtn = document.getElementById('loginBtn');
        const registerBtn = document.getElementById('registerBtn');
        if (loginBtn) {
            loginBtn.addEventListener('click', () => {
                const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
                loginModal.show();
            });
        }
        if (registerBtn) {
            registerBtn.addEventListener('click', () => {
                const registerModal = new bootstrap.Modal(document.getElementById('registerModal'));
                registerModal.show();
            });
        }

        // Handle login form submit
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = document.getElementById('loginEmail').value.trim();
                const password = document.getElementById('loginPassword').value;
                const errorDiv = document.getElementById('loginError');
                errorDiv.style.display = 'none';
                try {
                    const response = await fetch('/api/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify({ email, password })
                    });
                    const data = await response.json();
                    if (response.ok) {
                        bootstrap.Modal.getInstance(document.getElementById('loginModal')).hide();
                        location.reload();
                    } else {
                        errorDiv.textContent = data.error || 'Кирүү катасы';
                        errorDiv.style.display = 'block';
                    }
                } catch (err) {
                    errorDiv.textContent = 'Сервер катасы';
                    errorDiv.style.display = 'block';
                }
            });
        }

        // Handle register form submit
        const registerForm = document.getElementById('registerForm');
        if (registerForm) {
            registerForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = document.getElementById('registerEmail').value.trim();
                const password = document.getElementById('registerPassword').value;
                const errorDiv = document.getElementById('registerError');
                errorDiv.style.display = 'none';
                try {
                    const response = await fetch('/api/register', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify({ email, password })
                    });
                    const data = await response.json();
                    if (response.ok) {
                        bootstrap.Modal.getInstance(document.getElementById('registerModal')).hide();
                        alert('Катталуу ийгиликтүү! Эми кире аласыз.');
                    } else {
                        errorDiv.textContent = data.error || 'Катталуу катасы';
                        errorDiv.style.display = 'block';
                    }
                } catch (err) {
                    errorDiv.textContent = 'Сервер катасы';
                    errorDiv.style.display = 'block';
                }
            });
        }

        // Показывать/скрывать кнопки в зависимости от статуса
        function updateAuthButtons() {
            const logoutBtn = document.getElementById('logoutBtn');
            const loginBtn = document.getElementById('loginBtn');
            const registerBtn = document.getElementById('registerBtn');
            fetch('/api/history', {credentials: 'include'})
                .then(r => {
                    if (r.ok) {
                        logoutBtn.classList.remove('d-none');
                        loginBtn.classList.add('d-none');
                        registerBtn.classList.add('d-none');
                    } else {
                        logoutBtn.classList.add('d-none');
                        loginBtn.classList.remove('d-none');
                        registerBtn.classList.remove('d-none');
                    }
                });
        }
        updateAuthButtons();

        // Обработчик выхода
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', async () => {
                try {
                    const response = await fetch('/api/logout', {
                        method: 'POST',
                        credentials: 'include'
                    });
                    if (response.ok) {
                        location.reload();
                    }
                } catch (err) {
                    alert('Logout error');
                }
            });
        }
    }
    
    adjustInputHeight() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isLoading || this.messageInput.disabled) {
            return;
        }
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        this.addMessage(message, 'user');
        this.showTypingIndicator();
        try {
            this.isLoading = true;
            this.updateSendButton(false);
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({ message: message })
            });
            const data = await response.json();
            if (response.ok) {
                this.hideTypingIndicator();
                this.addMessage(data.response, 'bot', data.timestamp, data.message_id, data.category);
            } else {
                if (response.status === 401) {
                    this.hideTypingIndicator();
                    this.showError('Кирүү же катталуу талап кылынат.');
                } else {
                    throw new Error(data.error || 'Failed to send message');
                }
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.showError('Кечиресиз, ката кетти. Кайра аракет кылыңыз же банкка түздөн-түз кайрылыңыз.');
        } finally {
            this.isLoading = false;
            this.updateSendButton(true);
        }
    }
    
    addMessage(text, sender, timestamp = null, messageId = null, category = null, feedback = null) {
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
                <strong>Сиз</strong>
                <small class="text-muted ms-2">${this.formatTimestamp(timestamp)}</small>
            `;
            textDiv.innerHTML = `<p>${this.escapeHtml(text)}</p>`;
        } else {
            headerDiv.innerHTML = `
                <i class="fas fa-robot me-2"></i>
                <strong>Банк Жардамчысы</strong>
                <small class="text-muted ms-2">${this.formatTimestamp(timestamp)}</small>
                ${category ? `<span class="badge bg-secondary ms-2">${category}</span>` : ''}
            `;
            textDiv.innerHTML = this.formatBotMessage(text);
            
            // Add feedback section for bot messages
            if (messageId) {
                const feedbackDiv = document.createElement('div');
                feedbackDiv.className = 'message-feedback mt-2';
                feedbackDiv.innerHTML = this.createFeedbackSection(messageId, feedback);
                contentDiv.appendChild(feedbackDiv);
            }
        }
        
        contentDiv.appendChild(headerDiv);
        contentDiv.appendChild(textDiv);
        messageDiv.appendChild(contentDiv);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    createFeedbackSection(messageId, existingFeedback = null) {
        const hasExistingFeedback = existingFeedback && existingFeedback.rating;
        const currentRating = hasExistingFeedback ? existingFeedback.rating : 0;
        const isHelpful = hasExistingFeedback ? existingFeedback.is_helpful : null;
        
        return `
            <div class="feedback-section">
                <div class="feedback-question">
                    <small class="text-muted">Was this response helpful?</small>
                </div>
                <div class="feedback-controls mt-1">
                    <div class="rating-stars" data-message-id="${messageId}">
                        ${[1, 2, 3, 4, 5].map(star => `
                            <i class="fas fa-star rating-star ${star <= currentRating ? 'active' : ''}" 
                               data-rating="${star}" 
                               onclick="chatBot.submitRating(${messageId}, ${star})"></i>
                        `).join('')}
                    </div>
                    <div class="helpful-buttons ms-3">
                        <button class="btn btn-sm btn-outline-success ${isHelpful === true ? 'active' : ''}" 
                                onclick="chatBot.submitHelpful(${messageId}, true)">
                            <i class="fas fa-thumbs-up"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger ms-1 ${isHelpful === false ? 'active' : ''}" 
                                onclick="chatBot.submitHelpful(${messageId}, false)">
                            <i class="fas fa-thumbs-down"></i>
                        </button>
                    </div>
                </div>
                ${hasExistingFeedback && existingFeedback.comment ? `
                    <div class="feedback-comment mt-2">
                        <small class="text-muted">Your feedback: "${existingFeedback.comment}"</small>
                    </div>
                ` : ''}
            </div>
        `;
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
                <span class="me-2">Банк Жардамчысы жазууда</span>
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
            const response = await fetch('/api/history', {
                credentials: 'include'
            });
            if (response.ok) {
                const data = await response.json();
                this.chatMessages.innerHTML = '';
                data.messages.forEach(msg => {
                    this.addMessage(msg.message, 'user', msg.timestamp);
                    this.addMessage(msg.response, 'bot', msg.timestamp, msg.id, msg.category, msg.feedback);
                });
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }
    
    async clearChat() {
        if (!confirm('Маек тарыхын тазалоону каалайсызбы?')) {
            return;
        }
        
        try {
            const response = await fetch('/api/clear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include'
            });
            
            if (response.ok) {
                // Clear chat messages except welcome message
                const welcomeMessage = this.chatMessages.querySelector('.message');
                this.chatMessages.innerHTML = '';
                if (welcomeMessage) {
                    this.chatMessages.appendChild(welcomeMessage);
                }
                
                this.showSuccess('Маек тарыхы ийгиликтүү тазаланды');
            } else if (response.status === 401) {
                this.showError('Сессиянын мөөнөтү бүттү. Барактыды кайра жүктөңүз.');
            } else {
                throw new Error('Failed to clear chat history');
            }
        } catch (error) {
            console.error('Error clearing chat:', error);
            this.showError('Маек тарыхын тазалоо оңунан чыкпады. Кайра аракет кылыңыз.');
        }
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    formatTimestamp(timestamp) {
        if (!timestamp) {
            return 'Азыр эле';
        }
        
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        
        if (diffMins < 1) {
            return 'Азыр эле';
        } else if (diffMins < 60) {
            return `${diffMins} мүнөт мурун`;
        } else if (diffMins < 1440) {
            const hours = Math.floor(diffMins / 60);
            return `${hours} саат мурун`;
        } else {
            return date.toLocaleDateString();
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    async submitRating(messageId, rating) {
        try {
            const response = await fetch('/api/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({ 
                    message_id: messageId, 
                    rating: rating 
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Update the star display
                const ratingStars = document.querySelector(`[data-message-id="${messageId}"]`);
                if (ratingStars) {
                    const stars = ratingStars.querySelectorAll('.rating-star');
                    stars.forEach((star, index) => {
                        if (index < rating) {
                            star.classList.add('active');
                        } else {
                            star.classList.remove('active');
                        }
                    });
                }
                
                this.showSuccess('Пикириңиз үчүн рахмат!');
            } else {
                throw new Error(data.error || 'Failed to submit rating');
            }
        } catch (error) {
            console.error('Error submitting rating:', error);
            this.showError('Баа берүү оңунан чыкпады. Кайра аракет кылыңыз.');
        }
    }
    
    async submitHelpful(messageId, isHelpful) {
        try {
            const response = await fetch('/api/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({ 
                    message_id: messageId, 
                    is_helpful: isHelpful,
                    rating: 3 // Default rating if not provided
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Update the button states
                const feedbackSection = document.querySelector(`[data-message-id="${messageId}"]`).closest('.feedback-section');
                const buttons = feedbackSection.querySelectorAll('.helpful-buttons button');
                buttons.forEach(button => button.classList.remove('active'));
                
                // Activate the clicked button
                const clickedButton = feedbackSection.querySelector(`button[onclick*="${isHelpful}"]`);
                if (clickedButton) {
                    clickedButton.classList.add('active');
                }
                
                this.showSuccess('Пикириңиз үчүн рахмат!');
            } else {
                throw new Error(data.error || 'Failed to submit feedback');
            }
        } catch (error) {
            console.error('Error submitting feedback:', error);
            this.showError('Пикир жөнөтүү оңунан чыкпады. Кайра аракет кылыңыз.');
        }
    }
    
    setupAnalyticsModal() {
        // Load analytics when the modal is shown
        const analyticsModal = document.getElementById('analyticsModal');
        if (analyticsModal) {
            analyticsModal.addEventListener('show.bs.modal', () => {
                this.loadAnalytics();
            });
        }
    }
    
    async loadAnalytics() {
        try {
            const response = await fetch('/api/analytics', {
                credentials: 'include'
            });
            const data = await response.json();
            
            if (response.ok) {
                // Update feedback statistics
                const feedbackStats = data.feedback_stats;
                document.getElementById('avgRating').textContent = feedbackStats.average_rating ? feedbackStats.average_rating.toFixed(1) : '0.0';
                document.getElementById('totalFeedback').textContent = feedbackStats.total_feedback || 0;
                
                const helpfulPercentage = feedbackStats.total_feedback > 0 
                    ? Math.round((feedbackStats.helpful_count / feedbackStats.total_feedback) * 100)
                    : 0;
                document.getElementById('helpfulPercentage').textContent = helpfulPercentage;
                
                // Update category statistics
                const categoryStats = data.category_stats;
                const totalQuestions = categoryStats.reduce((sum, cat) => sum + cat.count, 0);
                
                const categoryTable = document.getElementById('categoryStats');
                categoryTable.innerHTML = '';
                
                if (!categoryStats || categoryStats.length === 0) {
                    categoryTable.innerHTML = '<tr><td colspan="3" class="text-center">No data available yet</td></tr>';
                } else {
                    categoryStats.forEach(stat => {
                        const percentage = totalQuestions > 0 ? Math.round((stat.count / totalQuestions) * 100) : 0;
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${stat.category || 'Unknown'}</td>
                            <td>${stat.count || 0}</td>
                            <td>${percentage}%</td>
                        `;
                        categoryTable.appendChild(row);
                    });
                }
            } else {
                throw new Error(data.error || 'Failed to load analytics');
            }
        } catch (error) {
            console.error('Error loading analytics:', error);
            
            // Set default values for feedback stats
            document.getElementById('avgRating').textContent = '0.0';
            document.getElementById('totalFeedback').textContent = '0';
            document.getElementById('helpfulPercentage').textContent = '0';
            
            // Show error message in category table
            document.getElementById('categoryStats').innerHTML = 
                '<tr><td colspan="3" class="text-center text-danger">Error loading analytics</td></tr>';
        }
    }
}

// Initialize the chatbot when the page loads
let chatBot;
document.addEventListener('DOMContentLoaded', () => {
    chatBot = new BankingChatbot();
});
