/**
 * Real-time synchronization system for enhanced timetable system
 * Provides automatic updates across admin, teacher, and student interfaces
 */

class RealtimeSync {
    constructor() {
        this.isActive = false;
        this.pollInterval = 10000; // 10 seconds
        this.intervalId = null;
        this.lastUpdateCheck = null;
        this.currentUser = null;
        this.currentPage = null;
        
        this.initializeSync();
    }
    
    initializeSync() {
        // Detect current page and user type
        this.detectCurrentContext();
        
        // Start polling for updates
        if (this.shouldStartPolling()) {
            this.startPolling();
        }
        
        // Listen for visibility changes to pause/resume sync
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseSync();
            } else {
                this.resumeSync();
            }
        });
        
        // Listen for browser focus/blur events
        window.addEventListener('focus', () => this.resumeSync());
        window.addEventListener('blur', () => this.pauseSync());
    }
    
    detectCurrentContext() {
        // Detect user type from URL or DOM elements
        const pathParts = window.location.pathname.split('/');
        
        if (pathParts.includes('admin')) {
            this.currentUser = 'admin';
        } else if (pathParts.includes('teacher')) {
            this.currentUser = 'teacher';
        } else if (pathParts.includes('student')) {
            this.currentUser = 'student';
        }
        
        // Detect current page
        if (pathParts.includes('timetable')) {
            this.currentPage = 'timetable';
        } else if (pathParts.includes('teachers')) {
            this.currentPage = 'teachers';
        } else if (pathParts.includes('students')) {
            this.currentPage = 'students';
        } else if (pathParts.includes('dashboard')) {
            this.currentPage = 'dashboard';
        } else if (pathParts.includes('announcements')) {
            this.currentPage = 'announcements';
        }
        
        console.log(`RealtimeSync initialized for ${this.currentUser} on ${this.currentPage} page`);
    }
    
    shouldStartPolling() {
        // Only start polling for admin and teacher interfaces
        // Student updates are less critical and can use manual refresh
        return this.currentUser === 'admin' || this.currentUser === 'teacher';
    }
    
    startPolling() {
        if (this.isActive) return;
        
        this.isActive = true;
        this.intervalId = setInterval(() => {
            this.checkForUpdates();
        }, this.pollInterval);
        
        console.log(`Real-time sync started (polling every ${this.pollInterval / 1000}s)`);
        
        // Show sync status indicator
        this.showSyncIndicator('active');
    }
    
    pauseSync() {
        if (!this.isActive) return;
        
        this.isActive = false;
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        
        console.log('Real-time sync paused');
        this.showSyncIndicator('paused');
    }
    
    resumeSync() {
        if (this.isActive) return;
        
        // Perform immediate update check when resuming
        this.checkForUpdates().then(() => {
            this.startPolling();
        });
        
        console.log('Real-time sync resumed');
    }
    
    async checkForUpdates() {
        if (!this.currentUser || this.currentUser === 'student') return;
        
        try {
            const endpoint = this.currentUser === 'teacher' ? '/api/teacher/updates/' : '/api/admin/updates/';
            const response = await fetch(endpoint, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            this.processUpdates(data);
            
            this.lastUpdateCheck = new Date();
            this.showSyncIndicator('active');
            
        } catch (error) {
            console.error('Failed to check for updates:', error);
            this.showSyncIndicator('error');
        }
    }
    
    processUpdates(updates) {
        if (!updates.has_updates) return;
        
        // Process different types of updates based on current page
        switch (this.currentPage) {
            case 'timetable':
                this.handleTimetableUpdates(updates);
                break;
            case 'teachers':
                this.handleTeacherUpdates(updates);
                break;
            case 'students':
                this.handleStudentUpdates(updates);
                break;
            case 'dashboard':
                this.handleDashboardUpdates(updates);
                break;
            case 'announcements':
                this.handleAnnouncementUpdates(updates);
                break;
        }
    }
    
    handleTimetableUpdates(updates) {
        if (updates.timetable_changed) {
            this.showUpdateNotification(
                'Timetable Updated', 
                'The timetable has been modified. Refresh to see changes.',
                () => window.location.reload()
            );
        }
    }
    
    handleTeacherUpdates(updates) {
        if (updates.teachers_changed) {
            this.showUpdateNotification(
                'Teacher Data Updated',
                'Teacher information has been modified. Refresh to see changes.',
                () => window.location.reload()
            );
        }
    }
    
    handleStudentUpdates(updates) {
        if (updates.students_changed) {
            this.showUpdateNotification(
                'Student Data Updated',
                'Student information has been modified. Refresh to see changes.',
                () => window.location.reload()
            );
        }
    }
    
    handleDashboardUpdates(updates) {
        // Update dashboard statistics in real-time without full page reload
        if (updates.stats_changed) {
            this.updateDashboardStats(updates.stats);
        }
        
        if (updates.announcements_changed) {
            this.refreshAnnouncementsList();
        }
    }
    
    handleAnnouncementUpdates(updates) {
        if (updates.announcements_changed) {
            this.showUpdateNotification(
                'New Announcements',
                'New announcements have been posted.',
                () => window.location.reload()
            );
        }
    }
    
    updateDashboardStats(stats) {
        // Update specific dashboard elements without page reload
        Object.keys(stats).forEach(statKey => {
            const element = document.querySelector(`[data-stat="${statKey}"]`);
            if (element) {
                element.textContent = stats[statKey];
                
                // Add visual indication of update
                element.style.animation = 'highlight 1s ease-in-out';
                setTimeout(() => {
                    element.style.animation = '';
                }, 1000);
            }
        });
    }
    
    async refreshAnnouncementsList() {
        try {
            const response = await fetch('/api/announcements/recent/', {
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateAnnouncementsList(data.announcements);
            }
        } catch (error) {
            console.error('Failed to refresh announcements:', error);
        }
    }
    
    updateAnnouncementsList(announcements) {
        const container = document.getElementById('announcementsList');
        if (!container) return;
        
        // Update announcements list with new data
        let html = '';
        announcements.forEach(announcement => {
            html += `
                <div class="announcement-item ${announcement.is_urgent ? 'urgent' : ''}" data-id="${announcement.id}">
                    <div class="announcement-header">
                        <strong>${announcement.title}</strong>
                        <span class="timestamp">${new Date(announcement.created_at).toLocaleDateString()}</span>
                    </div>
                    <div class="announcement-preview">
                        ${announcement.content_preview}
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
        
        // Show notification for new announcements
        this.showUpdateNotification('New Announcements', 'Fresh announcements have been added.');
    }
    
    showSyncIndicator(status) {
        let indicator = document.getElementById('syncIndicator');
        
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'syncIndicator';
            indicator.className = 'sync-indicator';
            document.body.appendChild(indicator);
        }
        
        const statusConfig = {
            active: { color: '#28a745', text: '●', title: 'Real-time sync active' },
            paused: { color: '#ffc107', text: '⏸', title: 'Real-time sync paused' },
            error: { color: '#dc3545', text: '●', title: 'Sync error - retrying...' },
            offline: { color: '#6c757d', text: '●', title: 'Offline - sync unavailable' },
            db_warming: { color: '#fd7e14', text: '●', title: 'Database warming up' }
        };
        
        const config = statusConfig[status] || statusConfig.offline;
        
        indicator.style.color = config.color;
        indicator.textContent = config.text;
        indicator.title = config.title;
        
        // Auto-hide after a delay for non-error states
        if (status !== 'error') {
            setTimeout(() => {
                if (indicator.style.opacity !== '0.3') {
                    indicator.style.opacity = '0.3';
                }
            }, 3000);
        }
    }
    
    showUpdateNotification(title, message, actionCallback = null) {
        // Check if notifications are already disabled by user
        if (localStorage.getItem('disableUpdateNotifications') === 'true') {
            return;
        }
        
        const notification = document.createElement('div');
        notification.className = 'update-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-icon">
                    <i class="fas fa-sync-alt"></i>
                </div>
                <div class="notification-text">
                    <strong>${title}</strong>
                    <p>${message}</p>
                </div>
                <div class="notification-actions">
                    ${actionCallback ? '<button class="btn btn-sm btn-primary" id="refreshBtn">Refresh</button>' : ''}
                    <button class="btn btn-sm btn-secondary" id="dismissBtn">Dismiss</button>
                </div>
            </div>
        `;
        
        // Position notification
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '9999';
        notification.style.maxWidth = '350px';
        
        document.body.appendChild(notification);
        
        // Handle button clicks
        const refreshBtn = notification.querySelector('#refreshBtn');
        const dismissBtn = notification.querySelector('#dismissBtn');
        
        if (refreshBtn && actionCallback) {
            refreshBtn.addEventListener('click', () => {
                actionCallback();
                notification.remove();
            });
        }
        
        dismissBtn.addEventListener('click', () => {
            notification.remove();
        });
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (document.body.contains(notification)) {
                notification.remove();
            }
        }, 10000);
    }
    
    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
    
    // Public methods for manual control
    disable() {
        this.pauseSync();
        localStorage.setItem('disableRealtimeSync', 'true');
        console.log('Real-time sync disabled');
    }
    
    enable() {
        localStorage.removeItem('disableRealtimeSync');
        if (this.shouldStartPolling()) {
            this.startPolling();
        }
        console.log('Real-time sync enabled');
    }
    
    forceUpdate() {
        this.checkForUpdates();
    }

    // DB health check to drive syncIndicator state for DB readiness
    async checkDbHealth() {
        try {
            const res = await fetch('/api/health/db/', { headers: { 'X-CSRFToken': this.getCSRFToken() } });
            if (!res.ok) throw new Error('DB not ready');
            const data = await res.json();
            if (data.ready) {
                this.showSyncIndicator('active');
                return true;
            }
        } catch (e) {
            this.showSyncIndicator('db_warming');
            return false;
        }
    }
}

// Initialize real-time sync when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Check if real-time sync is disabled
    if (localStorage.getItem('disableRealtimeSync') === 'true') {
        console.log('Real-time sync disabled by user preference');
        return;
    }
    
    // Initialize sync system
    window.realtimeSync = new RealtimeSync();
    // Kick a DB health check immediately and every 15s until ready
    (async function pollDb() {
        const ok = await window.realtimeSync.checkDbHealth();
        if (!ok) {
            setTimeout(pollDb, 15000);
        }
    })();
    
    // Add keyboard shortcut for manual refresh (Ctrl+Shift+U)
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.shiftKey && e.key === 'U') {
            e.preventDefault();
            if (window.realtimeSync) {
                window.realtimeSync.forceUpdate();
            }
        }
    });
});

