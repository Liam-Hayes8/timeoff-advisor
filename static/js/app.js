// Workday Time-Off Advisor Web Application JavaScript

class TimeOffAdvisorApp {
    constructor() {
        this.chatMessages = document.getElementById('chat-messages');
        this.queryForm = document.getElementById('query-form');
        this.queryInput = document.getElementById('query-input');
        this.loadingSpinner = document.getElementById('loading-spinner');
        this.suggestionsList = document.getElementById('suggestions-list');
        this.kbInfo = document.getElementById('kb-info');
        
        this.initializeEventListeners();
        this.loadInitialData();
    }
    
    initializeEventListeners() {
        // Handle form submission
        this.queryForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleQuery();
        });
        
        // Handle Enter key in input
        this.queryInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.handleQuery();
            }
        });
        
        // Auto-resize input
        this.queryInput.addEventListener('input', () => {
            this.queryInput.style.height = 'auto';
            this.queryInput.style.height = this.queryInput.scrollHeight + 'px';
        });
    }
    
    async loadInitialData() {
        try {
            // Load suggestions
            await this.loadSuggestions();
            
            // Load knowledge base info
            await this.loadKnowledgeBase();
            
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    }
    
    async loadSuggestions() {
        try {
            const response = await fetch('/api/suggestions');
            const data = await response.json();
            
            if (data.suggestions) {
                this.displaySuggestions(data.suggestions);
            }
        } catch (error) {
            console.error('Error loading suggestions:', error);
        }
    }
    
    async loadKnowledgeBase() {
        try {
            const response = await fetch('/api/knowledge-base');
            const data = await response.json();
            
            if (data.documents || data.policies || data.procedures) {
                this.displayKnowledgeBase(data);
            }
        } catch (error) {
            console.error('Error loading knowledge base:', error);
        }
    }
    
    displaySuggestions(suggestions) {
        this.suggestionsList.innerHTML = '';
        
        suggestions.forEach(suggestion => {
            const suggestionElement = document.createElement('div');
            suggestionElement.className = 'suggestion-item';
            suggestionElement.textContent = suggestion;
            suggestionElement.addEventListener('click', () => {
                this.queryInput.value = suggestion;
                this.handleQuery();
            });
            this.suggestionsList.appendChild(suggestionElement);
        });
    }
    
    displayKnowledgeBase(kbData) {
        this.kbInfo.innerHTML = '';
        
        // Documents
        if (kbData.documents && kbData.documents.length > 0) {
            const documentsSection = document.createElement('div');
            documentsSection.innerHTML = `
                <div class="kb-category">📄 Documents (${kbData.documents.length})</div>
                ${kbData.documents.map(doc => `<div class="kb-item">${doc}</div>`).join('')}
            `;
            this.kbInfo.appendChild(documentsSection);
        }
        
        // Policies
        if (kbData.policies && kbData.policies.length > 0) {
            const policiesSection = document.createElement('div');
            policiesSection.innerHTML = `
                <div class="kb-category">📋 Policies (${kbData.policies.length})</div>
                ${kbData.policies.map(policy => `<div class="kb-item">${policy}</div>`).join('')}
            `;
            this.kbInfo.appendChild(policiesSection);
        }
        
        // Procedures
        if (kbData.procedures && kbData.procedures.length > 0) {
            const proceduresSection = document.createElement('div');
            proceduresSection.innerHTML = `
                <div class="kb-category">⚙️ Procedures (${kbData.procedures.length})</div>
                ${kbData.procedures.map(proc => `<div class="kb-item">${proc}</div>`).join('')}
            `;
            this.kbInfo.appendChild(proceduresSection);
        }
        
        // Data Summary
        if (kbData.data_summary) {
            const dataSection = document.createElement('div');
            dataSection.innerHTML = `
                <div class="kb-category">📊 Data Summary</div>
                <div class="kb-item">Employees: ${kbData.data_summary.total_employees || 0}</div>
                <div class="kb-item">Avg PTO: ${kbData.data_summary.average_pto ? kbData.data_summary.average_pto.toFixed(1) : 0} days</div>
                <div class="kb-item">Requests: ${kbData.data_summary.total_requests || 0}</div>
            `;
            this.kbInfo.appendChild(dataSection);
        }
    }
    
    async handleQuery() {
        const query = this.queryInput.value.trim();
        
        if (!query) {
            return;
        }
        
        // Add user message to chat
        this.addMessage(query, 'user');
        
        // Clear input
        this.queryInput.value = '';
        this.queryInput.style.height = 'auto';
        
        // Show loading
        this.showLoading();
        
        try {
            // Send query to API
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            });
            
            const data = await response.json();
            
            if (data.error) {
                this.addMessage(`Error: ${data.error}`, 'bot');
            } else {
                // Add bot response
                this.addMessage(data.response, 'bot');
                
                // Update suggestions if provided
                if (data.suggestions && data.suggestions.length > 0) {
                    this.displaySuggestions(data.suggestions);
                }
            }
            
        } catch (error) {
            console.error('Error sending query:', error);
            this.addMessage('Sorry, I encountered an error while processing your request. Please try again.', 'bot');
        } finally {
            this.hideLoading();
        }
    }
    
    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const icon = document.createElement('i');
        icon.className = sender === 'user' ? 'fas fa-user' : 'fas fa-robot';
        
        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        
        // Format the text (preserve line breaks and lists)
        const formattedText = this.formatMessage(text);
        messageText.innerHTML = formattedText;
        
        messageContent.appendChild(icon);
        messageContent.appendChild(messageText);
        messageDiv.appendChild(messageContent);
        
        this.chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        this.scrollToBottom();
    }
    
    formatMessage(text) {
        // Convert line breaks to <br> tags
        let formatted = text.replace(/\n/g, '<br>');
        
        // Convert bullet points to HTML lists
        formatted = formatted.replace(/^•\s*(.+)$/gm, '<li>$1</li>');
        formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        
        // Convert numbered lists
        formatted = formatted.replace(/^\d+\.\s*(.+)$/gm, '<li>$1</li>');
        formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        
        // Add styling to specific patterns
        formatted = formatted.replace(/📊/g, '<span style="color: #007bff;">📊</span>');
        formatted = formatted.replace(/👥/g, '<span style="color: #28a745;">👥</span>');
        formatted = formatted.replace(/📄/g, '<span style="color: #17a2b8;">📄</span>');
        formatted = formatted.replace(/📋/g, '<span style="color: #ffc107;">📋</span>');
        formatted = formatted.replace(/⚙️/g, '<span style="color: #6c757d;">⚙️</span>');
        
        return formatted;
    }
    
    showLoading() {
        this.loadingSpinner.style.display = 'flex';
    }
    
    hideLoading() {
        this.loadingSpinner.style.display = 'none';
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    // Utility function to show typing indicator
    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-indicator';
        typingDiv.id = 'typing-indicator';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const icon = document.createElement('i');
        icon.className = 'fas fa-robot';
        
        const typingDots = document.createElement('div');
        typingDots.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        
        messageContent.appendChild(icon);
        messageContent.appendChild(typingDots);
        typingDiv.appendChild(messageContent);
        
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new TimeOffAdvisorApp();
});

// Add some utility functions for better UX
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Auto-resize textarea functionality
function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

// Add smooth scrolling
function smoothScrollTo(element, duration = 300) {
    const targetPosition = element.offsetTop;
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition;
    let startTime = null;

    function animation(currentTime) {
        if (startTime === null) startTime = currentTime;
        const timeElapsed = currentTime - startTime;
        const run = ease(timeElapsed, startPosition, distance, duration);
        window.scrollTo(0, run);
        if (timeElapsed < duration) requestAnimationFrame(animation);
    }

    function ease(t, b, c, d) {
        t /= d / 2;
        if (t < 1) return c / 2 * t * t + b;
        t--;
        return -c / 2 * (t * (t - 2) - 1) + b;
    }

    requestAnimationFrame(animation);
} 