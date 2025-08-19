/**
 * Admin Management JavaScript Handlers
 * Handles all admin panel interactive functionality
 */

// Teacher Management Functions
class TeacherManagement {
    
    // View teacher details in modal
    static viewTeacherDetails(teacherId) {
        const modal = new bootstrap.Modal(document.getElementById('teacherDetailModal') || createTeacherDetailModal());
        const modalContent = document.getElementById('teacherDetailContent');
        
        modalContent.innerHTML = `
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
        
        modal.show();
        
        // Fetch teacher details
        fetch(`/api/admin/teachers/${teacherId}/`, {
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const teacher = data.teacher;
                modalContent.innerHTML = `
                    <div class="card">
                        <div class="card-header bg-success text-white">
                            <h5 class="mb-0"><i class="fas fa-chalkboard-teacher me-2"></i>${teacher.name}</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <p><strong>Employee ID:</strong> ${teacher.employee_id}</p>
                                    <p><strong>Department:</strong> ${teacher.department || 'Not specified'}</p>
                                    <p><strong>Designation:</strong> ${teacher.designation || 'Not specified'}</p>
                                    <p><strong>Email:</strong> ${teacher.email}</p>
                                </div>
                                <div class="col-md-6">
                                    <p><strong>Phone:</strong> ${teacher.phone_number || 'Not provided'}</p>
                                    <p><strong>Specialization:</strong> ${teacher.specialization || 'Not specified'}</p>
                                    <p><strong>Join Date:</strong> ${new Date(teacher.created_at).toLocaleDateString()}</p>
                                    <p><strong>Status:</strong> 
                                        <span class="badge ${teacher.is_active ? 'bg-success' : 'bg-danger'}">
                                            ${teacher.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </p>
                                </div>
                            </div>
                            
                            <hr>
                            
                            <h6><i class="fas fa-book me-2"></i>Assigned Subjects</h6>
                            <div class="row">
                                ${teacher.subjects.map(subject => `
                                    <div class="col-md-4 mb-2">
                                        <div class="card card-body">
                                            <strong>${subject.code}</strong><br>
                                            <small class="text-muted">${subject.name}</small><br>
                                            <small class="text-info">${subject.course} - Year ${subject.year}</small>
                                        </div>
                                    </div>
                                `).join('') || '<p class="text-muted">No subjects assigned</p>'}
                            </div>
                        </div>
                        <div class="card-footer">
                            <button class="btn btn-warning btn-sm" onclick="editTeacher(${teacherId})">
                                <i class="fas fa-edit me-1"></i>Edit Details
                            </button>
                            <button class="btn btn-info btn-sm" onclick="viewTeacherSchedule(${teacherId})">
                                <i class="fas fa-calendar me-1"></i>View Schedule
                            </button>
                        </div>
                    </div>
                `;
            } else {
                modalContent.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-circle me-2"></i>
                        Error loading teacher details: ${data.message}
                    </div>
                `;
            }
        })
        .catch(error => {
            modalContent.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Error loading teacher details. Please try again.
                </div>
            `;
            console.error('Error:', error);
        });
    }
    
    // Edit teacher information
    static editTeacher(teacherId) {
        const modal = new bootstrap.Modal(document.getElementById('editTeacherModal') || createEditTeacherModal());
        const modalContent = document.getElementById('editTeacherContent');
        
        modalContent.innerHTML = `
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
        
        modal.show();
        
        // Fetch current teacher data
        fetch(`/api/admin/teachers/${teacherId}/`, {
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const teacher = data.teacher;
                modalContent.innerHTML = `
                    <form id="editTeacherForm">
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Name</label>
                                <input type="text" class="form-control" name="name" value="${teacher.name}" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Employee ID</label>
                                <input type="text" class="form-control" name="employee_id" value="${teacher.employee_id}" required>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Department</label>
                                <input type="text" class="form-control" name="department" value="${teacher.department || ''}">
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Designation</label>
                                <input type="text" class="form-control" name="designation" value="${teacher.designation || ''}">
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Email</label>
                                <input type="email" class="form-control" name="email" value="${teacher.email}" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Phone</label>
                                <input type="text" class="form-control" name="phone_number" value="${teacher.phone_number || ''}">
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Specialization</label>
                            <textarea class="form-control" name="specialization" rows="3">${teacher.specialization || ''}</textarea>
                        </div>
                        <div class="text-end">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="submit" class="btn btn-success">
                                <i class="fas fa-save me-1"></i>Save Changes
                            </button>
                        </div>
                    </form>
                `;
                
                // Handle form submission
                document.getElementById('editTeacherForm').addEventListener('submit', function(e) {
                    e.preventDefault();
                    TeacherManagement.updateTeacher(teacherId, new FormData(this));
                });
            }
        });
    }
    
    // Update teacher information
    static updateTeacher(teacherId, formData) {
        const submitBtn = document.querySelector('#editTeacherForm button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Saving...';
        
        fetch(`/api/admin/teachers/${teacherId}/update/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Teacher updated successfully', 'success');
                bootstrap.Modal.getInstance(document.getElementById('editTeacherModal')).hide();
                // Refresh page or update table row
                location.reload();
            } else {
                showToast('Error updating teacher: ' + data.message, 'error');
            }
        })
        .catch(error => {
            showToast('Error updating teacher', 'error');
            console.error('Error:', error);
        })
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        });
    }
    
    // Remove subject assignment
    static removeAssignment(assignmentId) {
        if (confirm('Are you sure you want to remove this subject assignment?')) {
            fetch(`/api/admin/assignments/${assignmentId}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Remove row from assignments table
                    const row = document.querySelector(`tr[data-assignment-id="${assignmentId}"]`);
                    if (row) {
                        row.remove();
                    }
                    showToast('Assignment removed successfully', 'success');
                } else {
                    showToast('Error removing assignment: ' + data.message, 'error');
                }
            })
            .catch(error => {
                showToast('Error removing assignment', 'error');
                console.error('Error:', error);
            });
        }
    }

    // View teacher schedule (placeholder)
    static viewTeacherSchedule(teacherId) {
        const modalId = 'teacherScheduleModal';
        let modalEl = document.getElementById(modalId);
        if (!modalEl) {
            modalEl = document.createElement('div');
            modalEl.className = 'modal fade';
            modalEl.id = modalId;
            modalEl.innerHTML = `
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Teacher Schedule</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body" id="teacherScheduleContent">
                            <div class="text-center">
                                <div class="spinner-border" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>`;
            document.body.appendChild(modalEl);
        }
        const modal = new bootstrap.Modal(modalEl);
        const content = document.getElementById('teacherScheduleContent');
        content.innerHTML = `<div class="text-muted">Schedule view will be implemented. Teacher ID: ${teacherId}</div>`;
        modal.show();
    }
}

