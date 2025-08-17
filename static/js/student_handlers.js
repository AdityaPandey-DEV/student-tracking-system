/**
 * Student dashboard and interactive functionality handlers
 * This script manages AI chat, search, and recommendation features
 */

// AI Chat functionality
class StudentAIChat {
    constructor() {
        this.currentSessionId = 'session_' + Date.now();
        this.isWaitingForResponse = false;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');

        if (messageInput) {
            // Enter key support
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });

            // Auto-resize textarea
            messageInput.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = (this.scrollHeight) + 'px';
            });
        }

        if (sendButton) {
            sendButton.addEventListener('click', () => this.sendMessage());
        }
    }

    // Send message to AI chat
    sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message || this.isWaitingForResponse) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Clear input
        messageInput.value = '';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Send to backend
        fetch(window.location.pathname, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                message: message,
                session_id: this.currentSessionId
            })
        })
        .then(response => response.json())
        .then(data => {
            this.hideTypingIndicator();
            if (data.response) {
                this.addMessage(data.response, 'ai');
            } else if (data.error) {
                this.addMessage('Sorry, I encountered an error. Please try again.', 'ai');
            }
        })
        .catch(error => {
            this.hideTypingIndicator();
            this.addMessage('Sorry, I couldn\'t process your request. Please check your connection and try again.', 'ai');
            console.error('Error:', error);
        });
    }

    // Add message to chat interface
    addMessage(text, sender) {
        const chatContainer = document.getElementById('chatContainer');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message ' + (sender === 'user' ? 'user-message' : 'ai-message');
        
        const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        const senderName = sender === 'user' ? 'You' : 'AI Assistant';
        const icon = sender === 'user' ? 'fas fa-user' : 'fas fa-robot';
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-header">
                    <i class="${icon} me-1"></i>
                    <strong>${senderName}</strong>
                    <small class="text-muted ms-2">${time}</small>
                </div>
                <div class="message-text">${text}</div>
            </div>
        `;
        
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Show typing indicator
    showTypingIndicator() {
        this.isWaitingForResponse = true;
        const chatContainer = document.getElementById('chatContainer');
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typingIndicator';
        typingDiv.className = 'message ai-message';
        typingDiv.innerHTML = `
            <div class="message-content">
                <div class="message-header">
                    <i class="fas fa-robot me-1"></i>
                    <strong>AI Assistant</strong>
                    <small class="text-muted ms-2">typing...</small>
                </div>
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        chatContainer.appendChild(typingDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        document.getElementById('sendButton').disabled = true;
    }

    // Hide typing indicator
    hideTypingIndicator() {
        this.isWaitingForResponse = false;
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
        document.getElementById('sendButton').disabled = false;
    }

    // Ask predefined question
    askPredefined(question) {
        document.getElementById('messageInput').value = question;
        this.sendMessage();
    }

    // Clear chat
    clearChat() {
        if (confirm('Are you sure you want to clear the chat?')) {
            const chatContainer = document.getElementById('chatContainer');
            chatContainer.innerHTML = `
                <div class="welcome-message">
                    <div class="message ai-message">
                        <div class="message-content">
                            <div class="message-header">
                                <i class="fas fa-robot me-1"></i>
                                <strong>AI Assistant</strong>
                                <small class="text-muted ms-2">Just now</small>
                            </div>
                            <div class="message-text">
                                Chat cleared! How can I help you today?
                            </div>
                        </div>
                    </div>
                </div>
            `;
            this.currentSessionId = 'session_' + Date.now();
        }
    }

    // Load previous chat
    loadChat(sessionId) {
        // Implementation for loading previous chat session
        alert('Loading chat session: ' + sessionId);
    }
}

// Student search functionality
class StudentSearch {
    constructor() {
        this.initializeSearchHandlers();
    }