// CSS styles for sync indicator and notifications
const syncStyles = `
.sync-indicator {
    position: fixed;
    top: 10px;
    right: 10px;
    z-index: 9998;
    font-size: 12px;
    opacity: 0.7;
    transition: opacity 0.3s ease;
}

.sync-indicator:hover {
    opacity: 1;
}

.update-notification {
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    animation: slideIn 0.3s ease-out;
}

.notification-content {
    display: flex;
    align-items: flex-start;
    padding: 16px;
    gap: 12px;
}

.notification-icon {
    color: #007bff;
    font-size: 18px;
    margin-top: 2px;
}

.notification-text {
    flex: 1;
}

.notification-text strong {
    display: block;
    margin-bottom: 4px;
    color: #333;
}

.notification-text p {
    margin: 0;
    color: #666;
    font-size: 14px;
    line-height: 1.4;
}

.notification-actions {
    display: flex;
    gap: 8px;
    align-items: center;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes highlight {
    0%, 100% { background-color: transparent; }
    50% { background-color: #fff3cd; }
}

/* Responsive design for mobile */
@media (max-width: 768px) {
    .update-notification {
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        right: 10px !important;
        max-width: none !important;
    }
    
    .notification-content {
        flex-direction: column;
        gap: 8px;
    }
    
    .notification-actions {
        justify-content: flex-end;
        width: 100%;
    }
}
`;

// Inject styles
const styleSheet = document.createElement('style');
styleSheet.textContent = syncStyles;
document.head.appendChild(styleSheet);

console.log('Real-time synchronization system loaded successfully!');
