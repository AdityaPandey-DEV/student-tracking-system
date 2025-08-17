/**
 * Announcement handlers for AJAX-based operations
 * This script manages viewing, editing, and deleting announcements
 */

// View announcement details in modal
function viewAnnouncement(announcementId) {
    const modal = new bootstrap.Modal(document.getElementById('viewModal'));
    document.getElementById('viewContent').innerHTML = 
        '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>';
    modal.show();
    
    // Fetch announcement details using AJAX
    fetch(`/api/announcements/${announcementId}/`)
        .then(response => response.json())
        .then(data => {
            // Update modal content with announcement details
            let html = `
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5>${data.title}</h5>
                        <span class="badge ${data.is_urgent ? 'bg-danger' : 'bg-info'}">${data.is_urgent ? 'Urgent' : 'Standard'}</span>
                    </div>
                    <div class="card-body">
                        <p>${data.content}</p>
                        <hr>
                        <div class="row">
                            <div class="col-md-6">
                                <small class="text-muted">
                                    <i class="fas fa-users me-1"></i> Audience: <strong>${data.target_audience_display}</strong>
                                </small>
                                ${data.target_course ? `<br><small class="text-muted">Course: ${data.target_course}</small>` : ''}
                                ${data.target_year ? `<br><small class="text-muted">Year: ${data.target_year}</small>` : ''}
                                ${data.target_section ? `<br><small class="text-muted">Section: ${data.target_section}</small>` : ''}
                            </div>
                            <div class="col-md-6 text-end">
                                <small class="text-muted">
                                    <i class="fas fa-calendar-alt me-1"></i> Posted: ${new Date(data.created_at).toLocaleString()}
                                </small>
                                <br>
                                <small class="text-muted">
                                    <i class="fas fa-user me-1"></i> By: ${data.posted_by_name}
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.getElementById('viewContent').innerHTML = html;
        })
        .catch(error => {
            document.getElementById('viewContent').innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Error loading announcement details. Please try again.
                </div>
            `;
            console.error('Error:', error);
        });
}

// Edit announcement 
function editAnnouncement(announcementId) {
    // Redirect to edit page or show edit form in modal
    window.location.href = `/admin/announcements/edit/${announcementId}/`;
}

// Delete announcement with confirmation
function deleteAnnouncement(announcementId) {
    if (confirm('Are you sure you want to delete this announcement? This action cannot be undone.')) {
        // Send AJAX request to delete endpoint
        fetch(`/api/announcements/${announcementId}/delete/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove announcement from DOM
                const row = document.querySelector(`tr[data-announcement-id="${announcementId}"]`);
                if (row) {
                    row.remove();
                }
                // Show success message
                showToast('Announcement deleted successfully', 'success');
            } else {
                showToast('Failed to delete announcement: ' + data.message, 'error');
            }
        })
        .catch(error => {
            showToast('Error deleting announcement', 'error');
            console.error('Error:', error);
        });
    }
}

// Filter announcements
function filterAnnouncements(filter) {
    const rows = document.querySelectorAll('.announcement-row');
    const now = new Date();
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    
    rows.forEach(row => {
        let show = true;
        
        if (filter === 'urgent') {
            show = row.dataset.urgent === 'true';
        } else if (filter === 'recent') {
            const created = new Date(row.dataset.created);
            show = created > weekAgo;
        }
        
        row.style.display = show ? '' : 'none';
    });
    
    // Update button states
    document.querySelectorAll('[onclick^="filterAnnouncements"]').forEach(btn => {
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-outline-secondary');
    });
    event.target.classList.remove('btn-outline-secondary');
    event.target.classList.add('btn-primary');
}

// Preview announcement
function previewAnnouncement() {
    const title = document.getElementById('title').value || 'Title will appear here';
    const content = document.getElementById('content').value || 'Content will appear here';
    const audience = document.getElementById('target_audience').value;
    const isUrgent = document.getElementById('is_urgent').checked;
    
    // Update preview content
    document.getElementById('previewTitle').textContent = title;
    document.getElementById('previewContent').textContent = content;
    
    // Update audience badge
    const audienceTexts = {
        'all': 'All Students',
        'course': 'Specific Course',
        'year': 'Specific Year',
        'section': 'Specific Section'
    };
    document.getElementById('audienceBadge').textContent = audienceTexts[audience];
    
    // Show/hide urgent badge
    const urgentBadge = document.getElementById('urgentBadge');
    urgentBadge.style.display = isUrgent ? 'inline' : 'none';
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('previewModal'));
    modal.show();
}

// Submit announcement form
function submitForm() {
    document.querySelector('form').submit();
}

// Toast notifications
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Show toast
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 3000
    });
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}