    initializeSearchHandlers() {
        // Global search input
        const searchInput = document.getElementById('globalSearch');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(this.performSearch.bind(this), 300));
        }

        // Subject search
        const subjectSearch = document.getElementById('subjectSearch');
        if (subjectSearch) {
            subjectSearch.addEventListener('input', this.debounce(this.searchSubjects.bind(this), 300));
        }
    }

    // Perform global search across content
    performSearch(event) {
        const query = event.target.value.trim();
        
        if (query.length < 2) return;

        // Show loading indicator
        this.showSearchLoading();

        // Fetch search results
        fetch(`/api/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                this.displaySearchResults(data);
            })
            .catch(error => {
                console.error('Search error:', error);
                this.hideSearchLoading();
            });
    }

    // Search subjects specifically
    searchSubjects(event) {
        const query = event.target.value.trim().toLowerCase();
        const subjectCards = document.querySelectorAll('.subject-card');

        subjectCards.forEach(card => {
            const subjectName = card.querySelector('.subject-name').textContent.toLowerCase();
            const subjectCode = card.querySelector('.subject-code').textContent.toLowerCase();
            
            const isVisible = subjectName.includes(query) || subjectCode.includes(query);
            card.style.display = isVisible ? 'block' : 'none';
        });
    }

    // Display search results
    displaySearchResults(results) {
        const resultsContainer = document.getElementById('searchResults');
        if (!resultsContainer) return;

        let html = '<div class="search-results-list">';
        
        if (results.subjects && results.subjects.length > 0) {
            html += '<h6>Subjects</h6>';
            results.subjects.forEach(subject => {
                html += `
                    <div class="search-result-item">
                        <i class="fas fa-book me-2"></i>
                        <strong>${subject.name}</strong> (${subject.code})
                    </div>
                `;
            });
        }

        if (results.announcements && results.announcements.length > 0) {
            html += '<h6>Announcements</h6>';
            results.announcements.forEach(announcement => {
                html += `
                    <div class="search-result-item">
                        <i class="fas fa-bullhorn me-2"></i>
                        <strong>${announcement.title}</strong>
                        <small class="text-muted d-block">${announcement.content_preview}</small>
                    </div>
                `;
            });
        }

        html += '</div>';
        resultsContainer.innerHTML = html;
        this.hideSearchLoading();
    }

    // Show/hide loading indicators
    showSearchLoading() {
        const loader = document.getElementById('searchLoader');
        if (loader) loader.style.display = 'block';
    }

    hideSearchLoading() {
        const loader = document.getElementById('searchLoader');
        if (loader) loader.style.display = 'none';
    }

    // Debounce function to limit API calls
    debounce(func, wait) {
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
}

// Recommendation system
class RecommendationHandler {
    // Generate recommendations
    static generateRecommendations() {
        const button = event.target;
        const originalText = button.innerHTML;
        
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Generating...';

        fetch('/api/recommendations/generate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.reload(); // Reload to show new recommendations
            } else {
                alert('Failed to generate recommendations: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error generating recommendations');
        })
        .finally(() => {
            button.disabled = false;
            button.innerHTML = originalText;
        });
    }

    // Dismiss recommendation
    static dismissRecommendation(recommendationId) {
        const alert = event.target.closest('.alert');
        
        fetch(`/api/recommendations/${recommendationId}/dismiss/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert.remove();
            }
        })
        .catch(error => {
            console.error('Error dismissing recommendation:', error);
        });
    }
}

// Attendance functionality
class AttendanceHandler {
    // View detailed attendance for a subject
    static viewAttendanceDetails(subjectId) {
        window.location.href = `/student/attendance/?subject=${subjectId}`;
    }

    // Generate attendance report
    static generateAttendanceReport() {
        const button = event.target;
        const originalText = button.innerHTML;
        
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Generating...';

        fetch('/api/attendance/report/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.blob())
        .then(blob => {
            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'attendance_report.pdf';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error generating attendance report');
        })
        .finally(() => {
            button.disabled = false;
            button.innerHTML = originalText;
        });
    }
}

// Initialize handlers when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize AI Chat if on chat page
    if (document.getElementById('chatContainer')) {
        window.aiChat = new StudentAIChat();
    }

    // Initialize search functionality
    window.studentSearch = new StudentSearch();

    // Add global functions to window for onclick handlers
    window.askPredefined = function(question) {
        if (window.aiChat) {
            window.aiChat.askPredefined(question);
        }
    };

    window.clearChat = function() {
        if (window.aiChat) {
            window.aiChat.clearChat();
        }
    };

    window.loadChat = function(sessionId) {
        if (window.aiChat) {
            window.aiChat.loadChat(sessionId);
        }
    };

    window.generateRecommendations = RecommendationHandler.generateRecommendations;
    window.dismissRecommendation = RecommendationHandler.dismissRecommendation;
    window.viewAttendanceDetails = AttendanceHandler.viewAttendanceDetails;
    window.generateAttendanceReport = AttendanceHandler.generateAttendanceReport;
});