// Student Management Functions
class StudentManagement {
    
    // View student details
    static viewStudentDetails(studentId) {
        const modal = new bootstrap.Modal(document.getElementById('studentDetailModal'));
        const modalContent = document.getElementById('studentDetailContent');
        
        modalContent.innerHTML = `
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
        
        modal.show();
        
        fetch(`/api/admin/students/${studentId}/`, {
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const student = data.student;
                modalContent.innerHTML = `
                    <div class="card">
                        <div class="card-header bg-primary text-white">
                            <h5 class="mb-0"><i class="fas fa-user-graduate me-2"></i>${student.name}</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <p><strong>Roll Number:</strong> ${student.roll_number}</p>
                                    <p><strong>Course:</strong> ${student.course}</p>
                                    <p><strong>Year:</strong> ${student.year}</p>
                                    <p><strong>Section:</strong> ${student.section}</p>
                                </div>
                                <div class="col-md-6">
                                    <p><strong>Email:</strong> ${student.email}</p>
                                    <p><strong>Phone:</strong> ${student.phone || 'Not provided'}</p>
                                    <p><strong>Status:</strong> 
                                        <span class="badge ${student.is_active ? 'bg-success' : 'bg-danger'}">
                                            ${student.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </p>
                                    <p><strong>Verified:</strong> 
                                        <span class="badge ${student.is_verified ? 'bg-info' : 'bg-warning'}">
                                            ${student.is_verified ? 'Verified' : 'Unverified'}
                                        </span>
                                    </p>
                                </div>
                            </div>
                            
                            <hr>
                            
                            <h6><i class="fas fa-book me-2"></i>Enrolled Subjects</h6>
                            <div class="row">
                                ${student.enrollments.map(enrollment => `
                                    <div class="col-md-4 mb-2">
                                        <div class="card card-body">
                                            <strong>${enrollment.subject_code}</strong><br>
                                            <small class="text-muted">${enrollment.subject_name}</small><br>
                                            <small class="text-info">Semester ${enrollment.semester}</small>
                                        </div>
                                    </div>
                                `).join('') || '<p class="text-muted">No subject enrollments</p>'}
                            </div>
                            
                            <hr>
                            
                            <h6><i class="fas fa-chart-bar me-2"></i>Attendance Summary</h6>
                            <div class="row text-center">
                                <div class="col-4">
                                    <h4 class="text-success">${student.attendance_stats.percentage}%</h4>
                                    <small class="text-muted">Overall Attendance</small>
                                </div>
                                <div class="col-4">
                                    <h4 class="text-primary">${student.attendance_stats.present_days}</h4>
                                    <small class="text-muted">Present Days</small>
                                </div>
                                <div class="col-4">
                                    <h4 class="text-danger">${student.attendance_stats.absent_days}</h4>
                                    <small class="text-muted">Absent Days</small>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            } else {
                modalContent.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-circle me-2"></i>
                        Error loading student details: ${data.message}
                    </div>
                `;
            }
        })
        .catch(error => {
            modalContent.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Error loading student details. Please try again.
                </div>
            `;
            console.error('Error:', error);
        });
    }
    
    // Edit student information
    static editStudent(studentId) {
        const existing = document.getElementById('editStudentModal');
        const modalEl = existing || document.createElement('div');
        if (!existing) {
            modalEl.className = 'modal fade';
            modalEl.id = 'editStudentModal';
            modalEl.innerHTML = `
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Edit Student</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body" id="editStudentContent"></div>
                    </div>
                </div>`;
            document.body.appendChild(modalEl);
        }
        const modal = new bootstrap.Modal(modalEl);
        const content = document.getElementById('editStudentContent');
        content.innerHTML = `
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>`;
        modal.show();

        fetch(`/api/admin/students/${studentId}/`, {
            headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value }
        })
        .then(r => r.json())
        .then(data => {
            if (!data.success) { content.innerHTML = `<div class="alert alert-danger">${data.message || 'Failed to load student'}</div>`; return; }
            const s = data.student;
            content.innerHTML = `
                <form id="editStudentForm">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">First Name</label>
                            <input type="text" class="form-control" name="first_name" value="${s.name.split(' ')[0] || ''}">
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Last Name</label>
                            <input type="text" class="form-control" name="last_name" value="${s.name.split(' ').slice(1).join(' ')}">
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Email</label>
                            <input type="email" class="form-control" name="email" value="${s.email}">
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Phone</label>
                            <input type="text" class="form-control" name="phone_number" value="${s.phone || ''}">
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <label class="form-label">Roll Number</label>
                            <input type="text" class="form-control" name="roll_number" value="${s.roll_number}">
                        </div>
                        <div class="col-md-4 mb-3">
                            <label class="form-label">Course</label>
                            <input type="text" class="form-control" name="course" value="${s.course}">
                        </div>
                        <div class="col-md-2 mb-3">
                            <label class="form-label">Year</label>
                            <input type="number" class="form-control" name="year" value="${s.year}">
                        </div>
                        <div class="col-md-2 mb-3">
                            <label class="form-label">Section</label>
                            <input type="text" class="form-control" name="section" value="${s.section}">
                        </div>
                    </div>
                    <div class="form-check mb-3">
                        <input class="form-check-input" type="checkbox" name="is_active" id="studentActive" ${s.is_active ? 'checked' : ''}>
                        <label class="form-check-label" for="studentActive">Active</label>
                    </div>
                    <div class="text-end">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="submit" class="btn btn-success"><i class="fas fa-save me-1"></i>Save Changes</button>
                    </div>
                </form>`;

            document.getElementById('editStudentForm').addEventListener('submit', function(e) {
                e.preventDefault();
                const btn = this.querySelector('button[type="submit"]');
                const orig = btn.innerHTML; btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Saving...';
                const formData = new FormData(this);
                fetch(`/api/admin/students/${studentId}/update/`, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value },
                    body: formData
                })
                .then(r => r.json())
                .then(resp => {
                    if (resp.success) {
                        showToast('Student updated successfully', 'success');
                        modal.hide();
                        location.reload();
                    } else {
                        showToast('Error updating student: ' + (resp.message || 'Unknown error'), 'error');
                    }
                })
                .catch(err => { showToast('Error updating student', 'error'); console.error(err); })
                .finally(() => { btn.disabled = false; btn.innerHTML = orig; });
            });
        })
        .catch(err => { content.innerHTML = `<div class=\"alert alert-danger\">Failed to load student</div>`; console.error(err); });
    }
    
    // Toggle student account status
    static toggleStudentStatus(studentId, currentStatus) {
        const action = currentStatus ? 'deactivate' : 'activate';
        
        if (confirm(`Are you sure you want to ${action} this student account?`)) {
            fetch(`/api/admin/students/${studentId}/toggle-status/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ is_active: !currentStatus })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast(`Student ${action}d successfully`, 'success');
                    location.reload();
                } else {
                    showToast(`Error ${action}ing student: ${data.message}`, 'error');
                }
            })
            .catch(error => {
                showToast(`Error ${action}ing student`, 'error');
                console.error('Error:', error);
            });
        }
    }
    
    // Export students data
    static exportStudents() {
        const button = event.target;
        const originalText = button.innerHTML;
        
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Exporting...';
        
        fetch('/api/admin/students/export/', {
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
            a.download = `students_export_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            showToast('Students data exported successfully', 'success');
        })
        .catch(error => {
            showToast('Error exporting students data', 'error');
            console.error('Error:', error);
        })
        .finally(() => {
            button.disabled = false;
            button.innerHTML = originalText;
        });
    }
}

