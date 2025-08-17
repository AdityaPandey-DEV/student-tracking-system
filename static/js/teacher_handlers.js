/**
 * Teacher Dashboard JavaScript Handlers
 * Handles teacher-specific functionality including attendance, materials, and class management
 */

// Attendance Management
class AttendanceManagement {
    
    // Mark attendance for a class
    static markAttendance(classId) {
        const modal = new bootstrap.Modal(document.getElementById('attendanceModal') || createAttendanceModal());
        const modalContent = document.getElementById('attendanceContent');
        
        modalContent.innerHTML = `
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
        
        modal.show();
        
        fetch(`/api/teacher/class/${classId}/students/`, {
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const students = data.students;
                modalContent.innerHTML = `
                    <form id="attendanceForm">
                        <div class="mb-3">
                            <h6><i class="fas fa-calendar-alt me-2"></i>Date: ${new Date().toLocaleDateString()}</h6>
                            <h6><i class="fas fa-book me-2"></i>Subject: ${data.class_info.subject_name}</h6>
                            <h6><i class="fas fa-users me-2"></i>Total Students: ${students.length}</h6>
                        </div>
                        
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <button type="button" class="btn btn-success btn-sm" onclick="markAllPresent()">
                                    <i class="fas fa-check-double me-1"></i>Mark All Present
                                </button>
                            </div>
                            <div class="col-md-6 text-end">
                                <button type="button" class="btn btn-danger btn-sm" onclick="markAllAbsent()">
                                    <i class="fas fa-times me-1"></i>Mark All Absent
                                </button>
                            </div>
                        </div>
                        
                        <div class="attendance-list" style="max-height: 400px; overflow-y: auto;">
                            ${students.map(student => `
                                <div class="card mb-2">
                                    <div class="card-body py-2">
                                        <div class="row align-items-center">
                                            <div class="col-md-6">
                                                <strong>${student.name}</strong><br>
                                                <small class="text-muted">${student.roll_number}</small>
                                            </div>
                                            <div class="col-md-6">
                                                <div class="form-check form-check-inline">
                                                    <input class="form-check-input" type="radio" name="attendance_${student.id}" 
                                                           id="present_${student.id}" value="present" checked>
                                                    <label class="form-check-label text-success" for="present_${student.id}">
                                                        <i class="fas fa-check me-1"></i>Present
                                                    </label>
                                                </div>
                                                <div class="form-check form-check-inline">
                                                    <input class="form-check-input" type="radio" name="attendance_${student.id}" 
                                                           id="absent_${student.id}" value="absent">
                                                    <label class="form-check-label text-danger" for="absent_${student.id}">
                                                        <i class="fas fa-times me-1"></i>Absent
                                                    </label>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        
                        <div class="text-end mt-3">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-save me-1"></i>Save Attendance
                            </button>
                        </div>
                    </form>
                `;
                
                // Handle form submission
                document.getElementById('attendanceForm').addEventListener('submit', function(e) {
                    e.preventDefault();
                    AttendanceManagement.saveAttendance(classId, students);
                });
            }
        });
    }
    
    // Save attendance data
    static saveAttendance(classId, students) {
        const attendanceData = {};
        students.forEach(student => {
            const status = document.querySelector(`input[name="attendance_${student.id}"]:checked`).value;
            attendanceData[student.id] = status;
        });
        
        const submitBtn = document.querySelector('#attendanceForm button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Saving...';
        
        fetch(`/api/teacher/attendance/save/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                class_id: classId,
                date: new Date().toISOString().split('T')[0],
                attendance: attendanceData
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Attendance saved successfully', 'success');
                bootstrap.Modal.getInstance(document.getElementById('attendanceModal')).hide();
            } else {
                showToast('Error saving attendance: ' + data.message, 'error');
            }
        })
        .catch(error => {
            showToast('Error saving attendance', 'error');
            console.error('Error:', error);
        })
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        });
    }
    
    // Generate attendance report
    static generateReport(subjectId) {
        const button = event.target;
        const originalText = button.innerHTML;
        
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Generating...';
        
        fetch(`/api/teacher/attendance/report/${subjectId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `attendance_report_${new Date().toISOString().split('T')[0]}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            showToast('Attendance report generated successfully', 'success');
        })
        .catch(error => {
            showToast('Error generating report', 'error');
            console.error('Error:', error);
        })
        .finally(() => {
            button.disabled = false;
            button.innerHTML = originalText;
        });
    }
}

// Study Materials Management
class MaterialsManagement {
    
    // Upload study material
    static uploadMaterial() {
        const modal = new bootstrap.Modal(document.getElementById('uploadModal') || createUploadModal());
        modal.show();
    }
    
    // Handle material upload form
    static handleUpload() {
        const form = document.getElementById('uploadForm');
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Uploading...';
        
        fetch(`/api/teacher/material/upload/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Material uploaded successfully', 'success');
                bootstrap.Modal.getInstance(document.getElementById('uploadModal')).hide();
                location.reload();
            } else {
                showToast('Error uploading material: ' + data.message, 'error');
            }
        })
        .catch(error => {
            showToast('Error uploading material', 'error');
            console.error('Error:', error);
        })
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        });
    }
    
    // Delete material
    static deleteMaterial(materialId) {
        if (confirm('Are you sure you want to delete this material?')) {
            fetch(`/api/teacher/material/${materialId}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const materialCard = document.querySelector(`[data-material-id="${materialId}"]`);
                    if (materialCard) {
                        materialCard.remove();
                    }
                    showToast('Material deleted successfully', 'success');
                } else {
                    showToast('Error deleting material: ' + data.message, 'error');
                }
            })
            .catch(error => {
                showToast('Error deleting material', 'error');
                console.error('Error:', error);
            });
        }
    }
}

// Class Management
class ClassManagement {
    
    // View class details
    static viewClassDetails(classId) {
        const modal = new bootstrap.Modal(document.getElementById('classDetailModal') || createClassDetailModal());
        const modalContent = document.getElementById('classDetailContent');
        
        modalContent.innerHTML = `
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
        
        modal.show();
        
        fetch(`/api/teacher/class/${classId}/details/`, {
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const classInfo = data.class_info;
                modalContent.innerHTML = `
                    <div class="card">
                        <div class="card-header bg-success text-white">
                            <h5 class="mb-0"><i class="fas fa-chalkboard me-2"></i>${classInfo.subject_name}</h5>
                        </div>
                        <div class="card-body">
                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <p><strong>Course:</strong> ${classInfo.course}</p>
                                    <p><strong>Year:</strong> ${classInfo.year}</p>
                                    <p><strong>Section:</strong> ${classInfo.section}</p>
                                </div>
                                <div class="col-md-6">
                                    <p><strong>Total Students:</strong> ${classInfo.total_students}</p>
                                    <p><strong>Room:</strong> ${classInfo.room}</p>
                                    <p><strong>Schedule:</strong> ${classInfo.schedule}</p>
                                </div>
                            </div>
                            
                            <h6><i class="fas fa-chart-bar me-2"></i>Attendance Statistics</h6>
                            <div class="row text-center mb-3">
                                <div class="col-4">
                                    <h4 class="text-success">${classInfo.attendance_stats.average_percentage}%</h4>
                                    <small class="text-muted">Average Attendance</small>
                                </div>
                                <div class="col-4">
                                    <h4 class="text-primary">${classInfo.attendance_stats.classes_held}</h4>
                                    <small class="text-muted">Classes Held</small>
                                </div>
                                <div class="col-4">
                                    <h4 class="text-info">${classInfo.attendance_stats.total_present}</h4>
                                    <small class="text-muted">Total Present</small>
                                </div>
                            </div>
                            
                            <h6><i class="fas fa-users me-2"></i>Student List</h6>
                            <div style="max-height: 200px; overflow-y: auto;">
                                <div class="row">
                                    ${classInfo.students.map(student => `
                                        <div class="col-md-6 mb-2">
                                            <div class="border p-2 rounded">
                                                <strong>${student.name}</strong><br>
                                                <small class="text-muted">${student.roll_number}</small><br>
                                                <small class="text-info">Attendance: ${student.attendance_percentage}%</small>
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                        <div class="card-footer">
                            <button class="btn btn-primary btn-sm" onclick="markAttendance(${classId})">
                                <i class="fas fa-check me-1"></i>Mark Attendance
                            </button>
                            <button class="btn btn-info btn-sm" onclick="generateReport(${classInfo.subject_id})">
                                <i class="fas fa-file-pdf me-1"></i>Generate Report
                            </button>
                        </div>
                    </div>
                `;
            }
        });
    }
    
    // Send class announcement
    static sendAnnouncement(classId) {
        const modal = new bootstrap.Modal(document.getElementById('announcementModal') || createAnnouncementModal());
        modal.show();
        
        // Set class ID in form
        document.getElementById('announcementForm').dataset.classId = classId;
    }
    
    // Handle announcement form submission
    static handleAnnouncement() {
        const form = document.getElementById('announcementForm');
        const formData = new FormData(form);
        const classId = form.dataset.classId;
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Sending...';
        
        formData.append('class_id', classId);
        
        fetch('/api/teacher/announcement/send/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Announcement sent successfully', 'success');
                bootstrap.Modal.getInstance(document.getElementById('announcementModal')).hide();
                form.reset();
            } else {
                showToast('Error sending announcement: ' + data.message, 'error');
            }
        })
        .catch(error => {
            showToast('Error sending announcement', 'error');
            console.error('Error:', error);
        })
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        });
    }
}

// Utility Functions for creating modals
function createAttendanceModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'attendanceModal';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title"><i class="fas fa-check-square me-2"></i>Mark Attendance</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="attendanceContent"></div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    return modal;
}

function createUploadModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'uploadModal';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title"><i class="fas fa-upload me-2"></i>Upload Study Material</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="uploadForm">
                        <div class="mb-3">
                            <label for="materialTitle" class="form-label">Title</label>
                            <input type="text" class="form-control" id="materialTitle" name="title" required>
                        </div>
                        <div class="mb-3">
                            <label for="materialDescription" class="form-label">Description</label>
                            <textarea class="form-control" id="materialDescription" name="description" rows="3"></textarea>
                        </div>
                        <div class="mb-3">
                            <label for="materialSubject" class="form-label">Subject</label>
                            <select class="form-select" id="materialSubject" name="subject_id" required>
                                <option value="">Select Subject</option>
                                <!-- Options will be populated dynamically -->
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="materialFile" class="form-label">File</label>
                            <input type="file" class="form-control" id="materialFile" name="file" required 
                                   accept=".pdf,.doc,.docx,.ppt,.pptx,.txt">
                            <div class="form-text">Supported formats: PDF, DOC, DOCX, PPT, PPTX, TXT</div>
                        </div>
                        <div class="text-end">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="MaterialsManagement.handleUpload()">
                                <i class="fas fa-upload me-1"></i>Upload
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    return modal;
}

function createClassDetailModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'classDetailModal';
    modal.innerHTML = `
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Class Details</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="classDetailContent"></div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    return modal;
}

function createAnnouncementModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'announcementModal';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title"><i class="fas fa-bullhorn me-2"></i>Send Announcement</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="announcementForm">
                        <div class="mb-3">
                            <label for="announcementTitle" class="form-label">Title</label>
                            <input type="text" class="form-control" id="announcementTitle" name="title" required>
                        </div>
                        <div class="mb-3">
                            <label for="announcementMessage" class="form-label">Message</label>
                            <textarea class="form-control" id="announcementMessage" name="message" rows="4" required></textarea>
                        </div>
                        <div class="mb-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="isUrgent" name="is_urgent">
                                <label class="form-check-label" for="isUrgent">
                                    <i class="fas fa-exclamation-triangle text-warning me-1"></i>Mark as Urgent
                                </label>
                            </div>
                        </div>
                        <div class="text-end">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="ClassManagement.handleAnnouncement()">
                                <i class="fas fa-paper-plane me-1"></i>Send
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    return modal;
}

// Helper functions for attendance modal
function markAllPresent() {
    const presentRadios = document.querySelectorAll('input[value="present"]');
    presentRadios.forEach(radio => {
        radio.checked = true;
    });
}

function markAllAbsent() {
    const absentRadios = document.querySelectorAll('input[value="absent"]');
    absentRadios.forEach(radio => {
        radio.checked = true;
    });
}

// Real-time synchronization
class TeacherSync {
    static init() {
        // Check for updates every 30 seconds
        setInterval(() => {
            TeacherSync.checkForUpdates();
        }, 30000);
        
        // Initial check
        TeacherSync.checkForUpdates();
    }
    
    static checkForUpdates() {
        fetch('/api/teacher/updates/', {
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.has_updates) {
                TeacherSync.showUpdateNotification();
            }
        })
        .catch(error => {
            console.log('Sync check error:', error);
        });
    }
    
    static showUpdateNotification() {
        // Only show notification if one isn't already visible
        if (!document.getElementById('sync-notification')) {
            const notification = document.createElement('div');
            notification.id = 'sync-notification';
            notification.className = 'alert alert-info alert-dismissible fade show position-fixed';
            notification.style.cssText = 'top: 20px; right: 20px; z-index: 1060; width: 300px;';
            notification.innerHTML = `
                <i class="fas fa-sync-alt me-2"></i>
                New updates available. <a href="javascript:void(0)" onclick="location.reload()">Refresh page</a>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            document.body.appendChild(notification);
            
            // Auto remove after 10 seconds
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 10000);
        }
    }
}

// Initialize real-time sync when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        TeacherSync.init();
    });
} else {
    TeacherSync.init();
}

// Make functions globally available
window.markAttendance = AttendanceManagement.markAttendance;
window.generateReport = AttendanceManagement.generateReport;
window.uploadMaterial = MaterialsManagement.uploadMaterial;
window.deleteMaterial = MaterialsManagement.deleteMaterial;
window.viewClassDetails = ClassManagement.viewClassDetails;
window.sendAnnouncement = ClassManagement.sendAnnouncement;
window.markAllPresent = markAllPresent;
window.markAllAbsent = markAllAbsent;

console.log('Teacher Management Handlers with Real-time Sync loaded successfully!');