// Timetable Management Functions
class TimetableManagement {
    
    // Edit timetable entry
    static editEntry(entryId) {
        const modal = new bootstrap.Modal(document.getElementById('editEntryModal'));
        const modalBody = document.querySelector('#editEntryModal .modal-body');
        
        modalBody.innerHTML = `
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
        
        modal.show();
        
        fetch(`/api/admin/timetable/${entryId}/`, {
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const entry = data.entry;
                modalBody.innerHTML = `
                    <form id="editEntryForm">
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Course</label>
                                <select class="form-select" name="course" required>
                                    ${data.courses.map(course => 
                                        `<option value="${course.name}" ${course.name === entry.course ? 'selected' : ''}>${course.name}</option>`
                                    ).join('')}
                                </select>
                            </div>
                            <div class="col-md-3 mb-3">
                                <label class="form-label">Year</label>
                                <select class="form-select" name="year" required>
                                    <option value="1" ${entry.year == 1 ? 'selected' : ''}>1st Year</option>
                                    <option value="2" ${entry.year == 2 ? 'selected' : ''}>2nd Year</option>
                                    <option value="3" ${entry.year == 3 ? 'selected' : ''}>3rd Year</option>
                                    <option value="4" ${entry.year == 4 ? 'selected' : ''}>4th Year</option>
                                </select>
                            </div>
                            <div class="col-md-3 mb-3">
                                <label class="form-label">Section</label>
                                <input type="text" class="form-control" name="section" value="${entry.section}" required>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Subject</label>
                                <select class="form-select" name="subject_id" required>
                                    ${data.subjects.map(subject => 
                                        `<option value="${subject.id}" ${subject.id == entry.subject_id ? 'selected' : ''}>${subject.code} - ${subject.name}</option>`
                                    ).join('')}
                                </select>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Teacher</label>
                                <select class="form-select" name="teacher_id" required>
                                    ${data.teachers.map(teacher => 
                                        `<option value="${teacher.id}" ${teacher.id == entry.teacher_id ? 'selected' : ''}>${teacher.name}</option>`
                                    ).join('')}
                                </select>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-4 mb-3">
                                <label class="form-label">Day</label>
                                <select class="form-select" name="day_of_week" required>
                                    <option value="1" ${entry.day_of_week == 1 ? 'selected' : ''}>Monday</option>
                                    <option value="2" ${entry.day_of_week == 2 ? 'selected' : ''}>Tuesday</option>
                                    <option value="3" ${entry.day_of_week == 3 ? 'selected' : ''}>Wednesday</option>
                                    <option value="4" ${entry.day_of_week == 4 ? 'selected' : ''}>Thursday</option>
                                    <option value="5" ${entry.day_of_week == 5 ? 'selected' : ''}>Friday</option>
                                    <option value="6" ${entry.day_of_week == 6 ? 'selected' : ''}>Saturday</option>
                                </select>
                            </div>
                            <div class="col-md-4 mb-3">
                                <label class="form-label">Time Slot</label>
                                <select class="form-select" name="time_slot_id" required>
                                    ${data.time_slots.map(slot => 
                                        `<option value="${slot.id}" ${slot.id == entry.time_slot_id ? 'selected' : ''}>Period ${slot.period_number}</option>`
                                    ).join('')}
                                </select>
                            </div>
                            <div class="col-md-4 mb-3">
                                <label class="form-label">Room</label>
                                <select class="form-select" name="room_id" required>
                                    ${data.rooms.map(room => 
                                        `<option value="${room.id}" ${room.id == entry.room_id ? 'selected' : ''}>${room.room_number}</option>`
                                    ).join('')}
                                </select>
                            </div>
                        </div>
                        <div class="text-end">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-save me-1"></i>Update Entry
                            </button>
                        </div>
                    </form>
                `;
                
                // Handle form submission
                document.getElementById('editEntryForm').addEventListener('submit', function(e) {
                    e.preventDefault();
                    TimetableManagement.updateEntry(entryId, new FormData(this));
                });
            }
        });
    }

    // Apply AI suggestion (placeholder)
    static applySuggestion(suggestionId) {
        if (!confirm('Apply this AI suggestion to the timetable?')) return;
        // Placeholder success UI
        showToast('AI suggestion applied (placeholder).', 'success');
        const modalEl = document.getElementById('suggestionModal');
        if (modalEl) {
            const m = bootstrap.Modal.getInstance(modalEl);
            m && m.hide();
        }
    }
    
    // Update timetable entry
    static updateEntry(entryId, formData) {
        const submitBtn = document.querySelector('#editEntryForm button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Updating...';
        
        fetch(`/api/admin/timetable/${entryId}/update/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Timetable entry updated successfully', 'success');
                bootstrap.Modal.getInstance(document.getElementById('editEntryModal')).hide();
                location.reload();
            } else {
                showToast('Error updating entry: ' + data.message, 'error');
            }
        })
        .catch(error => {
            showToast('Error updating entry', 'error');
            console.error('Error:', error);
        })
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        });
    }
    
    // Delete timetable entry
    static deleteEntry(entryId) {
        if (confirm('Are you sure you want to delete this timetable entry?')) {
            fetch(`/api/admin/timetable/${entryId}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Remove row from table
                    const row = document.querySelector(`tr[data-entry-id="${entryId}"]`);
                    if (row && row.parentNode) {
                        try { row.remove(); } catch (_) { row.parentNode.removeChild(row); }
                    }
                    showToast('Timetable entry deleted successfully', 'success');
                } else {
                    showToast('Error deleting entry: ' + data.message, 'error');
                }
            })
            .catch(error => {
                showToast('Error deleting entry', 'error');
                console.error('Error:', error);
            });
        }
    }
    
    // View AI suggestion details
    static viewSuggestion(suggestionId) {
        const modal = new bootstrap.Modal(document.getElementById('suggestionModal') || createSuggestionModal());
        const modalContent = document.getElementById('suggestionContent');
        
        modalContent.innerHTML = `
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
        
        modal.show();
        
        fetch(`/api/admin/ai-suggestions/${suggestionId}/`, {
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 401) throw new Error('Please log in to view AI suggestions.');
                if (response.status === 403) throw new Error('You do not have permission to view this suggestion.');
                if (response.status === 404) throw new Error('AI suggestion not found.');
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                const suggestion = data.suggestion;
                modalContent.innerHTML = `
                    <div class="card">
                        <div class="card-header bg-info text-white">
                            <h5 class="mb-0"><i class="fas fa-cogs me-2"></i>Timetable Suggestion (Algorithmic)</h5>
                        </div>
                        <div class="card-body">
                            <div class="row mb-3">
                                <div class="col-md-4">
                                    <strong>Course:</strong> ${suggestion.course}<br>
                                    <strong>Year:</strong> ${suggestion.year}<br>
                                    <strong>Section:</strong> ${suggestion.section}
                                </div>
                                <div class="col-md-4">
                                    <strong>Generated:</strong> ${new Date(suggestion.created_at).toLocaleDateString()}<br>
                                    <strong>Optimization Score:</strong> ${suggestion.optimization_score}/100<br>
                                    <strong>Status:</strong> ${suggestion.is_applied ? 'Applied' : 'Pending'}
                                </div>
                                <div class="col-md-4">
                                    <div class="text-center">
                                        <div class="progress mb-2">
                                            <div class="progress-bar ${suggestion.optimization_score > 80 ? 'bg-success' : suggestion.optimization_score > 60 ? 'bg-warning' : 'bg-danger'}" 
                                                 style="width: ${suggestion.optimization_score}%"></div>
                                        </div>
                                        <small class="text-muted">Optimization Level</small>
                                    </div>
                                </div>
                            </div>
                            
                            <h6><i class="fas fa-lightbulb me-2"></i>Analysis</h6>
                            <div class="alert alert-info">
                                ${suggestion.analysis || 'This suggestion balances teacher load, avoids double-booking, and spreads subject periods across the week.'}
                            </div>
                            
                            <h6><i class="fas fa-calendar-alt me-2"></i>Suggested Schedule</h6>
                            ${renderSuggestionGrid(suggestion.grid)}
                        </div>
                        <div class="card-footer">
                            ${!suggestion.is_applied ? `
                                <button class="btn btn-success btn-sm" onclick="applySuggestion(${suggestionId})">
                                    <i class="fas fa-check me-1"></i>Apply Suggestion
                                </button>
                            ` : ''}
                            <button class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                `;
            } else {
                showToast('Error loading suggestion: ' + (data.message || 'Unknown error'), 'error');
            }
        })
        .catch(err => {
            showToast(err.message || 'Error loading AI suggestion', 'error');
            console.error(err);
        });
    }
    
    // Export timetable
    static exportTimetable() {
        const button = event.target;
        const originalText = button.innerHTML;
        
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Exporting...';
        
        fetch('/api/admin/timetable/export/', {
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
            a.download = `timetable_export_${new Date().toISOString().split('T')[0]}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            showToast('Timetable exported successfully', 'success');
        })
        .catch(error => {
            showToast('Error exporting timetable', 'error');
            console.error('Error:', error);
        })
        .finally(() => {
            button.disabled = false;
            button.innerHTML = originalText;
        });
    }
    
    // Filter timetable grid
    static filterGrid() {
        const course = document.getElementById('gridCourse').value;
        const year = document.getElementById('gridYear').value;
        const section = document.getElementById('gridSection').value;
        
        // Clear and re-populate based on filters
        const cells = document.querySelectorAll('.timetable-cell');
        cells.forEach(cell => cell.innerHTML = '');
        
        const params = new URLSearchParams();
        if (course) params.append('course', course);
        if (year) params.append('year', year);
        if (section) params.append('section', section);
        
        fetch(`/api/admin/timetable/entries/?${params}`, {
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                data.entries.forEach(entry => {
                    const cell = document.getElementById(`cell_${entry.day_of_week}_${entry.period_number}`);
                    if (cell) {
                        cell.innerHTML = `
                            <div class="timetable-entry">
                                <strong>${entry.subject_code}</strong><br>
                                <small>${entry.course} Y${entry.year}${entry.section}</small><br>
                                <small>${entry.teacher_name}</small><br>
                                <small>${entry.room_number}</small>
                            </div>
                        `;
                    }
                });
                showToast(`Filtered timetable for ${course} ${year ? 'Year ' + year : ''} ${section || ''}`, 'info');
            }
        })
        .catch(error => {
            showToast('Error filtering timetable', 'error');
            console.error('Error:', error);
        });
    }
}

// Utility Functions
function createTeacherDetailModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'teacherDetailModal';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Teacher Details</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="teacherDetailContent"></div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    return modal;
}

function createEditTeacherModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'editTeacherModal';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Edit Teacher</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="editTeacherContent"></div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    return modal;
}

function createSuggestionModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'suggestionModal';
    modal.innerHTML = `
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">AI Timetable Suggestion</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="suggestionContent"></div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    return modal;
}

// Toast notification function (enhanced version)
function showToast(message, type = 'info') {
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="${icons[type] || icons.info} me-2"></i>${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: type === 'error' ? 5000 : 3000
    });
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Render a DB-backed suggestion grid
function renderSuggestionGrid(grid) {
    if (!grid || Object.keys(grid).length === 0) {
        return '<div class="alert alert-secondary">No suggested grid available.</div>';
    }
    const dayMap = { '1': 'Monday', '2': 'Tuesday', '3': 'Wednesday', '4': 'Thursday', '5': 'Friday' };
    const periods = new Set();
    Object.values(grid).forEach(rows => rows.forEach(r => periods.add(r.period_number)));
    const sortedPeriods = Array.from(periods).sort((a,b)=>a-b);
    let thead = '<thead><tr><th>Day</th>' + sortedPeriods.map(p=>`<th>Period ${p}</th>`).join('') + '</tr></thead>';
    let tbody = '<tbody>' + Object.keys(grid).sort().map(day => {
        const rowSlots = grid[day];
        const rowMap = {};
        rowSlots.forEach(s => { rowMap[s.period_number] = s; });
        const cells = sortedPeriods.map(p => {
            const s = rowMap[p];
            return `<td class="text-center">${s ? `<strong>${s.subject_code}</strong><br><small>${s.subject_name}${s.teacher_name ? '<br><em class=\'text-muted\'>' + s.teacher_name + '</em>' : ''}</small>` : '-'}</td>`;
        }).join('');
        return `<tr><td><strong>${dayMap[day] || day}</strong></td>${cells}</tr>`;
    }).join('') + '</tbody>';
    return `<div class="table-responsive"><table class="table table-sm table-bordered">${thead}${tbody}</table></div>`;
}

// Make functions globally available
window.viewTeacherDetails = TeacherManagement.viewTeacherDetails;
window.editTeacher = TeacherManagement.editTeacher;
window.removeAssignment = TeacherManagement.removeAssignment;
window.viewTeacherSchedule = TeacherManagement.viewTeacherSchedule;

window.viewStudentDetails = StudentManagement.viewStudentDetails;
window.editStudent = StudentManagement.editStudent;
window.toggleStudentStatus = StudentManagement.toggleStudentStatus;
window.exportStudents = StudentManagement.exportStudents;

window.editEntry = TimetableManagement.editEntry;
window.deleteEntry = TimetableManagement.deleteEntry;
window.viewSuggestion = TimetableManagement.viewSuggestion;
window.applySuggestion = TimetableManagement.applySuggestion;
window.exportTimetable = TimetableManagement.exportTimetable;
window.filterGrid = TimetableManagement.filterGrid;

window.showToast = showToast;

console.log('Admin Management Handlers loaded successfully!');
